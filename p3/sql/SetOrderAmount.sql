CREATE OR REPLACE FUNCTION SetOrderAmount() RETURNS void AS $$BEGIN UPDATE orders
SET
  totalamount = sumas.s + (tax/100)*sumas.s,
  netamount = sumas.s
FROM (select orderdetail.orderid as id, sum(price) as s
      from orderdetail, orders
      where orders.orderid = orderdetail.orderid group by orderdetail.orderid) as sumas
WHERE
 orders.orderid = sumas.id ;
END;$$
LANGUAGE plpgsql;

SELECT * FROM setOrderAmount();
