
class System_Networking:
    """Functions for managing System network"""

    def __init__(self,_parent=None):
        if not _parent:
            _parent                         =   System_Lib()
        self.T                              =   _parent.T

    @arg('-H','--host',action='append',
         choices                            =   parse_choices_from_pgsql("""
                                                    select distinct server res
                                                    from servers
                                                    where server_idx is not null
                                                    order by server
                                                 """) + ['all','ALL'],
         help='server host name')
    @arg('-p','--port',action='append',help='port(s) or port range(s)')
    @arg('-t','--tag',action='append',help='name/regex of service')
    def get(self,**args):
        """Returns [Device,Host,Service,Domain] from System pgsql with options to limit selection"""
        i_trace()
        # params                              =   ['host','port','tag']
        # d                                   =   dict(zip(params,[ args.__dict__.get(it) for it in params ]))
        # if d.values().count(None)==len(params):
        #     qry_params                      =   []
        # else:
        #     qry_params                      =   ['where']
        #     for k,v in d.iteritems():
        #         if v=='host':
        #             qry_params.append(          '_%s && array%s, and'%(k,v))
        #         elif v=='port':
        #             qry_params.append(          '_%s && array%s, and'%(k,v))
        #         elif v=='tag':
        #             qry_params.append(          '_%s && array%s, and'%(k,v))
        #     qry_params[-1]                  =   qry_params[-1][:-len(', and')]
        qry_params                      =   []
        df                                  =   self.T.pd.read_sql("select * from services %s" %
                                                                        ' '.join(qry_params),
                                                                   self.T.sys_eng)

        sort_params                         =   ['col','direction']
        return df

    @arg('port',help='port to map')
    @arg('tag',help='descriptive tag for labeling service using port')
    @arg('-H','--host',default='ALL',nargs='+',
         choices                            =   parse_choices_from_pgsql("""
                                                    select distinct server res
                                                    from servers
                                                    where server_idx is not null
                                                    order by server
                                                 """) + ['ALL'],
         help='server host name(s) for port endpoint(s)')
    def set(self,args):
        """Sets any values [Device,Host,Service,Domain] to System pgsql and updates iptables"""
        def update_pgsql():
            self.T.conn.set_isolation_level(        0)
            self.T.cur.execute(                     'DROP TABLE IF EXISTS %(tmp_tbl)s;' % self.T)
            self.results.to_sql(                    self.T['tmp_tbl'],self.T.eng)

            upd_set                             =   ','.join(['%s = t.%s' % (it,it) for it in self.results.columns])
            ins_cols                            =   ','.join(self.results.columns)
            sel_cols                            =   ','.join(['t.%s' % it for it in self.results.columns])

            self.T.update(                          {'upd_set'              :   upd_set,
                                                     'ins_cols'             :   ins_cols,
                                                     'sel_cols'             :   sel_cols,})
            # upsert to properties
            cmd                                 =   """
                                                    with upd as (
                                                        update properties p
                                                        set
                                                            %(upd_set)s
                                                        from %(tmp_tbl)s t
                                                        where p._property_id     =   t._property_id
                                                        returning t._property_id _property_id
                                                    )
                                                    insert into properties ( %(ins_cols)s )
                                                    select
                                                        %(sel_cols)s
                                                    from
                                                        %(tmp_tbl)s t,
                                                        (select array_agg(f._property_id) upd_property_ids from upd f) as f1
                                                    where (not upd_property_ids && array[t._property_id]
                                                        or upd_property_ids is null);

                                                    DROP TABLE %(tmp_tbl)s;
                                                    """ % self.T
            self.T.conn.set_isolation_level(        0)
            self.T.cur.execute(                     cmd)
        def update_router():
            nat_tbl                         =   'iptables -t nat'
            pre_routing                     =   '%s -A PREROUTING' % nat_tbl
            cmds                            =   ['#!/bin/sh',
                                                 '%s -F' % nat_tbl,
                                                 '%s -X' % nat_tbl,
                                                 '%s-Z' % nat_tbl,
                                                 '%s -p tcp -d 10.0.1.1 --dport 8080 -j REDIRECT --to-port 80' % pre_routing,
                                                 '%s -p tcp -d $(nvram get wan_ipaddr) --dport 22 -j DNAT --to $(nvram get lan_ipaddr):22' % pre_routing,
                                                 '%s -p tcp -d $(nvram get wan_ipaddr) --dport 23 -j DNAT --to $(nvram get lan_ipaddr):23' % pre_routing,
                                                 '%s -p tcp -d $(nvram get wan_ipaddr) --dport 80 -j DNAT --to 10.0.1.52:80' % pre_routing,
                                                 '%s -d $(nvram get wan_ipaddr) -j DNAT --to $(nvram get lan_ipaddr)' % pre_routing,]


        i_trace()


    def update_porting(self):

        pass

