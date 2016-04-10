#!/home/ub2/.virtualenvs/devenv/bin/python
# PYTHON_ARGCOMPLETE_OK

import inspect
x = BASE_FILE_PATH      =   inspect.stack()[-1][1]
BASE_FILE               =   x[x.rfind('/')+1:]
THIS_FILE               =   __file__[__file__.rfind('/')+1:].rstrip('c')

if BASE_FILE==THIS_FILE:
    from __init__ import *
else:
    from sysparse import basic_components
    _components = basic_components()
    for name,arg in _components:
        exec '%s = arg' % name
    from argh.decorators import *
    import os
    
class sys_build:

    def __init__(self,_parent=None):
        if hasattr(_parent,'T'):    self.T  =   _parent.T
        elif hasattr(self,'T'):                 pass
        else:                       self.T  =   sys_lib(['pgsql']).T
        s                                   =   sys_servers(self)
        self.servers                        =   s.servers
        self.worker                         =   s.worker
        self.params                         =   {}
        self.Reporter                       =   sys_reporter(self)
        from pb_tools.pb_tools                  import pb_tools as PB
        self.pb                             =   PB().pb

    def configure_scripts(self,*vars):
        if len(vars)==0: cmd_host   =   self.worker
        else:            cmd_host   =   vars[0]

        cmds                        =   ['cd $HOME/.scripts;',
                                         'if [ -n "$(cat ENV/bin/activate | grep \'source ~/.bashrc\')" ]; then',
                                         'echo -e "\nsource ~/.bashrc\n" >> ENV/bin/activate;'
                                         'fi;']
        (_out,_err)                 =   self.T.exec_cmds({'cmds':cmds,'cmd_host':cmd_host,'cmd_worker':self.worker})
        assert _err==None
        assert _out==''
