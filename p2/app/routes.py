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
            return render_template('informacion.html', title = "Pelicula", film=item)


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
            return render_template('login.html', title = "Sign In", mensaje="Login invalido")


        aux2 = hashlib.md5(request.form['contrasenna'].encode())
        aux2 = "" + aux2.hexdigest()
        if request.form['username'] == dato[0] and aux2 == dato[1]:
            session['usuario'] = request.form['username']
            session.modified=True
            # se puede usar request.referrer para volver a la pagina desde la que se hizo login
            return redirect(url_for('index'))
        else:
            # aqui se le puede pasar como argumento un mensaje de login invalido
            return render_template('login.html', title = "Sign In", mensaje="Login invalido2")
    else:
        # se puede guardar la pagina desde la que se invoca
        session['url_origen']=request.referrer
        session.modified=True
        # print a error.log de Apache si se ejecuta bajo mod_wsgi
        print (request.referrer, file=sys.stderr)
        return render_template('login.html', title = "Login")

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('usuario', None)
    return redirect(url_for('index'))



@app.route('/registro', methods=['GET', 'POST'])
def registro():

    if 'username' in request.form:


        cadena = os.getcwd() + "/app/usuarios/" + request.form['username']
        if path.exists(cadena):
            return render_template('registro.html', title = "Registro", mensaje="Ese nombre de usuario ya existe")
        else:

            os.mkdir(cadena)
            cadena = cadena + "/datos.dat"
            f = open(cadena, "w")
            aux_contrasenna = hashlib.md5(request.form['contrasenna'].encode())
            aux_contrasenna = "" + aux_contrasenna.hexdigest()

            f.write("usuario: " + request.form['username'] + "\n" +
                    "contrasenna: " + aux_contrasenna + "\n" +
                    "correo: " + request.form['email'] + "\n" +
                    "tarjeta: " + request.form['tarjeta'] + "\n" +
                    "saldo: " + "0" + "\n"
                    )
            f.close()
            return redirect(url_for('index'))
    else:
        return render_template('registro.html', title = "Registrarse")
