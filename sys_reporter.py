#!/home/ub2/.virtualenvs/devenv/bin/python
# PYTHON_ARGCOMPLETE_OK

# NOTE: cannot use arg decorators here without creating infinite importing loop
import inspect
x = BASE_FILE_PATH      =   inspect.stack()[-1][1]
BASE_FILE               =   x[x.rfind('/')+1:]
THIS_FILE               =   __file__[__file__.rfind('/')+1:].rstrip('c')
if BASE_FILE==THIS_FILE:
    from __init__ import *


class sys_reporter:
    """Functions for uniformly managing output and error communications"""

    def __init__(self,_parent=None):
        if hasattr(_parent,'T'):    self.T  =   _parent.T
        elif hasattr(self,'T'):                 pass
        else:                       self.T  =   sys_lib(['pgsql']).T

        from google_tools.google_main                   import Google
        from pb_tools.pb_tools                          import pb_tools as PB
        # # DISABLED UPON LOADING REPORTER IN GOOGLE
        # s                                 =   sys_servers(self)
        # self.servers                      =   s.servers
        # self.worker                       =   s.worker
        # self.pb                             =   PB().pb
        # self.google                       =   Google()
        # self.GV                           =   self.google.Voice
        locals().update(                        self.T.__dict__)

    def __get_params(self):
        return                              [name for name,fx in inspect.getmembers(self,inspect.ismethod)
                                             if name.find('_') and not name.find('__')]

    def manage(self,admin,results_and_errors):
        """Input is taken from self.process,
                                            .process_start,
                                            .process_params,
                                            .process_stout,
                                            .process_sterr, and
                                            .process_end


            Assuming this class has already been initiated with:

                self.Reporter               =   sys_reporter(self)


            Usage [ e.g., at the end of a function ]:

                return self.Reporter.manage(    self,results_and_errors)


            Where 'results_and_errors' is a list
                with any one or more of the options:

                                                ['','results_print','results_log','results_log_txt',
                                                 'results_paste_log','results_paste_log_txt',
                                                 'errors_print','errors_log','errors_log_txt',
                                                 'errors_paste_log','errors_paste_log_txt']

            NOTE, if designations only exist for errors,
              no results are processed if self.process_sterr is empty.


            Template:

                self.process                =   ''
                self.process_start          =   dt.now()
                self.process_params         =   {}
                self.process_stout          =   []
                self.process_sterr          =   None
                self.process_end            =   dt.now()
                return self.Reporter.manage(    self,results_and_errors='')
        """
        NOTE_TO_DEVS = """
        Flow of function:

            1. If no sterr, ignore rules provided re: errors.
            2. Combine all rules into single Rule.
            3. Create Message.
            4. Process results with Message and according to Rule.

        """

        results_and_errors          =   results_and_errors if type(results_and_errors)==list else [results_and_errors]
        res,err                     =   [],[]
        for it in results_and_errors:
            if   it.find('results_')==0:
                res.append(             it.replace('results_','') )
            elif it.find('errors_')==0:
                err.append(             it.replace('errors_','') )

    #   1. If no stderr, (a) if only rules provided are for stderr, return
    #                    (b) if result rules, ignore stderr rules
        if not res and not err:
            return
        elif not res and not admin.process_sterr:
            return
        elif not admin.process_sterr:
            grp                             =   res
        else: grp                           =   res + err

    #   2. Combine all rules into single Rule.
        t                                   =   []
        for it in grp:
            t.extend(                           it.split('_') )
        methods                             =   dict(zip(t,range(len(t)))).keys()

    #   3. Create Message.
        runtime                             =   (admin.process_end-admin.process_start)
        if runtime.total_seconds()/60.0 < 1:
            runtime_txt                     =   'Runtime: %s seconds' % str(runtime.total_seconds())
        else:
            runtime_txt                     =   'Runtime: %s minutes' % str(runtime.total_seconds()/60.0)

        msg_title                           =   '[\"%s\" ENDED]' % admin.process
        msg                                 =   [msg_title,
                                                '',
                                                'Parameters: %s' % str(admin.process_params),
                                                 '',
                                                 'Started: %s' % dt.isoformat(admin.process_start),
                                                 runtime_txt,
                                                 '']
        msg_summary                         =   ', '.join([it for it in msg if it!=''])

        if res:
            if type(admin.process_stout)!=list:
                admin.process_stout         =   [ admin.process_stout ]
            if not (len(admin.process_stout)==0 or [None,'None','',[]].count(admin.process_stout)==1):
                msg.extend(                     ['Output: ',''])
                msg.extend(                     admin.process_stout )
                msg.extend(                     [''] )

        if err:
            if type(admin.process_sterr)!=list:
                admin.process_sterr         =   [ admin.process_sterr ]
            if not (len(admin.process_sterr)==0 or [None,'None','',[]].count(admin.process_sterr)==1):
                msg.extend(                     ['Errors: ',''] )
                msg.extend(                     admin.process_sterr )
                msg.extend(                     [''] )

        msg_str                             =   '\n'.join([str(it) for it in msg])

    #   4. Process results with Message and according to Rule.
        if methods.count('print')==1:
            self._print(                        msg)

        if methods.count('paste')==1:
            pb_url                          =   self._paste(msg_title,msg_str)
            log_msg                         =   ' - '.join([ msg_summary,pb_url ])
        else:
            log_msg                         =   msg_summary

        if methods.count('txt')==1:
            self._txt(                          log_msg)

        if methods.count('log')==1:
            self._log(                          log_msg)

        # ---

    def _print(self,msg):
        for it in msg:
            print it
        return

    def _paste(self,msg_title,msg_str):
        if not hasattr(self,'pb'):
            self.pb                         =   PB().pb
        pb_url                              =   self.pb.createPaste( msg_str,
                                                    api_paste_name=msg_title,
                                                    api_paste_format='',
                                                    api_paste_private='1',
                                                    api_paste_expire_date='1M')
        return pb_url

    def _g_txt(self,log_msg,phone_num='6179823305'):
        self.GV._msg(                           phone_num, log_msg)
        return

    def _txt(self,log_msg):
        opt                                 =   'F' if os.environ['USER']=='admin' else 't'
        cmd                                 =   'echo "%s" | mail -%s 6174295700@vtext.com' % (log_msg,opt)
        proc                                =   self.T.sub_popen(cmd, stdout=self.T.sub_PIPE, shell=True)
        (_out, _err)                        =   proc.communicate()
        assert _out==''
        assert _err==None
        return

    def _log(self,log_msg):
        cmd                                 =   'logger -t "sys_reporter" "%s"' % log_msg
        proc                                =   self.T.sub_popen(cmd, stdout=self.T.sub_PIPE, shell=True)
        (_out, _err)                        =   proc.communicate()
        assert _out==''
        assert _err==None
        return

    def _growl(self,log_msg,url=''):
        if url:
            cmd                             =   'growlnotify -m "%s" --url %s' % (log_msg,url)
        else:
            cmd                             =   'growlnotify -m "%s"' % log_msg
        self.T.exec_cmds(                       {'cmds':[cmd],'cmd_host':'mbp2','cmd_worker':self.T.THIS_PC})
