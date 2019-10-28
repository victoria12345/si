#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from flask import render_template, request, url_for, redirect, session
import json
import os
import sys
import hashlib
import os.path as path

@app.route('/')
@app.route('/index',methods=['GET','POST'])
def index():

    #creamos el carrito para la sesion

    if not "carrito" in session:

        session['carrito'] = [] #creamos una lista vacia para el carrito
        session['precio'] = 0 #ponemos el precio final a 0
        session.modified = True
    # print (url_for('static', filename='estilo.css'), file=sys.stderr)
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    return render_template('index.html', title = "Home", movies=catalogue['peliculas'][:10])


@app.route('/informacion/<pelicula_id>', methods=['GET','POST'])
def informacion(pelicula_id):
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)

    movies=catalogue['peliculas']

    for item in movies:
        if item['id'] == int(pelicula_id):
            return render_template('informacion.html', title = "Pelicula", film=item, flag=False)


    return 'error'


@app.route('/busqueda', methods=['GET','POST'])
def busqueda():
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    movies=catalogue['peliculas']

    L=[]

    if request.form['buscar'] != "":
        for item in movies:
            if request.form['buscar'].lower() in item['titulo'].lower():
                L.append(item)
        if request.form['categoria'] != "":
            for item in L:
                if item['categoria'] != request.form['categoria']:
                    L.remove(item)

    elif request.form['categoria'] != "":
        for item in movies:
            if item['categoria'] == request.form['categoria']:
                L.append(item)

    else:
        return redirect(url_for('index'))

    return render_template('index.html', title = "Home", movies=L)



@app.route('/login', methods=['GET', 'POST'])
def login():
    # doc sobre request object en http://flask.pocoo.org/docs/1.0/api/#incoming-request-data
    if 'username' in request.form:

        dato =[]
        i = 0
        cadena = os.getcwd() + "/app/usuarios/" + request.form['username']

        if path.exists(cadena):
            cadena = cadena + "/datos.dat"
            with open(cadena) as f:
                for linea in f:
                    dato.append ((linea.split(": ")[1]).split('\n')[0])
                    i = i + 1
                    if i == 2:
                        break
        else:
            # aqui se le puede pasar como argumento un mensaje de login invalido
            return render_template('login.html', title = "Sign In", mensaje="No has realizado Login correctamente. Intentalo de nuevo")


        aux2 = hashlib.md5(request.form['contrasenna'].encode())
        aux2 = "" + aux2.hexdigest()
        if request.form['username'] == dato[0] and aux2 == dato[1]:
            session['usuario'] = request.form['username']
            session.modified=True
            # se puede usar request.referrer para volver a la pagina desde la que se hizo login
            return redirect(url_for('index'))
        else:
            # aqui se le puede pasar como argumento un mensaje de login invalido
            return render_template('login.html', title = "Sign In", mensaje="No has realizado Login correctamente. Intentalo de nuevo")
    else:
        # se puede guardar la pagina desde la que se invoca
        session['url_origen']=request.referrer
        session.modified=True
        # print a error.log de Apache si se ejecuta bajo mod_wsgi
        # print (request.referrer, file=sys.stderr)
        return render_template('login.html', title = "Login")

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('usuario', None)
    return redirect(url_for('index'))

@app.route('/saldo', methods=['GET', 'POST'])
def saldo():

    if 'saldo' in request.form:
        if "usuario" in session:
            dato = []
            i = 0
            #tenemos que meternos en los datos del usuario y comprobar si tiene saldo
            cadena = os.getcwd() + "/app/usuarios/" + session['usuario']
            cadena = cadena + "/datos.dat"
            with open(cadena) as f:
                for linea in f:
                    dato.append ((linea.split(": ")[1]).split('\n')[0])
                    i = i + 1
                    if i == 5:
                        break;

            saldo = float(dato[4])

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

            return redirect(url_for('index'))

    else:
        return render_template('saldo.html', title = "Registrarse")

@app.route('/registro', methods=['GET', 'POST'])
def registro():

    if 'username' in request.form:


        cadena = os.getcwd() + "/app/usuarios/" + request.form['username']
        if path.exists(cadena):
            return render_template('registro.html', title = "Registro", mensaje="Ese nombre de usuario ya existe")
        else:
            #si el usuario no existe creamos el fichero datos.dat que contiene los datos del usuario
            os.mkdir(cadena)
            cadena_datos = cadena + "/datos.dat"
            f = open(cadena_datos, "w")
            aux_contrasenna = hashlib.md5(request.form['contrasenna'].encode())
            aux_contrasenna = "" + aux_contrasenna.hexdigest()

            f.write("usuario: " + request.form['username'] + "\n" +
                    "contrasenna: " + aux_contrasenna + "\n" +
                    "correo: " + request.form['email'] + "\n" +
                    "tarjeta: " + request.form['tarjeta'] + "\n" +
                    "saldo: " + "0" + "\n"
                    )
            f.close()

            #cuando ya hemos creado el fichero datos.dat tenemso que crear el historial.json
            cadena_historial = cadena + "/historial.json"

            f = open (cadena_historial, "w")

            historial = { 'peliculas': [] }

            f.write(json.dumps(historial))
            return redirect(url_for('index'))
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
    # print("hola")
    for item in movies:
            if item['id'] == int(pelicula_id):
                session['carrito'].append(int(pelicula_id))
                session['precio'] += item['precio']
                session.modified = True
                # print(item['poster'])
                # print(session['carrito'])
                # print(session['precio'])
                return render_template('informacion.html', title = "Pelicula", film=item, flag=True)

# #esta funcion nos permitira cargar el carrito de la compra: 
# es decir la vista y ademas realizar diferentes funciones con el carrito

@app.route('/carrito/', methods=['GET', 'POST'])
def carrito():
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    movies=catalogue['peliculas']
    L = []
    # print(request)
    for item in movies:
        if item['id'] in session['carrito']:
            L.append(item)

    return render_template('carrito.html', title = "Carrito", carrito_lista = L)


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
        cadena = os.getcwd() + "/app/usuarios/" + session['usuario']

        cadena = cadena + "/datos.dat"
        dato = []
        i = 0

        with open(cadena) as f:
            for linea in f:
                dato.append ((linea.split(": ")[1]).split('\n')[0])
                i = i + 1
                if i == 5:
                    break;

            saldo = float(dato[4])

            if saldo <= 0 and saldo < session['precio']:
                for item in movies:
                    if item['id'] in session['carrito']:
                        L.append(item)
                #si no tiene saldo tenemos que decirle que no tiene saldo suficiente
                #esto podemos hacerlo como en el login, enviando un mensaje de compra no valida porque no tienes saldo
                return render_template('carrito.html', title = "Carrito", carrito_lista = L, mensaje="No tienes saldo para realizar la compra")
            
            #en caso de que si tenga saldo, tenemos que modificarlo y restarselo.
            else:

                #annadimos al historial las pelis compradas
                cadena2 = os.getcwd() + "/app/usuarios/" + session['usuario']
                historial_data = open(cadena2 + '/historial.json', encoding="utf-8").read()
                historial = json.loads(historial_data)

                for i in session['carrito']:
                    for item in movies:
                        if i == item['id']:
                            historial['peliculas'].append(item)
                
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
    cadena2 = os.getcwd() + "/app/usuarios/" + session['usuario']
    catalogue_data = open(cadena2+'/historial.json', encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    movies=catalogue['peliculas']
    L = []
    # print(request)
    for item in catalogue['peliculas']:
        L.append(item)

    print(L)

    return render_template('historial.html', title = "Historial", historial = L)