import re
from typing import Union

from dwh.jobs.abstract_job import AbstractJob
from dwh.services.database.jdbc.jdbc_connection_service import JdbcConnectionService
from dwh.services.file.file_locator import FileLocator
from dwh.services.notification.notification_service import NotificationService


class SchemaUpgradeJob(AbstractJob):

    # definitions:
    # major version: 1.0, 2.0, 3.0
    #  - major version is the first number in the version, and it is used to indicate a significant change in the schema.
    #  - major version changes indicate existing sql scripts may not work, and the schema may not be compatible with previous versions.
    # minor version: 1.1, 1.2, 2.1
    #  - minor version is the second number in the version, and it is used to indicate a change in the schema that is backwards compatible.
    #  - minor version changes indicate existing sql scripts will work, and the schema is compatible with previous versions.

    # todo: instead of over-writing version, we should append so w have a record of all applied versions, wghen they happened and by whom
    # todo: modify the get version sql to do a max(version)
    # todo: we should maintain ddls for each version - if not exists only the create needs to be run.
    # todo: scripts are to migrate from one minor version to another, not to create the schema from scratch.
    # todo: major version migration is not supported, and any attempt to migrate should not be allowed.
    # todo: change version from float to string, so we can support versions like 1.0.0, 1.0.1, etc.

    def __init__(
            self,
            alarm_service: NotificationService,
            ddl_file_service: FileLocator,
            postgres_service: JdbcConnectionService
    ):
        super(SchemaUpgradeJob, self).__init__()

        # Validate parameters
        if not isinstance(alarm_service, NotificationService):
            raise ValueError("alarm_service must be an instance of NotificationService")

        if not isinstance(ddl_file_service, FileLocator):
            raise ValueError("ddl_file_service must be an instance of FileLocator")

        if not isinstance(postgres_service, JdbcConnectionService):
            raise ValueError("postgres_service must be an instance of JdbcConnectionService")

        self.alarm_service = alarm_service
        self.ddl_file_service = ddl_file_service
        self.postgres_service = postgres_service

    def execute_job(self, schemas: Union[str, list[str]]):

        if not schemas:
            raise ValueError("schemas must be a non-empty list or csv string of schema names")

        if isinstance(schemas, str):
            schemas = schemas.split(',')

        print(f"Starting schema upgrade for schemas: {schemas}")

        results = []

        for schema in schemas:
            try:
                # For each schema, we need to:
                # 1. Check the current version (outside transaction)
                # 2. Start a transaction
                # 3. Apply upgrades
                # 4. Commit the transaction
                schema_results = self.upgrade_schema(schema)
                results.append(schema_results)
            except Exception as e:
                print(f"Error upgrading schema {schema}: {e}")
                raise

        print(f"Schema upgrade completed for schemas {schemas}: {results}")

        return results

    def upgrade_schema(self, schema: str):
        schema_files = self.ddl_file_service.list_files(f'ddls/redshift/{schema}')

        #  check for version outside of transaction
        current_version = self.get_schema_version(schema)

        # Process upgrades without using 'with conn:' since connection is already managed
        upgrades = self.list_upgrade_scripts(schema, schema_files, current_version)

        # If there are upgrades to apply, do it in a transaction
        if upgrades:
            try:
                # Start transaction by executing a BEGIN statement
                self.postgres_service.execute_query("BEGIN")

                # Apply each upgrade script
                for script_key in upgrades:
                    sql = self.download_script(script_key)
                    self.postgres_service.execute_query(sql)

                # Commit the transaction
                self.postgres_service.execute_query("COMMIT")
            except Exception as e:
                # Rollback on error
                self.postgres_service.execute_query("ROLLBACK")
                raise ValueError(f"Error upgrading schema {schema}: {e}")

        # No need to commit here as it's handled by the outer transaction

        upgrade_version = self.get_schema_version(schema)

        return {
            'schema': schema,
            'starting_version': current_version,
            'upgraded_version': upgrade_version,
        }

    def schema_exists(self, schema):
        sql = f"SELECT 1 FROM information_schema.schemata WHERE schema_name = '{schema}'"
        try:
            result = self.postgres_service.execute_query(sql)
            return bool(result)
        except Exception as e:
            raise ValueError(f"Error checking schema existence: {e}")

    def get_schema_version(self, schema):
        sql = f"SELECT version FROM {schema}.schema_version ORDER BY applied_at DESC LIMIT 1"
        try:
            result = self.postgres_service.execute_query(sql)
            if result and len(result) > 0:
                # Return version as a string to match test expectations
                return str(result[0]['version'])
            return 0.0
        except Exception as e:
            error_msg = str(e).lower()
            if ('relation' in error_msg and 'does not exist' in error_msg) or \
                    ('table' in error_msg and 'does not exist' in error_msg):
                return 0.0
            else:
                raise ValueError(f"Error getting schema version: {e}")

    def list_upgrade_scripts(self, schema: str, files: list[str], current_version: float) -> list[str]:
        if isinstance(current_version, str):
            current_version = float(current_version)

        version_parts = str(current_version).split('.')
        version_major = int(version_parts[0]) if len(version_parts) > 0 else 0

        # create_pattern = re.compile(rf'.*?/{schema}/\d+_create_{schema}_v(\d+)_(\d+)\.sql$', re.IGNORECASE)
        # Adjust pattern to match both forward slashes and backslashes in paths
        create_pattern = re.compile(rf'.*?[/\\]{schema}[/\\]?{schema}_v(\d+)_(\d+)\.(?:sql|ddl)$', re.IGNORECASE)
        upgrade_pattern = re.compile(
            rf'.*?[/\\]{schema}[/\\]?\d+_upgrade_{schema}_v(\d+)_(\d+)_to_v(\d+)_(\d+)\.sql$', re.IGNORECASE
        )

        create_script = None
        upgrades = []

        # todo: we should rely on major versions of schema to be in separate folders

        for f in files:
            m_create = create_pattern.search(f)
            m_upgrade = upgrade_pattern.search(f)
            if m_create:
                create_script = f
            elif m_upgrade:
                to_major = int(m_upgrade.group(3))
                to_minor = int(m_upgrade.group(4))
                to_version = float(f"{to_major}.{to_minor}")

                if (to_version > current_version):
                    upgrades.append((to_version, f))

        upgrades.sort()
        result = []
        if version_major == 0:
            if create_script:
                result.append(create_script)
            else:
                raise ValueError(f"No create script found for schema {schema}")
        result.extend(f for _, f in upgrades)
        return result

    def download_script(self, key) -> str:
        return self.ddl_file_service.read_file(key)

    def on_success(self, results: str) -> None:
        """
        Send a notification using the notification service.
        """
        class_name = self.__class__.__name__
        subject = f"{class_name}: Job Completed Successfully"
        print(f"{subject} with results: {results}")

    def on_failure(self, error_message) -> None:
        """
        Send a notification using the notification service.
        """
        try:
            class_name = self.__class__.__name__
            subject = f"{class_name}: Job Execution Failed"
            self.alarm_service.send_notification(subject=subject, message=error_message)
        except Exception as e:
            print(f"Exception sending notification: {e}")
            raise RuntimeError(f"Failed to send notification: {e}") from e
