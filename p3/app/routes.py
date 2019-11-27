#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from flask import render_template, request, url_for, redirect, session, make_response
import json
import os
import sys
import hashlib
import os.path as path
import random
import time
### para la base de datos ###
import sqlalchemy
import hashlib
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.sql import select
import  datetime


#vamos a crear la base de datos
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False)

#cargamos las tablas desde la base de datos
db_meta = MetaData(bind = db_engine, reflect = True)

#nos conectamos a la base de datos
db_conn = db_engine.connect() #esto no se si es necesario hacerlo aqui pero imagino que si


def getTopVentas():
    # 2016 porque queremos las pelis mas vendidas de los ultimos 2 annos
    sql  = sqlalchemy.text("SELECT * FROM getTopVentas(2016);")

    try:
        result = db_conn.execute(sql)
        result = list(result)
        return result
    except:
        return None


@app.route('/')
@app.route('/index',methods=['GET','POST'])
def index():


    #creamos el carrito para la sesion
    if not "carrito" in session:

        session['carrito'] = [] #creamos una lista vacia para el carrito
        session['precio'] = 0 #ponemos el precio final a 0
        session.modified = True

        # annadimos las pelis mas vendidas para que se muestren
    result = getTopVentas()
    catalogue = {}
    catalogue['peliculas'] = []
    for item in result:

        dicc={}
        dicc['titulo'] = item[1]
        dicc['id']=item[3]
        catalogue['peliculas'].append(dicc)

    return render_template('index.html', title = "Home", movies=catalogue['peliculas'])


def informacion_aux(pelicula_id):

    pelicula = {}

    # sacamos el titulo
    consulta = "SELECT language, genre, movietitle, directorname, price, movierelease, year"
    consulta += " FROM imdb_movies NATURAL JOIN languages NATURAL JOIN imdb_movielanguages"
    consulta += " NATURAL JOIN genres NATURAL JOIN imdb_moviegenres NATURAL JOIN imdb_directors"
    consulta += " NATURAL JOIN imdb_directormovies NATURAL JOIN products WHERE prod_id =" + str(pelicula_id)

    sql  = sqlalchemy.text(consulta)

    try:
        
        res = db_conn.execute(sql)
        res = list(res)

        titulo = res[0][2]
        idioma = res[0][0]
        categoria = res[0][1]
        director = res[0][3]
        precio = res[0][4]
        sinopsis = res[0][5]
        anno = res[0][6]
        pelicula['id'] = pelicula_id
        pelicula['titulo'] = titulo
        pelicula['idioma'] = idioma
        pelicula['categoria'] = categoria
        pelicula['director'] = director
        pelicula['precio'] = precio
        pelicula['sinopsis'] = sinopsis
        pelicula['anno'] = anno
       
        if sinopsis is None or sinopsis == "":
            pelicula['sinopsis'] = "este articulo no tiene sinopsis disponible"

        return pelicula

    except:
        return None

   


@app.route('/informacion/<pelicula_id>', methods=['GET','POST'])
def informacion(pelicula_id):
    item = informacion_aux(pelicula_id)
    

    if item is None:
        return 'error'

    return render_template('informacion.html', title = "Pelicula", film=item, flag=False)


##########################################################
# NO FUNCIONAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
######################################################
#################################################

def buscar_titulo(titulo):
    consulta = "SELECT prod_id, movietitle FROM imdb_movies NATURAL JOIN products NATURAL JOIN imdb_moviegenres NATURAL JOIN genres WHERE movietitle like \'%"+str(titulo)+"%\'"
    sql  = sqlalchemy.text(consulta)

    try:
        result = db_conn.execute(sql)
        result = list(result)
        print(result)
        L=[]
        for item in result:
            pelicula = {}
            pelicula['id'] = item[0]
            pelicula['titulo'] = item[1]
            # pelicula['categoria'] = item[10]
            L.append(pelicula)
        
        return L
    except:
        return None


