
class System_Build:

    def __init__(self):
        self.T                      =   System_Lib().T
        s                           =   System_Servers()
        self.servers                =   s.servers
        self.worker                 =   s.worker
        self.params                 =   {}
        self.Reporter               =   System_Reporter(self)
        from pb_tools.pb_tools                          import pb_tools as PB
        self.pb                     =   PB().pb

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
