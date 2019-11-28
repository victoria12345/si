DROP FUNCTION IF EXISTS getTopVentas(integer);
CREATE OR REPLACE FUNCTION getTopVentas(anno_entrada INTEGER,
OUT Anno INTEGER,
OUT Titulo VARCHAR,
OUT Ventas INTEGER,
OUT Id INTEGER)

RETURNS SETOF record
AS $$

SELECT DISTINCT ON (res.Anno) res.Anno, res.Titulo,res.Ventas, res.Id

FROM(
  SELECT cast(date_part('year', orders.orderdate) as INTEGER) as Anno,
  imdb_movies.movietitle as Titulo,
  cast(sum(orderdetail.quantity) as INTEGER) as Ventas,
  products.prod_id as Id

  FROM imdb_movies, orderdetail, orders, products

  WHERE orders.orderid = orderdetail.orderid AND
        products.prod_id = orderdetail.prod_id AND
        products.movieid = imdb_movies.movieid AND
        date_part('year', orders.orderdate) >=  anno_entrada

  GROUP BY Anno, imdb_movies.movietitle,products.prod_id

  ORDER BY Anno, Ventas DESC, Titulo ) as res $$
LANGUAGE SQL;