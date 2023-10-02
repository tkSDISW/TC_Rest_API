"""
    Mapping of Teamcenter commands with handling Teamcenter service API
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
__filename__ = 'handlers.py'


import teamcenter.services as svc
import teamcenter.commands as cmd

HANDLERS = {
    cmd.Login : svc.Session.login,
    cmd.Logout : svc.Session.logout,
    cmd.FindSavedQuery : svc.SavedQuery.find_saved_queries,
    cmd.DescribeSavedQueries : svc.SavedQuery.describe_saved_queries,
    cmd.ExecuteSavedQuery : svc.SavedQuery.execute_saved_query,
    cmd.LoadObjects : svc.DataManagement.load_objects,
    cmd.GetProperties : svc.DataManagement.get_properties,
    cmd.GetItemFromId : svc.DataManagement.get_item_from_id,
    cmd.ExpandGRMRelationsForPrimary : svc.DataManagement.expand_grm_relations_for_primary,
    cmd.GetRelatedDatasets : svc.DataManagement.expand_grm_relations_for_primary,
    cmd.CreateAndRelateDataset : svc.DataManagement.create_datasets2,
    cmd.CreateBOMWindow : svc.StructureManagement.create_bom_windows,
    cmd.ExpandPSAllLevels : svc.StructureManagement.expand_ps_all_levels,
    cmd.GetRevisionRule : svc.StructureManagement.get_revision_rules,
    cmd.CreateTraceLinks : svc.RequirementsManagement.create_tracelinks,
    cmd.GetHTML : svc.RequirementsManagement.export_to_application3,
    cmd.DownloadFile : svc.FMSClient.download_file,
    cmd.CreateItem : svc.DataManagement.create_attach_and_submit_objects,
}

