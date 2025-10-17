#!/usr/bin/env python
from . import bp
from flask import redirect, session, current_app
from urllib.parse import urlencode

def authz_url() -> str:
   params = {
       "response_type": "code",
       "client_id": current_app.config['CLIENT_ID'],
       "redirect_uri": current_app.config['REDIRECT_URI'],
       "scope": current_app.config['SCOPES'],
       "state": current_app.config['STATE_FIXED'],
   }
   return f"{current_app.config['AUTH_URL']}?{urlencode(params)}"


@bp.route('/login')
def login():
   session.pop("last_error", None)
   url = authz_url()
   print(url)
   print("[DEBUG] CLIENT_ID repr:", repr(current_app.config['CLIENT_ID']))
   print("[DEBUG] AUTH URL:", url)
   return redirect(url)
