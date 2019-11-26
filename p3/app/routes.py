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

    # catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    # catalogue = json.loads(catalogue_data)
    # movies=catalogue['peliculas']


    #creamos el carrito para la sesion
    if not "carrito" in session:
        session['n_producto_carrito'] = []
        for i in range(len(movies)):
            session['n_producto_carrito'].append(0)

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
    consulta += " NATURAL JOIN imdb_directormovies NATURAL JOIN products WHERE prod_id =" + pelicula_id

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
    consulta = "SELECT * FROM imdb_movies NATURAL JOIN products NATURAL JOIN imdb_moviegenres NATURAL JOIN genres movietitle like \'%"+titulo+"%\'"
    sql  = sqlalchemy.text(consulta)

    try:
        result = db_conn.execute(sql)
        result = list(result)
        L=[]
        for item in result:
            pelicula = {}
            pelicula['id'] = result[item][0]
            pelicula['titulo'] = result[item][1]
            pelicula['categoria'] = result[item][2]
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
    string = "SELECT password FROM customers WHERE username =\'" + username+"\'"
    sql = sqlalchemy.text(string)
    
    try:
        result = db_conn.execute(sql)
        result = list(result)
        if result[0]:
            #tenemos resultados, en el [0] se enecuentra la contraseña
            if result[0][0] == password:
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
            print(login_aux(username, password))

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

@app.route('/saldo', methods=['GET', 'POST'])
def saldo():
    dato = []
    i = 0
    #tenemos que meternos en los datos del usuario y comprobar si tiene saldo

    cadena = "usuarios/" + session['usuario'] + "/datos.dat"
    cadena = os.path.join(app.root_path,cadena)
    with open(cadena) as f:
        for linea in f:
            dato.append ((linea.split(": ")[1]).split('\n')[0])
            i = i + 1
            if i == 5:
                break

    saldo = float(dato[4])
    saldo = "{0:.2f}".format(saldo)
    saldo = float(saldo)

    if 'saldo' in request.form:
        if "usuario" in session:


            # Escribimos el nuevo saldo
            f = open(cadena, "r")
            lineas = f.readlines()
            f.close()

            f = open(cadena, "w")

            for linea in lineas:
                if not "saldo" in linea:
                    f.write(linea)

            saldo += float(request.form['saldo'])
            saldo_str = str(saldo)
            f.write("saldo: "+ saldo_str)

            return render_template('saldo.html', title = "Añadir Saldo", saldo = saldo)

    else:
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

# esta funcion nos permite añadir una pelicula al carrito de la compra. En la sesion hay un carrito de la compra creado
@app.route('/informacion/<pelicula_id>comprada', methods=['GET','POST'])
def comprar(pelicula_id):
    # Cuando compre una pelicula me pasan el id y tengo que comprobar que este en el catalogo.
    # Despues de comprobar que este en el catalogo tengo que añadir el id de la pelicula a la lista del carrito en la sesion
    # Tengo que actualizar el precio del carrito
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    movies=catalogue['peliculas']

    for item in movies:
            if item['id'] == int(pelicula_id):
                if 'carrito' not in session:
                    session['carrito'] = []
                session['carrito'].append(int(pelicula_id))
                if 'precio' not in session:
                    session['precio'] = 0
                session['precio'] += item['precio']
                if 'n_producto_carrito' not in session:
                    session['n_producto_carrito'] = []
                    for i in range(len(movies)):
                        session['n_producto_carrito'].append(0)
                session['n_producto_carrito'][int(pelicula_id)-1] += 1
                session.modified = True
                return render_template('informacion.html', title = "Pelicula", film=item, flag=True)

# #esta funcion nos permitira cargar el carrito de la compra:
# es decir la vista y ademas realizar diferentes funciones con el carrito

@app.route('/carrito/', methods=['GET', 'POST'])
def carrito():
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    movies=catalogue['peliculas']
    L = []

    for item in movies:
        if item['id'] in session['carrito']:
            L.append(item)

    return render_template('carrito.html', title = "Carrito", carrito_lista = L, numero_elementos = session['n_producto_carrito'], precio="{0:.2f}".format(session['precio']))


