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
__filename__ = 'test_connection.py'


import copy
import unittest
from unittest import TestCase

from teamcenter import connection

class MockCmd:
    def set_cmd(self, *args, **kwargs): pass

    def send_to(self, conn, endpoint): pass

def mock_get_command(cmd_name):
        
    return MockCmd()
        
def mock_handle(conn, ednpoint):

    pass
    

class TestConnection(TestCase):

    def setUp(self):
        self.original_get = connection.get_command
        self.original_handlers = copy.copy(connection.HANDLERS)
        connection.get_command = mock_get_command
        connection.HANDLERS[MockCmd] = mock_handle
    
    def tearDown(self):
        connection.get_command = self.original_get
        connection.HANDLERS = self.original_handlers

    def test_get_connection(self):
        pass #conn = connection.get_connection()
    
if __name__ == '__main__':
    unittest.main()
