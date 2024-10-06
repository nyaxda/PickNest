#!/usr/bin/python3
"""Blueprint for API"""

from flask import Blueprint

app_views = Blueprint('app_views', __name__, url_prefix='/api/')

from api.views.address import *  # noqa: E402
from api.views.client import *  # noqa: E402
from api.views.company import *  # noqa: E402
from api.views.items import *  # noqa: E402
from api.views.order_items import *  # noqa: E402
from api.views.orders import *  # noqa: E402
from api.views.payments import *  # noqa: E402
