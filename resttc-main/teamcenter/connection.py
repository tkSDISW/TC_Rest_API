"""
    Manages the connection with Teamcenter and handles command communication to
    Teamcenter service APIs
"""

__copyright__ = '''
# //--------------------------------------------------------------------------//
# //  Siemens Digital Industries Software                                     //
# //                                                                          //
# //  (C) Copyright 2022, Siemens                                             //
# //  All Rights Reserved                                                     //
'''
__license__ = '''
# //  Licensed Materials - Property of Siemens Digital Industries Software    //
# //                                                                          //
# //  No part of this file may be reproduced, stored in a retrieval system,   //
# //  or transmitted in any form or by any means --- electronic, mechanical,  //
# //  photocopying, recording, or otherwise --- without prior written         //
# //  permission of Siemens Digital Industries Software.                      //
# //                                                                          //
# //  WARRANTY:                                                               //
# //  Use all material in this file at your own risk. Siemens Digital         //
# //  Industries Software makes no claims about any material contained in     //
# //  this file.                                                              //
# //                                                                          //
'''
__authors__ = 'Jason Wickers <jason.wickers@siemens.com'
__version__ = '0.1'
__filename__ = 'connection.py'

from json import JSONDecodeError
import requests
import os
import sys

from teamcenter.handlers import HANDLERS
from teamcenter.alias import get_alias
from teamcenter.commands import get_command
from teamcenter.credentials import get_credentials, set_credential_dir

if sys.exec_prefix:
    set_credential_dir(sys.exec_prefix)

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls._instances[cls]

class TcConnection(metaclass=Singleton):
    def __init__(self, alias=None, credentials=None):
        self.set_alias(alias)
        self.set_credentials(credentials)
        self.logged_in = False       

    def set_alias(self, alias=None):
        global SET_ALIAS
        if alias is None:
            self.alias = SET_ALIAS
        else:
            self.alias = alias

    def set_credentials(self, credentials=None):
        if credentials:
            self.credentials = credentials
        else:
            self.credentials = get_credentials(self.alias.name)

    def handle(self, cmd):
        handler = HANDLERS.get(type(cmd))

        return handler(self, cmd)

    def login(self):
        self.session = requests.Session()

        li = get_command('Login')
        li.set_cmd(self.credentials.username,
                    self.credentials.password)
        result= self.handle(li)
        self.logged_in = True
        return result

    def logout(self):
        lo = get_command('Logout')
        lo.set_cmd()
        result = self.handle(lo)
        self.close()
        return result

    def close(self):
        self.session.cookies.clear()
        self.session.close()
        self.logged_in = False
        
    def __del__(self):
        try:
            self.close()
        except: pass
        
SET_ALIAS =  get_alias('DEFAULT')
def config_alias(alias = 'DEFAULT'):
    global SET_ALIAS
    
    SET_ALIAS = get_alias(alias)
    
    
def create_connection(alias):
    global SET_ALIAS

    if alias:
        #use the provided
        conn = TcConnection(alias)
        
    else:
        #use the configured
        conn = TcConnection(SET_ALIAS)

    return conn
    
#use only one connection, logged in only once for matlab (performance)
def get_connection(alias=None):
    conn = create_connection(alias)
    
    if not conn.logged_in:
        conn.login()
        
    return conn
    
def reset_connection():
    conn = get_connection()
    conn.logout()
