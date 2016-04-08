
class sys_lib:

    def __init__(self,*args,**kwargs):
        """
        args:
            encoding
            pgsql
            reporter
            exec_cmd
        """

        def run_cmd(cmd,**kwargs):

            defaults = {'return_err'        :   False,
                        'source_env'        :   False}

            for name, value in defaults.iteritems():
                exec "%s = %s" % (name, value) in globals(),locals()

            for name, value in kwargs.iteritems():
                exec "%s = %s" % (name, value) in globals(),locals()

            if source_env:
                cmd = '; '.join(['source %s/.scripts/shell_env/_base' % os.environ['HOME'],
                                cmd.rstrip(';')])
            
            p = sub_popen(cmd,
                          stdout=sub_PIPE,
                          shell=True,
                          executable='/bin/zsh')
            
            res = None
            if not locals().has_key('background'):
                (_out,_err) = p.communicate()
                assert _err is None
                res = _out.rstrip('\n')

            res = (res,_err) if return_err else res
            return res



        def growl(msg):
            growl = ' '.join(['timeout --kill-after=5 4s',
                            'ssh mbp2 -F /home/ub2/.ssh/config',
                            '"/usr/local/bin/growlnotify --sticky --message \'%s\'"'])
            run_cmd(growl % msg)
            raise SystemExit
        def _load_connectors():
            eng                             =   create_engine(r'postgresql://%(DB_USER)s:%(DB_PW)s@%(DB_HOST)s:%(DB_PORT)s/%(DB_NAME)s'
                                                              % T,
                                                              encoding='utf-8',
                                                              echo=False)
            conn                            =   pg_connect("dbname='%(DB_NAME)s' host='%(DB_HOST)s' port=%(DB_PORT)s \
                                                           user='%(DB_USER)s' password='%(DB_PW)s' "
                                                           % T);
            cur                             =   conn.cursor()
            return eng,conn,cur

        
        # ------------------------------------------------------------------
        #   BASE
        
        from types                          import NoneType
        
        # ------------------------------------------------------------------
        # ------------------------------------------------------------------
        #   DEFAULTS
        
        defaults = {    'debug'             :   False,
                        'encoding'          :   False}

        for name, value in defaults.iteritems():
            exec "%s = %s" % (name, value) in globals(),locals()
        
        # ------------------------------------------------------------------
        # ------------------------------------------------------------------
        #   KWARGS
        
        for name, value in kwargs.iteritems():
            exec "%s = %s" % (name, value) in globals(),locals()
        
        # ------------------------------------------------------------------

        
        import                                  sys
        import                                  codecs
        if encoding:
            reload(sys)
            sys.setdefaultencoding('UTF8')
        if debug:
            from traceback                  import format_exc               as tb_format_exc
        from uuid                           import getnode                  as get_mac
        from os                             import system                   as os_cmd
        from sys                            import path                     as py_path
        from os                             import environ                  as os_environ
        from os                             import access                   as os_access
        from os                             import X_OK                     as os_X_OK
        from os                             import mkdir                    as os_mkdir
        import                                  os,sys
        import                                  inspect                     as I
        from subprocess                     import Popen                    as sub_popen
        from subprocess                     import check_output             as sub_check_output
        from subprocess                     import PIPE                     as sub_PIPE
        from subprocess                     import STDOUT                   as sub_stdout
        import                                  shlex
        from datetime                       import datetime as dt
        from dateutil                       import parser as DU
        import                                  time
        delay                               =   time.sleep
        from uuid                           import uuid4                    as get_guid
        from datetime                       import datetime                 as dt
        from dateutil                       import parser                   as DU
        from json                           import dumps                    as j_dump
        from re                             import findall                  as re_findall
        import                                  pandas                      as pd
        pd.set_option(                          'expand_frame_repr',False)
        pd.set_option(                          'display.max_columns', None)
        pd.set_option(                          'display.max_rows', 1000)
        pd.set_option(                          'display.width',180)
        np                                  =   pd.np
        np.set_printoptions(                    linewidth=200,threshold=np.nan)
        sys.path.append(                        os.environ['BD'] + '/py_classes')  
        from py_classes                     import To_Class,To_Class_Dict,To_Sub_Classes
        T                                   =   To_Class()
        T.config                            =   To_Class(kwargs,recursive=True)
        if T.config:
            T.update(                           T.config.__dict__)
        
        db_vars = ['DB_NAME','DB_HOST','DB_PORT','DB_USER','DB_PW']
        db_vars = [it for it in db_vars if not T.config._has_key(it)]

        if not db_vars:
            pass

        elif locals().keys().count('system_settings'):
            from system_settings import DB_NAME,DB_HOST,DB_PORT
            for it in db_vars:
                eval('T["%s"] = %s' % (it,it))
            
        else:
            z = eval("__import__('system_settings')")
            for it in db_vars:
                T[it] = getattr(z,it)


        if args.count('pgsql'):
            from sqlalchemy                 import create_engine
            import                              logging
            logging.basicConfig()
            logging.getLogger(                      'sqlalchemy.engine').setLevel(logging.WARNING)
            from psycopg2                   import connect as pg_connect
            try:
                eng,conn,cur                    =   _load_connectors()
            except:
                from getpass import getpass
                pw = getpass('Root password (to create DB:"%s" via CL): ' % DB_NAME)
                p = sub_popen(" ".join(["echo '%s' | sudo -S prompt='' " % pw,
                                        'su postgres -c "psql --cluster 9.4/main -c ',
                                        "'create database %s;'" % DB_NAME,
                                        '"']),
                              stdout=sub_PIPE,
                              shell=True)
                (_out, _err) = p.communicate()
                assert _err is None
                eng,conn,cur                    =   _load_connectors()


        if args.count('exec_cmd'):
            from sys_admin                  import sys_admin
            exec_cmd                        =   sys_admin().exec_cmds

        D                                   =   {'user'                     :   os_environ['USER'],
                                                 'guid'                     :   str(get_guid().hex)[:7]}
        D.update(                               {'tmp_tbl'                  :   'tmp_'+D['guid']})
        self.T                              =   To_Class(D)
        all_imports                         =   locals().keys()
        
        excludes                            =   ['D','self']
        for k in all_imports:
            if not excludes.count(k):
                self.T.update(                  {k                          :   eval(k) })
        
        
        if args.count('reporter'):
            self.T.Reporter                     =   System_Reporter(self)

        globals().update(                       self.T.__dict__)
