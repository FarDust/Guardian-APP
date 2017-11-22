# from watcher import db
from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify
# import flask_bootstrap
import json

guardian = Blueprint('auth', __name__, url_prefix='/guardian')


@guardian.route('/')
def index(post_id):
    return render_template("guardian/index.html")