@app.route('/busqueda', methods=['GET','POST'])
def busqueda():
    # catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    # catalogue = json.loads(catalogue_data)
    # movies=catalogue['peliculas']

    L=[]

    if request.form['buscar'] != "":
        res = buscar_titulo(request.form['buscar'])
        print(res)
        if res is None:
            return render_template('index.html', title = "Home", movies=L)
        else:
            for item in res:
                L.append(item)

        # print(L)
        # if request.form['categoria'] != "":
        #     for item in L:
        #         if item['categoria'] != request.form['categoria']:
        #             L.remove(item)

    # elif request.form['categoria'] != "":
    #     res = buscar_categoria(categoria)
    #     for item in movies:
    #         if item['categoria'] == request.form['categoria']:
    #             L.append(item)

    # else:
    #     return redirect(url_for('index'))

    return render_template('index.html', title = "Home", movies=L)

#vamos a hacernos una funcion auxiliar que nos permita hacer las querys aqui
def login_aux(username, password):

    
    #hacemos la consulta para obtener la password
    string = "SELECT password FROM customers WHERE password = \'" + password + "\' AND username =\'" + username+"\'"
    sql = sqlalchemy.text(string)
    
    try:
        result = db_conn.execute(sql)
        result = list(result)
        if result[0]:
            #tenemos resultados, en el [0] se enecuentra la contraseña
            if result[0][0] == password:
                string = "SELECT customerid FROM customers WHERE password = \'" + password + "\' AND username =\'" + username+"\'"
                sql = sqlalchemy.text(string)
                result = db_conn.execute(sql)
                result = list(result)

                session['userid'] = result[0][0]
                return True
            else:
                return False
    except:
        return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    # doc sobre request object en http://flask.pocoo.org/docs/1.0/api/#incoming-request-data
    if 'username' in request.form:

        #cogemos el username y la passowrd
        username = request.form['username']
        password = request.form['contrasenna']

        if login_aux(username, password):

            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('nombre',request.form['username'] )

            session['usuario'] = request.form['username']
            session.modified=True

            return resp#                 break
        else:
            # aqui se le puede pasar como argumento un mensaje de login invalido
            return render_template('login.html', title = "Sign In", mensaje="No has realizado Login correctamente. Intentalo de nuevo")
    else:
        nombre = request.cookies.get('nombre')
        # se puede guardar la pagina desde la que se invoca
        session['url_origen']=request.referrer
        session.modified=True
        return render_template('login.html', title = "Login", nombre = nombre)

@app.route('/logout', methods=['GET', 'POST'])
def logout():

    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    movies=catalogue['peliculas']
    session['n_producto_carrito'] = []
    for i in range(len(movies)):
        session['n_producto_carrito'].append(0)

    session['carrito'] = [] #creamos una lista vacia para el carrito
    session['precio'] = 0 #ponemos el precio final a 0
    session.modified = True
    session.pop('usuario', None)
    return redirect(url_for('index'))


def saldo_aux(userid):
    string = "SELECT saldo FROM customers WHERE customerid = " +str(userid) + ";"
    sql = sqlalchemy.text(string)
    result = db_conn.execute(sql)
    result = list(result)

    saldo = float(result[0][0])
    saldo = "{0:.2f}".format(saldo)
    saldo = float(saldo)

    return saldo

def saldo_annadir(userid , saldo):
    string = "UPDATE customers SET saldo = saldo + " + str(saldo) + " WHERE customerid = " +str(userid) + ";"
    sql = sqlalchemy.text(string)
    db_conn.execute(sql)


@app.route('/saldo', methods=['GET', 'POST'])
def saldo():
    userid = session['userid']

    if 'saldo' in request.form:
        if "usuario" in session:
            
            
            saldo_annadir(userid, request.form['saldo'])
            saldo = saldo_aux(userid)

            return render_template('saldo.html', title = "Añadir Saldo", saldo = saldo)

    else:
        
        saldo = saldo_aux(userid)
        return render_template('saldo.html', title = "Añadir Saldo", saldo = saldo)

