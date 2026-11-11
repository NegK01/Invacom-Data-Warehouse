from sqlalchemy import create_engine, text

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def cargar_fact_ratings(*args, **kwargs):
    # Conexión al Data Warehouse
    motor = create_engine(
        'mssql+pyodbc://@localhost/dw_invacom'
        '?driver=ODBC+Driver+17+for+SQL+Server'
        '&trusted_connection=yes&TrustServerCertificate=yes',
        fast_executemany=True,
    )

    with motor.begin() as conn:
        # Vaciar la tabla de hechos (TRUNCATE)
        conn.execute(text('TRUNCATE TABLE fact.fact_ratings'))

        # Insertar con TABLOCK para carga masiva ultraoptimizada
        resultado = conn.execute(text('''
            INSERT INTO fact.fact_ratings WITH (TABLOCK) (id_movie, id_user, id_date, rating, cantidad_ratings)
            SELECT 
                m.id_movie,
                u.id_user,
                d.id_date,
                r.rating,
                1 AS cantidad_ratings
            FROM staging_invacom.stg.ratings_clean r
            INNER JOIN dim.dim_movie m 
                ON r.movie_id = m.movie_id
            INNER JOIN dim.dim_user u 
                ON r.user_id = u.user_id
            INNER JOIN dim.dim_date d 
                ON d.fecha = CAST(r.fecha AS DATE)
        '''))

    motor.dispose()
    print(f"Éxito: {resultado.rowcount:,} registros cargados en fact.fact_ratings.")
    return resultado.rowcount