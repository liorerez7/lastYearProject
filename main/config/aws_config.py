aws_config = {
  "source": {
    "endpoint": "",
    "DBInstanceIdentifier": "mysql-source-db2",
    #"DBName": "employees",extendedEmp
    "DBName": "extendedEmp",
    "Engine": "mysql",
    "MasterUsername": "admin",
    "MasterUserPassword": "StrongPassword123",
    "DBInstanceClass": "db.t3.micro",
    "AllocatedStorage": 20,
  },
  "destination": {
    "endpoint": "",
    "DBInstanceIdentifier": "postgres-dest-db",
    "DBName": "sakila_migrated",
    "Engine": "postgres",
    "MasterUsername": "pgadmin",
    "MasterUserPassword": "StrongPassword456",
    "DBInstanceClass": "db.t3.micro",
    "AllocatedStorage": 20
  }
}


