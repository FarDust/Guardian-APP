from watcher import app
from flask import render_template, request, Response, send_from_directory, request
from pymongo import *
# from watcher.db import Database as DB
import json
# import flask_bootstrap


@app.route('/')
def inicio():
    """
    Ruta de inicio de la API. Retorna un simple string
    de bievenida.
    """
    return render_template("index.html")