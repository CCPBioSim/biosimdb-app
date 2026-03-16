#!/usr/bin/env python
from flask import Blueprint

form_bp = Blueprint('form', __name__)

from . import webform
from . import webform2