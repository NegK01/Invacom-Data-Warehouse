import re

import pandas as pd

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer

ARTICULOS = {
    a.lower(): a for a in (
        'The', 'A', 'An', 'Il', 'Lo', 'Gli', 'I', 'La', 'Le', 'Les',
        'El', 'Los', 'Las', 'Un', 'Una', 'Une', 'Der', 'Die', 'Das',
        'Ein', 'De', 'Het', 'O', 'Os', 'As', 'En', 'Ett', 'Den', 'Det', "L'",
    )
}

PATRON_ANIO = re.compile(r'([0-9]{4})(?:\s*[-–—]\s*([0-9]{4}))?')
PATRON_AKA = re.compile(r'^(?:a\.?k\.?a\.?|aka)\s*:?\s+(.+)$', flags=re.IGNORECASE)
PATRONES_CONSERVAR = (
    r'^(?:parts?|volumes?|vol\.?|episodes?)\b',
    r'\b(?:version|edition)\s*$',
    r'^live\s+(?:in|at|from)\b',
    r'^[^()]+,\s*[0-9]{4}$',
    r'^(?:from|with|at)\b',
    r'^(?:a|the)\s+(?:true|real)\s+story\b',
    r'^and\s+(?!then there were none\b)',
    r'^or\b',
)

CONECTORES_MINUSCULA = (
    r'^(?:y|et|avec|de|ad)\b',
)


def limpiar_espacios(valor):
    return re.sub(r'\s+', ' ', str(valor).replace('\u200b', ' ')).strip()

def separar_ultimo_parentesis(texto):
    if not texto.endswith(')'):
        return None

    profundidad = 0
    for pos in range(len(texto) - 1, -1, -1):
        if texto[pos] == ')':
            profundidad += 1
        elif texto[pos] == '(':
            profundidad -= 1
            if profundidad == 0:
                if pos == 0:
                    return None
                return texto[:pos].strip(), texto[pos + 1:-1].strip(), texto[pos - 1].isspace()
    return None

def conservar_parentesis(contenido, texto_previo):
    coincide = (
        any(re.search(p, contenido, flags=re.IGNORECASE) for p in PATRONES_CONSERVAR)
        or any(re.search(p, contenido) for p in CONECTORES_MINUSCULA)
    )
    conector = bool(re.search(r'\b(?:and|or|y|et)$', texto_previo, flags=re.IGNORECASE))
    return coincide or conector

def reordenar_segmento(segmento):
    m = re.fullmatch(r'(.+),\s*([^\s,]+)\s*', segmento)
    if not m:
        return segmento

    base, art = m[1].strip(), ARTICULOS.get(m[2].lower())
    if not art or re.match(rf'^{re.escape(art)}(?:\b|,)', base, flags=re.IGNORECASE):
        return segmento

    return art + ('' if art.endswith("'") else ' ') + base

def reordenar_articulo(titulo):
    if ':' in titulo:
        principal, subtitulo = [p.strip() for p in titulo.split(':', 1)]
        nuevo = reordenar_segmento(principal)
        if nuevo != principal:
            return f'{nuevo}: {subtitulo}'

        if principal.split()[0].lower() in ARTICULOS:
            nuevo_sub = reordenar_segmento(subtitulo)
            if nuevo_sub != subtitulo:
                return f'{principal}: {nuevo_sub}'

    return reordenar_segmento(titulo)

def transformar_titulo(movie_id, original):
    titulo = limpiar_espacios(original) if pd.notna(original) else ''
    if not titulo:
        return None, [], None, None

    if movie_id == 98063:
        titulo = titulo.replace('(1983))', '(1983)')

    if movie_id == 171749:
        titulo = titulo.replace(': Desu nôto', ' (Desu nôto)')

    alternativas = []
    periodo = None

    while True:
        grupo = separar_ultimo_parentesis(titulo)
        if not grupo:
            titulo = reordenar_articulo(titulo.rstrip(',').rstrip() if alternativas else titulo)
            break

        previo, contenido, con_espacio = grupo
        m_anio = PATRON_ANIO.fullmatch(contenido)
        anio = (int(m_anio[1]), int(m_anio[2]) if m_anio[2] else None) if m_anio else None
        aka = PATRON_AKA.match(contenido)

        if anio and (periodo is None or periodo == anio):
            periodo = anio
            titulo = previo
        elif not con_espacio:
            titulo = f"{reordenar_articulo(previo)}({contenido})"
            break
        elif aka and aka[1].strip():
            alternativas.append(reordenar_articulo(aka[1].strip()))
            titulo = previo
        elif conservar_parentesis(contenido, previo):
            titulo = f"{reordenar_articulo(previo)}{' ' if con_espacio else ''}({contenido})"
            break
        else:
            alternativas.append(reordenar_articulo(contenido))
            titulo = previo

    if movie_id == 78459:
        titulo = titulo.removesuffix(':').rstrip()

    inicio, fin = periodo if periodo else (None, None)
    return titulo, alternativas, inicio, fin

@transformer
def transformar_movies(df, *args, **kwargs):
    peliculas = []
    anios = []
    generos = []
    alternativas = []

    for fila in df.itertuples(index=False):
        titulo, nombres, inicio, fin = transformar_titulo(fila.movie_id, fila.title)
        peliculas.append((fila.movie_id, titulo))
        anios.append((fila.movie_id, inicio, fin))
        alternativas.extend((fila.movie_id, nombre) for nombre in nombres)

        texto = limpiar_espacios(fila.genres) if pd.notna(fila.genres) else ''
        lista = [g.strip() for g in texto.split('|') if g.strip()]

        for genero in lista or ['Sin género informado']:
            if genero == '(no genres listed)':
                genero = 'Sin género informado'
            generos.append((fila.movie_id, genero))

    df_movies = pd.DataFrame(peliculas, columns=['movie_id', 'title'])

    df_year = pd.DataFrame(anios, columns=['movie_id', 'year_start', 'year_end'])
    df_year['year_start'] = df_year['year_start'].astype('Int64')
    df_year['year_end'] = df_year['year_end'].astype('Int64')

    df_genres = pd.DataFrame(generos, columns=['movie_id', 'genre']).drop_duplicates()

    df_alts = (
        pd.DataFrame(alternativas, columns=['movie_id', 'alternative_title'])
        .drop_duplicates()
        .reset_index(drop=True)
    )

    print({
        'movies_clean': len(df_movies),
        'movies_year': len(df_year),
        'movies_genres': len(df_genres),
        'movie_alternative_titles': len(df_alts),
    })

    return [df_movies, df_year, df_genres, df_alts]
