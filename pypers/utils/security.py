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
import getpass
import requests
import nespipe.utils.utils as ut
from nespipe.config import cfg cfg.SERVICE_ROOT_URL, cfg.SSL_CERTIFICATE


KEYDIR     = os.path.join(os.getenv('HOME'), ".ssh")
TOKEN_FILE = os.path.join(KEYDIR, 'pypers-token')



def save_token(token):
    """
    Save the token file in the token directory
    """

    if not os.path.exists(KEYDIR):
        os.makedirs(KEYDIR, mode=0600)
    with open(TOKEN_FILE, 'w') as fh:
        fh.write(token)
    os.chmod(TOKEN_FILE, 0600)


def read_token():
    """
    Read the token file from the token directory
    """

    token = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as fh:
            token = fh.read()
    return token


def get_new_token(user):
    """
    Send request to the server to get a new token
    """

    pwrd = getpass.getpass("Please enter your password: ")
    address = "%s/login" % (cfg.SERVICE_ROOT_URL)
    data = {'user': user, 'password': pwrd}
    ut.pretty_print("Sending request to...%s" % address)
    response = requests.post(address, data=data, verify=False)
    if response.json().get('token'):
        ut.pretty_print("user %s successsfully authenticated" % user)
        token = response.json()['token']
        save_token(token)
    else:
        ut.pretty_print("Invalid username or password")
        token = None
    return token

def validate_token(token):
    """
    Send request to the server to check if the token is valid
    """

    valid = False
    if token:
        address = "%s/verifytoken" % (cfg.SERVICE_ROOT_URL)
        ut.pretty_print("Sending request to...%s" % address)
        response = requests.get(address, data={"token": token, "username": getpass.getuser()}, verify=False)
        valid = response.json()['valid']
    if not valid:
        ut.pretty_print("User %s not authenticated" %getpass.getuser())
    return valid


def get_token(user):
    """
    Read the stored token and check is validity.
    If the local token is not valid then get a new token from the server
    performing an ldap authentication
    """
    token = read_token()
    if not validate_token(token):
        token = get_new_token(user)
        save_token(token)
    return token

