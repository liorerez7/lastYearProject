from engine.awsUploader import awsUploader
from engine.aws_upload_config import aws_config
import boto3

def main():


    # running the script of the pgloader somehow
    # get the output file that works with the postgres
    # continue with this code to upload the file to postgres

    uploader = awsUploader()

    # הגדרות ל־PostgreSQL
    uploader.set_postgres_connection_details(
        "postgres-dest-db.cdg0qswm8uxu.us-east-1.rds.amazonaws.com",
        aws_config["destination"]
    )

    uploader.upload_postgres("output.sql")
    

if __name__ == "__main__":
    main()

'''
    # מגדירים פרטי התחברות ל־MySQL
    uploader.set_mysql_connection_details("mysql-source-db2.cdg0qswm8uxu.us-east-1.rds.amazonaws.com",
     aws_config["source"])

    uploader.connect()

    # ⬆️ מעלים את הסכמה והדאטה (שני הקבצים)
    uploader.upload("sakila-schema.sql")
    uploader.upload("sakila-data.sql")
    '''

# connect to ec2
# upload sql files
# run mysql commands on files
# pgloader to postgres
# command to retrive output file

