# from watcher import db
from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify, Response
# import flask_bootstrap
import json
from watcher import render

render.start()


def gen():
    while True:
        frame = render.get_frame()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


feeds = Blueprint('auth1', __name__, url_prefix='/feed')


@feeds.route('/')
def index():
    return render_template("feed/index.html")


@feeds.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
