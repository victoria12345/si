explain select count(*)
from orders
where status is null;

explain select count(*)
from orders
where status ='Shipped';

CREATE INDEX idx_status ON orders(status);

explain select count(*)
from orders
where status is null;

explain select count(*)
from orders
where status ='Shipped';

-- ESTADISTICAS 
analyze orders;

explain analyze select count(*)
from orders
where status is null;

explain analyze select count(*)
from orders
where status ='Shipped';

explain analyze select count(*)
from orders
where status ='Paid';

explain analyze select count(*)
from orders
where status ='Processed';