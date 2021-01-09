#!/bin/bash

container=5DATA-erp
network=5-DATA
user=postgres
password=postgres
schema=ERP
dir=$(dirname  $0)

net=$(docker network ls -f name=5-DATA | wc -l)

if [ $net -ne 2 ]
then
	echo "[INFO] Network 5-DATA is missing, creating..."
	docker network create 5-DATA
fi

set -euo pipefail
echo "[INFO] stopping 5DATA-erp if it already exists"
docker stop $container || true

docker run --rm --name $container -e POSTGRES_USER -e POSTGRES_PASSWORD=$password -e POSTGRES_DB=$schema -d --network $network -p 5432:5432 postgres:alpine
until docker exec -ti $container pg_isready > /dev/null;
    do echo "[INFO] Waiting for Postgres to start" && sleep 0.2;
done

docker cp $dir/../sources/ERP/* $container:/tmp
echo "[INFO] Creating schema"
docker exec -ti $container psql -U $user -d $schema -f /tmp/DDL.sql

# Populating tables
for table in campuses companies students subjects professors events audiences lessons attendances apprenticeships grades;
    do docker cp $dir/../data/output/$table.csv $container:/tmp && \
    fields=$(head -1 $dir/../data/output/$table.csv) && \
    docker exec -ti $container psql -U $user -d $schema -c "copy $table($fields) from '/tmp/$table.csv' delimiter ',' csv header"
done
