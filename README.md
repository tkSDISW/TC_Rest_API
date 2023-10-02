# resttc
Repository containing Python package for Teamcenter REST communication 


# Example of Basic Usage
```
from teamcenter.connection import get_connection, config_alias, reset_connection
from teamcenter.commands import get_command

#Establish connection
conn = get_connection()

#Get the Requirement Spec
print('Retrieving specification')
gifi = get_command('GetItemFromId')
gifi.set_cmd('010101', 'A')
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
```

