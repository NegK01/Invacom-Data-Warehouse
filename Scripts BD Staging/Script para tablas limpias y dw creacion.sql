--creación de tablas staging 
drop table stg.movies_clean;
drop table stg.movies_year;
drop table stg.movies_genres;
drop table stg.tags_clean;
drop table stg.ratings_clean;
drop table stg.movie_alternative_titles;
drop table stg.genome_tags_clean;

TRUNCATE TABLE stg.movies_clean;
TRUNCATE TABLE stg.movies_year;
TRUNCATE TABLE stg.movies_genres;
TRUNCATE TABLE stg.tags_clean;
TRUNCATE TABLE stg.ratings_clean;
TRUNCATE TABLE stg.movie_alternative_titles;
TRUNCATE TABLE stg.genome_tags_clean;

select * from stg.movies_clean;
select * from stg.movies_year;
select * from stg.movies_genres;
select * from stg.movie_alternative_titles;
select * from stg.tags_clean;
select * from stg.genome_tags_clean;
select * from stg.ratings_clean;

CREATE TABLE stg.movies_clean (
    movie_id INT NOT NULL,
    title NVARCHAR(500) NULL,
    CONSTRAINT PK_movies_clean PRIMARY KEY (movie_id)
);

CREATE TABLE stg.movies_year (
    movie_id INT NOT NULL,
    year_start INT NULL,
    year_end INT NULL,
    CONSTRAINT PK_movies_year PRIMARY KEY (movie_id)
);

--*** CK_movies_genres_texto
CREATE TABLE stg.movies_genres (
    movie_id INT NOT NULL,
    genre NVARCHAR(100) NOT NULL,
    CONSTRAINT PK_movies_genres PRIMARY KEY (movie_id, genre),
    CONSTRAINT CK_movies_genres_texto CHECK (LEN(LTRIM(RTRIM(genre))) > 0)
);

--*** CK_tags_clean_texto    ***(0)  ***(850)
CREATE TABLE stg.tags_clean (
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    tag NVARCHAR(850) NOT NULL,
    fecha DATETIME2(0) NOT NULL,
    CONSTRAINT CK_tags_clean_texto CHECK (LEN(LTRIM(RTRIM(tag))) > 0)
);

--*** DECIMAL(2,1)   *** CK_ratings_clean_rating    ***(0)
CREATE TABLE stg.ratings_clean (
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    rating DECIMAL(2,1) NOT NULL,
    fecha DATETIME2(0) NOT NULL,
    CONSTRAINT CK_ratings_clean_rating CHECK (rating IN (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0))
);

--*** CK_movie_alternative_titles_texto
CREATE TABLE stg.movie_alternative_titles (
    movie_id INT NOT NULL,
    alternative_title NVARCHAR(500) NOT NULL,
    CONSTRAINT PK_movie_alternative_titles PRIMARY KEY (movie_id, alternative_title),
    CONSTRAINT CK_movie_alternative_titles_texto CHECK (LEN(LTRIM(RTRIM(alternative_title))) > 0)
);

--*** CK_genome_tags_clean_texto
CREATE TABLE stg.genome_tags_clean (
    tag_id INT NOT NULL,
    tag NVARCHAR(500) NOT NULL,
    CONSTRAINT PK_genome_tags_clean PRIMARY KEY (tag_id),
    CONSTRAINT CK_genome_tags_clean_texto CHECK (LEN(LTRIM(RTRIM(tag))) > 0)
);



-- Creacion de las vistas
CREATE OR ALTER VIEW stg.v_movies AS 
SELECT
    m.movie_id AS movie_id,
    m.title AS title,
    y.year_start AS year_start,
    y.year_end AS year_end
FROM stg.movies_clean m
LEFT JOIN stg.movies_year y
    ON m.movie_id = y.movie_id;

GO
CREATE OR ALTER VIEW stg.v_users AS
SELECT user_id
FROM stg.ratings_clean
UNION
SELECT user_id
FROM stg.tags_clean;



--creacion de dw
CREATE DATABASE dw_invacom;
GO
USE dw_invacom;
GO
CREATE SCHEMA dim;
GO
CREATE SCHEMA fact;

-- dim y fact
GO
CREATE TABLE dim.dim_movie (
    id_movie INT IDENTITY(1,1) PRIMARY KEY,
    movie_id INT NOT NULL,
    title NVARCHAR(500) NULL,
    year_start INT NULL,
    year_end INT NULL,

    CONSTRAINT UQ_dim_movie_movie_id UNIQUE (movie_id)
);

