"""
    Functions called by Simulink Requirements to integrate with Teamcenter Requirements
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
__filename__ = 'tc_slreq.py'

import requests
import os
import sys
import urllib.parse
from bs4 import BeautifulSoup

from teamcenter.connection import get_connection, config_alias, reset_connection, set_credential_dir
from teamcenter.commands import get_command

def setup_python(pythonhome):
    set_credential_dir(pythonhome)

def get_spec(tc_url):
    """Gets the specification from Teamcenter
    
    Given a Teamcenter URL, get the specification information from Teamcenter
    
    Parameters
    ----------
    tc_url : str
        Active Workspace showObject url with uid in query field
    
    Returns
    -------
    list
        a list containing information about spec: uid, item id, item rev, name, description
    """
    #get our connection to Teamcenter
    conn = get_connection()
    
    #Get the UID from the showObject?uid=... URL
    parsesplit = urllib.parse.urlsplit(tc_url)
    parsesplit_f = urllib.parse.urlsplit(parsesplit.fragment)
    queryl = urllib.parse.parse_qsl(parsesplit_f.query)
    query = dict(queryl)
    
    spec_uid = query["uid"]
    
    #Get the RequirementSpec model object
    lo = get_command('LoadObjects')
    lo.set_cmd([spec_uid])
    tc_spec = conn.handle(lo)[0]
        
    specId = tc_spec["props"]["object_string"]["uiValues"][0].split(';')[0]

    specRev = specId.split('/')[-1]
    specId = specId.split('/')[0]

    specName = tc_spec["props"]["object_string"]["uiValues"][0].split(';')[-1].split('-',1)[-1]
    specDesc = tc_spec["props"]["object_desc"]["uiValues"][0]

    return [spec_uid, specId, specRev, specName, specDesc]

def get_summary(doc, location):
    """Gets the summary of the item from Teamcenter
    
    Gets the summary, aka name, of the document, requirement, or paragraph from Teamcenter
    
    Parameters
    ----------
    doc : str
        document requirement is within in form of ID_REV, example:  SPEC-00001_A

    location : str
        requirement to get the text for in form of ID_REV, example:  REQ-00001_A
    
    Returns
    -------
    str
        the name of the document, requirement or paragraph
    """

    #get our connection to Teamcenter
    conn = get_connection()

    if not location:
        location = doc
        
    #split spec_identifier, ex: VnV_030116_A;ACC Specification
    part = location.split(';')[0]
    itemRev = part.rsplit('_',1)[-1]
    itemId = part.rsplit('_',1)[0]
    
    #Get the item rev object
    gifi = get_command('GetItemFromId')
    gifi.set_cmd(itemId, itemRev)
    item_rev = conn.handle(gifi)

    #Get the name of the item rev object (which is the summary)
    name = item_rev["props"]["object_string"]["uiValues"][0]
    
    return name


def get_viewable_html(doc, location):
    """Gets html formatted text of a requirement/paragraph
    
    Gets the html formatted text of a requirement/paragraph from
    the html cache.
    
    Parameters
    ----------
    doc : str
        document requirement is within in form of ID_REV, example:  SPEC-00001_A

    location : str
        requirement to get the text for in form of ID_REV, example:  REQ-00001_A
    
    Returns
    -------
    str
        the html formatted text of the requirement or paragraph
    """
    gh = get_command('GetHTML')
    
    if not location:
        location = doc
        
    #split spec_identifier, ex: VnV_030116_A;ACC Specification
    part = location.split(';')[0]
    itemRev = part.rsplit('_',1)[-1]
    itemId = part.rsplit('_',1)[0]
    
    item_str = itemId+"_"+itemRev
    
    html = gh.htmltextcache.get(item_str, '<b>Failed to Get HTML!</b>')
    
    return html

def get_viewable_text(doc, location):
    """Gets text of a requirement/paragraph
    
    Gets the text without HTML formatting of a requirement/paragraph from
    the html cache.
    
    Parameters
    ----------
    doc : str
        document requirement is within in form of ID_REV, example:  SPEC-00001_A

    location : str
        requirement to get the text for in form of ID_REV, example:  REQ-00001_A
    
    Returns
    -------
    str
        the text of the requirement or paragraph
    """
    vhtml = get_viewable_html(doc, location)

    #use beautifulsoup on html to change to text only
    soup = BeautifulSoup(vhtml, 'html.parser')
    
    return str(soup.get_text())

def get_url(document, location):
    """Get Teamcenter URL
    
    Generates a Teamcenter URL for navigating to the document or content within
    Active Workspace
    
    Parameters
    ----------
    conn : TcConnection
        connection to Teamcenter
        
    tc_spec_contents : list
        list of Teamcenter requirement/paragraph objects
    
    Returns
    -------
    str
        a formatted url for matlab to use in show document command    
    """

    try:
        #get our connection to Teamcenter
        conn = get_connection()
        
        #split spec_identifier, ex: VnV_030116_A;ACC Specification
        part = document.split(';')[0]
        specRev = part.rsplit('_',1)[-1]
        specId = part.rsplit('_',1)[0]
        
        
        #Get the RequirementSpec model object by query
        gifi = get_command('GetItemFromId')
        gifi.set_cmd(specId, specRev)
        tc_spec = conn.handle(gifi)
        
        return '{}/#/com.siemens.splm.clientfx.tcui.xrt.showObject?uid={}'.format(conn.alias.get_base_url(), tc_spec["uid"])

    except Exception as e:
        import traceback
        print(e)
        traceback.print_tb(sys.exc_info()[2])
        raise(e)

def cache_all_html(conn, tc_spec_contents):
    """Caches html text for all contents of a requirements specificiation
    
    For all the paragraphs/requirements in a specification, gets the html
    text and downloads all images relevant. Caching them locally for later
    viewing.
    
    Parameters
    ----------
    conn : TcConnection
        connection to Teamcenter
        
    tc_spec_contents : list
        list of Teamcenter requirement/paragraph objects
    
    Returns
    -------
    list
        an ordered list of all html content aligned with tc_spec_contents
    """
    item_strs = []
    
    for tc_obj in tc_spec_contents:
        val = tc_obj["props"]["object_string"]["uiValues"][0]
        part = val.split(';',1)[0]
        itemRev = part.rsplit('/',1)[-1]
        itemId = part.rsplit('/',1)[0]
        item_strs.append(itemId + "_" + itemRev)

    gh = get_command('GetHTML')
    gh.set_cmd(item_strs, tc_spec_contents)

    result = conn.handle(gh)
    
    return result


def matlab_content(tc_parent, tc_spec_contents, labels, depths, locations, depth=0):
    """Structures requirement spec contents for matlab
    
    Recursively formats labels, depths, and locations information which is a result
    for the get_contents function
    
    Parameters
    ----------
    tc_parent : dict
        parent object potentially having structured contents
        
    tc_spec_contents : list
        list of Teamcenter requirement/paragraph objects in requirement spec
        
    labels : list
        names of content in requirements
    
    depths : list
        positions of content in requirement spec
    
    locations : list
        identifiers of contents in requirement spec in form of ID_REV, 
        example:  SPEC-00001_A
        
    depth : int, optional
        content level in requirement spec (default is 0)
        
    Returns
    -------
    None
        labels, depths, and locations are set directly in given parameter list references
    """
    children = []
    for structure in tc_spec_contents["output"]:
        if not structure["parent"]: continue
        
        if structure["parent"]["itemRevOfBOMLine"]["uid"] == tc_parent["uid"]:
            children = structure["children"]
            break

    for child in children:
        child_uid = child["itemRevOfBOMLine"]["uid"]
        tc_req = tc_spec_contents["ServiceData"]["modelObjects"][child_uid]

        reqName = tc_req["props"]["object_string"]["uiValues"][0].split(';')[-1].split('-',1)[-1]

        part = tc_req["props"]["object_string"]["uiValues"][0].split(';')[0]

        reqRev = part.split('/')[-1]
        reqId = part.split('/')[0]


        location = tc_req["uid"]
        labels.append(reqName)
        locations.append(reqId + "_" + reqRev)
        depths.append(depth)

        matlab_content(tc_req, tc_spec_contents, labels, depths, locations, depth+1)


def get_contents(spec_identifier):
    """Obtain all content of a requirement specification from Teamcenter
    
    Queries the full requirement specification in Teamcenter finding all
    paragraphs/requirements within, their names, ids, revision, and text.
    
    Caches text for later retrieval.
    
    Parameters
    ----------
    spec_identifier : str
        requirement specification to get contents from in form of ID_REV, 
        example:  SPEC-00001_A
    
    Returns
    -------
    tuple
        a tuple containing labels of requirements, position in requirement spec,
        and their identifier
    """
    
    #get our connection to Teamcenter
    conn = get_connection()
    
    #split spec_identifier, ex: VnV_030116_A;ACC Specification
    part = spec_identifier.split(';')[0]
    specRev = part.rsplit('_',1)[-1]
    specId = part.rsplit('_',1)[0]

    try:
        gifi = get_command('GetItemFromId')
        gifi.set_cmd(specId, specRev)
        tc_spec = conn.handle(gifi)
        
        #Get the Revision Rule used for the structure contents
        grr = get_command('GetRevisionRule')
        grr.set_cmd('Latest Working')
        rev_rule = conn.handle(grr)
        
        #Get the structure contents of the RequirementSpec
        print('...retrieving specification structure',end='')
        
        cbw = get_command('CreateBOMWindow')
        cbw.set_cmd(tc_spec, rev_rule)
        
        bom_window_line = conn.handle(cbw)
        
        expandall = get_command('ExpandPSAllLevels')
        expandall.set_cmd(bom_window_line)
        tc_spec_contents = conn.handle(expandall)
        
        print('. completed.')
        
        tc_objs = []
        for o in  tc_spec_contents["ServiceData"]["modelObjects"].values():
            if "Requirement Revision" in o["type"]:
                tc_objs.append(o)
        
        #Cache all the HTML
        print('...retrieving text for contents',end='')

        cache_all_html(conn,tc_objs)
            
        print('. completed.')
        
        #Format the contents for matlab import
        labels, depths, locations = [],[],[]
        matlab_content(tc_spec, tc_spec_contents, 
            labels, depths, locations)
            
    except Exception as e:
        import traceback
        print(e)
        traceback.print_tb(sys.exc_info()[2])
        raise(e)
    
    return labels, depths, locations


def insert_backlinks(requirement, matlabmodel, back_link_label, navcmd):
    """Creates backlinks in Teamcenter
    
    Creates surrogate model, back link object attached to surrogate model,
    and trace link from back link object with requirement in Teamcenter.
    
    Parameters
    ----------
    requirement : str
        requirement to create trace link with in form of ID_REV, example:  REQ-00001_A
        
    matlabmodel : str
        full file path to matlab model which will have surrogate created for
        
    back_link_label : str
        name of back link object
        
    navcmd : str
        matlab/simulink navigation command stored in description of back link object
    """

    try:

        conn = get_connection()

        matlabmodel = os.path.split(matlabmodel)[-1]

        #Get our saved query...
        fsq = get_command('FindSavedQuery')
        fsq.set_cmd('Item Revision...')
        
        saved_query = conn.handle(fsq)
    
        #confirm model exists in TC, if not create
        esq = get_command('ExecuteSavedQuery')
        esq.set_cmd(saved_query,
                    ["Type","Name"],
                    ["Item Revision", matlabmodel],
                    1)
                    
        matlab_models = conn.handle(esq)
        
        if matlab_models:
            mm_rev = matlab_models[0]
        else:
            ci = get_command('CreateItem')
            ci.set_cmd(matlabmodel, "Surrogate Matlab Model")
            
            mm_rev = conn.handle(ci)
        
        #get all HTML dataset "links" for model in TC
        grd = get_command('GetRelatedDatasets')
        grd.set_cmd(mm_rev)
        link_objs = conn.handle(grd)
        
        #determine creates
        existing_link_labels = {}
        for lo in link_objs:
            existing_link_labels[lo["props"]["object_string"]["uiValues"][0]] = lo
        
        create = False
        if back_link_label not in existing_link_labels:
            create = True
            
        #create new dataset and relate if needed
        if create:
            crd = get_command('CreateAndRelateDataset')
            crd.set_cmd(mm_rev, back_link_label, navcmd)
            
            existing_link_labels[back_link_label] = conn.handle(crd)

        lo = existing_link_labels[back_link_label]

        #get requirement object
        reqRev = requirement.rsplit('_',1)[-1]
        reqId = requirement.rsplit('_',1)[0]
 
        gifi = get_command('GetItemFromId')
        gifi.set_cmd(reqId, reqRev)
 
        ro = conn.handle(gifi)
        
        #trace dataset with requirement for relationship browser and spec navigation
        ct = get_command('CreateTraceLinks')
        ct.set_cmd(lo, ro)
        
        conn.handle(ct)

    except Exception as e:
        import traceback
        print(e)
        traceback.print_tb(sys.exc_info()[2])
        raise(e)

def set_alias(alias_name):
    """Set the TcConnection alias to be used
    
    Configures the TcConnection to instantiate with the given alias in tcaliases.ini
    
    Parameters
    ----------
    alias_name : str
        alias name which is section header in tcaliases.ini, default alias is DEFAULT
    
    Returns
    ----------
    None
        returns nothing
    """
    config_alias(alias_name)

#def backlink_check(mw_source_artifact, mw_item_id, req_spec, req_id):   
    # """Check status of backlink between contextual items
    
    # Checks if a backlink exists between items, if not will return a
    # tuple of (False, '') , if it does exist will return a tuple of
    # (True, (tracelink_obj, surrogateitem_obj)) that can be used for
    # cleanup later if necessary.
    
    # Parameters
    # ----------
    # mw_source_artifact : str
        # matlab/simulink source artifact file name

    # mw_item_id : str
        # id of item within matlab/simulink source artifact
        
    # req_spec : str
        # requirement specification in Teamcenter
        
    # req_id : str
        # id of requirement within requirement specification in Teamcenter
    
    # Returns
    # ----------
    # tuple
        # a tuple of two items consisting of True/False representing link existence and link_data if exists
    # """
    
    # #get info from link cache, create link cache if needed
    # link_cache = link_cache_get(mw_source_artifact, req_spec)

    # link_data = link_cache.get((mw_item_id, req_id), None)
    # if link_data is None:
        # tf = False
    # else:
        # tf = True
        
    # return tf, link_data
    
    
