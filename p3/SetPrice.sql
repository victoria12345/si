-- Sabiendo que los precios de las películas se han ido incrementando un 2% anualmente,
-- elaborar la consulta setPrice.sql que complete la columna 'price' de la tabla
-- 'orderdetail', sabiendo que el precio actual es el de la tabla 'products'.

-- lo que tenemos que hacer es obtener los años que llevan las peliculas para
-- calcular la diferencia y ver cuantas veces tenemos que sumar el 2%

-- el precio actual lo cogemos de la tabla products -----> se llama price
-- hay que coger la fecha de orderdetail
-- hay que coger el año actual  -----> SELECT EXTRACT( year from  NOW())
-- para cambiarlo hacemos SET

UPDATE orderdetail
SET --aqui tenemos que poner lo que queremos
	price = orderdetail.quantity*products.price* pow(1.02, (SELECT EXTRACT( year from  NOW()) - (SELECT EXTRACT( year from orders.orderdate))))

FROM products, orders

WHERE orderdetail.prod_id = products.prod_id and orderdetail.orderid = orders.orderid;
