""" 
 This file is part of Pypers.

 Pypers is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 Pypers is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Pypers.  If not, see <http://www.gnu.org/licenses/>.
 """

import os
import ldap

from flask import request, make_response, jsonify, g
from flask.ext.restful import reqparse, Resource
from flask.ext.httpauth import HTTPBasicAuth

from itsdangerous import TimedJSONWebSignatureSerializer as TimedJWSSerializer
from itsdangerous import SignatureExpired, BadSignature
from flask.ext.cache import Cache
from passlib.apps import custom_app_context as pwd_context
from bson import json_util

from nespipe.utils import utils as ut
from nespipe import config as cfg 
from nespipe.utils.security import KEYDIR

from nespipe.api import app, cache
from nespipe.db.models.mongo import PipelineDbConnector


auth = HTTPBasicAuth()
db = PipelineDbConnector()


def install_secret_key(app):
    """
    Configure the SECRET_KEY from a file in the instance directory.
    If the file does not exist, print instructions to create it from a shell with a random key, then exit.
    """
    keyfile = os.path.join(KEYDIR, 'flask_key')
    try:
        if not os.path.exists(keyfile):
            ut.pretty_print('No key file found: creating it')
            if not os.path.exists(KEYDIR):
                os.makedirs(KEYDIR, mode=0700)
            with open(keyfile, 'wb') as fh:
                key = os.urandom(256)
                fh.write(key)
                app.config['SECRET_KEY'] = key
        else:
            app.config['SECRET_KEY'] = open(keyfile, 'rb').read()
    except:
        raise Exception("Unable to install flask key")



def generate_token(username, password, expiration=600):
    """
    Generate an authorized token
    """

    doc = {'username':username, 'password_hash':pwd_context.encrypt(password)}
    db.sessions.find_one_and_update(
        {'username': username},
        {"$set": doc},
        upsert=True
    )

    if (cfg.ACME_PROD or cfg.ACME_DEV) and (username == 'serveruser'):
        EXPIRES_IN_A_YEAR = 365 * 24 * 60 * 60
        print 'token that EXPIRES_IN_A_YEAR'
        s = TimedJWSSerializer(app.config['SECRET_KEY'], expires_in=EXPIRES_IN_A_YEAR)
    else:
        print 'token that expires', cfg.ACME_LCL
        s = TimedJWSSerializer(app.config['SECRET_KEY'], expires_in=expiration)

    return s.dumps({'username': username, 'password': password})

@cache.cached(timeout=60*5)
def verify_token(username, token):
    """
    Verify validity of token
    """
    s = TimedJWSSerializer(app.config['SECRET_KEY'])

    try:
        ut.pretty_print("Trying to load the token")
        data = s.loads(token)
    except SignatureExpired:
        ut.pretty_print("ERROR: Expired Token")
        return False
    except BadSignature:
        ut.pretty_print("ERROR: Invalid Token")
        return False
    else:
        ut.pretty_print("Token successfully loaded")
        stored = db.sessions.find_one(filter={'username': data['username']}, sort=[('_id',-1)])

        if not stored:
            return False
        result = json_util.loads(json_util.dumps(stored))

        return pwd_context.verify(data['password'], result['password_hash']) and data['username'] == username


def auth_get_username(auth, user):
    """
    Get the username from a token
    """
    s = TimedJWSSerializer(app.config['SECRET_KEY'])

    token_user = s.loads(auth.get('password')).get('username')
    return token_user


@auth.verify_password
def verify_authorization(username, token):
    return verify_token(username, token)

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


class Authentication(Resource):
    """
    This class is the interface to execute  pipeline
    """
    parser = reqparse.RequestParser()

    def post(self):
        """
        Queue the specific pipeline type
        """
        user = request.form['user']
        password = request.form['password']

        # ip = request.remote_addr

        ut.pretty_print("Checking user %s" % user)

        # TODO : Provide proper code for special users wilee and demux
        if((cfg.ACME_DEV or cfg.ACME_PROD) and (user == 'wilee' or user == 'demux')):
            return {'token': generate_token(user, password)}
        else:
            try:
                # Make sure the password is not empty to prevent LDAP anonymous bind to succeed
                if not password:
                    raise ldap.LDAPError("Empty password for user %s!" % user)

                #check if the LDAP binding works
                ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
                conn = ldap.initialize(cfg.LDAPS_ADDRESS)
                conn.set_option(ldap.OPT_REFERRALS, 0)
                conn.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
                conn.set_option(ldap.OPT_X_TLS_CACERTFILE, cfg.search_cfg_file('certificate_file.cer'))
                conn.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
                conn.set_option(ldap.OPT_X_TLS_DEMAND, True)

                bind = conn.simple_bind_s("%s@%s"%user, password, cfg.COMPANY_ADDRESS)
                ut.pretty_print("Bind success!!")
                #then create a session
                return {'token' : generate_token(user, password)}
            except ldap.LDAPError, e:
                ut.pretty_print("ERROR: authentication error: %s" % e)
                return "Authentication error", 401


    class VerifyToken(Resource):
        def get(self):
            """
            Validate the input token
            """
            parser = reqparse.RequestParser()
            parser.add_argument('token', type=str, default=None)
            parser.add_argument('username',  type=str, default=None)
            args = parser.parse_args()
            token = args.get('token')
            username = args.get('username')

            return {'valid': verify_token(username, token)}


    @staticmethod
    def connect(api):
        """
        Connects the endpoints to the API
        """
        api.add_resource(Authentication,                '/login')
        api.add_resource(Authentication.VerifyToken,    '/verifytoken')
