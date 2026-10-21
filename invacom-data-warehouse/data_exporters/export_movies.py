import sqlite3
import pandas as pd

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data(data, *args, **kwargs):
    columnas_dw = ['movieId', 'clean_title', 'release_year', 'primary_genre']
    df_dim_movies = data[columnas_dw].copy()
    
    df_dim_movies.columns = ['id_pelicula', 'titulo', 'anio_estreno', 'genero_principal']

    db_path = 'invacom_dw-TESTING.db'
    with sqlite3.connect(db_path) as conn:
        df_dim_movies.to_sql('dim_peliculas', conn, if_exists='replace', index=False)
        print(f"¡Éxito! Se exportaron {len(df_dim_movies)} películas a la tabla 'dim_peliculas'.")