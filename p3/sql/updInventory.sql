DROP TRIGGER IF EXISTS updInventory on orderdetail;
DROP FUNCTION IF EXISTS updInventoryFunction() CASCADE;

CREATE OR REPLACE FUNCTION updInventoryFunction() RETURNS TRIGGER AS $$ 
DECLARE product record;
  BEGIN
    
FOR product IN 
  SELECT prod_id, stock, sales, quantity 
  FROM orders NATURAL JOIN orderdetail NATURAL JOIN inventory
  WHERE OLD.orderid = orderid

LOOP

  UPDATE inventory
  SET 
    stock = product.stock - product.quantity,
    sales = product.sales + product.quantity
  WHERE
    inventory.prod_id = product.prod_id;

  IF product.stock <= product.quantity THEN
    INSERT INTO alerts (prod_id, orderdate) VALUES (product.prod_id, NOW());
  END IF;
END LOOP;


NEW.orderdate = 'NOW()';

RETURN NEW;

END;


$$ LANGUAGE plpgsql;

DROP  TRIGGER IF EXISTS  updInventory ON orders;
CREATE TRIGGER updInventory
BEFORE UPDATE OF status ON orders
    FOR EACH ROW 
    WHEN (NEW.status = 'Paid')
    EXECUTE PROCEDURE updInventoryFunction();
