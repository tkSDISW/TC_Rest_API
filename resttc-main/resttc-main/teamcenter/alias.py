"""
    Sets and Provides the alias used for connecting with Teamcenter
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
__filename__ = 'alias.py'

import configparser
import sys
from pathlib import Path, PurePath

CONFIG_FILE = 'tcaliases.ini'

#tcalises.ini is installed in the teamcenter directory of the python that is running

ALIAS_DIR = None
if sys.exec_prefix:
    ALIAS_DIR = PurePath(sys.exec_prefix,'teamcenter')

def set_alias_dir(python_home):
    global ALIAS_DIR
    ALIAS_DIR = PurePath(python_home, 'teamcenter')

class TcAlias(object):

    def __init__(self, name='DEFAULT',
                        scheme = 'http',
                        host = '10.134.153.117',
                        port = '3000',
                        fmsport = '4544',
                        awpath='',
                        basepath = '/tc/JsonRestServices/'):
        self.name = name
        self.scheme = scheme
        self.host = host
        self.port = port
        self.fmsport = fmsport

        if len(awpath) > 1 and not awpath.endswith('/'):
            awpath += '/'
        self.awpath = awpath

        #should end with '/'
        if not basepath.endswith('/'):
            basepath += '/'
        
        #should not begin with '/' if awpath
        if self.awpath and basepath.startswith('/'):
            basepath = basepath[1:]

        self.basepath = basepath 
    
    def get_base_url(self):
        if self.port == '80':
            base_url = self.scheme + '://' + self.host + self.awpath
        
        else:
            base_url = self.scheme + '://' + self.host + ':' + self.port + self.awpath

        return base_url

    def get_fms_url(self):
        return self.scheme + '://' + self.host + ':' + self.fmsport
    
    def get_url(self, endpoint):
        return self.get_base_url() + self.basepath + endpoint

def load_aliases():
    global ALIASES
    global ALIAS_DIR
    ALIASES = {}

    config_fpath = PurePath(ALIAS_DIR, CONFIG_FILE)
    
    config = configparser.ConfigParser()
    config.read(config_fpath)

    for section in config:
        myalias = TcAlias()
        myalias.name = section
        myalias.scheme = config[section].get('scheme',myalias.scheme)
        myalias.host = config[section].get('host',myalias.host)
        myalias.port = config[section].get('port',myalias.port)
        myalias.fmsport = config[section].get('fmsport',myalias.fmsport)
        myalias.awpath = config[section].get('awpath',myalias.awpath)
        myalias.basepath = config[section].get('basepath',myalias.basepath)

        #should end with '/'
        if not myalias.basepath.endswith('/'):
            myalias.basepath += '/'
            
        if not myalias.basepath.startswith("/"):
            myalias.basepath = "/" + myalias.basepath
            
        #awpath should not end with /
        if myalias.awpath.endswith("/"):
            myalias.awpath = myalias.awpath[:-1]

        ALIASES[section] = myalias
    

ALIASES = None
def get_alias(name='DEFAULT'):
    global ALIASES
    
    if not ALIASES:
        load_aliases()
        
    return ALIASES.get(name, TcAlias(name))
    