def registro_aux(username, password, email, creditcard):
    #hacemos la consulta para obtener la password
    string = "SELECT password FROM customers WHERE username =\'" + username+"\'"
    sql = sqlalchemy.text(string)

    try:
        result = db_conn.execute(sql)
        result = list(result)
        if result[0]:
            return 'usuario existente'
        return False

    except:
        # registramos al usuario
        string = "INSERT INTO customers(username, password, creditcard, email)"
        string += "VALUES (\'" + username + "\'"
        string += ", \'" + password+ "\'"
        string += ", \'" + creditcard+ "\'"
        string += ", \'" + email+ "\' )"
        print("la segunda query: ")
        print(string)

        sql = sqlalchemy.text(string)
        try:
            result = db_conn.execute(sql)
            return True
        except:
            return False

@app.route('/registro', methods=['GET', 'POST'])
def registro():

    if 'username' in request.form:

        passowrd = request.form['contrasenna']
        username = request.form['username']
        email = request.form['email']
        creditcard = request.form['tarjeta']

        res = registro_aux(username, passowrd, email, creditcard)
        if res:
            if res == 'usuario existente':
                return render_template('registro.html', title= "Registro", mensaje="Ese nombre de usuario ya existe")
            else:
                return redirect(url_for('index'))
        else:
            return render_template('registro.html', title = "Registrarse")
    else:
        return render_template('registro.html', title = "Registrarse")

def comprar_aux(pelicula_id, userid):

    # seleccionamos toda la informacion del pedidido cuyo estado sea null y sea del usuario que esta en la sesion
    string = "SELECT * FROM orders WHERE status is null AND customerid =" + str(userid) +";"
    sql = sqlalchemy.text(string)

    # ejecutamos la query
    result = db_conn.execute(sql)
    result = list(result)

     # si no obtenemos lista es porque no tenemos ese order en la tabla con lo cual tenemos que añadirlo 
     # tenemos que añadirlo tanto a orders como a orderdetail
    if result == []:
        print ("ESTOY INTENTANDO INSERTAR EN ORDERS")
        string = "INSERT INTO orders (orderdate,customerid, tax) VALUES (NOW()," + str(userid) + ", 15);"
        sql = sqlalchemy.text(string)
        db_conn.execute(sql)
        # ahora que ya lo tenemos queremos obtener el id de este pedido para poder actualizar orderdetail 
        string = "SELECT orderid FROM orders WHERE status is null AND customerid =" + str(userid) +";"
        sql = sqlalchemy.text(string)
        result = db_conn.execute(sql)
        result = list(result)
    
    # Una vez estanmos aqui, es porque ya lo tenemos en la lista o lo acabamos de añadir 
    # entonces lo que pasara es que tendremos que actualizar el orderdetail si ya esta --> esto es porque ya teniamos la venta
    # tendremos que insertarlo en orderdetail si no estaba en orders --> esto es porque no tenemos esa venta el orders
    orderid = result[0][0]
    #tengo que mirar si esta en orderdetail o no
    string = "SELECT * FROM orderdetail WHERE orderid = " + str(orderid) + "AND prod_id = "+str(pelicula_id)+ ";"
    sql = sqlalchemy.text(string)
    result = db_conn.execute(sql)
    result = list(result)

    if result == []: #si esta vavia es porque no esta en orderdetail --> tenemos que añadirla
        string = "INSERT INTO orderdetail (orderid, prod_id, price, quantity) VALUES ( " + str(orderid) + "," + str(pelicula_id)
        string += ", ( SELECT price FROM products WHERE prod_id = " + str(pelicula_id) + "), 1 )"
        sql = sqlalchemy.text(string)
        db_conn.execute(sql)

    else: # no esta vacia, con lo cual ya esta en orderdetail y solo tenemos que actualizar
        string = "UPDATE orderdetail SET quantity = quantity + 1"
        string += "WHERE prod_id = " + str(pelicula_id) + " AND orderid = " + str(orderid) + ";"
        sql = sqlalchemy.text(string)
        db_conn.execute(sql)

# esta funcion nos permite añadir una pelicula al carrito de la compra. En la sesion hay un carrito de la compra creado
@app.route('/informacion/<pelicula_id>comprada', methods=['GET','POST'])
def comprar(pelicula_id):

    if not 'userid' in session:
        return render_template('login.html', title = "Login")

    userid = session['userid']
    comprar_aux(pelicula_id, userid)

    item = informacion_aux(pelicula_id)

    return render_template('informacion.html', title = "Pelicula", film=item, flag=True)


