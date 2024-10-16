#!/usr/bin/python3

import sys
import os
from flasgger import Swagger
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

from flask import Flask  # noqa: E402
from api.views import app_views  # noqa: E402
from models import storage  # noqa: E402

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'nyakundi'
app.config['DEBUG'] = True

# Initialize Swagger
swagger = Swagger(app)

# Registering app_views that has the routes
app.register_blueprint(app_views)

@app.teardown_appcontext
def close_storage(exception):
    """Closes the storage on teardown"""
    storage.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
