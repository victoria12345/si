-- recibe unos umbrales: numero de productos e Importe
-- y devuelva los meses (en realidad la pareja año-mes)
-- en los que se ha superado alguno de los dos umbrales, junto con su
-- importe y productos. Probadla con umbrales de 19.000 artículos y 320.000 euros.
DROP FUNCTION IF EXISTS getTopMonths(integer, integer);

CREATE OR REPLACE FUNCTION getTopMonths(products_entrada INTEGER, importe_entrada INTEGER,
OUT Anno INTEGER,
OUT Mes INTEGER,
OUT Importe INTEGER,
OUT Productos INTEGER)

RETURNS SETOF record
AS $$

SELECT *

FROM(
  SELECT
  cast(date_part('year', orders.orderdate) as INTEGER) as Anno,
  cast(date_part('month', orders.orderdate) as INTEGER) as Mes,
  cast(sum(orders.totalamount) as INTEGER) as Importe,
  cast(sum(orderdetail.quantity) as INTEGER) as Productos


  FROM imdb_movies, orderdetail, orders, products

  WHERE orders.orderid = orderdetail.orderid AND
        products.prod_id = orderdetail.prod_id AND
        products.movieid = imdb_movies.movieid

  GROUP BY Anno, Mes

  ) as res

  WHERE
	res.Importe >  importe_entrada OR res.Productos > products_entrada

$$

LANGUAGE SQL;


