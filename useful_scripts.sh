sudo service redis-server restart

CREATE INDEX value_code_index ON value(series_code);
CREATE INDEX series_code_index ON series_code(code);

DROP INDEX value_code_index;
DROP INDEX series_code_index;

EXPLAIN QUERY PLAN
SELECT o.code,o.name,v.year,v.value FROM value v
            join series_code sc 
            on v.series_code = sc.code
            join occupation_code o
            on o.code = sc.occupation_code
            join sitemap sm
            on sm.area_code=sc.area_code
            where sm.slug='wausau-wi.html'
            and sc.industry_code='000000'
            and sc.data_type='01'
            order by 1 asc, 2 asc
            LIMIT 5;

EXPLAIN QUERY PLAN
    SELECT o.code,o.name,v.year,v.value 
    FROM value v, occupation_code o, series_code sc
    WHERE v.series_code IN
    (
        SELECT sc.code FROM series_code sc
        WHERE sc.area_code = (SELECT area_code from sitemap where slug = 'wisconsin-arts-design-entertainment-sports-and-media-occupations.html' )
        AND sc.occupation_code IN (
            SELECT code from occupation_code o
            WHERE substr(code,1,2) = (
                SELECT substr(occupation_code,1,2) FROM sitemap 
                WHERE slug ='wisconsin-arts-design-entertainment-sports-and-media-occupations.html'
            )
        )
    )
    AND sc.code = v.series_code
    AND o.code = sc.occupation_code;

SELECT occupation_code FROM sitemap 
WHERE slug ='wisconsin-arts-design-entertainment-sports-and-media-occupations.html';



SELECT o.code,o.name,v.year,v.value 
    FROM value v, occupation_code o, series_code sc
    WHERE v.series_code IN
    (
        SELECT sc.code FROM series_code sc
        WHERE sc.area_code = (SELECT area_code from sitemap where slug = 'national-community-and-social-service-occupations.html' )
        AND sc.occupation_code IN (
            SELECT code from occupation_code o
            WHERE substr(code,1,2) = (
                SELECT substr(occupation_code,1,2) FROM sitemap 
                WHERE slug = 'national-community-and-social-service-occupations.html'
            )
        )
        AND SC.industry_code = '000000'
    )
    AND sc.code = v.series_code
    AND o.code = sc.occupation_code
    order by 1 asc, 2 asc;