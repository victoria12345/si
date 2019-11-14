-- tendremos que igualar los orderid para saber donde tengo que actualizar

UPDATE orders
SET
  netamount = suma
  totalamount = suma + impuestos

WHERE orders.orderid = orderdetail.orderid


------------------


UPDATE orders
SET
	totalamout = suma
FROM orders
WHERE

(select sum(price) from orderdetail, orders where orders.orderid = orderdetail.orderid group by orderdetail.orderid) as suma;
