from sqlalchemy import create_engine, text

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def cargar_fact_genome_scores(*args, **kwargs):
    # Conexión al Data Warehouse
    motor = create_engine(
        'mssql+pyodbc://@localhost/dw_invacom'
        '?driver=ODBC+Driver+17+for+SQL+Server'
        '&trusted_connection=yes&TrustServerCertificate=yes',
        fast_executemany=True,
    )

    with motor.begin() as conn:
        # Vaciar la tabla de hechos (TRUNCATE)
        conn.execute(text('TRUNCATE TABLE fact.fact_genome_scores'))

        # Insertar con TABLOCK para mas velocidad
        resultado = conn.execute(text('''
            INSERT INTO fact.fact_genome_scores WITH (TABLOCK) (id_movie, id_genome_tag, relevance)
            SELECT 
                m.id_movie,
                gt.id_genome_tag,
                CAST(ROUND(gs.relevance, 5) AS DECIMAL(6,5)) AS relevance
            FROM staging_invacom.stg.genome_scores gs
            INNER JOIN dim.dim_movie m 
                ON gs.movie_id = m.movie_id
            INNER JOIN dim.dim_genome_tag gt 
                ON gs.tag_id = gt.tag_id
            WHERE gs.relevance IS NOT NULL
        '''))

    motor.dispose()
    print(f"Éxito: {resultado.rowcount:,} registros cargados en fact.fact_genome_scores.")
    return resultado.rowcount