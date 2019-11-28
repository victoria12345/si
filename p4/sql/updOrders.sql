DROP TRIGGER IF EXISTS updOrders on orderdetail;
DROP FUNCTION IF EXISTS updOrdersFunction();

CREATE OR REPLACE FUNCTION updOrdersFunction() RETURNS TRIGGER AS $$
  BEGIN
    IF (TG_OP = 'INSERT') THEN -- SE AÑADE UN ARTICULO AL CARRITO

      UPDATE orders
      SET
        totalamount = (NEW.price * NEW.quantity)+ (tax/100)*(NEW.price * NEW.quantity),
        netamount = NEW.price * NEW.quantity
     
      WHERE
      orders.orderid = NEW.orderid ;
      RETURN NEW;

    ELSIF (TG_OP = 'UPDATE') THEN -- SE ACTUALIZA UN ARTICULO DEL CARRITO
      IF  (NEW.quantity = 0) THEN
        
        DELETE FROM orderdetail WHERE orderdetail.orderid = OLD.orderid AND orderdetail.prod_id = OLD.prod_id;
        RETURN NEW;

      END IF;

      UPDATE orders
      SET
        totalamount = (netamount + NEW.price * (NEW.quantity-OLD.quantity))+ (tax/100)*(netamount + NEW.price * (NEW.quantity-OLD.quantity)),
        netamount = netamount + NEW.price * (NEW.quantity-OLD.quantity)
     
      WHERE
      orders.orderid = NEW.orderid ;
      RETURN NEW;
  END IF;
END;


$$ LANGUAGE plpgsql;
DROP  TRIGGER IF EXISTS  updOrders ON  orderdetail;
CREATE TRIGGER updOrders
AFTER INSERT OR UPDATE ON orderdetail
    FOR EACH ROW EXECUTE PROCEDURE updOrdersFunction();
