"""
    Services and API available for communicating with Teamcenter
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
__authors__ = 'Jason Wickers <jason.wickers@siemens.com>'
__version__ = '0.1'
__filename__ = 'services.py'


import os
import urllib.parse
from urllib.request import urlretrieve
import inspect

import inflection
    
class TcRestService(object):
    '''
    A Teamcenter Service having APIs
    '''
    pass
        
#note: just add endpoints to add supported APIs!
API_ENDPOINTS = ['Core-2011-06-Session/login',
                     'Core-2006-03-Session/logout',
                     'Query-2010-04-SavedQuery/findSavedQueries',
                     'Query-2006-03-SavedQuery/describeSavedQueries',
                     'Query-2006-03-SavedQuery/executeSavedQuery',
                     'Core-2007-09-DataManagement/loadObjects',
                     'Core-2006-03-DataManagement/getProperties',
                     'Core-2007-01-DataManagement/getItemFromId',
                     'Core-2007-09-DataManagement/expandGRMRelationsForPrimary',
                     'Core-2016-09-DataManagement/createAttachAndSubmitObjects',
                     'Core-2008-06-DataManagement/createDatasets2',
                     'Cad-2007-01-StructureManagement/createBOMWindows',
                     'Cad-2007-01-StructureManagement/expandPSAllLevels',
                     'Cad-2007-01-StructureManagement/getRevisionRules',
                     'Internal-AWS2-2017-06-RequirementsManagement/exportToApplication3',
                     'AWS2-2018-12-RequirementsManagement/createTracelinks',
                     ]

def add_api_to_service(svc, api_name, endpoint):

    def fn(cls, conn, cmd):
        return cmd.send_to(conn, conn.alias.get_url(endpoint))
        
    setattr(svc, api_name, classmethod(fn))


for endpoint in API_ENDPOINTS:
    #print('Loading... ' + endpoint)
    service, api_name = endpoint.rsplit('/',1)
    
    #make snake case
    api_name = inflection.underscore(api_name)

    service_name = service.rsplit('-',1)[1]

    if service_name not in globals():
        svc = globals()[service_name] = type(service_name, (TcRestService, ), {})
    else:
        svc = globals()[service_name]

    add_api_to_service(svc, api_name, endpoint)

    del(api_name)
    del(service)
    del(service_name)
    del(svc)
    
class UndefinedService(Exception): pass


class FMSClient(TcRestService):

    @classmethod
    def download_file(cls, conn, cmd):

        return cmd.send_to(conn, None)
    

def get_service(service_name):
    svc = globals().get(service_name, object)
    if inspect.isclass(svc) and issubclass(svc, TcRestService) and svc != TcRestService:
        return svc
    else:
        raise UndefinedService('No Teamcenter service defined called: {}'.format(service_name))
