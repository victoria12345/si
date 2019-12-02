# -*- coding: utf-8 -*-

import os
import sys, traceback, time

from sqlalchemy import create_engine
import sqlalchemy
import hashlib
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.sql import select

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False, execution_options={"autocommit":False})

def dbConnect():
    return db_engine.connect()

def dbCloseConnect(db_conn):
    db_conn.close()

def getListaCliMes(db_conn, mes, anio, iumbral, iintervalo, use_prepare, break0, niter):

    # TODO: implementar la consulta; asignar nombre 'cc' al contador resultante
   
    
    # TODO: ejecutar la consulta 
    if use_prepare:
        consulta = " PREPARE getListaCliMes(int, int, int) as SELECT COUNT (DISTINCT customerid) as cc  FROM orders WHERE  extract (month from orderdate) = $1 AND  extract (year from orderdate) = $2 and orders.totalamount >= $3 ; "
        sql  = sqlalchemy.text(consulta)
        db_conn.execute(sql)
    # - mediante PREPARE, EXECUTE, DEALLOCATE si use_prepare es True
    # - mediante db_conn.execute() si es False

    # Array con resultados de la consulta para cada umbral
    dbr=[]
    
    for ii in range(niter):
        if use_prepare:
            consulta = "EXECUTE getListaCliMes("+str(mes)+", "+str(anio)+","+str(iumbral)+")"
        
        else: 
            consulta = " SELECT COUNT (DISTINCT customerid) as cc  FROM orders WHERE  extract (month from orderdate) = "+ str(mes)+" AND  extract (year from orderdate) = "+ str(anio) + "and orders.totalamount >= " + str(iumbral)+ " ; "
        
        sql  = sqlalchemy.text(consulta)
        res = db_conn.execute(sql)
        res = list(res)[0]
        # Guardar resultado de la query
        dbr.append({"umbral":iumbral,"contador":res['cc']})

        # TODO: si break0 es True, salir si contador resultante es cero
        
        # Actualizacion de umbral
        iumbral = iumbral + iintervalo

    if use_prepare:
        consulta = "DEALLOCATE getListaCliMes;"
        sql  = sqlalchemy.text(consulta)
        db_conn.execute(sql)

    return dbr

def getMovies(anio):
    # conexion a la base de datos
    db_conn = db_engine.connect()

    query="select movietitle from imdb_movies where year = '" + anio + "'"
    resultproxy=db_conn.execute(query)

    a = []
    for rowproxy in resultproxy:
        d={}
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for tup in rowproxy.items():
            # build up the dictionary
            d[tup[0]] = tup[1]
        a.append(d)
        
    resultproxy.close()  
    
    db_conn.close()  
    
    return a
    
def getCustomer(username, password):
    # conexion a la base de datos
    db_conn = db_engine.connect()

    query="select * from customers where username='" + username + "' and password='" + password + "'"
    res=db_conn.execute(query).first()
    
    db_conn.close()  

    if res is None:
        return None
    else:
        return {'firstname': res['firstname'], 'lastname': res['lastname']}
    
def delCustomer(customerid, bFallo, bSQL, duerme, bCommit):
    
    # Array de trazas a mostrar en la página
    dbr=[]

    db_conn = dbConnect()

    # TODO: Ejecutar consultas de borrado
    # - ordenar consultas según se desee provocar un error (bFallo True) o no
    # - ejecutar commit intermedio si bCommit es True
    # - usar sentencias SQL ('BEGIN', 'COMMIT', ...) si bSQL es True
    # - suspender la ejecución 'duerme' segundos en el punto adecuado para forzar deadlock
    # - ir guardando trazas mediante dbr.append()
    
    try:
        
        # TODO: ejecutar consultas
        if bSQL:
            consulta = "BEGIN; "
            sql  = sqlalchemy.text(consulta)
            db_conn.execute(sql)
        else:
            transaccion = db_conn.begin()

        dbr.append("Realizamos BEGIN")
        
        if bFallo:
            
            consulta = " delete from orderdetail where orderdetail.orderid in (select orderid from orders where orders.customerid ="+str(customerid)+");"
            sql  = sqlalchemy.text(consulta)
            db_conn.execute(sql)
            dbr.append("Borrado detalles del pedido del cliente con exito")
            
            if bCommit:
                if bSQL:
                    consulta = "COMMIT; "
                    sql  = sqlalchemy.text(consulta)
                    db_conn.execute(sql)
                    consulta = "BEGIN; "
                    sql  = sqlalchemy.text(consulta)
                    db_conn.execute(sql)
                else:
                    transaccion.commit()
                    transaccion = db_conn.begin()
                
                dbr.append("Commit intermedio realizado")
            
            
            #borrar cliente primero para que de el fallo de foreing key
            consulta = " delete from customers where customerid ="+str(customerid)+";"
            sql  = sqlalchemy.text(consulta)
            db_conn.execute(sql)
            dbr.append("Borrado cliente con exito")

            #borrar orders
            consulta = " delete from orders where customerid ="+str(customerid)+";"
            sql  = sqlalchemy.text(consulta)
            db_conn.execute(sql)
            dbr.append("Borrado orders del cliente indicado sin exito")

            time.sleep(duerme)

        else:
            
            #si no hay error --> se borra todo bien
            consulta = " delete from orderdetail where orderdetail.orderid in (select orderid from orders where orders.customerid ="+str(customerid)+");"
            sql  = sqlalchemy.text(consulta)
            db_conn.execute(sql)
            dbr.append("Borrado detalles del pedido del cliente con exito")
            
            #borrar orders
            consulta = " delete from orders where customerid ="+str(customerid)+";"
            sql  = sqlalchemy.text(consulta)
            db_conn.execute(sql)
            dbr.append("Borrado orders del cliente indicado con exito")

            time.sleep(duerme)

            #borrar cliente primero para que de el fallo de foreing key
            consulta = " delete from customers where customerid ="+str(customerid)+";"
            sql  = sqlalchemy.text(consulta)
            db_conn.execute(sql)
            dbr.append("Borrado cliente con exito")


    except Exception as e:
        # TODO: deshacer en caso de error
        
        dbr.append("Se ha producido algun error")
        
        if bSQL:
            consulta = "ROLLBACK; "
            sql  = sqlalchemy.text(consulta)
            db_conn.execute(sql)
            
        else:
            transaccion.rollback()

        dbr.append("Rollback realizado")

    else:
        # TODO: confirmar cambios si todo va bien
        dbr.append("Todo ha ido bien")
        if bSQL:
            consulta = "COMMIT; "
            sql  = sqlalchemy.text(consulta)
            db_conn.execute(sql)
            
        else:
            transaccion.commit()
        
        dbr.append("Se ha realizado un commit")
    
    db_conn.close()

        
    return dbr

