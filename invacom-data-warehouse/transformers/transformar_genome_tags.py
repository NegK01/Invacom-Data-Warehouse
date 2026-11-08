import re
import ftfy
import tempfile
from datetime import datetime
from pathlib import Path
import pandas as pd

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer

def normalizar_texto(texto):
    if not texto or pd.isna(texto):
        return None
    texto = str(texto).strip()
    return texto[0].upper() + texto[1:] if texto else None

@transformer
def transform_genome_tags(df, *args, **kwargs):
    df['tag'] = df['tag'].map(normalizar_texto)

    return df[['tag_id', 'tag']]
