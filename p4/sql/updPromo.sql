ALTER TABLE customers ADD promo numeric DEFAULT 0;

DROP TRIGGER IF EXISTS updPromo on customers;
DROP FUNCTION IF EXISTS updPromoFunction() CASCADE;

CREATE OR REPLACE FUNCTION updPromoFunction() RETURNS TRIGGER AS $$ 
BEGIN
    IF (TG_OP = 'UPDATE' ) THEN

    UPDATE orders
    SET
        netamount = netamount*(100-NEW.promo)/100
    WHERE 
        customerid = NEW.customerid and status is NULL;
    
    END IF;

    PERFORM pg_sleep(7);
    RETURN NEW;
END;


$$ LANGUAGE plpgsql;


DROP  TRIGGER IF EXISTS  updPromo ON customers;
CREATE TRIGGER updPromo
AFTER UPDATE ON customers
    FOR EACH ROW EXECUTE PROCEDURE updPromoFunction();

