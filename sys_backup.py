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


class sys_backup:
    """Perform backup operations to select systems"""

    def __init__(self,_parent=None):
        if hasattr(_parent,'T'):    self.T  =   _parent.T
        elif hasattr(self,'T'):                 pass
        else:                       self.T  =   sys_lib(['pgsql']).T
        s                                   =   sys_servers(self)
        self.servers                        =   s.servers
        self.worker                         =   s.worker
        self.base_dir                       =   s.base_dir
        self.priority                       =   s.priority
        self.ready                          =   s.mnt(['ub2','ub1'])
        # self.cfg                            =   self.get_cfg()
        self.params                         =   {}
        # self.dry_run                        =   True
        self.dry_run                        =   False
        self.Reporter                       =   sys_reporter(self)
        #   REPORTER HAS PB
        # from pb_tools.pb_tools                          import pb_tools as PB
        self.pb                             =   PB().pb

    def __add_options(self):
        options                     =   [ 'verbose','verbose','recursive','archive','update',
                                          'one-file-system','compress','prune-empty-dirs',
                                          'itemize-changes']
                                        #,"filter='dir-merge /.rsync-filter'"]
                                        # ,'delete-before'
        if self.dry_run==True:          options.append('dry-run')
        self.params.update(             { 'options'     :   map(lambda s: '--%s'%s,options) })

    def __add_exclusions(self):
        exclude                     =   self.cfg.exclude.map(lambda s: '--exclude='+str(s)).tolist()
        if len(exclude)!=0:
            self.params.update(         { 'exclusions':   exclude, })

    def __add_inclusions(self):
        include                     =   self.cfg.include.map(lambda s: '--include='+str(s)).tolist()
        if len(include)!=0:
            self.params.update(         { 'inclusions':   include, })

    def __add_logging(self):
        self.params.update(             { 'logging'     :   ['--outbuf=L'], })

    def ipython(self,params=''):
        """OLD FUNC -- rsync ipython on ub2"""
        self.process                =   'backup_ipython'
        self.process_start          =   dt.isoformat(dt.now())
        self.add_options(               )
        self.add_exclusions(            )
        from_dir                    =   '/home/ub2/BD_Scripts/ipython'
        to_dir                      =   '/home/ub2/'
        src                         =   from_dir if self.worker=='ub2' else '/Volumes/ub2'+from_dir
        dest                        =   to_dir   if self.worker=='ub2' else '/Volumes/ub2'+to_dir
        self.params.update(             {'src_dir'      :   src,
                                         'dest_dir'     :   dest,
                                         'operation'    :   '%s: %s'%(self.worker,self.process)})
        self.run_rsync(                 )
        self.process_end            =   dt.isoformat(dt.now())
        return self.to_pastebin(        )

    @arg()
    def databases(self,args):
        """Backup all pgSQL databases as identified in the 'databases' pgSQL table"""
        self.process                        =   'backup_databases'
        self.process_start                  =   self.T.dt.now()
        self.process_params                 =   {}
        self.process_stout                  =   []
        d                                   =   sys_databases()
        self.databases                      =   d.databases
        self.database_names                 =   self.databases.db_name.tolist()
        for i in range(len(self.databases)):
            T                               =   {'started'                  :   dt.isoformat(dt.now())}
            db_info                         =   self.databases.ix[i,['backup_path','db_server','db_name','backup_cmd']].map(str)

            serv_info                       =   self.servers[self.servers.git_tag==db_info['db_server']].iloc[0,:].to_dict()

            T.update(                           {'DB'                       :   '%s @ %s' % (db_info['db_name'],
                                                                                     serv_info['server'])})

            fpath                           =   '%s/%s_%s_%s.sql' % tuple(db_info[:-1].tolist() + [dt.strftime(dt.now(),'%Y_%m_%d')])
            fname                           =   fpath[fpath.rfind('/')+1:]
            cmd                             =   """%s -d %s -h 0.0.0.0 -p 8800 --username=postgres > %s 2>&1
                                                """.replace('\n','').replace('\t','').strip() % (db_info['backup_cmd'],
                                                                                                 db_info['db_name'],
                                                                                                 fpath)
            (_out,_err)                     =   exec_cmds({'cmds':[cmd],'cmd_host':serv_info['server'],'cmd_worker':self.worker})
            T.update(                           {   'stdout'                :   _out })
            assert _err==None

            cmds                            =   ['scp %(host)s@%(serv)s:%(fpath)s /Volumes/EXT_HD/.pg_dump/;'
                                                 % ({ 'host'                :   serv_info['host'],
                                                      'serv'                :   serv_info['server'],
                                                      'fpath'               :   fpath })]

            (_out,_err)                     =   exec_cmds({'cmds':cmds,'cmd_host':'ub1','cmd_worker':self.worker})
            assert _out==''
            assert _err==None

            T.update(                           {   'ended'             :   dt.isoformat(dt.now())} )

            self.process_stout.append(          T )

        self.process_sterr                  =   None
        self.process_end                    =   dt.now()
        return self.Reporter.manage(            self,results_and_errors=['results_paste_log'])

    def system(self,params=''):
        """OLD FUNC -- rsync all servers to external HD"""
        self.cfg                        =   self.get_cfg()
        self.process                    =   'backup_system'
        self.process_start              =   dt.isoformat(dt.now())
        self.add_options(                   )
        self.add_exclusions(                ) # DON'T ADD INCLUSIONS -- see sync_items below
        cfg                             =   self.cfg
        cols                            =   cfg.columns.map(str).tolist()
        t_cols                          =   [it for it in cols if it[0].isdigit()]

        grps,pt                         =   [],0
        for i in range(len(t_cols)/2):
            x                           =   cfg[[t_cols[pt],t_cols[pt+1],'include']].apply(lambda s: [str(s[0])+'-'+str(s[1]),str(s[2])],axis=1).tolist()
            grps.extend(                    x   )
            pt                         +=   2
        res                             =   [it for it in grps if (str(it).find("['-',")==-1 and str(it).find("'']")==-1) ]
        d                               =   pd.DataFrame({  'server_pair'       :   map(lambda s: s[0],res),
                                                        'transfer_files'    :   map(lambda s: s[1],res)})
        _iters                          =   d.server_pair.unique().tolist()
        for pair in _iters:
            sync_items                  =   d[d.server_pair==pair].transfer_files
            incl                        =   sync_items.map(lambda s: ' --include='+s).tolist()
            a,b                         =   pair.split('-')
            a_serv,b_serv               =   map(lambda s: str(self.servers[self.servers.tag==s].server.iloc[0]),pair.split('-'))
            a_dir,b_dir                 =   map(lambda s: str(self.servers[self.servers.tag==s].home_env.iloc[0]),pair.split('-'))
            # _host                     =    b if priority[a]>priority[b] else a
            src                         =   a_dir if a_serv==self.worker else '/Volumes/'+a_serv+a_dir
            dest                        =   b_dir if b_serv==self.worker else '/Volumes/'+b_serv+b_dir
            for it in sync_items:
                self.params.update(         {'src_dir'      :   src+'/'+it.lstrip('/'),
                                             'dest_dir'     :   dest+'/',
                                             'operation'    :   '%s: %s -- %s -- %s'%(self.worker,self.process,pair,it)})
                self.run_rsync(             )
        self.process_end                =   dt.isoformat(dt.now())
        return self.to_pastebin(            )


    @arg('lib',nargs='+',default='ALL',
         choices=parse_choices_from_pgsql("""
                                            select json_object_keys(pip_libs::json) res
                                            from servers
                                            where pip_libs is not null
                                            and server ilike '%s'
                                         """,['--target']) + ['ALL'],
        help='known pip libs to backup\n(list avail. when target included)')
    @arg('target',nargs='?',default=os.environ['USER'],
         choices=parse_choices_from_pgsql("""
                                            SELECT DISTINCT tag res 
                                            FROM servers 
                                            WHERE s_idx IS NOT NULL 
                                            ORDER BY tag
                                          """),
        help='target server on which to backup pip')
    def pip(self,args):
        """Backup specific pip library requirements from a specified server to pgSQL"""

        SERVS                               =   args.target if not args.target=='ALL' \
                                                else self.servers[self.servers.pip_libs.isnull()==False].server.tolist()
        SERVS                               =   SERVS if type(SERVS) is list else [SERVS]
        spec_libs                           =   args.lib if args.lib else []

        self.process                        =   'backup_pip'
        self.process_start                  =   dt.now()
        self.process_params                 =   {'SERVS'             :   SERVS }
        self.process_stout                  =   []

        for serv in SERVS:
            libs,skip_libs                  =   {},{}
            if len(spec_libs)==0 or spec_libs=='ALL':
                libs                        =   self.servers[ self.servers.tag==serv ].pip_libs.tolist()[0]
            else:
                all_libs                    =   self.servers[ self.servers.tag==serv ].pip_libs.tolist()[0]
                for it in all_libs.keys():
                    if spec_libs.count(it)>0 or spec_libs==['ALL']:
                        libs.update({           it                  :   all_libs[it] }  )
                    else:
                        skip_libs.update({      it                  :   all_libs[it] }  )

            self.process_stout.append(          { '%s_pip_libs'%serv  :   str(libs) })

            D,old_reqs                      =   {},[]
            for k,v in libs.iteritems():

                if v['requirements']!='':
                    old_reqs.append(            v['requirements'].replace('http://pastebin.com/','')  )

                lib_loc                     =   v['location']
                cmds                        =   ['cd %s' % lib_loc]
                if lib_loc.find('ENV')>0:
                    cmds.append(                'source bin/activate'  )
                cmds.append(                    'pip freeze'  )

                cmd                         =   '; '.join(cmds)
                if serv!=self.worker:
                    cmd                     =   "ssh %s '%s'" % (serv,cmd)

                proc                        =   sub_check_output(cmd, stderr=sub_stdout, shell=True)

                pb_url                      =   self.pb.createPaste(proc,
                                                                    api_paste_name='%s -- pip_lib: %s' % (serv,k),
                                                                    api_paste_format='',
                                                                    api_paste_private='1',
                                                                    api_paste_expire_date='N')

                D.update(                       { k     :   {'location'     :   lib_loc,
                                                             'requirements' :   pb_url }
                                                })

                # Append any libs not updated
                for k,v in skip_libs.iteritems():
                    D.update(                   { k     :   v }  )

                # Push to servers DB
                cmd                         =   """
                                                    UPDATE servers SET
                                                    pip_libs            =   '%s',
                                                    pip_last_updated    =   'now'::timestamp with time zone
                                                    WHERE tag = '%s'
                                                """ % (j_dump(D),serv)

                conn.set_isolation_level(       0)
                cur.execute(                    cmd   )

                # Delete old Pastes
                for it in old_reqs:
                    self.pb.deletePaste(        it)

        self.process_sterr                  =   [None]
        self.process_end                    =   dt.now()

        return self.Reporter.manage(            self,results_and_errors=['results_paste_log'])

    def __to_pastebin(self,params=''):
        if self.dry_run==True:          return True
        else:

            condition                   =   """
                                                operation ilike '%s: %s%s'
                                                and started >=  '%s'::timestamp with time zone
                                                and ended   <  '%s'::timestamp with time zone
                                            """ % (self.worker,self.process,'%%',
                                               self.process_start,self.process_end)

            df                          =   pd.read_sql("select * from system_log where %s" % condition,eng)

            T                           =   df.iloc[0].to_dict()
            T['operation']              =   '%s: %s' % (self.worker,self.process)
            pb_url                      =   self.pb.createPaste(df.to_html(), api_paste_name = T['operation'],
                                                          api_paste_format = 'html5', api_paste_private = '1',
                                                          api_paste_expire_date = '2W')

            T['stout']                  =   pb_url
            T['ended']                  =   dt.isoformat(dt.now())
            T['parameters']             =   '\n\n'.join(df.parameters.tolist()).replace("'","''")
            c                           =   """insert into system_log values ('%(operation)s','%(started)s',
                                                              '%(parameters)s','%(stout)s',
                                                              '%(sterr)s','%(ended)s')"""%T
            conn.set_isolation_level(       0)
            cur.execute(                    c   )

            conn.set_isolation_level(       0)
            cur.execute(                    "delete from system_log where %s " % condition  )
            return True

    def __run_rsync(self):
        c,keys                          =   ['rsync'],self.params.keys()
        if keys.count('options'):           c.extend(self.params['options'])
        if keys.count('inclusions'):        c.extend(self.params['inclusions'])
        if keys.count('exclusions'):        c.extend(self.params['exclusions'])
        if keys.count('logging'):           c.extend(self.params['logging'])

        c.extend([                          self.params['src_dir'], self.params['dest_dir'] ])
        cmd                             =   ' '.join(c)
        start_ts                        =   dt.isoformat(dt.now())
        proc                            =   sub_popen([cmd], stdout=sub_PIPE, shell=True)
        (t, err)                        =   proc.communicate()
        c                               =   "insert into system_log values ('%s','%s','%s','%s','%s','%s')"%(
                                            self.params['operation'],start_ts,
                                            '%s %s'%(self.params['src_dir'],self.params['dest_dir']),
                                            unicode(t).replace("'","''"), unicode(err).replace("'","''"), dt.isoformat(dt.now()))
        conn.set_isolation_level(           0)
        cur.execute(                        c)
        return True
