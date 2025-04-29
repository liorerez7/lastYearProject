import boto3
import uuid

s3 = boto3.client('s3')
bucket_name = 'db-migration-file'  #  actual S3 bucket name
async def upload_migration_files_service(schema_file, data_file):
    session_id = f"session_{uuid.uuid4()}"

    # Upload schema file
    schema_content = await schema_file.read()
    s3.put_object(Bucket=bucket_name, Key=f"uploads/{session_id}/original_schema.sql", Body=schema_content)

    # Upload data file
    data_content = await data_file.read()
    s3.put_object(Bucket=bucket_name, Key=f"uploads/{session_id}/original_data.sql", Body=data_content)

    return {
        "session_id": session_id,
        "message": "Files uploaded to S3 under session folder."
    }
