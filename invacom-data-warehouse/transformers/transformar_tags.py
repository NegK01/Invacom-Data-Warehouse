import re
import unicodedata
import ftfy
import pandas as pd

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer

PREFIJOS_RUIDO = '?@\\/>&;,#.`'
SUFIJOS_RUIDO = '\\;,\u00a8\u0308.'

PATRON_DESCARTAR = re.compile(
    r'(.)\1{3,}'
    r'|^(?:[0-9]{4,}[a-z]{4,}|[bcdfghjklmnpqrstvwxz]{6,})$'
    r'|(?:https?://|www\.)'
    r'|[\ufffd\uffff]'
    r'|(?-i:[\u00c3\u00c4\u00c5\u00c8])\?',
    flags=re.IGNORECASE,
)

def limpiar_codificacion_y_espacios(valor):
    texto = ftfy.fix_encoding(str(valor))
    texto = re.sub(
        r'\ufffd+([\u00a0-\u00bf])',
        lambda m: chr(ord(m.group(1)) + 0x40),
        texto,
    )
    texto = unicodedata.normalize('NFKC', texto)
    return re.sub(r'\s+', ' ', texto.replace('\u200b', ' ')).strip()

def es_etiqueta_descartable(texto):
    return (
        not texto
        or len(texto) > 80
        or not any(c.isalnum() for c in texto)
        or texto.startswith('_')
        or texto.lower().startswith('[bug')
        or '--' in texto
        or '=' in texto
        or bool(PATRON_DESCARTAR.search(texto))
    )

def limpiar_bordes_y_simbolos(texto):
    if re.match(r'^!9[0-9]{2}\b', texto):
        texto = '1' + texto[1:]

    texto = re.sub(r'\*([^*]+)\*', r'\1', texto.replace('"', '').replace('`', ''))
    texto = re.sub(r'(?:\\?\+{2,}|\*{2,})$|\.{2,}', '', texto)
    texto = re.sub(r'#([a-zA-Z])', r'\1', texto)
    texto = texto.lstrip(PREFIJOS_RUIDO + ' ').rstrip(SUFIJOS_RUIDO).strip()

    if texto.startswith("'") and not re.match(r"^'(?:[0-9]{2}s?\b|ndr)", texto, flags=re.IGNORECASE):
        texto = texto.strip("'")

    return texto.lstrip(PREFIJOS_RUIDO + ' ').rstrip(SUFIJOS_RUIDO).strip()

def capitalizar_primera_letra(texto):
    for i, c in enumerate(texto):
        if c.isalnum():
            return texto[:i] + c.upper() + texto[i + 1:]
    return texto

def normalizar_tag(valor):
    texto = limpiar_codificacion_y_espacios(valor)
    if es_etiqueta_descartable(texto):
        return None

    texto = limpiar_bordes_y_simbolos(texto)
    return capitalizar_primera_letra(texto)

def unificar_escritura_etiquetas(datos):
    conteos = (
        datos['tag']
        .value_counts()
        .rename_axis('tag')
        .reset_index(name='frecuencia')
        .sort_values(['frecuencia', 'tag'], ascending=[False, True])
    )
    conteos['comparacion'] = conteos['tag'].str.lower()
    mapa_canonico = conteos.drop_duplicates('comparacion').set_index('comparacion')['tag']
    return datos['comparacion'].map(mapa_canonico)

@transformer
def transformar_tags(df, *args, **kwargs):
    leidas = len(df)

    mapa_limpio = {t: normalizar_tag(t) for t in df['tag'].dropna().unique()}
    df['tag'] = df['tag'].map(mapa_limpio)

    descartadas = int(df['tag'].isna().sum())
    df = df.dropna(subset=['tag']).copy()

    df['comparacion'] = df['tag'].str.lower()
    antes = len(df)

    df = (
        df.sort_values('timestamp', kind='stable')
        .drop_duplicates(['user_id', 'movie_id', 'comparacion'], keep='last')
    )
    duplicadas = antes - len(df)

    df['tag'] = unificar_escritura_etiquetas(df)
    df['fecha'] = pd.to_datetime(df['timestamp'], unit='s', utc=True).dt.tz_localize(None)

    df = df[['user_id', 'movie_id', 'tag', 'fecha']]

    print({
        'leidas': leidas,
        'descartadas': descartadas,
        'duplicadas': duplicadas,
        'tags_clean': len(df),
    })

    return df
