#!/bin/bash

# Usage:
# ./migrate.sh <mysql_user> <mysql_pass> <postgres_conn_string> <sql_file1> [sql_file2 ... sql_fileN]

# Check minimum args
if [ "$#" -lt 4 ]; then
  echo "❌ Usage: $0 <mysql_user> <mysql_pass> <postgres_conn_string> <sql_file1> [sql_file2 ...]"
  exit 1
fi

MYSQL_USER=$1
MYSQL_PASS=$2
POSTGRES_CONN=$3
MYSQL_PORT=3307
SQL_FILES=("${@:4}")  # All remaining args are SQL files

# Step 1: Start MySQL 5.7 container
echo "🚀 Starting MySQL 5.7 Docker container..."
docker run --name mysql57 \
  -e MYSQL_ROOT_PASSWORD=$MYSQL_PASS \
  -p $MYSQL_PORT:3306 \
  -d mysql:5.7

# Step 2: Wait for MySQL to initialize
echo "⏳ Waiting for MySQL to initialize..."
sleep 10
# Step 3: Create database 'sakila'
echo "📦 Creating 'sakila' database..."
docker exec -i mysql57 mysql -u $MYSQL_USER -p$MYSQL_PASS -e "CREATE DATABASE IF NOT EXISTS sakila;"

# Step 4: Copy and execute each SQL file
for file in "${SQL_FILES[@]}"; do
  echo "📤 Copying and running $file..."
  docker cp "$file" mysql57:/tmp.sql
  docker exec -i mysql57 mysql -u $MYSQL_USER -p$MYSQL_PASS sakila < "$file"
done

# Step 5: Run pgloader to migrate to PostgreSQL
echo "🔄 Running pgloader to migrate from MySQL to PostgreSQL..."
docker run --rm dimitri/pgloader:latest \
  pgloader \
  mysql://$MYSQL_USER:$MYSQL_PASS@host.docker.internal:$MYSQL_PORT/sakila \
  $POSTGRES_CONN

echo "✅ Migration completed!"

echo "🧹 Cleaning up Docker container..."
docker stop mysql57 >/dev/null
docker rm mysql57 >/dev/null
echo "🗑️ Docker container 'mysql57' removed."
#how to run:
#./mysql_to_postgres.sh.sh  root rootpass postgresql://postgres:postgres@172.24.128.1:5432/sakila sakila-schema.sql sakila-data.sql
#change ip in pgloader.sh to my ip (write ipconfig: Ethernet adapter vEthernet (WSL (Hyper-V firewall)):
                                                    #
                                                    #   Connection-specific DNS Suffix  . :
                                                    #   Link-local IPv6 Address . . . . . : fe80::512a:700f:a5d5:84d9%61
                                                    #   IPv4 Address. . . . . . . . . . . : 172.24.128.1
                                                    #   Subnet Mask . . . . . . . . . . . : 255.255.240.0
                                                    #   Default Gateway . . . . . . . . . :
                                                    #

#changed also in the pg_hba.conf the last line to this : host    all             all             0.0.0.0/0               trust
#and then restart to postgres service
