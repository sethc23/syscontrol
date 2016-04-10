#!/home/ub2/.virtualenvs/devenv/bin/python
# PYTHON_ARGCOMPLETE_OK

import inspect
x = BASE_FILE_PATH      =   inspect.stack()[-1][1]
BASE_FILE               =   x[x.rfind('/')+1:]
THIS_FILE               =   __file__[__file__.rfind('/')+1:].rstrip('c')

if BASE_FILE==THIS_FILE:
    from __init__ import *
else:
    import os,sys
    sys.path.append(os.environ['HOME_ENV'] + '/.scripts')
    from sysparse import basic_components
    _components = basic_components()
    for name,arg in _components:
        exec '%s = arg' % name
    from argh.decorators import *
    import os

class sys_admin:
    """Functions for operating administrative features"""

    def __init__(self,_parent=None):
        if hasattr(_parent,'T'):    self.T  =   _parent.T
        elif hasattr(self,'T'):                 pass
        else:                       self.T  =   sys_lib(['pgsql']).T

    @arg('cmds',action=Store_List,help="a 'list' of command(s) to execute")
    @arg('-H','--cmd_host',nargs='?',default=os.environ['USER'],
         choices=parse_choices_from_pgsql("""
                                            SELECT DISTINCT tag res 
                                            FROM servers 
                                            WHERE s_idx IS NOT NULL 
                                            ORDER BY tag
                                          """),
         help="server to execute CMDS")
    @arg('-W','--cmd_worker',nargs='?',default=os.environ['USER'],
         choices=parse_choices_from_pgsql("""
                                            SELECT DISTINCT tag res 
                                            FROM servers 
                                            WHERE s_idx IS NOT NULL 
                                            ORDER BY tag
                                          """),
         help="server sending CMDS script to CMD_HOST")
    @arg('-T','--tag',nargs='?',default='exec_cmds',help='label to apply to authorization request for purposes of logging')
    @arg('-R','--results',nargs='*',
         default=['log'],
         choices = result_choices(),
         help='options for handling RESULTS')
    @arg('-E','--errors',nargs='*',
         default=['paste','log','txt'],
         choices                    =   [name.lstrip('_') for name,fx
                                         in inspect.getmembers(sys_reporter,inspect.ismethod)
                                         if (name.find('_')==0 and name.find('__')==-1)],
         help='options for handling ERRORS (Note: No reporting if only ERRORS are defined and no error output)')
    def exec_cmds(self,args,**kwargs):
        """Executes commands and returns (_out,_err).\nNote, SSH is used when cmd_host!=this_worker"""
        def run_cmd(args):
            cmd                             =   ' '.join(args.cmds)
            if args.cmd_host==args.cmd_worker:
                p                           =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
            else:
                cmd                         =   "ssh %s '%s'" % (args.cmd_host,cmd)
                p                           =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
            return p.communicate(),p

        if not hasattr(self,'T'):
            from py_classes                 import To_Class
            self.T                          =   To_Class({})
        for k,v in kwargs.iteritems():
            self.T.update(                      { 'kw_' + k                 :   v})

        if ( not hasattr(self.T,'kw_return_output')
            and not os.environ.has_key('in_args') ):
            self.T.update(                      { 'kw_return_output'        :   True})

        if [tuple,dict,list].count(type(args)):
            D                               =   argparse.Namespace()

            argh_args,arg_list              =   getattr(self.exec_cmds,'argh_args'),[]
            for it in argh_args:
                _default                    =   '' if not it.has_key('default') else it['default']
                this_arg                    =   it['option_strings'][-1].strip('-')
                arg_list.append(                this_arg)
                setattr(                        D,this_arg,_default)

            if type(args)==dict:
                for k,v in args.iteritems():
                    setattr(                    D,k,v)
            elif [tuple,list].count(type(args)):
                for i in range(len(args)):
                    setattr(                    D,arg_list[i],args[i])

            for k,v in kwargs.iteritems():
                setattr(                        D,k,[v] if D.__dict__.has_key(k) and type(getattr(D,k)) is list else v)

            args                            =   D

        args.cmds                           =   args.cmds if [list,argparse.Namespace].count(type(args.cmds)) else [args.cmds]

        if len(args.cmds)>1:    args.cmds   =   [ it.rstrip(';') + ';' for it in args.cmds[:-1] ] + [ args.cmds[-1].rstrip(' ;') + ';' ]
        else:                   args.cmds   =   [args.cmds[0].rstrip(' ;') + ';']


        if (not ' '.join(args.cmds).count('sudo')
            and not (hasattr(args,'root') and args.root==True)):
            (_out,_err),p                   =   run_cmd(args)
            if hasattr(self.T,'kw_return_process') and self.T.kw_return_process:
                return (_out,_err),p
            else:
                return (_out,_err)

        else:
            if not hasattr(self.T,'dt'):
                from datetime               import datetime as dt
                self.T.dt                   =   dt

            self.process                    =   args.tag
            self.process_start              =   self.T.dt.now()
            self.process_params             =   {'cmd'                      :   args.cmds}


            # cmds                          =   ['echo "%s" | sudo -S -k --prompt=\'\' ' % PASS,
            #                                    'bash -i -l -c "%s";' % cron_cmd]
            args.cmds                       =   [''.join(["SCR_OPT=$(if [ -n $(env | grep -E '^HOME' | grep 'Users/admin') ];",
                                                 ' then echo "-qc"; else echo "-q"; fi;);']),
                                                 'echo "%s" | sudo -S --prompt=\'\' ' % PASS,
                                                 'script $SCR_OPT \"bash -i -l -c \'',
                                                 '%s' % ' '.join(args.cmds),  #.replace(';','\\;'),
                                                 '\'\" | tail -n +2;',
                                                 'echo "%s" | sudo -S --prompt=\'\' rm -f typescript;' % PASS,
                                                 'unset SCR_OPT;',
                                                ]
            (_out,_err),p                   =   run_cmd(args)
            _out                            =   _out.rstrip('\r\n')
            res                             =   []
            if hasattr(self.T,'kw_return_output') and self.T.kw_return_output:
                res.extend(                     [_out,_err])
            if hasattr(self.T,'kw_return_process') and self.T.kw_return_process:
                res.append(                     p)

            if res:
                return res
            
            self.process_end                =   self.T.dt.now()
            self.process_stout              =   _out
            self.process_sterr              =   _err
            if not self.process_sterr:
                results_and_errors          =   ['_'.join(['results'] + args.results)]   # default -> ['results_log']
            else:
                results_and_errors          =   ['_'.join(['errors'] + args.errors)]     # default -> ['errors_paste_log_txt']
            return sys_reporter().manage(    self,results_and_errors=results_and_errors)