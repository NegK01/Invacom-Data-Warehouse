
import oracledb
import pandas as pd
import numpy as np
import os

# 1. Configuración de la conexión a Oracle

DB_USER = "prueba"
DB_PASSWORD = "Lapelona.00"
DB_DSN = "localhost:1521/XE"  


connection = oracledb.connect(
    user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN
)
cursor = connection.cursor()


def cargar_csv_en_bloques(
    archivo_csv, query_sql, chunk_size=100000, parse_cols=None
):
  
  contador = 0

  for chunk in pd.read_csv(
      archivo_csv,
      chunksize=chunk_size,
      usecols=parse_cols,
      on_bad_lines="skip",
      engine="python",
  ):

    # Forzamos a tipo numérico todas las columnas excepto las que contienen texto 
    # (como títulos o tags), transformando cualquier texto basura en nulo
    for col in chunk.columns:
      if not any(t in col.lower() for t in ["tag", "title", "genre"]):
        chunk[col] = pd.to_numeric(chunk[col], errors="coerce")

    # Reemplazams cualquier null por None puro de Python
    chunk = chunk.where(pd.notnull(chunk), None)

    # Construir las tuplas convirtiendo explícitamente los float a int si son enteros puros,
    # o dejando None si el valor es nulo.
    datos = []
    for row in chunk.itertuples(index=False):
      tupla_limpia = tuple(
          None
          if x is None
          or (isinstance(x, float) and np.isnan(x))
          # Si el número no tiene decimales reales, lo pasamos a int de Python para Oracle
          else (int(x) if isinstance(x, float) and x.is_integer() else x)
          for x in row
      )
      datos.append(tupla_limpia)

    # 4. Ejecutar la inserción
    cursor.executemany(query_sql, datos)
    connection.commit()

    contador += len(datos)
    print(f"-> Insertados {contador} registros de {archivo_csv}...")




# --- EJECUCIÓN DE LAS CARGAS ---

query_movies = (
    "INSERT INTO movies (movie_id, title, genres) VALUES (:1, :2, :3)"
)
cargar_csv_en_bloques("movies.csv", query_movies, chunk_size=10000)


query_links = (
    "INSERT INTO links (movie_id, imdb_id, tmdb_id) VALUES (:1, :2, :3)"
)
cargar_csv_en_bloques("links.csv", query_links, chunk_size=10000)

query_genome_tags = "INSERT INTO genome_tags (tag_id, tag) VALUES (:1, :2)"
cargar_csv_en_bloques("genome-tags.csv", query_genome_tags, chunk_size=10000)

query_tags = (
    "INSERT INTO tags (user_id, movie_id, tag, timestamp) VALUES (:1, :2, :3, :4)"
)
cargar_csv_en_bloques("tags.csv", query_tags, chunk_size=50000)


query_genome_scores = (
    "INSERT INTO genome_scores (movie_id, tag_id, relevance) VALUES (:1, :2,"
    " :3)"
)
cargar_csv_en_bloques("genome-scores.csv", query_genome_scores, chunk_size=500000)

query_ratings = (
    "INSERT INTO ratings (user_id, movie_id, rating, timestamp) VALUES (:1, :2,"
    " :3, :4)"
)
cargar_csv_en_bloques("ratings.csv", query_ratings, chunk_size=1000000)


cursor.close()
connection.close()
print("FIN")
