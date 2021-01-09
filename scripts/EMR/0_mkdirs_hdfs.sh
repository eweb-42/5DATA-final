#!/bin/bash

environment=""
bucket=""

while getopts e:b: arg
do
    case "${arg}" in
        e) environment=${OPTARG}
        ;;
        b) bucket=${OPTARG}
    esac
done

if [ -z "$environment" ]; then
    echo "please specify the environment with -e (DEV, PPROD ou PROD)"
    exit
fi

if [ -z "$bucket" ]; then
    echo "please specify the name of the bucket with -b"
    exit
fi

data=(
    /$environment/data/ERP/APPRENTICESHIPS
    /$environment/data/ERP/ATTENDANCES
    /$environment/data/ERP/AUDIENCES
    /$environment/data/ERP/CAMPUSES
    /$environment/data/ERP/COMPANIES
    /$environment/data/ERP/EVENTS
    /$environment/data/ERP/GRADES
    /$environment/data/ERP/LESSONS
    /$environment/data/ERP/PROFESSORS
    /$environment/data/ERP/STUDENTS
    /$environment/data/ERP/SUBJECTS
    /$environment/data/CLICKSTREAM
)

for dir in "${data[@]}"
    do echo "creating HDFS directory $dir" && \
    hdfs dfs -mkdir -p $dir;
done