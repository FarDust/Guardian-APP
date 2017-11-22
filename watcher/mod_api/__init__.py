from flask import Flask
from requests import get,post,put

app = Flask(__name__)

import watcher.views

if __name__ == "__main__":
    app.run(port=5001,debug=True)
