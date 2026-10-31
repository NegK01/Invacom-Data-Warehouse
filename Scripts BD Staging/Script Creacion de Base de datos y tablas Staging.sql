CREATE DATABASE staging_invacom;
GO
USE staging_invacom;
GO
CREATE SCHEMA stg;
GO

CREATE TABLE stg.movies (
    movie_id  INT           NOT NULL,
    title     NVARCHAR(500) NULL,
    genres    NVARCHAR(200) NULL
);

CREATE TABLE stg.links (
    movie_id  INT NULL,
    imdb_id   INT NULL,
    tmdb_id   INT NULL
);

CREATE TABLE stg.ratings (
    user_id   INT    NULL,
    movie_id  INT    NULL,
    rating    FLOAT  NULL,
    timestamp BIGINT NULL
);

CREATE TABLE stg.tags (
    user_id   INT            NULL,
    movie_id  INT            NULL,
    tag       NVARCHAR(1000) NULL,
    timestamp BIGINT         NULL
);

CREATE TABLE stg.genome_tags (
    tag_id INT           NULL,
    tag    NVARCHAR(500) NULL
);

CREATE TABLE stg.genome_scores (
    movie_id  INT   NULL,
    tag_id    INT   NULL,
    relevance FLOAT NULL
);
GO