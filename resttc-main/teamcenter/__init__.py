
from .alias import set_alias_dir
from .credentials import set_credential_dir

def init_python(python_home):
    set_alias_dir(python_home)
    set_credential_dir(python_home)