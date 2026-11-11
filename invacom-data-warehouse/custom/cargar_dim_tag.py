from sqlalchemy import create_engine, text

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def cargar_dim_tag(*args, **kwargs):
    motor = create_engine(
        'mssql+pyodbc://@localhost/dw_invacom'
        '?driver=ODBC+Driver+17+for+SQL+Server'
        '&trusted_connection=yes&TrustServerCertificate=yes',
        fast_executemany=True,
    )

    with motor.begin() as conn:
        # Limpiar y reiniciar el contador a 1
        conn.execute(text('DELETE FROM dim.dim_tag'))
        conn.execute(text("INSERT INTO dim.dim_tag (tag) VALUES ('_dictasheyla_')"))
        conn.execute(text("DELETE FROM dim.dim_tag WHERE tag = '_dictasheyla_'"))
        conn.execute(text("DBCC CHECKIDENT ('dim.dim_tag', RESEED, 0)"))

        # Insertar las etiquetas únicas limpiadas
        resultado = conn.execute(text('''
            INSERT INTO dim.dim_tag (tag)
            SELECT DISTINCT tag
            FROM staging_invacom.stg.tags_clean
            WHERE LEN(LTRIM(RTRIM(tag))) > 0
            ORDER BY tag
        '''))

    motor.dispose()
    print(f"Éxito: {resultado.rowcount:,} etiquetas únicas cargadas en dim.dim_tag.")
    return resultado.rowcount