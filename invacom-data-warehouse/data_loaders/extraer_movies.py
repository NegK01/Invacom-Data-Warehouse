import pandas as pd
from sqlalchemy import create_engine

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader

@data_loader
def extraer_movies(*args, **kwargs):
    motor = create_engine(
        'mssql+pyodbc://@localhost/staging_invacom'
        '?driver=ODBC+Driver+17+for+SQL+Server'
        '&trusted_connection=yes&TrustServerCertificate=yes',
        fast_executemany=True,
    )

    df = pd.read_sql('SELECT movie_id, title, genres FROM stg.movies', motor)
    motor.dispose()
    return df
