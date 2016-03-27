
class System_Databases:

    def __init__(self):
        self.T                      =   System_Lib().T
        self.databases              =   self.T.pd.read_sql('select * from databases where is_active is True',sys_eng)

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
                        id serial NOT NULL,
                        tag text,
                        web_service text,
                        domain text,
                        local_addr text,
                        local_port integer,
                        server text,
                        home_dir text,
                        subdomain_dest text,
                        production_usage text,
                        server_idx integer,
                        mac bigint,
                        remote_addr text,
                        is_active boolean,
                        subdomain text,
                        dns_ip text,
                        socket text,
                        remote_port integer,
                        model_id text,
                        serial_id text,
                        last_updated timestamp with time zone,
                        git_sub_src text,
                        git_sub_dest text,
                        git_master_src text,
                        git_master_dest text,
                        pip_libs json,
                        pip_last_updated timestamp with time zone,
                        git_tag text,
                        host text,
                        mnt_up text[],
                        mnt_dev text[],
                        CONSTRAINT servers_pkey PRIMARY KEY (id)
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
