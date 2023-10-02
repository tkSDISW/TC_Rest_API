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
__filename__ = 'test_services.py'


import unittest
from unittest import TestCase

from teamcenter import services

class MockAlias(object):
    @classmethod
    def get_url(cls, endpoint): return endpoint
    
    
class MockConn(object):
    alias = MockAlias()
    
class MockCmd(object):
    def send_to(self, conn, endpoint):
        return endpoint
    
class TestServices(TestCase):

    def test_rm(self):
        services.get_service('Session')
    
    def test_undefined(self):
        self.assertRaises(services.UndefinedService, services.get_service, 'foo')
        
    def test_api_on_service(self):
        session_svc = services.get_service('Session')
        result = session_svc.login(MockConn(), MockCmd())
        self.assertTrue(result.endswith('/login'))
    
    
if __name__ == '__main__':
    unittest.main()
