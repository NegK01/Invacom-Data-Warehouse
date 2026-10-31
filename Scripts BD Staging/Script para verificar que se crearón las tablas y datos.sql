SELECT 'ratings' AS tabla, COUNT(*) AS filas FROM stg.ratings
UNION ALL SELECT 'genome_scores', COUNT(*) FROM stg.genome_scores
UNION ALL SELECT 'tags', COUNT(*) FROM stg.tags
UNION ALL SELECT 'movies', COUNT(*) FROM stg.movies
UNION ALL SELECT 'links', COUNT(*) FROM stg.links
UNION ALL SELECT 'genome_tags', COUNT(*) FROM stg.genome_tags;