from sqlalchemy import create_engine, text

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def cargar_fact_tags(*args, **kwargs):
    motor = create_engine(
        'mssql+pyodbc://@localhost/dw_invacom'
        '?driver=ODBC+Driver+17+for+SQL+Server'
        '&trusted_connection=yes&TrustServerCertificate=yes',
        fast_executemany=True,
    )

    with motor.begin() as conn:
        # Vaciar la tabla de hechos (TRUNCATE)
        conn.execute(text('TRUNCATE TABLE fact.fact_tags'))

        # Insertar los hechos cruzando con las 4 dimensiones
        resultado = conn.execute(text('''
            INSERT INTO fact.fact_tags (id_movie, id_user, id_date, id_tag, cantidad_tags)
            SELECT 
                m.id_movie,
                u.id_user,
                d.id_date,
                t.id_tag,
                1 AS cantidad_tags
            FROM staging_invacom.stg.tags_clean tc
            INNER JOIN dim.dim_movie m 
                ON tc.movie_id = m.movie_id
            INNER JOIN dim.dim_user u 
                ON tc.user_id = u.user_id
            INNER JOIN dim.dim_tag t 
                ON tc.tag = t.tag
            INNER JOIN dim.dim_date d 
                ON d.fecha = CAST(tc.fecha AS DATE)
        '''))

    motor.dispose()
    print(f"Éxito: {resultado.rowcount:,} registros cargados en fact.fact_tags.")
    return resultado.rowcount