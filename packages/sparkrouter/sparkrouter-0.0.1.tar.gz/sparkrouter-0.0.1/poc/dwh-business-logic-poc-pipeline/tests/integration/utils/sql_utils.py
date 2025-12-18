class SQLUtils:

    @staticmethod
    def drop_all_non_system_schemas(conn):
        """
        Drops all non-system schemas in the connected Postgres database.
        Excludes system schemas such as pg_catalog, information_schema, public, pg_toast, pg_temp_1, pg_toast_temp_1, and any schema starting with 'pg_'.
        """
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT schema_name
                        FROM information_schema.schemata
                        WHERE schema_name NOT IN (
                                                  'pg_catalog', 'information_schema', 'public',
                                                  'pg_toast', 'pg_temp_1', 'pg_toast_temp_1'
                            )
                          AND schema_name NOT LIKE 'pg\\_%'
                        """)
            schemas = [row[0] for row in cur.fetchall()]
            for schema in schemas:
                cur.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE;')
            # Optionally, drop all tables in public schema as well
            cur.execute("""
                DO $$
                DECLARE
                    r RECORD;
                BEGIN
                    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                        EXECUTE 'DROP TABLE IF EXISTS public.' || quote_ident(r.tablename) || ' CASCADE;';
                    END LOOP;
                END
                $$;
            """)
        conn.commit()
