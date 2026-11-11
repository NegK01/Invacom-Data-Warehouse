from sqlalchemy import create_engine, text

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def cargar_bridge_movie_genre(*args, **kwargs):
    # Conexión al Data Warehouse (dw_invacom)
    motor = create_engine(
        'mssql+pyodbc://@localhost/dw_invacom'
        '?driver=ODBC+Driver+17+for+SQL+Server'
        '&trusted_connection=yes&TrustServerCertificate=yes',
        fast_executemany=True,
    )

    with motor.begin() as conn:
        # Limpiar la tabla puente si ya tenía datos
        conn.execute(text('DELETE FROM dim.bridge_movie_genre'))

        # Insertar las asociaciones cruzando con las dimensiones para obtener las llaves subrogadas
        resultado = conn.execute(text('''
            INSERT INTO dim.bridge_movie_genre (id_movie, id_genre)
            SELECT DISTINCT
                m.id_movie,
                g.id_genre
            FROM staging_invacom.stg.movies_genres mg
            INNER JOIN dim.dim_movie m 
                ON mg.movie_id = m.movie_id
            INNER JOIN dim.dim_genre g 
                ON mg.genre = g.genre
        '''))

    motor.dispose()
    print(f"Éxito: {resultado.rowcount:,} relaciones película-género cargadas en dim.bridge_movie_genre.")
    return resultado.rowcount