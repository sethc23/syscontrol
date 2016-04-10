
import os
from sys                                        import path                     as py_path
py_path.append(                                 os.environ['BD'])
py_path.append(                                 os.environ['HOME_ENV'] + '/.scripts')

from system_settings                            import *
from sysparse                                   import *

# Import all from all
from importlib import import_module
import inspect
_from_file = inspect.stack()[-1][1]
_from_file = _from_file[_from_file.rfind('/')+1:]
exclude_py = ['__init__.py',_from_file,'sys_control.py',]
dir_list = sorted([it for it in os.listdir(os.getcwd()) 
                    if it[-3:]=='.py' and not exclude_py.count(it)])

for _file in dir_list:
    _module = _file.rsplit('.')[0]
    imported_mod = import_module(_module)
    exec '%s = getattr(imported_mod,_module)' % _module


try:
    from ipdb import set_trace as i_trace   # i_trace()
    # ALSO:  from IPython import embed_kernel as embed; embed()
except:
    pass

