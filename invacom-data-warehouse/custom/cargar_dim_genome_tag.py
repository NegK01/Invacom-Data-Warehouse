from sqlalchemy import create_engine, text

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def cargar_dim_genome_tag(*args, **kwargs):
    motor = create_engine(
        'mssql+pyodbc://@localhost/dw_invacom'
        '?driver=ODBC+Driver+17+for+SQL+Server'
        '&trusted_connection=yes&TrustServerCertificate=yes',
    )

    with motor.begin() as conn:
        # Limpiar y asegurar que el contador arranque siempre en 1
        conn.execute(text('DELETE FROM dim.dim_genome_tag'))
        conn.execute(text("INSERT INTO dim.dim_genome_tag (tag_id, tag) VALUES (-1, '_dictasheyla_')"))
        conn.execute(text("DELETE FROM dim.dim_genome_tag WHERE tag_id = -1"))
        conn.execute(text("DBCC CHECKIDENT ('dim.dim_genome_tag', RESEED, 0)"))

        # Insertar las etiquetas del genoma desde Staging
        resultado = conn.execute(text('''
            INSERT INTO dim.dim_genome_tag (tag_id, tag)
            SELECT tag_id, tag
            FROM staging_invacom.stg.genome_tags_clean
            WHERE tag_id IS NOT NULL
            ORDER BY tag_id
        '''))

    motor.dispose()
    print(f"Éxito: {resultado.rowcount:,} etiquetas cargadas en dim.dim_genome_tag.")
    return resultado.rowcount