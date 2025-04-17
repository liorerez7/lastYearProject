import os

from main.core.uploader.uploader import dbUploader
import boto3
import pymysql
import subprocess


class awsUploader(dbUploader):
    """
    AWS-specific implementation for uploading a MySQL dump to an RDS instance.
    """
    def __init__(self):
        self.created_endpoints = None
        self.connection = None
        self.rds_host = None
        self.rds_user = None
        self.rds_password = None
        self.rds_db = None
        self.rds_port = None

    def set_mysql_connection_details(self, endpoint, config):
        self.rds_host = endpoint
        self.rds_user = config["MasterUsername"]
        self.rds_password = config["MasterUserPassword"]
        self.rds_db = config["DBName"]
        self.rds_port = config.get("Port", 3306)

    def set_postgres_connection_details(self, endpoint, config):
        self.rds_host = endpoint
        self.rds_user = config["MasterUsername"]
        self.rds_password = config["MasterUserPassword"]
        self.rds_db = config["DBName"]
        self.rds_port = config.get("Port", 5432)

    def upload_postgres(self, dump_path):
        print(f"🚀 Uploading dump file to AWS RDS PostgreSQL from {dump_path}...")
        try:
            command = [
                'psql',
                f'-h', self.rds_host,
                f'-U', self.rds_user,
                f'-p', str(self.rds_port),
                f'-d', self.rds_db,
                '-f', dump_path
            ]
            env = os.environ.copy()
            env['PGPASSWORD'] = self.rds_password  # כדי לא להקליד את הסיסמה

            result = subprocess.run(command, capture_output=True, text=True, env=env)
            if result.returncode != 0:
                print(f"❌ Upload failed: {result.stderr}")
            else:
                print("✅ Upload complete.")
        except Exception as e:
            print(f"❌ Exception during upload to PostgreSQL: {e}")
            raise

    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=self.rds_host,
                user=self.rds_user,
                password=self.rds_password,
                db=self.rds_db,
                port=self.rds_port
            )
            print("✅ Connected to AWS RDS MySQL instance.")
        except Exception as e:
            print(f"❌ Failed to connect to RDS: {e}")
            raise

    def upload(self, dump_path):
        print(f"🚀 Uploading dump file to AWS RDS from {dump_path}...")
        try:
            command = [
                'mysql',
                f'-h{self.rds_host}',
                f'-u{self.rds_user}',
                f'-p{self.rds_password}',
                self.rds_db
            ]
            with open(dump_path, 'rb') as f:
                result = subprocess.run(command, stdin=f, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"❌ Upload failed: {result.stderr}")
                else:
                    print("✅ Upload complete.")
        except Exception as e:
            print(f"❌ Exception during upload: {e}")
            raise

    def close(self):
        if self.connection:
            self.connection.close()
            print("🔒 Connection to RDS closed.")

    def get_endpoint(self, instance_id):
        """
        Get the current endpoint address of an RDS instance by ID.
        """
        try:
            rds = boto3.client('rds')
            response = rds.describe_db_instances(DBInstanceIdentifier=instance_id)
            return response['DBInstances'][0]['Endpoint']['Address']
        except Exception as e:
            print(f"❌ Failed to retrieve endpoint for '{instance_id}': {e}")
            raise

    def get_or_create_endpoints(self, aws_upload_config):
        """
        Retrieves endpoints for source and destination RDS instances.
        Creates them if they don't exist.
        """
        rds = boto3.client('rds')
        self.created_endpoints = {}

        for db_type in ['source', 'destination']:
            db_config = aws_upload_config[db_type]
            instance_id = db_config['DBInstanceIdentifier']

            try:
                # Check if instance exists
                response = rds.describe_db_instances(DBInstanceIdentifier=instance_id)
                endpoint = response['DBInstances'][0]['Endpoint']['Address']
                print(f"🔁 RDS instance '{instance_id}' already exists.")
            except rds.exceptions.DBInstanceNotFoundFault:
                # Create it if not found
                print(f"🚀 Creating RDS instance: {instance_id}")
                # TODO ADD A GROUP RULE SO WE CAN REACH THE DB FROM THE OUTSIDE
                rds.create_db_instance(
                    DBInstanceIdentifier=instance_id,
                    DBName=db_config['DBName'],
                    Engine=db_config['Engine'],
                    MasterUsername=db_config['MasterUsername'],
                    MasterUserPassword=db_config['MasterUserPassword'],
                    DBInstanceClass=db_config['DBInstanceClass'],
                    AllocatedStorage=db_config['AllocatedStorage'],
                )

                print("⏳ Waiting for RDS instance to become available...")
                waiter = rds.get_waiter('db_instance_available')
                waiter.wait(DBInstanceIdentifier=instance_id)

                # Get endpoint after creation
                response = rds.describe_db_instances(DBInstanceIdentifier=instance_id)
                endpoint = response['DBInstances'][0]['Endpoint']['Address']
                print(f"✅ Created RDS instance '{instance_id}'.")

            except Exception as e:
                print(f"❌ Failed to get or create {db_type} RDS instance '{instance_id}': {e}")
                raise

            self.created_endpoints[db_type] = endpoint
            print(f"🌐 Endpoint for {db_type}: {endpoint}")

        return self.created_endpoints


