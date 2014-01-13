# -*- coding: utf-8 -*-
# :Progetto:  otpauth --
# :Creato:    gio 26 dic 2013 00:39:30 CET
# :Autore:    Alberto Berti <alberto@metapensiero.it>, Sean Davis
# :Licenza:   GNU General Public License version 2 or later
#
import logging
from functools import wraps
import urllib
import urllib2
from flask import Flask, request, Response, json, session, after_this_request

logger = logging.getLogger('otpauth')

def checkAuth(config, username, password):
    """This function is called to check if a username /
    password combination is valid.
    The response json structure is something similar to::

     {
       "version": "LinOTP 2.4",
       "jsonrpc": "2.0",
       "result": {
          "status": true,
          "value": false
       },
       "id": 0
     }

    If status is true the request was handled successfully.
    If value is true the user was authenticated successfully.

    See http://www.linotp.org/doc/latest/part-module-dev/authentication/validate.html
    """
    result = False
    validator_url = config.get('OTP_VALIDATOR_URL')
    realm = config.get('OTP_REALM')
    data = {'user': username, 'pass': password}
    if realm is not None:
        data['realm']
    data = urllib.urlencode(data)
    url = '{0}?{1}'.format(validator_url, data)
    try:
        response_file = urllib2.urlopen(url, timeout=3)
        auth_data = json.load(response_file)
        result = auth_data['result']['status'] and auth_data['result']['value']
    except:
        raise
    return result


def fillSession(session, request, client_ip):
    session['username'] = request.auth.username
    session['client_ip'] = client_ip


def inc_session():
    c = session.setdefault('counter', 0)
    session['counter'] = c + 1
    print c


def authenticate(realm):
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="{0}"'.format(realm)})


def getUpstreamReqData(app, request):
    data_src = app.config.get('SERVER_TYPE', 'paster')
    if data_src == 'paster':
        data = dict(method=request.headers['X-Original-Method'],
                    client_ip=request.headers['X-Original-Remote-Address'],
                    realm=request.headers.get('X-OTP-Realm', 'Login required'))
    elif data_src == 'uwsgi':
        data = dict(method=request.headers['ORIGINAL_METHOD'],
                    client_ip=request.headers['ORIGINAL_REMOTE_ADDRESS'],
                    realm=request.headers.get('OTP_REALM', 'Login required'))
    return data

application = Flask(__name__)


@application.route('/login')
def login():
    auth = request.authorization
    req_data = getUpstreamReqData(application, request)
    logger.debug('Client IP: %s, method: %s, realm: %s', req_data['client_ip'],
                 req_data['method'], req_data['realm'])
    if req_data['method'] not in ['GET', 'HEAD']:
        if not 'counter' in session:
            print "session not present"
            if not auth or not checkAuth(application.config, auth.username,
                                         auth.password):
                return authenticate()
            else:
                inc_session()
        else:
            inc_session()
    return 'OK'


def app_factory(global_conf, **local_conf):
    from logging.config import fileConfig
    from ConfigParser import ConfigParser
    import os
    application.config.update(local_conf)
    config_file = os.path.abspath(global_conf['__file__'])
    parser = ConfigParser()
    parser.read(config_file)
    if parser.has_section('loggers'):
        fileConfig(config_file,
                   dict(__file__=config_file, here=os.path.dirname(config_file)))

    return application.wsgi_app

if __name__ == '__main__':
    application.run()