#con esta funcion eliminaremos una pelicula del carrito
@app.route('/carrito/<pelicula_id>eliminada', methods=['GET', 'POST'])
def eliminar(pelicula_id):
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    movies=catalogue['peliculas']
    L = []

    for item in movies:
        if item['id'] == (int(pelicula_id)):
            session['carrito'].remove(int(pelicula_id))
            session['precio'] -= item['precio']
            session['n_producto_carrito'][int(pelicula_id)-1] -= 1
    session.modified=True

    # for item in movies:
    #     if item['id'] in session['carrito']:
    #         L.append(item)
    # return carrito()
    return redirect(url_for('carrito'))


# Esta funcion nos permite finalizar la compra
# Para ello debemos comprobar que el usuario que esta en la sesion esta registrado o ha iniciado sesion
# Si no esta registrado, le llevaremos a la pagina donde se puede hacer login
# para finalizar una compra tambien se debe de tener saldo

@app.route('/finalizar', methods=['GET', 'POST'])
def finalizar():
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    movies=catalogue['peliculas']
    L = []

    #primero voy a comprobar que el usuario este registrado en la aplicacion

    #Si hay un usuario logeado en la sesion hacemos las comprobaciones pertinentes: saldo
    #si no esta logeado le llevamos a que inicie sesion
    if "usuario" in session:
        #tenemos que meternos en los datos del usuario y comprobar si tiene saldo

        cadena = "usuarios/" + session['usuario'] + "/datos.dat"
        cadena = os.path.join(app.root_path,cadena)

        dato = []
        i = 0

        with open(cadena) as f:
            for linea in f:
                dato.append ((linea.split(": ")[1]).split('\n')[0])
                i = i + 1
                if i == 5:
                    break;

            saldo = float(dato[4])

            if saldo <= 0 or saldo < session['precio']:
                for item in movies:
                    if item['id'] in session['carrito']:
                        L.append(item)
                #si no tiene saldo tenemos que decirle que no tiene saldo suficiente
                #esto podemos hacerlo como en el login, enviando un mensaje de compra no valida porque no tienes saldo
                return render_template('carrito.html', title = "Carrito", carrito_lista = L, mensaje="No tienes saldo para realizar la compra",numero_elementos = session['n_producto_carrito'], precio = session['precio'])

            #en caso de que si tenga saldo, tenemos que modificarlo y restarselo.
            else:

                #annadimos al historial las pelis compradas
                cadena2 = "usuarios/" + session['usuario']
                cadena2 = os.path.join(app.root_path,cadena2)
                historial_data = open(cadena2 + '/historial.json', encoding="utf-8").read()
                historial = json.loads(historial_data)
                fecha = time.strftime("%d/%m/%y")
                if str(fecha) not in historial:
                    historial[str(fecha)] = []

                for i in session['carrito']:
                    for item in movies:
                        if i == item['id']:
                            in_history = 0
                            for j in historial[str(fecha)]:
                                if j['id'] == item['id']:
                                    j['cantidad'] += 1
                                    in_history = 1
                            if not in_history:
                                item['cantidad']=1
                                historial[str(fecha)].append(item)






                with open(cadena2 + '/historial.json','w') as file:
                    json.dump(historial, file, indent= 3)


                f = open(cadena, "r")
                lineas = f.readlines()
                f.close()

                f = open(cadena, "w")

                for linea in lineas:
                    if not "saldo" in linea:
                        f.write(linea)
                saldo -= session['precio']
                session['precio'] = 0
                session['carrito'] = []
                for i in range(len(movies)):
                    session['n_producto_carrito'][i] = 0
                session.modified = True
                saldo_str = str(saldo)
                f.write("saldo: " + saldo_str + "\n")
                f.close()
                return redirect(url_for('carrito'))


    else:
        return render_template('login.html', title = "Login")

# #esta funcion nos permitira cargar el historial de un cliente

@app.route('/historial/', methods=['GET', 'POST'])
def historial():

    cadena2 = "usuarios/" + session['usuario']
    cadena2 = os.path.join(app.root_path,cadena2)

    catalogue_data = open(cadena2+'/historial.json', encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)

    return render_template('historial.html', title = "Historial", historial = catalogue)

@app.route('/numeroUsuarios/', methods=['GET'])
def numeroUsuarios():
    return str(random.randint(1, 1000))
