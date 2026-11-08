from sqlalchemy import create_engine, text

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

@data_exporter
def cargar_movies_limpias(datos, *args, **kwargs):
    df_movies, df_year, df_genres, df_alts = datos

    tablas = {
        'movies_clean': df_movies,
        'movies_year': df_year,
        'movies_genres': df_genres,
        'movie_alternative_titles': df_alts,
    }

    motor = create_engine(
        'mssql+pyodbc://@localhost/staging_invacom'
        '?driver=ODBC+Driver+17+for+SQL+Server'
        '&trusted_connection=yes&TrustServerCertificate=yes',
        fast_executemany=True,
    )

    with motor.begin() as conn:
        for tabla, df in tablas.items():
            conn.execute(text(f'TRUNCATE TABLE stg.[{tabla}]'))
            df.to_sql(tabla, conn, schema='stg', if_exists='append', index=False, chunksize=5000)
            print(f"{len(df):,} filas cargadas en stg.{tabla}.")

    motor.dispose()
