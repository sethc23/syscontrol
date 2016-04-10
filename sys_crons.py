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

class sys_crons:
    """Cron functions to operate"""

    def __init__(self,_parent=None):

        if hasattr(_parent,'T'):    self.T  =   _parent.T
        elif hasattr(self,'T'):                 pass
        else:                       self.T  =   sys_lib(['pgsql']).T

        SERVERS                             =   sys_servers(self)
        S                                   =   SERVERS.servers
        S                                   =   S[(S.s_idx.isnull()==False)&(S.home_env.isnull()==False)].copy()
        S['SERV_dir']                       =   S.ix[:,['home_env','s_idx']].apply(lambda s: s[0]+'/SERVER'+str(int(s[1])),axis=1)
        S['crontab_dir']                    =   S.SERV_dir.map(lambda STR: STR + '/crons')

        self.T.cron_list                    =   self.T.pd.read_sql('SELECT * FROM crons WHERE is_active IS true',self.T.eng)
        self.T.cron_json                    =   self.T.To_Class()
        self.T.cron_cnt                     =   len(self.T.cron_list)
        self.T.mailto                       =   'seth.t.chase@gmail.com'
        self.T.SCRIPT_RUNNER                =   self.T.os.environ['USER']
        
        # self.T.CRON_SCRIPT = '~/cron_script'
        # self.T.TMP_CRONTAB = '/tmp/crontab'

        from crontab                        import CronTab
        from crontab                        import CronItem as type_cron

        all_imports                         =   locals().keys()
        for k in all_imports:
            self.T.update(                      {k              :   eval(k) })
        locals().update(                        self.T.__dict__)
        globals().update(                       self.T.__dict__)

    def osx_env(self):
        shell           =   '/bin/zsh'
        return              "SHELL="+shell+"\nPATH=%(s_path)s\nMAILTO=%(mailto)s"

    def ubuntu_env(self):
        shell           =   '/bin/zsh'
        return              "SHELL="+shell+"\nPATH=%(s_path)s\nMAILTO=%(mailto)s"

    # OLD
        # def update_cron_json(self,current_server,target_server,cron_info,cron_json):
        #     cron_id                     =   str(self.T.get_guid())
            
        #     cron                        =   self.T.CronTab()
        #     cron.lines                  =   []
        #     if target_server.tag==current_server.tag:
        #         crontab_copy            =   'cp -R /tmp/crontab %s/crons/' % target_server.SERV_dir
        #     else:
        #         crontab_copy            =   "ssh %s 'scp %s:/tmp/crontab $SERV_HOME/crons/'" % (target_server,current_server)


        #     # Create Crontab File
        #     cmd                         =   cron_info.cmd % target_server
        #     # (move cmd inside bash script)
        #     cmd                         =   cmd.replace("'","\'")
        #     cmd                         =   "./cron_script '" + cmd + "'"
            
        #     cmt                         =   cron_info.tag
        #     j                           =   cron.new(command=cmd,comment=cmt)

        #     if type(cron_info.special) ==   self.T.NoneType:
        #         t                       =   cron_info
        #         run_time                =   (t.minute,t.hour,t.day_of_month,t.month,t.day_of_week)
        #         j.setall(                   '%s %s %s %s %s'%run_time)
        #     else:
        #         s                       =   cron_info.special
        #         if   s == '@reboot':        j.every_reboot()
        #         elif s == '@hourly':        j.every().hours()
        #         elif s == '@daily':         j.every().dom()
        #         elif s == '@weekly':        j.setall('0 0 * * 0')
        #         elif s == '@monthly':       j.every().month()
        #         elif s == '@yearly':        j.every().year()
        #         elif s == '@annually':      j.every().year()
        #         elif s == '@midnight':      j.setall('0 0 * * *')
            
        #     # Add Environment Vars
        #     if target_server.tag.find('ub')==0:  
        #         e_v                             =   self.ubuntu_env(current_server.tag,
        #                                                             target_server.home_env)
        #     else:                   
        #         e_v                             =   self.osx_env()
            
        #     crontab_load                        =   "ssh %s 'crontab %s/crons/crontab'"%(current_server.tag,
        #                                                                                  target_server.SERV_dir)
            
        #     if not cron_json.has_key(target_server.tag):
        #         cron_json.update({                  target_server.tag           :   {}      })
                
        #     cron_json[target_server.tag].update(    {cron_id                    :   {'cron'             :   str(j.cron),
        #                                                                              'cron_env'         :   e_v,
        #                                                                              'crontab_copy'     :   crontab_copy,
        #                                                                              'crontab_load'     :   crontab_load}
        #                                             })
            
        #     return cron_json
    
    def update_cron_json(self,cmd_server,target_server,cron_data):
        d               =   cron_data
        cron_id         =   str(self.T.get_guid())        
        cron            =   self.T.CronTab()
        cron.lines      =   []

        if cmd_server.s_user==target_server.s_user:
            crontab_copy=   'cp -R /tmp/crontab %(crontab_dir)s/' % target_server
        else:
            crontab_copy=   ' '.join(['timeout --kill-after=12 10s',
                                     'gzip -c /tmp/crontab | ssh %(s_user)s "' % target_server,
                                     # 'source ~/.zshrc; ',
                                     'cd %(crontab_dir)s; ' % target_server,
                                     'rm -fr crontab; ',
                                     ':> crontab; ',
                                     'gzip -d > crontab; ',
                                     'crontab crontab; "'])

        # Create Crontab File -- SERVER 1
        cmd             =   d.cmd % target_server
        # (move cmd inside bash script)
        cmd             =   cmd.replace("'","\'")
        cmd             =   "~/cron_script '" + cmd + "'"
        
        cmt             =   d.tag
        j               =   cron.new(command=cmd,comment=cmt)

        if type(d.special) == self.T.NoneType:
            run_time    =   (d.minute,d.hour,d.day_of_month,d.month,d.day_of_week)
            j.setall('%s %s %s %s %s' % run_time)
        else:
            s = d.special
            if   s == '@reboot':     j.every_reboot()
            elif s == '@hourly':     j.every().hours()
            elif s == '@daily':      j.every().dom()
            elif s == '@weekly':     j.setall('0 0 * * 0')
            elif s == '@monthly':    j.every().month()
            elif s == '@yearly':     j.every().year()
            elif s == '@annually':   j.every().year()
            elif s == '@midnight':   j.setall('0 0 * * *')
        
        # Add Environment Vars
        e_v             =   self.ubuntu_env() if target_server.s_user.startswith('ub')==0 else self.osx_env()
        e_v             =   e_v % target_server 
        
         #crontab_load = "ssh %s 'crontab %s/crons/crontab'"%(username,THIS_SERVER.SERV_dir)
        
        if not hasattr(self.T.cron_json,target_server.s_user):
            self.T.cron_json.update({target_server.s_user:{}})
            
        self.T.cron_json[target_server.s_user].update({cron_id:
                                        {'cron'          : str(j.cron),
                                         'cron_env'      : e_v,
                                         'crontab_copy'  : crontab_copy,
                                        }})
        
        return

    def load_crons_from_json(self,serv_cron_json):
        for grp_k,grp_v in serv_cron_json.iteritems():
            cron                            =   self.T.CronTab()
            cron.lines,cmt_dict             =   [],{}
            max_cmd_len                     =   0

            for k,v in grp_v.iteritems():
                cronjob                     =   v['cron'].strip('\n')
                cron_cmt                    =   cronjob[cronjob.rfind('#')+1:]
                cronjob                     =   cronjob[:len(cronjob) - len(cron_cmt) - 1].strip()
                max_cmd_len                 =   max_cmd_len if max_cmd_len>len(cronjob) else len(cronjob)
                if not cron_cmt:
                    cron_cmt                =   '_' + self.T.get_guid().hex
                cmt_dict.update(                {cron_cmt.strip():cronjob})
                cron_env                    =   v['cron_env']
                crontab_copy                =   v['crontab_copy']

            max_cmd_len                     +=  5
            cron.lines.extend(                  cron_env.split('\n'))
            cron.lines.append(                  '')
            for it in sorted(cmt_dict.keys()):
                _cronjob                    =   cmt_dict[it]
                _space                      =   ' ' * ( max_cmd_len - len(_cronjob) )
                cronjob_w_fmt               =   ''.join([_cronjob,_space,'#  ',it])
                cron.lines.append(              cronjob_w_fmt )

            # LOCAL -- Copy & Load Crontab File
            if grp_k == self.T.SCRIPT_RUNNER:
                cron.write_to_user()

            # REMOTE -- Create local file, gzip/ssh to target, & load
            else:

                with open('/tmp/crontab','w') as f: f.write('')
                cron.write('/tmp/crontab')
                
                p = self.T.sub_popen(crontab_copy,
                                     stdout=self.T.sub_PIPE,
                                     shell=True,
                                     executable='/bin/zsh')
                (_out,_err) = p.communicate()
                assert _err is None

        return
    
    @arg('target',nargs='*',default=os.environ['USER'],
         choices=parse_choices_from_pgsql("""
                                            SELECT DISTINCT tag res 
                                            FROM servers 
                                            WHERE s_idx IS NOT NULL 
                                            ORDER BY tag
                                         """) + ['ALL'],
         help='target server on which to change cron settings')
    @arg('-R','--results',nargs='*',
         default=['log'],
         choices                            =   [name.lstrip('_') for name,fx
                                                in inspect.getmembers(sys_reporter,inspect.ismethod)
                                                if (name.find('_')==0 and name.find('__')==-1)],
         help='options for handling RESULTS')
    @arg('-E','--errors',nargs='*',
         default=['paste','log','txt'],
         choices                            =   [name.lstrip('_') for name,fx
                                                in inspect.getmembers(sys_reporter,inspect.ismethod)
                                                if (name.find('_')==0 and name.find('__')==-1)],
         help='options for handling ERRORS (Note: No reporting if only ERRORS are defined and no error output)')
    def load(self,args):
        """Load all crons in target server(s)"""

        # cron_list                           =   self.T.pd.read_sql("""  SELECT * FROM crons
        #                                                                 WHERE is_active IS true
        #                                                            """, self.T.eng)
        target_servs                        =   args.target if not args.target==['ALL'] else sorted(self.T.S.tag.unique().tolist())
        cmd_server                          =   self.T.S[self.T.S.tag==self.T.SCRIPT_RUNNER].iloc[0,:]
        for _serv in target_servs:
            serv_cron_list                  =   self.T.cron_list[cron_list.server.str.contains(_serv)]
            if not len(serv_cron_list):
                pass
            else:
                target_server               =   self.T.S[self.T.S.tag==_serv].iloc[0,:]
                target_server['mailto']     =   self.T.mailto
                for idx,cron_data in serv_cron_list.iterrows():
                    self.update_cron_json(cmd_server,target_server,cron_data)
        
            self.load_crons_from_json(          { _serv : self.T.cron_json[_serv] } )
        return

    
    @arg('cron',nargs='?',
         choices=parse_choices_from_pgsql(  """
                                            SELECT DISTINCT tag res
                                            FROM crons
                                            WHERE NOT is_active IS false
                                            """),
         help='cron tag to disable')
    def disable(self,args):
        """Disable a specific cron on one, several, or all servers (feat. under devel.)"""
        self.T.conn.set_isolation_level( 0)
        self.T.cur.execute(              "update crons set is_active = false where tag = '%s';" % args.cron)    
        self.list(                      args.cron)

    @arg('cron',nargs='?',
         choices=parse_choices_from_pgsql(  """
                                            SELECT DISTINCT tag res
                                            FROM crons
                                            WHERE is_active IS false
                                            """),
         help='cron tag to enable')
    def enable(self,args):
        """Enable a specific cron on one, several, or all servers (feat. under devel.)"""
        self.T.conn.set_isolation_level( 0)
        self.T.cur.execute(              "update crons set is_active = true where tag = '%s';" % args.cron)
        self.list(                      args.cron)

    @arg()
    def list(self,args):
        """List all stored crons and details"""
        print self.T.pd.read_sql("SELECT * FROM crons ORDER BY is_active,tag",self.T.eng)


    @arg('-R','--results',nargs='*',
         default=['log'],
         choices                            =   [name.lstrip('_') for name,fx
                                                in inspect.getmembers(sys_reporter,inspect.ismethod)
                                                if (name.find('_')==0 and name.find('__')==-1)],
         help='options for handling RESULTS')
    @arg('-E','--errors',nargs='*',
         default=['paste','log','txt'],
         choices                            =   [name.lstrip('_') for name,fx
                                                in inspect.getmembers(sys_reporter,inspect.ismethod)
                                                if (name.find('_')==0 and name.find('__')==-1)],
         help='options for handling ERRORS (Note: No reporting if only ERRORS are defined and no error output)')
    def check_logrotate(self,args):
        """Test for checking whether logrotate is working on THIS server"""
        self.process                        =   'check_logrotate'
        self.process_start                  =   self.T.dt.now()
        self.process_params                 =   {}
        self.process_stout                  =   []
        self.process_sterr                  =   None

        (_out,_err)                         =   sys_admin().exec_cmds({'cmds':['cat /etc/logrotate.d/sv_syslog'],'cmd_host':self.worker,'cmd_worker':self.worker})
        assert _err                        is   None
        rotate_period                       =   7

        cmds                                =   ['cat /var/lib/logrotate/status | grep syslogs | grep -v \'tmp_\'']
        (_out,_err)                         =   sys_admin().exec_cmds({'cmds':cmds,'cmd_host':self.worker,'cmd_worker':self.worker})
        assert _err                        is   None
        today                               =   dt.now()
        report_failure                      =   False
        for it in _out.split('\n'):
            if it!='':
                t                           =   it.split()[1]
                z                           =   t[:t.rfind('-')]
                cron_d                      =   dt.strptime(z,'%Y-%m-%d')
                y                           =   cron_d-today
                days_since                  =   abs(y.days)
                if days_since>rotate_period:
                    report_failure          =   True

        self.process_end                    =   dt.now()
        if report_failure:
            self.process_stout.append(          'LogRotate does not appear to be working on %s' % self.worker )
            results_and_errors              =   ['_'.join(['errors'] + args.errors)]     # default -> ['errors_paste_log_txt']
        else:
            self.process_stout.append(          'LogRotate looks good on %s' % self.worker )
            results_and_errors              =   ['_'.join(['results'] + args.results)]   # default -> ['results_log']

        return self.Reporter.manage(            self,results_and_errors=results_and_errors)


    @arg('-R','--results',nargs='*',
         default=['log'],
         choices                            =   [name.lstrip('_') for name,fx
                                                in inspect.getmembers(sys_reporter,inspect.ismethod)
                                                if (name.find('_')==0 and name.find('__')==-1)],
         help='options for handling RESULTS')
    @arg('-E','--errors',nargs='*',
         default=['paste','log','txt'],
         choices                            =   [name.lstrip('_') for name,fx
                                                in inspect.getmembers(sys_reporter,inspect.ismethod)
                                                if (name.find('_')==0 and name.find('__')==-1)],
         help='options for handling ERRORS (Note: No reporting if only ERRORS are defined and no error output)')
    def find_new_pip_libs(self,args):
        """Finds new pip libs on all servers"""

        self.process                        =   'find_new_pip_libs'
        self.process_start                  =   self.T.dt.now()
        SERVS                               =   self.servers[(self.servers.server_idx>0)&(self.servers.server!='serv')].server.tolist()
        # serv excluded because redundant and sudo command difficult
        self.process_params                 =   {'SERVS'             :   SERVS }
        self.process_stout                  =   []
        self.process_sterr                  =   []
        for serv in SERVS:
            (_out,_err)                     =   exec_cmds({'cmds':['sudo /usr/bin/updatedb > /dev/null 2>&1'],'cmd_host':serv,'cmd_worker':self.worker})
            cmds                            =   ['echo $HOME;',
                                                 'a=$(which grep);',
                                                 'locate /ENV | env $a --color=never -E \'/ENV$\'']
            (_out,_err)                     =   exec_cmds({'cmds':cmds,'cmd_host':serv,'cmd_worker':self.worker})
            if not _err is None:                self.process_sterr.append(_err)
            serv_home                       =   _out.split('\n')[0]
            found_lib_locs                  =   [ it for it in _out.split('\n')[1:] if it.count(serv_home)>0 and it.count('/ENV')==1 ]
            saved_libs                      =   self.servers[self.servers.tag==serv].pip_libs.tolist()[0]

            if not saved_libs:
                to_save_locs                =  []
            else:
                known_lib_locs              =   [ saved_libs[it]['location'] for it in saved_libs.keys() ]
                new_lib_locs                =   [ it for it in found_lib_locs if known_lib_locs.count(it)==0 ]
                if not hasattr(self,'ignore_lib_D'):
                    self.health             =   sys_status()
                    self.ignore_lib_D       =   dict(zip(self.health.ignore.param2.tolist(),
                                                    self.health.ignore.server_tag.tolist()))
                to_save_locs                =   [ it for it in new_lib_locs if (self.ignore_lib_D.has_key(it)==False and it!='') ]


            if to_save_locs:

                # update dict from DB
                lib_names                   =   []
                for it in to_save_locs:
                    lib_name                =   it[it.rstrip('/ENV').rfind('/')+1:].rstrip('/ENV')
                    pt                      =   1
                    while saved_libs.keys().count(lib_name)>0:
                        if saved_libs.keys().count(lib_name+'_'+str(pt))==0:
                            lib_name        =   lib_name+'_'+str(pt)
                        else:   pt         +=   1
                    lib_names.append(           lib_name)
                    lib_info                =   {lib_name               :   { 'requirements':'','location':it }   }
                    saved_libs.update(          lib_info)
                    self.process_stout.append(  ['new_pip_lib',serv,lib_name,it])

                # update DB with updated dict
                conn.set_isolation_level(       0)
                f_saved_libs                =   self.T.j_dump(saved_libs)
                cmd                         =   """ update servers set pip_libs='%s' where tag='%s' """ % (f_saved_libs,serv)
                cur.execute(                    cmd)

                # Run backup_pip to save lib reqs to paste
                if not hasattr(self,'SYS'):
                    self.Backup             =   sys_backup(self)
                vars                        =   [serv] + lib_names
                self.Backup.pip(                *vars )

        self.process_end                    =   self.T.dt.now()
        if not self.process_sterr:
            results_and_errors              =   ['_'.join(['results'] + args.results)]   # default -> ['results_log']
        else:
            results_and_errors              =   ['_'.join(['errors'] + args.errors)]     # default -> ['errors_paste_log_txt']

        return self.Reporter.manage(            self,results_and_errors=results_and_errors)

    @arg('-R','--results',nargs='*',
         default=['log'],
         choices                            =   [name.lstrip('_') for name,fx
                                                in inspect.getmembers(sys_reporter,inspect.ismethod)
                                                if (name.find('_')==0 and name.find('__')==-1)],
         help='options for handling RESULTS')
    @arg('-E','--errors',nargs='*',
         default=['paste','log','txt'],
         choices                            =   [name.lstrip('_') for name,fx
                                                in inspect.getmembers(sys_reporter,inspect.ismethod)
                                                if (name.find('_')==0 and name.find('__')==-1)],
         help='options for handling ERRORS (Note: No reporting if only ERRORS are defined and no error output)')
    def run_git_fsck(self,args):
        """Runs `git fsck` on all master and sub repos"""
        self.process                        =   'git_fsck'
        self.process_start                  =   self.T.dt.now()
        self.process_params                 =   {}
        self.process_stout                  =   []
        self.process_sterr                  =   []
        g                                   =   self.T.pd.read_sql('select * from servers where git_tag is not null',eng)
        sub_srcs,sub_dest                   =   g.git_sub_src.tolist(),g.git_sub_dest.tolist()
        master_src                          =   g.git_master_src.tolist()
        all_repos                           =   sub_srcs + sub_dest + master_src
        all_repos                           =   sorted(dict(zip(all_repos,range(len(all_repos)))).keys())
        serv                                =   '0'
        for it in all_repos:
            if it.find(serv)!=0:
                serv                        =   it[it.find('@')+1:it.rfind(':')]
            s_path                          =   it[it.rfind(':')+1:]
            cmds                            =   ['cd %s;' % s_path,
                                                 'git fsck 2>&1;']
            (_out,_err)                     =   sys_admin().exec_cmds({'cmds':cmds,'cmd_host':serv,'cmd_worker':self.worker})
            assert _err==None
            if _out!='':
                T                           =   { 'msg'                 :   'Repo needs work >>%s<<' % it,
                                                  'stdout'              :   _out}
                self.process_sterr.append(      T )

        self.process_end                    =   self.T.dt.now()
        if not self.process_sterr:
            self.process_stout.append(          'git_fsck indicates all repos look good' )
            results_and_errors              =   ['_'.join(['results'] + args.results)]   # default -> ['results_log']
        else:
            results_and_errors              =   ['_'.join(['errors'] + args.errors)]     # default -> ['errors_paste_log_txt']

        return self.Reporter.manage(            self,results_and_errors=results_and_errors)

if __name__ == '__main__':
    run_custom_argparse()