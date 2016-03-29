from syscontrol import *

class sys_servers:
    """Functions for Mounting & Unmounting system drives"""

    def __init__(self,_parent=None):

        if (not hasattr(self,'T') and not _parent):
            from syscontrol.sys_lib import sys_lib
            self.T                          =   sys_lib(['pgsql']).T
        else:
            self.T = _parent.T if not hasattr(self,'T') else self.T

        locals().update(                        self.T.__dict__)
        shares                              =   self.T.pd.read_sql('select * from shares',self.T.eng)
        s                                   =   self.T.pd.read_sql('select * from servers where s_idx is not null',self.T.eng)
        self.sh         =   self.shares     =   shares
        self.s          =   self.servers    =   s
        server_dir_dict                     =   dict(zip(s.tag.tolist(),s.home_env.tolist()))
        mac                                 =   [int(str(get_mac()))]
        worker                              =   s[ s.mac.isin(mac) & s.home_env.isin([os_environ['HOME']]) ].iloc[0].to_dict()
        self.worker                         =   worker['s_user']
        self.worker_host                    =   worker['s_host']
        global THIS_SERVER
        THIS_SERVER                         =   self.worker
        self.base_dir                       =   worker['home_env']
        self.server_idx                     =   worker['s_idx']
        # rank                                =   {'high':3,'medium':2,'low':1,'none':0}
        # s['ranking']                        =   s.production_usage.map(rank)
        # self.priority                       =   dict(zip(s.tag.tolist(),s.ranking.tolist()))
        self.mgr                            =   self
        all_imports                         =   locals().keys()
        
        excludes                            =   ['D','self']
        for k in all_imports:
            if not excludes.count(k):
                self.T.update(                  {k                          :   eval(k) })
        
        globals().update(                       self.T.__dict__)

    @arg('mnt_src',nargs='?',help="SSH source, e.g., admin@localhost:1234:/home/admin/foo (see 'bind_address' in `man ssh`)")
    @arg('mnt_as_vol',nargs='?',default='',help='name of mount point dir in \'/Volumes\'')
    def mnt_sshfs(self,mnt_src,mnt_as_vol):
        """mount ssh source to this server in dir '/Volumes'"""

        sshfs                       =   self.T.os_environ['SSHFS']+' '

        cmds                        =   ['sudo umount -f %s > /dev/null 2>&1;' % mnt_as_vol]
        (_out,_err)                 =   self.T.exec_cmds({'cmds':cmds})

        cmds                        =   ['mkdir -p %s;' % mnt_as_vol,
                                         '%s %s %s -o ConnectTimeout=5 2>&1;' % (sshfs,mnt_src,mnt_as_vol),]

        err                         =   False
        try:
            (_out,_err)             =   self.T.exec_cmds({'cmds':cmds})
            if _out.count('Connection reset'):
                err                 =   True
        except:
            err                     =   True

        if err:
            t                       =   mnt_as_vol.split('/')[-1]
            # serv_is_low_prod_use    =   len(self.s[ (self.s.tag==t) &
            #                                         (self.s.production_usage=='low') ] )
            # if not serv_is_low_prod_use:
            #     i_trace()
            #     print                   mnt_src,'mount failed'
            (_out,_err)             =   self.T.exec_cmds({'cmds':['rm -fR %s ; ' % mnt_as_vol]})
            assert _err            is   None

        return

    @arg('shares',nargs='+',default='',choices=arg_by_pgsql("""
            select _res res
            from (
                select distinct unnest(res) _res
                from (

                    select string_to_array(concat(a,','::text,b),','::text) res 
                    from (
                        select * from
                        (select array_to_string(array_agg(distinct tag),','::text) a from shares) shares,
                        (select array_to_string(array_agg(tag),','::text) b from servers where server_idx is not null) servers
                    ) f
                ) f2
            ) f3
            order by _res asc """),more_choices=['DEV','ALL','_'],
            help='target server on which to backup pip')
    def mnt(self,shares=[]):
        """mount known shares to this server at '/Volumes/{SHARE}'"""

        shares                              =   shares.shares if shares.__class__.__module__=='argparse' else shares

        # Compensate for short-hand references to servers, i.e., 'ub1' for 'SERVER1'
        # servs                               =   self.s[self.s.server_idx.isnull()==False].ix[:,['tag','server_idx']]
        # serv_dict                           =   dict(zip(servs.tag.tolist(),
        #                                                  servs.server_idx.map(lambda t: 'SERVER'+str(int(t))) ))
        # shares                              =   map(lambda t: t if not serv_dict.has_key(t) else serv_dict[t],shares)

        if not shares or shares[:]==['_']:
            shares                          =   map(lambda s: str(s.strip("'")),
                                                self.s[self.s.tag==self.worker].mnt_up.tolist()[:][0] )
            shares_D                        =   dict(zip([ '/Volumes/' + it for it in shares ],
                                                         [ '%s:/' % it for it in shares ]))
        elif shares[:].count('DEV'):
            shares                          =   map(lambda s: str(s.strip("'")),
                                                    self.s[self.s.tag==self.worker].mnt_dev.tolist()[:][0] )
            shares_D                        =   dict(zip([ '/Volumes/' + it for it in shares ],
                                                         [ '%s:/' % it for it in shares ]))

        elif shares[:].count('ALL'):
            new_shares                      =   self.sh[self.sh.remote_path.str.contains(self.worker)==False]
            shares_D                        =   dict(zip(new_shares.tag.tolist(),new_shares.remote_path.tolist()))

        else:
            mnt_srcs                        =   map(lambda it: '%s:/' % it if not self.sh[self.sh.tag==it].remote_path.tolist() 
                                                    else self.sh[self.sh.tag==it].remote_path.tolist()[0],shares)
            shares_D                        =   dict(zip([ '/Volumes/' + it for it in shares ],
                                                 mnt_srcs))

        (_out,_err)                         =   self.T.exec_cmds({'cmds':'ps -axww'})
        assert _err                        is   None

        for mnt_as_vol,mnt_src in shares_D.iteritems():
            if not re_findall(mnt_as_vol,_out):
                self.mnt_sshfs(                 mnt_src,mnt_as_vol)

        return

    @arg('shares',nargs='+',default='',
         choices=arg_by_shell("echo `ls /Volumes > /dev/null 2>&1`;",lambda s: s.strip('\n').split()),
            more_choices=['ALL'],
            help='share dirs on this server')
    def umnt(self,dirs=['ALL'],local=True):
        """unmount linked source(s) from this server in dir '/Volumes'"""
        if dirs==['ALL']:
            cmds                    =   ["df 2>/dev/null | awk '/\\/Volumes\\// {print $NF}' | xargs -I{} sudo /bin/umount -f {};",
                                         "unalias ls > /dev/null 2&<1;",
                                         "ls /Volumes | xargs -I{} /bin/rmdir /Volumes/{};",]
            (_out,_err)             =   self.T.exec_cmds({'cmds':cmds})
            assert _err            is   None
            assert _out            ==   ''
        else:
            cmds                    =   []
            for it in dirs:
                cmds.extend(            ['sudo /bin/umount -f /Volumes/%s;' % it,
                                         '/bin/rmdir /Volumes/%s;' % it] )
            (_out,_err)             =   self.T.exec_cmds({'cmds':cmds})
            assert _err            is   None
            assert _out            ==   ''
