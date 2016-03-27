
class System_Status:
    """Functions for checking system statuses"""

    def __init__(self):
        self.T                      =   System_Lib().T
        locals().update(                self.T.__dict__)
        s                           =   System_Servers()
        self.servers                =   s.servers
        self.worker                 =   s.worker
        h                           =   pd.read_sql('select * from system_health',sys_eng)
        self.Reporter               =   System_Reporter(self)
        self.processes              =   h[h.type_tag=='process'].copy()
        self.mounts                 =   h[h.type_tag=='mount'].copy()
        self.checks                 =   h[h.type_tag=='check'].copy()
        self.ignore                 =   h[h.type_tag=='ignore'].copy()

    @arg('target',nargs='?',default=os_environ['USER'],choices=parse_choices_from_pgsql("""
                                                                select distinct server res
                                                                from servers
                                                                where server_idx is not null
                                                                order by server
                                                             """),
        help="server on which to check status")
    @arg('-R','--results',nargs='*',#action='append',
         default=['log'],
         choices                    =   [name.lstrip('_') for name,fx
                                         in inspect.getmembers(System_Reporter,inspect.ismethod)
                                         if (name.find('_')==0 and name.find('__')==-1)] + ['',None],
         help='options for handling RESULTS')
    @arg('-E','--errors',nargs='*',#action='append',
         default=['paste','log','txt'],
         choices                    =   [name.lstrip('_') for name,fx
                                         in inspect.getmembers(System_Reporter,inspect.ismethod)
                                         if (name.find('_')==0 and name.find('__')==-1)] + ['',None],
         help='options for handling ERRORS (Note: No reporting if only ERRORS are defined and no error output)')
    def make_display_check(self,args):
        """ Compares active processes on target server with expected processes from DB and returns pretty results. """

        self.process                        =   'System_Status_Check on %s' % args.target
        self.process_start                  =   self.T.dt.now()
        self.process_params                 =   {}
        self.process_stout                  =   []
        self.process_sterr                  =   []
        chk_sys                             =   args.target
        P                                   =   self.processes
        procs                               =   P[ P.server_tag==chk_sys ].ix[:,['param1','param2']]
        procs                               =   dict(zip(procs.param1.tolist(),procs.param2.tolist()))

        if  chk_sys                        !=   self.worker:
            t                               =   'ssh %s "ps -axww"'%chk_sys
            cmd                             =   shlex.split(t)
        else: cmd                           =   ['ps','-axww']

        p                                   =   sub_popen(cmd,stdout=sub_PIPE)
        (ap, err)                           =   p.communicate()
        res,errs,wc                         =   [],[],r'#'
        chk_templ                           =   "printf $(tput bold && tput setaf 1)\"chk\"$(tput setaf 9 && `tput rmso`)\\\\t\"%s\\\\n\";"
        ok_templ                            =   "printf $(tput bold && tput setaf 2)\"ok\"$(tput setaf 9 && `tput rmso`)\\\\t\"%s\\\\n\";"
        issue_templ                         =   'Issue on "%s" with check: "%s"'

        for k in sorted(procs.keys()):

            if len(re_findall(procs[k],ap))==0:

                res.append(                     chk_templ % k)
                errs.append(                    issue_templ % (chk_sys,k) )
            else:
                res.append(                     ok_templ % k)

        C                                   =   self.checks
        checks                              =   C[ C.server_tag==chk_sys ].ix[:,['param1','param2']]
        checks                              =   dict(zip(checks.param1.tolist(),checks.param2.tolist()))
        for k in sorted(checks.keys()):

            cmd                             =   checks[k]
            if chk_sys!=self.worker:
                cmd                         =   "ssh %s '%s'" % (chk_sys,cmd)
            p                               =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
            (_out,_err)                     =   p.communicate()

            if not _out.count('1'):
                res.append(                     chk_templ % k)
                errs.append(                    issue_templ % (chk_sys,k))
            else:
                res.append(                     ok_templ % k)

        print ''.join(                          res).rstrip('\\n";') + '";'

        self.process_sterr                  =   errs if errs else None
        self.process_end                    =   self.T.dt.now()

        if not self.process_sterr and hasattr(args,'results'):
            results_and_errors              =   ['_'.join(['results'] + args.results)]   # default -> ['results_log']
            return self.Reporter.manage(        self,results_and_errors=results_and_errors)
        elif hasattr(args,'errors'):
            results_and_errors              =   ['_'.join(['errors'] + args.errors)]     # default -> ['errors_paste_log_txt']
            return self.Reporter.manage(        self,results_and_errors=results_and_errors)

        return
