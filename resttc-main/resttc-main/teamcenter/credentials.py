"""
    Manages the user credentials during communication with
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
__filename__ = 'credentials.py'
import sys
from pathlib import Path, PurePath
from cryptography.fernet import Fernet

CREDENTIAL_DIR = None
if sys.exec_prefix:
    CREDENTIAL_DIR = PurePath(sys.exec_prefix, 'teamcenter')

def set_credential_dir(python_home):
    global CREDENTIAL_DIR

    CREDENTIAL_DIR = PurePath(python_home, 'teamcenter')

class TcCredentials(object):

    def __init__(self, alias, credentials):
        self.__credentials = credentials
        self.set_key(alias)

    def set_key(self,alias):
        self.__key = get_key(alias)
        
    @property
    def username(self):
        return self.__credentials['Username']
        
    @property
    def password(self):
        f = Fernet(self.__key)
        epasswd = self.__credentials['Password']
        
        passwd = f.decrypt(epasswd.encode()).decode()
        return passwd
        
def get_key(alias):
    global CREDENTIAL_DIR
    key_file = PurePath(CREDENTIAL_DIR, alias + '_key.key') 
    key = ''

    kf = Path(key_file)
    if not kf.is_file():
        raise Exception('Key File does not exist for alias: {}'.format(alias))

    with open(str(key_file),'r') as key_in:
        key = key_in.read().encode()

    return key

def get_credentials(alias):
    global CREDENTIAL_DIR
    cred_filename = PurePath(CREDENTIAL_DIR, alias + '_CredFile.ini')
    cf = Path(cred_filename)
    if not cf.is_file():
        raise Exception('Credential file does not exist for alias: {}'.format(alias))
     
    key = get_key(alias)
    f = Fernet(key)
    with open(cred_filename,'r') as cred_in:
        lines = cred_in.readlines()
        credentials = {}
        for line in lines:
            tuples = line.rstrip('\n').split('=',1)
            if tuples[0] in ('Username','Password'):
                credentials[tuples[0]] = tuples[1]
     
    return TcCredentials(alias, credentials)
    