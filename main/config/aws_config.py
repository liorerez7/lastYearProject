aws_config = {
  "source": {
    "endpoint": "mysql-source-db2.czeew2ce4dpa.us-east-1.rds.amazonaws.com",
    "DBInstanceIdentifier": "mysql-source-db2",
    "DBName": "finalEmp",
    "Engine": "mysql",
    "MasterUsername": "admin",
    "MasterUserPassword": "StrongPassword123",
    "DBInstanceClass": "db.t3.micro",
    "AllocatedStorage": 20,
  },
  "destination": {
    "endpoint": "postgres-dest-db.czeew2ce4dpa.us-east-1.rds.amazonaws.com",
    "DBInstanceIdentifier": "postgres-dest-db",
    "DBName": "sakila_migrated",
    "Engine": "postgres",
    "MasterUsername": "pgadmin",
    "MasterUserPassword": "strongpassword123",
    "DBInstanceClass": "db.t3.micro",
    "AllocatedStorage": 20
  }
}


