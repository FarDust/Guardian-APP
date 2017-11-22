# from watcher import db
from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify
# import flask_bootstrap
import json

mod_api = Blueprint('auth', __name__, url_prefix='/api')


@mod_api.route('/<string:post_id>', methods=['GET', 'POST'])
def index(post_id):
    #db.db.users.find({'_id': post_id})
    return render_template("api/index.html")


@mod_api.route('/menssages/<id>', methods=["GET"])
def mensajes(r_id):
    return jsonify(db["menssage"].find_one({"id": r_id}, {"_id": 0})), 200


@mod_api.route('/artits/<id>', methods=["GET"])
def artista(r_id):
    return jsonify(db["artist"].fin_one({"id": r_id}, {"_id": 0}))