def backlinks_cleanup(mw_source_artifact, req_spec, links_data):
    reset_connection()
    # """Insert and cleanup backlinks in bulk
    
    # Insert all non-existing backlinks. Remove backlinks and proxies if no backlinks remain
    
    
    # Parameters
    # ----------
    # mw_source_artifact : str
        # matlab/simulink source artifact file name

    # req_spec : str
        # requirement specification in Teamcenter
        
    # links_data : list
        # list of link data found during backlinks_check that needs to be cleaned up
    
    # Returns
    # ----------
    # tuple
        # a tuple of two items consisting of backlinks removed count and checked count
    # """
    # try:

        # conn = get_connection()
    
        # #insert back links if any to insert
        # insert_backlinks = get_new_backlinks(mw_source_artifact, req_spec)
        # bl_ins = get_command('InsertBackLinks')
        # bl_ins.set_cmd(insert_backlinks)
        # ins_cnt = conn.handle(bl_ins)
        
        # assert ins_cnt == len(insert_backlinks), 'Expected same number of links inserted as requested'

        # #remove backlinks
        # bl_del = get_command('RemoveBackLinks')
        # bl_del.set_cmd(links_data)
        # del_cnt = conn.handle(bl_del)
        
        # #remove surrogate model items without backlinks
        # smi_del = get_command('DeleteSurrogateItems')
        # smi_del.set_cmd(mw_source_artifact)
        # chk_cnt = conn.handle(smi_del)
        
    # except:
        # import traceback
        # print(e)
        # traceback.print_tb(sys.exc_info()[2])
        # raise(e)
    
    # finally:
        # #The link cache between the source and req_spec is no longer needed
        # link_cache_del(mw_source_artifact, req_spec)

    # return del_cnt, chk_cnt
    

