#!/bin/bash

# Exit if any command fails
set -e

# Load configuration from .env file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/.env"

# Use environment variables from .env
CONTAINER_NAME="$SQLSERVER_CONTAINER_NAME"
SA_PASSWORD="$SQLSERVER_PASSWORD"
HOST_PORT="$SQLSERVER_HOST_PORT"
DB_NAME="$SQLSERVER_DB_NAME"

# Pull latest SQL Server 2022 image
# docker pull mcr.microsoft.com/mssql/server:2022-latest

# Stop and remove any existing container with the same name
docker rm -f $CONTAINER_NAME 2>/dev/null || true

# Run SQL Server container
docker run -e "ACCEPT_EULA=Y" \
    -e "MSSQL_SA_PASSWORD=$SA_PASSWORD" \
    -p $HOST_PORT:1433 \
    --name $CONTAINER_NAME \
    -d mcr.microsoft.com/mssql/server:2022-latest

echo "Waiting for SQL Server to start..."
sleep 15

# Create test database using sqlcmd inside the container
# In SQL Server 2022, sqlcmd is located at /opt/mssql-tools18/bin/sqlcmd
docker exec $CONTAINER_NAME /opt/mssql-tools18/bin/sqlcmd \
    -S localhost -U SA -P "$SA_PASSWORD" -C -Q "IF DB_ID('$DB_NAME') IS NULL CREATE DATABASE [$DB_NAME];"

echo "Test SQL Server is running."
echo "Connect with:"
echo "  Host: localhost"
echo "  Port: $HOST_PORT"
echo "  User: SA"
echo "  Password: $SA_PASSWORD"
echo "  Database: $DB_NAME"