GO
CREATE TABLE dim.dim_user (
    id_user INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,

    CONSTRAINT UQ_dim_user_user_id UNIQUE (user_id)
);

GO
CREATE TABLE dim.dim_date (
    id_date INT PRIMARY KEY,
    fecha DATE NOT NULL,
    anio INT NOT NULL,
    trimestre INT NOT NULL,
    mes INT NOT NULL,
    nombre_mes NVARCHAR(20) NOT NULL,
    dia INT NOT NULL,
    dia_semana INT NOT NULL,
    nombre_dia NVARCHAR(20) NOT NULL,
    semana_anio INT NOT NULL,

    CONSTRAINT UQ_dim_date_fecha UNIQUE (fecha)
);

GO
CREATE TABLE dim.dim_tag (
    id_tag INT IDENTITY(1,1) PRIMARY KEY,
    tag NVARCHAR(850) NOT NULL,

    CONSTRAINT UQ_dim_tag_tag UNIQUE (tag)
);

GO
CREATE TABLE dim.dim_genome_tag (
    id_genome_tag INT IDENTITY(1,1) PRIMARY KEY,
    tag_id INT NOT NULL,
    tag NVARCHAR(500) NOT NULL,

    CONSTRAINT UQ_dim_genome_tag_tag_id UNIQUE (tag_id)
);



GO
CREATE TABLE dim.dim_genre (
    id_genre INT IDENTITY(1,1) PRIMARY KEY,
    genre NVARCHAR(100) NOT NULL,
    CONSTRAINT UQ_dim_genre_genre UNIQUE (genre)
);

GO
CREATE TABLE dim.bridge_movie_genre (
    id_movie INT NOT NULL,
    id_genre INT NOT NULL,
    CONSTRAINT PK_bridge_movie_genre PRIMARY KEY (id_movie, id_genre),
    CONSTRAINT FK_bridge_movie_genre_movie FOREIGN KEY (id_movie) REFERENCES dim.dim_movie(id_movie),
    CONSTRAINT FK_bridge_movie_genre_genre FOREIGN KEY (id_genre) REFERENCES dim.dim_genre(id_genre)
);



GO
CREATE TABLE fact.fact_ratings (
    id_movie INT NOT NULL,
    id_user INT NOT NULL,
    id_date INT NOT NULL,

    rating DECIMAL(2,1) NOT NULL,
    cantidad_ratings INT NOT NULL DEFAULT 1,

    CONSTRAINT PK_fact_ratings
        PRIMARY KEY (id_movie, id_user, id_date),

    CONSTRAINT FK_fact_ratings_movie
        FOREIGN KEY (id_movie) REFERENCES dim.dim_movie(id_movie),

    CONSTRAINT FK_fact_ratings_user
        FOREIGN KEY (id_user) REFERENCES dim.dim_user(id_user),

    CONSTRAINT FK_fact_ratings_date
        FOREIGN KEY (id_date) REFERENCES dim.dim_date(id_date)
);

GO
CREATE TABLE fact.fact_tags (
    id_movie INT NOT NULL,
    id_user INT NOT NULL,
    id_date INT NOT NULL,
    id_tag INT NOT NULL,

    cantidad_tags INT NOT NULL DEFAULT 1,

    CONSTRAINT PK_fact_tags
        PRIMARY KEY (id_movie, id_user, id_date, id_tag),

    CONSTRAINT FK_fact_tags_movie
        FOREIGN KEY (id_movie) REFERENCES dim.dim_movie(id_movie),

    CONSTRAINT FK_fact_tags_user
        FOREIGN KEY (id_user) REFERENCES dim.dim_user(id_user),

    CONSTRAINT FK_fact_tags_date
        FOREIGN KEY (id_date) REFERENCES dim.dim_date(id_date),

    CONSTRAINT FK_fact_tags_tag
        FOREIGN KEY (id_tag) REFERENCES dim.dim_tag(id_tag)
);

GO
CREATE TABLE fact.fact_genome_scores (
    id_movie INT NOT NULL,
    id_genome_tag INT NOT NULL,

    relevance DECIMAL(6,5) NOT NULL,

    CONSTRAINT PK_fact_genome_scores
        PRIMARY KEY (id_movie, id_genome_tag),

    CONSTRAINT FK_fact_genome_scores_movie
        FOREIGN KEY (id_movie) REFERENCES dim.dim_movie(id_movie),

    CONSTRAINT FK_fact_genome_scores_tag
        FOREIGN KEY (id_genome_tag)
        REFERENCES dim.dim_genome_tag(id_genome_tag)
);
