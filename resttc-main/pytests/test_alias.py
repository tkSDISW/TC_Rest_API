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
__filename__ = 'test_alias.py'


import unittest
from unittest import TestCase

from teamcenter import alias
from urllib import parse

class TestAlias(TestCase):

    def test_alias(self):
        myalias = alias.get_alias('DEFAULT')
    
    def test_get_base_url(self):
        myalias = alias.get_alias('DEFAULT')
        myalias.get_base_url()
        
    def test_get_fms_url(self):
        myalias = alias.get_alias('DEFAULT')
        myalias.get_fms_url()
    
    def test_get_url(self):
        myalias = alias.get_alias('DEFAULT')
        myalias.get_url('foo')

    def test_dev_1(self):
        myalias = alias.get_alias('DEV 1')
        myalias.get_url('foo')
        self.assertNotEqual(myalias.host,'localhost')

    def test_aliases(self):
        for a in alias.ALIASES.values():
            print(a.get_url('endpoint'))
            print(a.get_base_url())
    
if __name__ == '__main__':
    unittest.main()
