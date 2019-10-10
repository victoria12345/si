#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from flask import render_template, request, url_for, redirect, session
import json
import os
import sys

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

@app.route('/registro',methods=['GET','POST'])
def registro():
    # print (url_for('static', filename='estilo.css'), file=sys.stderr)
    # catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    # catalogue = json.loads(catalogue_data)
    return render_template('registro.html', title = "Registro")


@app.route('/busqueda', methods=['GET','POST'])
def busqueda():
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    movies=catalogue['peliculas']

    L=[]

    if request.form['buscar'] != "":
        for item in movies:
            if item['titulo'] == request.form['buscar']:
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

        #tendriamos que situarnos en la carpeta que tiene nombre <username>
        #tendriamos que hacer un fread del fichero datos.dat

        if request.form['username'] == '':
            session['usuario'] = request.form['username']
            session.modified=True
            # se puede usar request.referrer para volver a la pagina desde la que se hizo login
            return redirect(url_for('index'))
        else:
            # aqui se le puede pasar como argumento un mensaje de login invalido
            return render_template('login.html', title = "Sign In")
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
