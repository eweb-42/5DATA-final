#!/bin/bash

container=5DATA-airflow
network=5-DATA
bucket=''
dir=$(dirname  $0)

while getopts b: arg
do
    case "${arg}" in
        b) bucket=${OPTARG}
    esac
done

if [ -z "$bucket" ]; then
    echo "Please specify the name of the S3 bucket with -b"
    exit
fi

# for some reason creating cons via cli on puckel/docker-airflow creates an error due to missing fernet key
# a common containment is to set $FERNET_KEY with a 32 char url safe base 64 encoded byte
fernet=$(openssl rand -base64 32)

set -euo pipefail
echo "[INFO] stopping 5DATA-airflow if it already exists"
docker stop $container || true

echo "[INFO] Starting Airflow"
docker run -d -p 8080:8080 --rm --network $network --name $container -v $(pwd)/dags:/usr/local/airflow/dags -v $(pwd)/scripts/requirements.txt:/requirements.txt -e FERNET_KEY=$fernet puckel/docker-airflow webserver

until curl -s localhost:8080 > /dev/null
    do echo "[INFO] waiting for Airflow to start" && sleep 1.2
done

docker exec -ti $container airflow connections --add --conn_id '5DATA-ERP' --conn_uri 'postgresql://postgres:postgres@5DATA-erp:5432/ERP'
docker exec -ti $container airflow variables -s bucket_name $bucket