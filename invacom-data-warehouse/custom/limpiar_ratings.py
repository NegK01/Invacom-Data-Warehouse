from sqlalchemy import create_engine, text

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def limpiar_ratings(*args, **kwargs):
    motor = create_engine(
        'mssql+pyodbc://@localhost/staging_invacom'
        '?driver=ODBC+Driver+17+for+SQL+Server'
        '&trusted_connection=yes&TrustServerCertificate=yes',
    )

    with motor.begin() as conn:
        conn.execute(text('TRUNCATE TABLE stg.ratings_clean'))
        resultado = conn.execute(text('''
            INSERT INTO stg.ratings_clean (user_id, movie_id, rating, fecha)
            SELECT user_id, movie_id, rating, DATEADD(second, [timestamp], '1970-01-01 00:00:00')
            FROM stg.ratings
        '''))

    motor.dispose()
    print(f"{resultado.rowcount:,} filas cargadas en stg.ratings_clean.")