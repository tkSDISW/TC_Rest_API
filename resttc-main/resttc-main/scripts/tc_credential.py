#!Python

"""
    Creates a credential file to be used when connecting to Teamcenter
    for a given alias
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
__filename__ = 'tc_credential.py'

#Creates a credential file.
from cryptography.fernet import Fernet
import re
import ctypes
import time
import os
import sys
import getpass

from optparse import OptionParser

from pathlib import Path, PurePath

CREDENTIAL_DIR = PurePath(sys.exec_prefix, 'teamcenter')

class Credentials():

    def __init__(self, alias='DEFAULT'):
        self.__alias = alias
        self.__username = ""
        self.__key = ""
        self.__password = ""
        self.__key_file = PurePath(CREDENTIAL_DIR, alias + '_key.key')
        self.__time_of_exp = -1

#----------------------------------------
# Getter setter for attributes
#----------------------------------------

    @property
    def username(self):
        return self.__username

    @username.setter
    def username(self,username):
        while (username == ''):
            username = input('Enter a proper User name, blank is not accepted:')
        self.__username = username

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self,password):
        self.__key = Fernet.generate_key()
        f = Fernet(self.__key)
        self.__password = f.encrypt(password.encode()).decode()
        del f

    @property
    def expiry_time(self):
        return self.__time_of_exp

    @expiry_time.setter
    def expiry_time(self,exp_time):
        if(exp_time >= 2):
            self.__time_of_exp = exp_time


    def create_cred(self):
        """
        This function is responsible for encrypting the password and create key file for
        storing the key and create a credential file with user name and password
        """

        cred_filename = PurePath(CREDENTIAL_DIR, self.__alias + '_CredFile.ini')

        with open(cred_filename,'w') as file_in:
            file_in.write("#Credential file:\nUsername={}\nPassword={}\nExpiry={}\n"
            .format(self.__username,self.__password,self.__time_of_exp))
            file_in.write("++"*20)


        #If there exists an older key file, This will remove it.
        if(os.path.exists(self.__key_file)):
            os.remove(self.__key_file)

        #Open the Key.key file and place the key in it.
        #The key file is hidden.
        try:

            os_type = sys.platform
            if (os_type == 'linux'):
                self.__key_file = '.' + self.__key_file

            with open(self.__key_file,'w') as key_in:
                key_in.write(self.__key.decode())
                #Hidding the key file.
                #The below code snippet finds out which current os the script is running on and does the task base on it.
                if(os_type == 'win32'):
                    ctypes.windll.kernel32.SetFileAttributesW(str(self.__key_file), 2)
                else:
                    pass

        except PermissionError:
            os.remove(self.__key_file)
            print("A Permission error occurred.\n Please re run the script")
            sys.exit()

        self.__username = ""
        self.__password = ""
        self.__key = ""
        self.__key_file
        self.__alias
        

def main(alias):

    # Creating an object for Credentials class
    creds = Credentials(alias)

    #Accepting credentials
    creds.username = input("Enter UserName:")
    creds.password = getpass.getpass("Enter Password:")

    #calling the Credit
    creds.create_cred()
    print("**"*20)
    print("Cred file created successfully at {}"
    .format(time.ctime()))


    print("**"*20)

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-a", "--alias", dest="alias",
                        help="alias credential is for", default='DEFAULT')

    (options, args) = parser.parse_args()
    main(options.alias)
