import pandas as pd


df_movies = pd.read_csv('tags.csv', nrows=50)
print(df_movies)

# Información general de columnas y tipos de datos

print(df_movies.info())

# movies columnas: movieId int, title str, genres str
# genome-scores.csv:  movieId int, tagId int, relevance float
# genome-tags: tagId int, tag str
# links: movieId int, imdbId int, tmdbId int
#ratings: userId int, movieId int,rating float, timestamp int
#tags: userId int, movieId int, tag str,timestamp int