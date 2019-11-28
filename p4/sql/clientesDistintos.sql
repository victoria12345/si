
CREATE INDEX idx_totalamount ON orders(totalamount);

EXPLAIN SELECT COUNT (DISTINCT customerid)  FROM orders WHERE orders.totalamount >= 100 AND (SELECT extract (month from orderdate)) = 4;

DROP INDEX idx_totalamount;

CREATE INDEX idx_orderdate ON orders(orderdate);

EXPLAIN SELECT COUNT (DISTINCT customerid)  FROM orders WHERE orders.totalamount >= 100 AND (SELECT extract (month from orderdate)) = 4;

DROP INDEX idx_orderdate;




EXPLAIN SELECT COUNT (DISTINCT customerid)  FROM orders WHERE 
extract (month from orderdate) = 4 AND 
extract (year from orderdate) = 2015 and
orders.totalamount >= 100 ;