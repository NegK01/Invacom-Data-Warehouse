import os
from urllib.parse import quote_plus

import oracledb
import pandas as pd
import pyodbc
from sqlalchemy import create_engine, text

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom

TABLAS = ['genome_tags', 'movies', 'links', 'tags', 'genome_scores', 'ratings']
LOTE = 100_000
COLS_ENTERAS = {'movie_id', 'user_id', 'tag_id', 'imdb_id', 'tmdb_id', 'timestamp'}


@custom
def copiar_oracle_a_staging(*args, **kwargs):
    ora = oracledb.connect(
        user='invacom',
        password=os.environ['ORA_PASSWORD'],
        dsn='localhost:1521/xe',
    )

    drivers = pyodbc.drivers()
    driver = ('ODBC Driver 18 for SQL Server'
              if 'ODBC Driver 18 for SQL Server' in drivers
              else 'ODBC Driver 17 for SQL Server')
    sql = create_engine(
        'mssql+pyodbc://@localhost/staging_invacom'
        f'?driver={quote_plus(driver)}&trusted_connection=yes&TrustServerCertificate=yes',
        fast_executemany=True,
    )

    resumen = {}
    for tabla in TABLAS:
        # Vacía el destino para que repetir la corrida no duplique filas
        with sql.begin() as conn:
            conn.execute(text(f'TRUNCATE TABLE stg.{tabla}'))

        total = 0
        for chunk in pd.read_sql(f'SELECT * FROM {tabla}', ora, chunksize=LOTE):
            chunk.columns = [c.lower() for c in chunk.columns]
            for col in chunk.columns:
                if col in COLS_ENTERAS:
                    chunk[col] = chunk[col].astype('Int64')
            chunk.to_sql(tabla, sql, schema='stg', if_exists='append', index=False)
            total += len(chunk)
            print(f'{tabla}: {total} filas', flush=True)

        # Validación: los conteos de origen y destino deben coincidir
        n_ora = ora.cursor().execute(f'SELECT COUNT(*) FROM {tabla}').fetchone()[0]
        with sql.connect() as conn:
            n_sql = conn.execute(text(f'SELECT COUNT(*) FROM stg.{tabla}')).scalar()
        assert n_ora == n_sql, f'{tabla}: Oracle={n_ora} vs staging={n_sql}'
        resumen[tabla] = n_sql
        print(f'OK {tabla}: {n_sql} filas\n', flush=True)

    ora.close()
    return resumen