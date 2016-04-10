#!/home/ub2/.virtualenvs/devenv/bin/python
# PYTHON_ARGCOMPLETE_OK
# _ARC_DEBUG

import inspect
x = BASE_FILE_PATH      =   inspect.stack()[-1][1]
BASE_FILE               =   x[x.rfind('/')+1:]
THIS_FILE               =   __file__[__file__.rfind('/')+1:].rstrip('c')

if BASE_FILE==THIS_FILE:
    import ipdb as I; I.set_trace()
    from __init__ import *
else:
    from sysparse import basic_components
    _components = basic_components()
    for name,arg in _components:
        exec '%s = arg' % name
    from argh.decorators import *
    import os


class sys_control:
    """Manages Distributed Systems"""

    def __init__(self,return_cls=None):
        if not return_cls:
            pass
        else:
            i_trace()
            if hasattr(self,return_cls):
                setattr(self,return_cls,getattr(self,return_cls))


if __name__ == '__main__':
    run_custom_argparse()

    
    # import os
    # f                                       =   __file__
    # THIS_MODULE                             =   os.path.dirname(os.path.abspath(f)) + f[f.rfind('/'):]
    # mod_regex                               =   'System_(.*)'
    # mod_excludes                            =   ['sys_lib','sys_argparse','sys_databases']

    # c                                       =   parse_module(mod_path=THIS_MODULE,
    #                                                          regex=mod_regex,
    #                                                          excludes=mod_excludes)
    # if not c:                                   raise SystemExit
    # if type(c)==tuple:                  c   =   c[0]
    # D                                       =   {}
    # D.update(                                   locals())
    # for k,v in D.iteritems():
    #     if re_findall(mod_regex,k) and inspect.isclass(v) and not mod_excludes.count(k):
    #         if re_sub(mod_regex,'\\1',k).lower() == c._class:
    #             THIS_CLASS                  =   v()
    #             break

    # return_var                              =   getattr(THIS_CLASS,c._func)(c)
    # if locals().has_key('return_var'):
    #     if return_var:                          print return_var





    # NEED TO ADD 'overright' and 'upgrade' to install-pip options

    # if c._func=='admin':
    #     SYS                                 =   sys_admin()
    #     getattr(SYS, c._func)(c)
    # elif c._func=='backup':
    #     i_trace()
    #     pass
    # elif c._func=='install':
    #     SYS                                 =   sys_admin()
    #     install_vars                        =   [c.pip_dest,c.install_dest,
    #                                              c.pip_src,c.pip_lib,
    #                                              c.install_opts]
    #     SYS.install_pip(                        *install_vars)
    # elif c._func=='status':
    #     SYS                                 =   sys_health()
    #     for it in c.status:
    #         SYS.make_display_check(             it)
    #
    #
    # elif c._func=='cron':
    #     SYS                                 =   sys_crons()
    #     getattr(SYS, c.cron[0])(c.cron_params)
    #
    # elif c._func=='config':
    #     pass
    #
    # elif c._func=='mnt' or c._func=='umnt':
    #     pass



    #     elif argv[1]=='cron':
    #         CRON                        =   sys_crons()
    #         if   argv[2]=='logrotate':
    #             CRON.check_log_rotate(      )
    #         elif argv[2]=='git_fsck':
    #             CRON.run_git_fsck(          )
    #         elif argv[2]=='find_new_pip_libs':
    #             CRON.find_new_pip_libs(     argv[3:])
    #         elif argv[2]=='authorize':
    #             CRON.authorize(             argv[3:])

    #     elif argv[1]=='settings':
    #         CFG                         =   sys_config()
    #         return_var                  =   CFG.adjust_settings( *argv[2:] )

    #     elif ['mnt','umnt'].count(argv[1]):
    #         SERVS                       =   sys_servers()
    #         return_var                  =   SERVS.mnt_shares(argv[2:]) if argv[1]=='mnt' else SERVS.umnt_shares(argv[2:])



    #     if argv[1].find('backup_')==0:
    #         SYS                         =   sys_admin()
    #         if (len(argv)>2 and argv[2]=='dry-run'):
    #             SYS.dry_run             =   True
    #         elif len(argv)>2:
    #             vars                    =   argv[2:]
    #         else:
    #             vars                    =   []


    #         if  argv[1]=='backup_all':
    #             SYS.backup_ipython(         )
    #             SYS.backup_databases(       )
    #             SYS.backup_system(          )
    #             SYS.backup_pip(             )


    #         elif  argv[1]=='backup_ipython':     SYS.backup_ipython()
    #         elif  argv[1]=='backup_databases':   SYS.backup_databases()
    #         elif  argv[1]=='backup_system':      SYS.backup_system()
    #         elif  argv[1]=='backup_pip':         SYS.backup_pip(*vars)

    # if return_var:                          print return_var