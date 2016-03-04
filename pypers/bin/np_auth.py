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

import getpass
import nespipe.utils.utils as ut

from nespipe.utils import security

if __name__ == '__main__':

    doc="""
    Create a new  authentication tokem
    """

    user = getpass.getuser()
    token = security.read_token()
    if not security.validate_token(token):
        ut.pretty_print("get new toke....")
        token = security.get_new_token(user)
    else:
        ut.pretty_print('%s already has a valid token' % user)

