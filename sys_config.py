class System_Config:
    """Functions for getting and setting system configurations"""

    def __init__(self):
        """

            Entry Format: [ {settings directory},{settings file},{cmd to reset program settings} ]

        """
        self.T                      =   System_Lib().T
        locals().update(                self.T.__dict__)
        D                           =   {'aprinto'  :   ['%(SERV_HOME)s/aprinto',
                                                         'aprinto_settings.py'],
                                         'gitserv'  :   ['%(GIT_SERV_HOME)s/celery/git_serv',
                                                         'git_serv_settings.py'],
                                         'nginx'    :   ['%(SERV_HOME)s/nginx/setup/nginx/sites-available',
                                                         'run_aprinto.conf',
                                                         ' '.join(['echo "%(PASS)s" | sudo -S -k --prompt=\'\'',
                                                                   'sh -c "%(SERV_HOME)s/nginx/push_ng_config.bash;',
                                                                   'nginx -s reload -p %(SERV_HOME)s/run -c',
                                                                   '/usr/local/openresty/nginx/conf/nginx.conf -g',
                                                                   '\\"user %(ROOT)s %(ROOT_GRP)s; pid',
                                                                   '%(SERV_HOME)s/run/pids/sv_nginx.pid; daemon on;\\"";'])
                                                         ],
                                         'hosts'    :   ['/etc','hosts']
                                        }
        os_environ.update(              {'PASS'     :   PASS})
        self.auth                   =   'echo "%(PASS)s" | sudo -S -k --prompt=\'\' ' % os_environ + 'sh -c "%(cmd)s";'
        self.D                      =   D

    def get_cfg(self):
        base                        =   self.base_dir if self.worker=='ub2' else '/Volumes/ub2'+self.base_dir
        cfg_fpath                   =   base + '/BD_Scripts/files_folders/rsync/backup_system_config.xlsx'
        cfg                         =   pd.read_excel(cfg_fpath, na_values ='', keep_default_na=False, convert_float=False)
        cols                        =   cfg.columns.tolist()
        cols_lower                  =   [str(it).lower() for it in cols]
        cfg.columns                 =   [cols_lower]
        for it in cols_lower:
            cfg[it]                 =   cfg[it].map(lambda s: '' if str(s).lower()=='nan' else s)
        tbl                         =   'config_rsync'
        conn.set_isolation_level(       0)
        cur.execute(                    'drop table if exists %s'%tbl)
        cfg.to_sql(                     tbl,sys_eng,index=False)
        return cfg

    def adjust_settings(self,*vars):
        """
                                        '/home/ub3/SERVER4/aprinto'
        Aprinto:                        'aprinto_settings.py'
            BEHAVE_TXT_ON_ERROR
            CELERY_TXT_NOTICE
            FWD_ORDER

                                        '/home/jail/home/serv/system_config/SERVER5/celery/git_serv'
        GitServ                         'git_serv_settings.py'
            GITSERV_TXT_NOTICE
            GITSERV_GROWL_NOTICE
            BEHAVE_VERIFICATION


        BINARY USAGE:

            ... System_Control.py settings aprinto behave_txt_false

            ... System_Control.py settings nginx access_log_disable




        """

        if vars[0]=='restore':
            assert len(vars)==2
            return self.restore_orig_settings(vars[1])

        prog                        =   vars[0]
        D                           =   self.D
        binary_toggles              =   [ ['true','false'],
                                          ['enable','disable'] ]

        settings_dir                =   D[ prog ][0] % os_environ
        settings_file               =   D[ prog ][1] % os_environ
        t                           =   vars[1]
        toggle                      =   t[t.rfind('_')+1:].lower()
        param                       =   t[:-len(toggle)-1].upper()

        toggle_from,toggle_to       =   '',''
        for it in binary_toggles:
            stop                    =   False
            if it.count(toggle)==1:
                toggle_to           =   it[ it.index(toggle) ]
                toggle_from         =   it[0] if it.index(toggle)==1 else it[1]
                stop                =   True
                break

        # TO CHANGE NON-BINARY SETTINGS ... if (toggle_from,toggle_to)==('',''): ...

        delim                       =   None if ['nginx','hosts'].count(prog)==1 else '='
        cfg_file                    =   settings_dir + '/' + settings_file

        cfgs                        =   self.get_config_params(cfg_file,param,
                                                               delim=delim,
                                                               toggle_from=toggle_from)

        cfgs                        =   self.change_config_params(prog,cfg_file,cfgs,toggle_from,toggle_to)

        updated                     =   self.update_program_with_settings(prog)
        assert updated==True

        return cfgs

    def restore_settings(self,cfgs):

        # not sure this double eval is necessary BUT IT IS !!
        cfgs                        =   cfgs if type(cfgs)==list else eval(cfgs)
        cfgs                        =   cfgs if type(cfgs)==list else eval(cfgs)

        progs                       =   []
        for d in cfgs:

            d.update(                   {'from'                 :   d['to'],
                                         'to'                   :   d['from'] } )

            cmd                     =   'sed -i \'%(line)ss/%(from)s/%(to)s/g\' %(fpath)s' % d
            cmd                     =   cmd if os_access(d['fpath'],os_X_OK) else self.auth % {'cmd':cmd}
            p                       =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
            (_out,_err)             =   p.communicate()
            assert _err==None
            if progs.count(d['prog'])==0:
                progs.append(           d['prog'])

        for prog in progs:
            updated                     =   self.update_program_with_settings(prog)
            assert updated==True

    def get_config_params(self,cfg_file,cfg_params,delim=None,toggle_from=''):
        mod                         =   '#' if toggle_from=='disable' else ''
        param_value                 =   toggle_from if ['enable','disable'].count(toggle_from)==0 else ''
        D                           =   {'fpath'                :   cfg_file,
                                         'mod'                  :   mod,
                                         'param_val'            :   param_value}
        cfg_params                  =   cfg_params if type(cfg_params)==list else [cfg_params]
        cfgs                        =   []

        for it in cfg_params:
            D.update(                   {'param'                :   it} )
            cmd                     =   'cat %(fpath)s | grep -i -E -n \'^[[:space:]]*%(mod)s%(param)s.*%(param_val)s\';' % D

            p                       =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
            (_out,_err)             =   p.communicate()
            assert _err==None

            for it in _out.split('\n'):
                line                =   it[:it.find(':')]
                it                  =   it[it.find(':')+1:]
                t                   =   it.split() if not delim else it.split(delim)
                m                   =   ' ' if not delim else delim

                if len(t)>=2:
                    cfgs.append(        {'line'                 :   line,
                                         'param'                :   t[0].strip(),
                                         'value'                :   '%s'%m.join(t[1:]).lstrip(' %s' % m) })

        return cfgs

    def change_config_params(self,prog,cfg_file,cfg_params,toggle_from,toggle_to):
        for d in cfg_params:

            t_from,t_to             =   d['value'],toggle_to

            if ['enable','disable'].count(toggle_from)>0:
                t_from,t_to         =   d['param'],d['param']
                t_to                =   t_to.lstrip('#') if toggle_to=='enable' else t_to
                t_to                =   '#' + t_from if toggle_to=='disable' else t_to

            t_to                    =   t_to.lower() if t_from.islower() else t_to
            t_to                    =   t_to.title() if t_from.istitle() else t_to
            t_to                    =   t_to.upper() if t_from.isupper() else t_to

            d.update(                   {'prog'                 :   prog,
                                         'fpath'                :   cfg_file,
                                         'from'                 :   t_from,
                                         'to'                   :   t_to } )


            cmd                     =   'sed -i \'%(line)ss/%(from)s/%(to)s/g\' %(fpath)s' % d
            cmd                     =   cmd if os_access(cfg_file,os_X_OK) else self.auth % {'cmd':cmd}
            p                       =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
            (_out,_err)             =   p.communicate()
            assert _err==None

        return cfg_params

    def update_program_with_settings(self,prog):
        if len(self.D[prog])==3:
            cmd                     =   self.D[prog][2] % os_environ
            p                       =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
            (_out,_err)             =   p.communicate()
            assert _err==None
        return True

