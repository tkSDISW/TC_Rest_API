
import unittest

USER='ed'
PWRD=USER

#ACC Test Specification in Daily Environment
TEST_SPEC = r'http://awc/62/wd142/aw/#/com.siemens.splm.clientfx.tcui.xrt.showObject?pageId=tc_xrt_Content&uid=RzmFnsGGpFYgSC&c_uid=SR%3A%3AN%3A%3AArm0RequirementSpecElement..Fnd0RequirementBOMLine..10.FwEgpcg0NA9ALC.xJuNw3cP5lUBQD..CtkFnsGGpFYgSC.KEmFnsGGpFYgSC..%2C%2CAWBCB&o_uid=SR%3A%3AN%3A%3AArm0RequirementSpecElement..Fnd0RequirementBOMLine..10.FwEgpcg0NA9ALC.xJuNw3cP5lUBQD..CtkFnsGGpFYgSC.KEmFnsGGpFYgSC..%2C%2CAWBCB&pci_uid=SR%3A%3AN%3A%3AAwb0ProductContextInfo..P%3ARzmFnsGGpFYgSC%2CGR%3Atrue%2CPA%3A1%2CSS%3A1%2CEXP%3A0%2C%2C%2CAWBCB&spageId=tc_xrt_Documentation&t_uid=SR%3A%3AN%3A%3AArm0RequirementSpecElement..Fnd0RequirementBOMLine..10.FwEgpcg0NA9ALC.xJuNw3cP5lUBQD..CtkFnsGGpFYgSC.KEmFnsGGpFYgSC..%2C%2CAWBCB'

from teamcenter.alias import TcAlias
from teamcenter.credentials import TcCredentials
from teamcenter.connection import TcConnection,config_alias
from teamcenter.commands import get_command
import teamcenter.tc_slreq

class IntCredentials(TcCredentials):
    
    def __init__(self, alias):
        credentials = {'Username':USER,'Password':PWRD}
        super().__init__(alias,credentials)
        self.__credentials = credentials

    def set_key(self, alias):
        pass #override

    @property
    def username(self):
        return self.__credentials['Username']
        
    @property
    def password(self):
        return self.__credentials['Password']
        
class TestIntegration(unittest.TestCase):
    
    def setUp(self):
        '''Establish connection for testing'''
        self.alias = TcAlias(
            name='TEST_ALIAS',
            host='awc',
            port='80',
            awpath='/62/wd141/aw'
            )
        config_alias(self.alias.name)
        self.conn = TcConnection(alias=self.alias, 
                                credentials=IntCredentials(self.alias))
        self.conn.login()

    def tearDown(self):
        '''Disconnect on completion of testing'''
        self.conn.logout()
        self.conn.close()
        del(self.conn)
        del(self.alias)

    def test_get_specification(self):
        
        #spec_details [uid, item_id, revision, name, description]
        spec_details = teamcenter.tc_slreq.get_spec(TEST_SPEC)
        self.assertEqual(spec_details,
            ['RzmFnsGGpFYgSC', 'VnV_030116', 'A', 'ACC Specification', 'ACC Specification'])

        contents = teamcenter.tc_slreq.get_contents(spec_details[1] + "_" + spec_details[2])
        self.assertEqual(contents,
            (['ACC Requirements', 'Basic Control Strategy', 'Adjust Subject Vehicle Speed', 
            'Brake within Set Distance', 'Minimum distance for emergency stop', 
            'Maintain Following Distance', 'Maintain Set Speed'], 
            [0, 1, 1, 1, 1, 1, 1], 
            ['REQ-885274_A', 'REQ-885262_A', 'REQ-885246_A', 'REQ-885257_A', 'REQ-885248_A', 
            'REQ-885263_A', 'REQ-885283_A']))
        
if __name__ == '__main__':
    unittest.main()
