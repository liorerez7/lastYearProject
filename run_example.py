from engine.awsUploader import awsUploader
from engine.aws_upload_config import aws_config
import boto3

def main():

    # connect to ec2
    # upload sql files
    # run mysql commands on files
    # pgloader to postgres
    # command to retrive output file


    uploader = awsUploader()

    # הגדרות ל־PostgreSQL
    uploader.set_postgres_connection_details(
        "postgres-dest-db.cdg0qswm8uxu.us-east-1.rds.amazonaws.com",
        aws_config["destination"]
    )

    uploader.upload_postgres("output.sql")
    
    '''
    # מגדירים פרטי התחברות ל־MySQL
    uploader.set_mysql_connection_details("mysql-source-db2.cdg0qswm8uxu.us-east-1.rds.amazonaws.com", aws_config["source"])

    uploader.connect()
    
    # ⬆️ מעלים את הסכמה והדאטה (שני הקבצים)
    uploader.upload("sakila-schema.sql")
    uploader.upload("sakila-data.sql")
    '''

if __name__ == "__main__":
    main()
'''
rds = boto3.client("rds")
    instance_id = aws_config["source"]["DBInstanceIdentifier"]
    response = rds.describe_db_instances(DBInstanceIdentifier=instance_id)
    endpoint = response["DBInstances"][0]["Endpoint"]["Address"]
    print("🔍 Endpoint:", endpoint)
'''
