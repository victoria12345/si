DROP TRIGGER IF EXISTS updOrders on orderdetail;
DROP FUNCTION IF EXISTS updOrdersFunction();

CREATE OR REPLACE FUNCTION updOrdersFunction() RETURNS TRIGGER AS $$ DECLARE nuevo integer;
  BEGIN
    IF (TG_OP = 'INSERT') THEN -- SE AÑADE UN ARTICULO AL CARRITO
      nuevo := NEW.totalamount;

      UPDATE orders
      SET -- queremos cambiar los precios
        totalamount = netamount + netamount*(tax/100) + nuevo*(tax/100) + nuevo,
        netamount = netamount + nuevo
      WHERE
          orderid = NEW.orderid;
      RETURN NEW;

    ELSIF (TG_OP = 'UPDATE') THEN -- SE ACTUALIZA UN ARTICULO DEL CARRITO
      nuevo := NEW.totalamount - OLD.totalamount;

      UPDATE orders

      SET
        totalamount = netamount + netamount*(tax/100) + nuevo*(tax/100) + nuevo,
        netamount = netamount + nuevo
      WHERE
        orderid = NEW.orderid;
      RETURN NEW;
    ELSE -- SE ELIMINA UN ARTICULO DEL CARRITO
      nuevo := - OLD.totalamount;

      UPDATE orders
      SET
        totalamount = netamount + netamount*(tax/100) + nuevo*(tax/100) + nuevo,
        netamount = netamount + nuevo
      WHERE
        orderid = OLD.orderid;
      RETURN OLD;

  END IF;
END;


$$ LANGUAGE plpgsql;

CREATE TRIGGER updOrders
BEFORE INSERT OR UPDATE OR DELETE ON orderdetail
    FOR EACH ROW EXECUTE PROCEDURE updOrdersFunction();
