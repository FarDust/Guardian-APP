from flask import Flask, Response
# from flask_pymongo import PyMongo
import json
# Importar modulo de la base de datos

from flask import Flask
from guardian import render


app = Flask(__name__)
app.config.from_object('config')


@app.errorhandler(404)
def not_found(error):
    respuesta = Response(json.dumps(
        {"error": 404, "description": "route not found"}), status=404, mimetype='application/json')
    return respuesta


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = "Origin, X-Requested-With, Content-Type, Accept"
    return response


from watcher.mod_api.views import mod_api as api_module
from watcher.feeds.views import feeds as stream


app.register_blueprint(api_module)
app.register_blueprint(stream)
# app.register_blueprint(<another module>)
