#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
# _ARC_DEBUG=1
"""

Manages Distributed Systems

"""
from os                                         import environ                  as os_environ
from sys                                        import path                     as py_path
py_path.append(                                 os_environ['BD'])
py_path.append(                                 os_environ['HOME_ENV'] + '/.scripts')

from system_settings                            import *
from sysparse                                   import *

try:
    from ipdb import set_trace as i_trace   # i_trace()
    # ALSO:  from IPython import embed_kernel as embed; embed()
except:
    pass

class sys_control:

    def __init__(self,return_cls=None):
        if not return_cls:
            pass
        else:
            i_trace()
            if hasattr(self,return_cls):
                setattr(self,return_cls,getattr(self,return_cls))


### --- MUST LEAVE THIS CLASS AT BOTTOM ---

### ---                      ---

if __name__ == '__main__':
    run_custom_argparse()
    import os
    f                                       =   __file__
    THIS_MODULE                             =   os.path.dirname(os.path.abspath(f)) + f[f.rfind('/'):]
    mod_regex                               =   'System_(.*)'
    mod_excludes                            =   ['System_Lib','System_Argparse','System_Databases']

    c                                       =   parse_module(mod_path=THIS_MODULE,
                                                             regex=mod_regex,
                                                             excludes=mod_excludes)
    if not c:                                   raise SystemExit
    if type(c)==tuple:                  c   =   c[0]
    D                                       =   {}
    D.update(                                   locals())
    for k,v in D.iteritems():
        if re_findall(mod_regex,k) and inspect.isclass(v) and not mod_excludes.count(k):
            if re_sub(mod_regex,'\\1',k).lower() == c._class:
                THIS_CLASS                  =   v()
                break

    return_var                              =   getattr(THIS_CLASS,c._func)(c)
    if locals().has_key('return_var'):
        if return_var:                          print return_var





    # NEED TO ADD 'overright' and 'upgrade' to install-pip options

    # if c._func=='admin':
    #     SYS                                 =   System_Admin()
    #     getattr(SYS, c._func)(c)
    # elif c._func=='backup':
    #     i_trace()
    #     pass
    # elif c._func=='install':
    #     SYS                                 =   System_Admin()
    #     install_vars                        =   [c.pip_dest,c.install_dest,
    #                                              c.pip_src,c.pip_lib,
    #                                              c.install_opts]
    #     SYS.install_pip(                        *install_vars)
    # elif c._func=='status':
    #     SYS                                 =   System_Health()
    #     for it in c.status:
    #         SYS.make_display_check(             it)
    #
    #
    # elif c._func=='cron':
    #     SYS                                 =   System_Crons()
    #     getattr(SYS, c.cron[0])(c.cron_params)
    #
    # elif c._func=='config':
    #     pass
    #
    # elif c._func=='mnt' or c._func=='umnt':
    #     pass



    #     elif argv[1]=='cron':
    #         CRON                        =   System_Crons()
    #         if   argv[2]=='logrotate':
    #             CRON.check_log_rotate(      )
    #         elif argv[2]=='git_fsck':
    #             CRON.run_git_fsck(          )
    #         elif argv[2]=='find_new_pip_libs':
    #             CRON.find_new_pip_libs(     argv[3:])
    #         elif argv[2]=='authorize':
    #             CRON.authorize(             argv[3:])

    #     elif argv[1]=='settings':
    #         CFG                         =   System_Config()
    #         return_var                  =   CFG.adjust_settings( *argv[2:] )

    #     elif ['mnt','umnt'].count(argv[1]):
    #         SERVS                       =   System_Servers()
    #         return_var                  =   SERVS.mnt_shares(argv[2:]) if argv[1]=='mnt' else SERVS.umnt_shares(argv[2:])



    #     if argv[1].find('backup_')==0:
    #         SYS                         =   System_Admin()
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