# #esta funcion nos permitira cargar el carrito de la compra:
# es decir la vista y ademas realizar diferentes funciones con el carrito

@app.route('/carrito/', methods=['GET', 'POST'])
def carrito():
    userid = session['userid']
    # ESTO ES EL CARRITO
    # seleccionamos toda la informacion del pedidido cuyo estado sea null y sea del usuario que esta en la sesion
    string = "SELECT prod_id, orderid FROM orders NATURAL JOIN orderdetail WHERE status is null AND customerid = " + str(userid) +";"
    sql = sqlalchemy.text(string)

    # ejecutamos la query
    result = db_conn.execute(sql)
    result = list(result)

    L = []
    precio = 0

    #no tienes carrito todavia
    if result == []:
        return render_template('carrito.html', title = "Carrito", carrito_lista = L, precio="{0:.2f}".format(session['precio']))

    #en caso de que si tengamos carrito
    for prod in result:
        item = informacion_aux(prod[0])
        
        string = "SELECT quantity FROM orderdetail WHERE prod_id = " + str(item['id']) + "AND orderid =" + str(prod[1]) + ";"
        sql = sqlalchemy.text(string)
        result = db_conn.execute(sql)
        result = list(result)

        item['cantidad'] = result[0][0]
        precio += item['precio']*item['cantidad']
        L.append(item)

    session['precio'] = precio
    return render_template('carrito.html', title = "Carrito", carrito_lista = L, precio="{0:.2f}".format(precio))

def eliminar_aux(pelicula_id, userid):

    string = "SELECT * FROM orders WHERE status is null AND customerid = " + str(userid) +";"
    sql = sqlalchemy.text(string)

    # ejecutamos la query
    result = db_conn.execute(sql)
    result = list(result)

    if result == []: 
        print("ERROR no deberiamos estar aqui porque estamos intntando borrar algo que deberia de estar en la BD")
    
    orderid = result[0][0]
    #tengo que mirar si esta en orderdetail o no --> deberia de estar
    string = "SELECT * FROM orderdetail WHERE orderid = " + str(orderid) + "AND prod_id = "+str(pelicula_id)+ ";"
    sql = sqlalchemy.text(string)
    result = db_conn.execute(sql)
    result = list(result)

    if result == []:
        print("ERROR no deberiamos estar aqui porque estamos intntando borrar algo que deberia de estar en la BD")
    
    string = "UPDATE orderdetail SET quantity = quantity - 1" #TENGO QUE CAMBIAR EL PRECIO PERO NO SE COMO HACERLO
    string += "WHERE prod_id = " + str(pelicula_id) + " AND orderid = " + str(orderid) + ";"
    sql = sqlalchemy.text(string)
    db_conn.execute(sql)

#con esta funcion eliminaremos una pelicula del carrito
@app.route('/carrito/<pelicula_id>eliminada', methods=['GET', 'POST'])
def eliminar(pelicula_id):
    userid = session['userid']

    eliminar_aux(pelicula_id, userid)
    
    return redirect(url_for('carrito'))

