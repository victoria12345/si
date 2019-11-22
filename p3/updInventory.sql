DROP TRIGGER IF EXISTS updInventory on orderdetail;
DROP FUNCTION IF EXISTS updInventoryFunction();

CREATE OR REPLACE FUNCTION updInventoryFunction() RETURNS TRIGGER AS $$ DECLARE result integer;
  BEGIN
    IF (NEW.status is not null and OLD.status is null) -- cuando tengamos un nuevo estado

    -- QUEREMOS QUE ACTUALICE ORDERS E INVENTORY CUANDO SE FINALICE LA COMPRA
    -- El trigger también deberá crear una alerta en una nueva tabla llamada 'alertas'
    -- si la cantidad en stock llega a cero. Realizar los cambios necesarios en la
    -- base de datos para incluir dicha tabla, incorporándolos al script actualiza.sql.

    -- cuando se finalice la compra queremos que se inserte en la tabla ORDERS
    -- cuando se finalice la compra queremos que en el inventory se modifique el stock --> aqui si llegamos a 0 hacemos una alerta
      UPDATE inventory
      SET
        stock = stock - num_products --num_products sera algo que nos diga cuantas peliculas compramos
        sales = sales + num_products
      WHERE
        orderdetail.prod_id = inventory.prod_id AND
        OLD.orderid = orderdetail.orderid ;

      -- YA TENEMOS ACTUALIZADO EL INVENTARIO
      -- AHORA QUETENEMOS QUE SE CREE LA alerta
      -- suponemos que tenemos una tabla llamada alerts que tengo que poner en actualiza.SQL
      -- ESTA TABLA NOS VA A DAR LA INFORMACION DE LOS PRODUCTOS CUYO STOCK ESTA A 0

      -- Aqui tenemos que eliminarlo
      DELETE FROM alerts
      SELECT prod_id
      WHERE ;


      -- Ahora tendre que terlo de nuevo en la TABLA
      INSERT INTO alerts
      SELECT prod_id
      WHERE ;



    END IF;
  END;


$$ LANGUAGE plpgsql;

CREATE TRIGGER updInventory
BEFORE INSERT OR UPDATE OR DELETE ON orderdetail
    FOR EACH ROW EXECUTE PROCEDURE updInventoryFunction();
