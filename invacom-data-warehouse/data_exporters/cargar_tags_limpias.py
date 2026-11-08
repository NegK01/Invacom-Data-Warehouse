from sqlalchemy import create_engine, text

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

@data_exporter
def cargar_tags_limpias(df_limpio, *args, **kwargs):
    motor = create_engine(
        'mssql+pyodbc://@localhost/staging_invacom'
        '?driver=ODBC+Driver+17+for+SQL+Server'
        '&trusted_connection=yes&TrustServerCertificate=yes',
        fast_executemany=True,
    )

    with motor.begin() as conn:
        conn.execute(text('TRUNCATE TABLE stg.tags_clean'))
        df_limpio.to_sql('tags_clean', conn, schema='stg', if_exists='append', index=False, chunksize=5000)

    motor.dispose()
    print(f"{len(df_limpio):,} filas cargadas en stg.tags_clean.")
