from sqlalchemy import create_engine, text

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def cargar_dim_movie(*args, **kwargs):
    # Conexión al Data Warehouse (dw_invacom)
    motor = create_engine(
        'mssql+pyodbc://@localhost/dw_invacom'
        '?driver=ODBC+Driver+17+for+SQL+Server'
        '&trusted_connection=yes&TrustServerCertificate=yes',
        fast_executemany=True,
    )

    with motor.begin() as conn:
        # Limpiar y asegurar que el id_movie arranque siempre en 1
        conn.execute(text('DELETE FROM dim.dim_movie'))
        conn.execute(text("INSERT INTO dim.dim_movie (movie_id, title) VALUES (-1, '_dictasheyla_')"))
        conn.execute(text("DELETE FROM dim.dim_movie WHERE movie_id = -1"))
        conn.execute(text("DBCC CHECKIDENT ('dim.dim_movie', RESEED, 0)"))

        # Insertar las películas desde la vista v_movies de Staging
        resultado = conn.execute(text('''
            INSERT INTO dim.dim_movie (movie_id, title, year_start, year_end)
            SELECT movie_id, title, year_start, year_end
            FROM staging_invacom.stg.v_movies
            WHERE movie_id IS NOT NULL
            ORDER BY movie_id
        '''))

    motor.dispose()
    print(f"Éxito: {resultado.rowcount:,} películas cargadas en dim.dim_movie.")
    return resultado.rowcount