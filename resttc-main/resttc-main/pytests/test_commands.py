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
__filename__ = 'test_commands.py'


import unittest
from unittest import TestCase

from teamcenter import commands

class TestCommands(TestCase):

    def test_get_command(self):
        commands.get_command('Login')
    
    def test_undefined(self):
        self.assertRaises(commands.UndefinedCommand, commands.get_command, 'foo')
        
    def test_cmd_set(self):
        l = commands.get_command('Login')
        l.set_cmd('ed','ed')
    
if __name__ == '__main__':
    unittest.main()
