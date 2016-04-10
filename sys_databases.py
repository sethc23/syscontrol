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
    
class sys_databases:

    def __init__(self,_parent=None):
        if hasattr(_parent,'T'):    self.T  =   _parent.T
        elif hasattr(self,'T'):                 pass
        else:                       self.T  =   sys_lib(['pgsql']).T
        self.databases                      =   self.T.pd.read_sql('SELECT * FROM databases WHERE is_active IS True',self.T.eng)

    class Tables:

        def __init__(self,_parent):
            self.T                      =   _parent.T
            self.Create                 =   self.Create(self)

        class Create:

            def __init__(self,_parent):
                self.T                  =   _parent.T
                self.Create             =   self

            def config_rsync(self):
                t = """
                    CREATE TABLE config_rsync
                    (
                        consider text,
                        include text,
                        exclude text,
                        "1.0" text,
                        "2.0" text,
                        "3.0" text,
                        "4.0" text,
                        "5.0" text,
                        "6.0" text,
                        "7.0" text,
                        "8.0" text,
                        "9.0" text,
                        "10.0" text,
                        "11.0" text,
                        "12.0" text,
                        "unnamed: 15" text,
                        prep_scripts text,
                        source_5 text,
                        functions text,
                        uid integer NOT NULL,
                        last_updated timestamp with time zone,
                        CONSTRAINT config_rsync_pkey PRIMARY KEY (uid)
                    );
                """
                pass

            def crons(self):
                t = """
                    CREATE TABLE crons
                    (
                        tag text,
                        server text,
                        minute text,
                        hour text,
                        day_of_month text,
                        month text,
                        day_of_week text,
                        uid integer NOT NULL DEFAULT z_next_free('crons'::text, 'uid'::text, 'crons_uid_seq'::text),
                        special text,
                        cmd text,
                        is_active boolean,
                        last_updated timestamp with time zone,
                        CONSTRAINT crons_pkey PRIMARY KEY (uid)
                    );
                """

            def databases(self):
                t = """
                    CREATE TABLE databases
                    (
                        db_name text,
                        db_server text,
                        backup_cmd text,
                        backup_path text,
                        is_active boolean,
                        last_updated timestamp with time zone,
                        uid integer NOT NULL,
                        CONSTRAINT databases_pkey PRIMARY KEY (uid)
                    );
                """

            def servers(self):
                t = """
                    CREATE TABLE servers
                    (
                        tag text,
                        s_user text,
                        s_host text,
                        s_path text,
                        home_env text,
                        local_ip cidr,
                        local_port integer,
                        ext_ip cidr,
                        mac bigint,
                        model_id text,
                        serial_id text,
                        is_active boolean,
                        git_sync jsonb,
                        pip_libs json,
                        pip_last_updated timestamp with time zone
                    );
                """

            def shares(self):
                t = """
                    CREATE TABLE shares
                    (
                        remote_path text,
                        tag text,
                        last_updated timestamp with time zone,
                        uid integer NOT NULL,
                        CONSTRAINT tmp_pkey PRIMARY KEY (uid)
                    );
                """

            def system_health(self):
                t = """
                    CREATE TABLE system_health
                    (
                        type_tag text,
                        server_tag text,
                        param1 text,
                        param2 text,
                        last_updated timestamp with time zone,
                        uid integer NOT NULL,
                        CONSTRAINT system_health_pkey PRIMARY KEY (uid)
                    );
                """

            def system_log(self):
                t = """
                    CREATE TABLE system_log
                    (
                        operation text,
                        started timestamp with time zone,
                        parameters text,
                        stout text,
                        sterr text,
                        ended timestamp with time zone,
                        uid integer NOT NULL,
                        last_updated timestamp with time zone,
                        CONSTRAINT system_log_pkey PRIMARY KEY (uid)
                    );
                """

            def gmail(self):
                t = """
                    CREATE TABLE gmail
                    (
                        orig_msg jsonb,
                        gmail_id bigint,
                        msg_id text
                    );
                """
                self.T.conn.set_isolation_level(0)
                self.T.cur.execute(t)
