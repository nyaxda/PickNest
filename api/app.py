#!/usr/bin/python3

from flask import Flask
from api.views import app_views
from models import storage

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nyakundi'
# Registering app_views that has the routes
app.register_blueprint(app_views)


@app.teardown_appcontext
def close_storage(exception):
    """Closes the storage on teardown"""
    storage.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