def finalizar_aux(userid):

    string = "SELECT * FROM orders WHERE status is null AND customerid = " + str(userid) +";"
    sql = sqlalchemy.text(string)

    # ejecutamos la query
    result = db_conn.execute(sql)
    result = list(result)

    if result == []: 
        print("ERROR no deberiamos estar aqui porque estamos intntando borrar algo que deberia de estar en la BD")
    
    orderid = result[0][0]

    #ahora tenemos que comprobar que el usuario tiene saldo para pagarlo
    string = "SELECT saldo FROM customers WHERE customerid = " + str(userid) + ";"
    sql = sqlalchemy.text(string)
    result = db_conn.execute(sql)
    result = list(result)

    saldo = result[0][0]
    precio = session['precio']

    L = []
    ##################################
    #EN CASO DE QUE NO TENGAMOS SALDO#
    ##################################
    if saldo < precio or saldo <= 0:

        #OBTENEMOS LOS PRODUCTOS QUE TENEMOS EN EL CARRITO
        string = "SELECT prod_id, orderid FROM orders NATURAL JOIN orderdetail WHERE status is null AND customerid = " + str(userid) +";"
        sql = sqlalchemy.text(string)
        result = db_conn.execute(sql)
        result = list(result)
        #en caso de que si tengamos carrito
        for prod in result:
            item = informacion_aux(prod[0])
            precio += item['precio']

            string = "SELECT quantity FROM orderdetail WHERE prod_id = " + str(item['id']) + "AND orderid =" + str(prod[1]) + ";"
            sql = sqlalchemy.text(string)
            result = db_conn.execute(sql)
            result = list(result)

            item['cantidad'] = result[0][0]
            L.append(item)
        
        return render_template('carrito.html', title = "Carrito", carrito_lista = L, mensaje="No tienes saldo para realizar la compra", precio = precio)

    ##################################
    #EN CASO DE QUE SI TENGAMOS SALDO#
    ##################################
    else:
        string = "UPDATE orders SET status='Paid' WHERE orderid = " + str(orderid) + ";"
        sql = sqlalchemy.text(string)
        db_conn.execute(sql)

        print("********PRECIO*********")
        print(precio)
        string = "UPDATE customers SET saldo = saldo -" + str(precio) + "WHERE customerid = " + str(userid)+ ";"
        sql = sqlalchemy.text(string)
        db_conn.execute(sql)

        return redirect(url_for('carrito'))



# Esta funcion nos permite finalizar la compra
# Para ello debemos comprobar que el usuario que esta en la sesion esta registrado o ha iniciado sesion
# Si no esta registrado, le llevaremos a la pagina donde se puede hacer login
# para finalizar una compra tambien se debe de tener saldo

@app.route('/finalizar', methods=['GET', 'POST'])
def finalizar():
    
    #primero voy a comprobar que el usuario este registrado en la aplicacion

    #Si hay un usuario logeado en la sesion hacemos las comprobaciones pertinentes: saldo
    #si no esta logeado le llevamos a que inicie sesion
    if "usuario" in session:
        userid = session['userid']
        #tenemos que meternos en los datos del usuario y comprobar si tiene saldo
        return finalizar_aux(userid)


    else:
        return render_template('login.html', title = "Login")

# #esta funcion nos permitira cargar el historial de un cliente

@app.route('/historial/', methods=['GET', 'POST'])
def historial():
    userid = session['userid']
    L = []
    precio = 0
    # cadena2 = "usuarios/" + session['usuario']
    # cadena2 = os.path.join(app.root_path,cadena2)

    # catalogue_data = open(cadena2+'/historial.json', encoding="utf-8").read()
    # catalogue = json.loads(catalogue_data)

    #OBTENEMOS LOS PRODUCTOS QUE TENEMOS EN EL CARRITO
    string = "SELECT prod_id, orderid, orderdate FROM orders NATURAL JOIN orderdetail WHERE status = 'Paid' AND customerid = " + str(userid) +";"
    sql = sqlalchemy.text(string)
    result = db_conn.execute(sql)
    result = list(result)
    #en caso de que si tengamos carrito
    for prod in result:
        item = informacion_aux(prod[0])
        precio += item['precio']
        item['fecha'] = prod[2]
        string = "SELECT quantity FROM orderdetail WHERE prod_id = " + str(item['id']) + "AND orderid =" + str(prod[1]) + ";"
        sql = sqlalchemy.text(string)
        result = db_conn.execute(sql)
        result = list(result)

        item['cantidad'] = result[0][0]
        L.append(item)
    string = "SELECT DISTINCT orderdate FROM orders NATURAL JOIN orderdetail WHERE status = 'Paid' AND customerid = " + str(userid) +";"
    sql = sqlalchemy.text(string)
    result = db_conn.execute(sql)
    result = list(result)
    
    return render_template('historial.html', title = "Historial", historial = L, fechas = result)

@app.route('/numeroUsuarios/', methods=['GET'])
def numeroUsuarios():
    return str(random.randint(1, 1000))
