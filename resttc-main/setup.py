from setuptools import setup

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

setup(name='Siemens Teamcenter integration',
      version='0.1.7',
      description='Use Python to integrate with Teamcenter',
      author='Jason Wickers',
      author_email='jason.wickers@siemens.com',
      packages=['teamcenter'],
      install_requires=['certifi','requests','inflection','bs4','cryptography'],
      package_data={'teamcenter': ['icons/*.png','matlab/*.m']},
      data_files=[('teamcenter', ['tcaliases.ini','docs/Install Guide - Requirements integration for MATLAB_SIMULINK.pdf'])],
      scripts=['scripts/tc_credential.py'],
      test_suite='pytests',
      license=__license__
     )