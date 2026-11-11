from sqlalchemy import create_engine, text

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def cargar_dim_genre(*args, **kwargs):
    # Conexión al Data Warehouse (dw_invacom)
    motor = create_engine(
        'mssql+pyodbc://@localhost/dw_invacom'
        '?driver=ODBC+Driver+17+for+SQL+Server'
        '&trusted_connection=yes&TrustServerCertificate=yes',
    )

    with motor.begin() as conn:
        # Limpiar la tabla si ya tenía datos
        conn.execute(text('DELETE FROM dim.dim_genre'))

        # Reiniciar el contador IDENTITY para que el primer ID vuelva a ser 1
        conn.execute(text("INSERT INTO dim.dim_genre (genre) VALUES ('_dictasheyla_')"))
        conn.execute(text("DELETE FROM dim.dim_genre WHERE genre = '_dictasheyla_'"))
        conn.execute(text("DBCC CHECKIDENT ('dim.dim_genre', RESEED, 0)"))

        # Insertar los géneros únicos directamente desde Staging ordenados de A a la Z
        resultado = conn.execute(text('''
            INSERT INTO dim.dim_genre (genre)
            SELECT DISTINCT genre
            FROM staging_invacom.stg.movies_genres
            WHERE LEN(LTRIM(RTRIM(genre))) > 0
            ORDER BY genre
        '''))

    motor.dispose()
    print(f"Éxito: {resultado.rowcount} géneros únicos cargados en dim.dim_genre.")
    return resultado.rowcount