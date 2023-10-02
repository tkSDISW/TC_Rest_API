"""
    Commands for Teamcenter Service APIs
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
__filename__ = 'commands.py'


import os
import sys
import base64
import pathlib
import urllib.parse
import json
import html
import uuid
import inspect
import pprint
import tempfile
from urllib.request import urlretrieve
from bs4 import BeautifulSoup

from pathlib import Path, PurePath

class TcCommand(object):
    DEFAULT_JSON_CMD = {
          "header": {
            "state": {
              "stateless": True,
              "clientID": "ActiveWorkspaceClient"
            }
          },
          "body": {}
        }
    
    def __init__(self):
        self.cmd_json = {}
        self.cmd_json.update(TcCommand.DEFAULT_JSON_CMD)
        
    def set_cmd(self,*args,**kwargs):
        raise NotImplementedError('Implement Me')
        
    def send_to(self, conn, endpoint):
        raise NotImplementedError('Implement Me')
        
    def _send_to(self, conn, endpoint):
        
        headers = {}
        headers.update({'Cache-Control':'no-cache, no-store, must-revalidate'})
        headers.update({'Pragma':'no-cache'})
        headers.update({'Expires':'0'})

 
        response = conn.session.post(endpoint, 
                data=json.dumps(self.cmd_json), 
                headers=headers
                )
                
        response.raise_for_status()
        
        executed_result = response.json()
        return executed_result


class CreateItem(TcCommand):

    def set_cmd(self, name, description):
        
        self.cmd_json["body"] = {
            "inputs": [
              {
                "clientId": "CreateObject",
                "createData": {
                  "boName": "Item",
                  "propertyNameValues": {
                    
                    "object_name": [
                      name
                    ],
                    "object_desc": [
                      description
                    ]
                  },
                  "compoundCreateInput": {
                    "revision": [
                      {
                        "boName": "ItemRevision",
                        "propertyNameValues": {
                          "item_revision_id": [
                            "A"
                          ],
                          "fnd0ContextProvider": [
                            ""
                          ]
                        },
                        "compoundCreateInput": {}
                      }
                    ]
                  }
                },
                "dataToBeRelated": {},
                "workflowData": {},
                "pasteProp": "",
                "targetObject": {
                  "uid": "AAAAAAAAAAAAAA",
                  "type": "unknownType"
                }
              }
            ]
          }

    def send_to(self, conn, endpoint):
        executed_result = self._send_to(conn, endpoint)
        
        for o in executed_result["output"][0]["objects"]:
            if o["type"] == "ItemRevision":
                return o
                
        return None

class CreateAndRelateDataset(TcCommand):

    def set_cmd(self, container, dataset_name, description, dataset_type="HTML", relation_type="TC_Attaches"):
        self.cmd_json["body"] = {
                "input": [
                    {
                        "clientId": dataset_name,
                        "type": dataset_type,
                        "name": dataset_name,
                        "description": description,
                        "toolUsed": "",
                        "datasetId": "",
                        "datasetRev": "",
                        "container": container,
                        "relationType": relation_type
                    }
                ]
            }
        

    def send_to(self, conn, endpoint):
        executed_result = self._send_to(conn, endpoint)

        assert len(executed_result["output"]) >= 1 , 'Expected at least one output result\n' + str(executed_result)

        return executed_result["output"][0]

class GetRelatedDatasets(TcCommand):

    def set_cmd(self, primary_obj, relation_type="TC_Attaches"):
        self.cmd_json["body"] = {
                "primaryObjects": [
                    primary_obj
                ],
                "pref": {
                    "expItemRev": False,
                    "returnRelations": False,
                    "info": [
                        {
                        "relationTypeName": relation_type,
                        "otherSideObjectTypes": []
                    }
                    ]
                 }
            }
        
        
    def send_to(self, conn, endpoint):
        executed_result = self._send_to(conn, endpoint)
        
        result = []
        for plain in executed_result["ServiceData"]["plain"]:
            result.append(executed_result["ServiceData"]["modelObjects"][plain])
            
        return result

class CreateTraceLinks(TcCommand):

    def set_cmd(self, primary_obj, secondary_obj, relation_type="FND_TraceLink"):
        self.cmd_json["body"] = {
                "input": [
                    {
                        "clientId": "",
                        "tracelinkCreateInput": {
                            "boName": relation_type,
                            "propertyNameValues": {},
                            "compoundCreateInput": {}
                        },
                        "primaryObj": primary_obj,
                        "secondaryObj": secondary_obj,
                        "requestPref": {}
                    }
                ]
            }

    def send_to(self, conn, endpoint):
        executed_result = self._send_to(conn, endpoint)

        try:
            return executed_result["output"][0]["traceLinkObject"]
        except :
            return None
            

class Login(TcCommand):

    def set_cmd(self, username , password , group="", role="", locale="en_US"):
        suuid = str(uuid.uuid1())
        self.cmd_json["body"] = {
                "credentials": {
                    "user": username,
                    "password": password,
                    "group": group,
                    "role": role,
                    "locale": locale,
                    "descrimator": "PYTHON-" + suuid
                }
            }
            
            
    def send_to(self, conn, endpoint):
        conn.session.get(conn.alias.get_base_url())
        if 'XSRF-TOKEN' in conn.session.cookies:
            conn.session.headers.update({'X-XSRF-TOKEN':conn.session.cookies['XSRF-TOKEN']})

        if '_csrf' in conn.session.cookies:
            conn.session.headers.update({'X-CSRFToken':conn.session.cookies['_csrf']})
        
        executed_result = self._send_to(conn, endpoint)
        
        return executed_result    
            
            
class Logout(TcCommand):

    def set_cmd(self):
        self.cmd_json["body"] = { }
            
            
    def send_to(self, conn, endpoint):

        executed_result = self._send_to(conn, endpoint)
        
        return executed_result    

class GetItemFromId(TcCommand):

    def set_cmd(self, itemid, itemrev, returnRev=True):
        self.returnRev = returnRev

        self.cmd_json["body"] = {
                "infos": [
                    {
                        "itemId": itemid,
                        "revIds": [
                            itemrev
                        ]
                    }
                ],
                "nRev": 0,
                "pref": {
                    "prefs": []
                }
            }
            
            
    def send_to(self, conn, endpoint):

        executed_result = self._send_to(conn, endpoint)
        
        if self.returnRev:
            output = executed_result["output"][0]["itemRevOutput"]
            if isinstance(output, list):
                output = output[0]["itemRevision"]
        else:
            output = executed_result["output"][0]["item"]
            
        return executed_result["ServiceData"]["modelObjects"][output["uid"]]
    
class GetRevisionRule(TcCommand):

    def set_cmd(self, rev_rule_name):
        self.rev_rule_name = rev_rule_name

        self.cmd_json["body"] = { }

    def send_to(self, conn, endpoint):
    
        get_rev_rules_result = self._send_to(conn, endpoint)
    
        for mo in get_rev_rules_result["ServiceData"]["modelObjects"].values():
            if not "props" in mo:
                continue
                
            if not "object_name" in mo["props"]:
                continue
                
            if mo["props"]["object_name"]["uiValues"] == [self.rev_rule_name]:
                return mo

        return None

class CreateBOMWindow(TcCommand):

    def set_cmd(self, itemrev_model_object, rev_rule):

        self.cmd_json["body"] = {
                "info": [
                    {
                        "clientId": "SIMULINK",
                        "item": "None2",
                        "itemRev": itemrev_model_object,
                        "bomView": "None2",
                        "revRuleConfigInfo": {
                            "clientId": "SIMULINK",
                            "revRule": rev_rule,
                            "props": {
                                "unitNo": -1,
                                "date": "",
                                "today": True,
                                "endItem": "None2",
                                "endItemRevision": "None2",
                                "overrideFolders": [
                                    {
                                        "ruleEntry": "None2",
                                        "folder": "None2"
                                    }
                                ]
                            }
                        },
                        "objectForConfigure": "None2",
                        "activeAssemblyArrangement": "None2"
                    }
                ]
            }
    
    def send_to(self, conn, endpoint):

        executed_result = self._send_to(conn, endpoint)
        
        return executed_result["output"][0]["bomLine"]
        
        
class ExpandGRMRelationsForPrimary(TcCommand):

    def set_cmd(self, primary_objs, relation_name='TC_Attaches'):
        self.cmd_json["body"] = {
            "primaryObjects": primary_objs,
            "pref": {
                "expItemRev": False,
                "returnRelations": False,
                "info": [
                    {
                    "relationTypeName": relation_name,
                    "otherSideObjectTypes": []
                }
                ]
             }}

    def send_to(self, conn, endpoint):

        executed_result = self._send_to(conn, endpoint)
        
        return executed_result

class ExpandPSAllLevels(TcCommand):

    def set_cmd(self, bom_line):
        self.cmd_json["body"] = {
                "input": {
                    "parentBomLines": [bom_line],
                    "excludeFilter": "None",
                },
                "pref": {
                    "expItemRev": False,
                    "info":[]
                }
            }

    def send_to(self, conn, endpoint):

        executed_result = self._send_to(conn, endpoint)
        
        return executed_result

class DescribeSavedQueries(TcCommand):

    def set_cmd(self, query_objs):
        self.cmd_json["body"] = {
                "queries": query_objs
            }

    def send_to(self, conn, endpoint):
        executed_result = self._send_to(conn, endpoint)

        return executed_result

class FindSavedQuery(TcCommand):
    #known queries cacheing
    _saved_queries = {}

    def set_cmd(self, saved_query_name):
        self.saved_query_name = saved_query_name
        
        self.cmd_json["body"] = {
                    "inputCriteria":
                    [{
                        "queryNames": [saved_query_name],
                        "queryDesc":[],
                        "queryType":0
                    }]
                }
            


    def send_to(self, conn, endpoint):
            
        if self.saved_query_name not in self._saved_queries:
            executed_result = self._send_to(conn, endpoint)

            saved_query = executed_result["savedQueries"][0]
            self._saved_queries[self.saved_query_name] = saved_query
        else:
            saved_query = self._saved_queries[self.saved_query_name]

        return saved_query
        
class ExecuteSavedQuery(TcCommand):

    def set_cmd(self, saved_query, entries, values, limit):
        self.cmd_json["body"] = {
                "query": saved_query,
                "entries": entries,
                "values": values,
                "limit": limit
            }

    def send_to(self, conn, endpoint):

        executed_result = self._send_to(conn, endpoint)

        try:
            tc_objs = executed_result["objects"]
        except KeyError:
            tc_objs = []

        return tc_objs
        
class GetProperties(TcCommand):

    def set_cmd(self, tc_objs, attributes):
        self.cmd_json["body"] = {
                "objects": tc_objs,
                "attributes":attributes
            }
        

    def send_to(self, conn, endpoint):
        executed_result = self._send_to(conn, endpoint)
        
        return executed_result
        
class GetHTML(TcCommand):
    htmltextcache = {}
    
    def set_cmd(self, item_strs, tc_objs):

        self.item_strs = item_strs
        self.tc_objs = tc_objs
        
        self.cmd_json["body"] = {
                    "input": [
                        {
                            "templateName": "",
                            "applicationFormat": "HTML",
                            "objectsToExport": tc_objs,
                            "targetObjectsToExport": [],
                            "exportOptions": [
                                {
                                    "option": "base_url",
                                    "optionvalue": None
                                }
                            ],
                            "recipeSourceObjects": [],
                            "recipeTargetObjects": [],
                            "attributesToExport": [],
                            "objectTemplateInputs": [],
                            "includeAttachments": True
                        }
                    ]
                }

    def send_to(self, conn, endpoint):
    
        htmls = []
        
        if len(self.item_strs) == 0:
            return htmls
        
        self.cmd_json["body"]["input"][0]["exportOptions"][0]["optionvalue"] = "http://"+conn.alias.host+":"+conn.alias.fmsport+"/fms/fmsdownload/"
        #print(self.cmd_json["body"]["input"][0]["exportOptions"][0]["optionvalue"])
        executed_result = self._send_to(conn, endpoint)
        
        #now cache the data per object
        for i in range(len(self.tc_objs)):
            html = self.cache_html_text(conn, self.item_strs[i], self.tc_objs[i], executed_result["transientFileReadTickets"][i])
            htmls.append(html)
            
        return htmls


    def cache_html_text(self, conn, item_str, tc_obj, escaped_html):
        
        unescaped_html = html.unescape(escaped_html)

        soup = BeautifulSoup(unescaped_html, 'html.parser')

        localpath = os.path.join('specimages',item_str)
        folderpath = os.path.join(os.environ["LOCALAPPDATA"],'Temp/RMI/TEAMCENTER/',localpath)
        createdPath = pathlib.Path(folderpath).mkdir(parents=True, exist_ok=True)

        #remove the unnecessary requirement title in the text
        for req_header in soup.find_all('div',class_='aw-requirement-header'):
            req_header.extract()

        #save the images to file because of simulink requirements handling
        i=1        
        for img in soup.find_all('img'):
            filename = "{}_{}".format(item_str, i)
            
            try:
                datainfo, filedata = img["src"].split(";",1)
            except ValueError:
                
                #save image stored in fms
                if "fms/fmsdownload/" in img["src"]:
                    fileext = img["src"].rsplit(".",1)[-1] 
                    
                    df = DownloadFile()
                    df.set_cmd(folderpath, filename + '.' + fileext, img["src"])
                    
                    conn.handle(df)
                else:
                    raise

            else:
                #save embedded images
                fileext = datainfo.split('/')[-1]
                filedata = filedata.split(',',1)[-1]
                
                filepath = os.path.join(folderpath, filename + '.' + fileext)
                with open(filepath,'wb') as fp:
                    fp.write(base64.b64decode(filedata))

            lfilepath = os.path.join(localpath, filename + '.' + fileext)
            img["src"] = lfilepath.replace("\\","/")
            i+=1

        self.htmltextcache[item_str] =  str(soup)
            
        return self.htmltextcache[item_str]

class DownloadFile(TcCommand):

    def set_cmd(self, folderpath, filename, url):   
        self.folderpath = folderpath
        self.filename = filename
        self.url = url
        
    def send_to(self, conn, endpoint):
    
        file_url = urllib.parse.urljoin(conn.alias.get_fms_url(), self.url)
        
        local_filename = os.path.join(self.folderpath, self.filename)

        urlretrieve(file_url, local_filename)
        
        return local_filename


class LoadObjects(TcCommand):
    def set_cmd(self, uids):
        self.cmd_json["body"] = {
            "uids": uids
        }  

    def send_to(self, conn, endpoint):
        executed_result = self._send_to(conn, endpoint)
        
        plain_objects = executed_result["plain"] #list[str]
        model_objects = executed_result["modelObjects"] #dict[uid][model_obj]
        
        
        plain_model_objs = []
        for plain_obj in plain_objects:
            model_obj = model_objects[plain_obj]
            plain_model_objs.append(model_obj)
            
        return plain_model_objs

class UndefinedCommand(Exception): pass

def get_command(command_name):
    cmd = globals().get(command_name)
    if inspect.isclass(cmd) and issubclass(cmd, TcCommand) and cmd != TcCommand:
        return cmd()
    else:
        raise UndefinedCommand('No Teamcenter Command defined called: {}'.format(command_name))
        
