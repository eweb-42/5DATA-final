DROP TABLE IF EXISTS data_${hiveconf:env}_5data.STUDENTS;
CREATE EXTERNAL TABLE data_${hiveconf:env}_5data.STUDENTS (
    ID STRING,
    FIRST_NAME STRING,
    LAST_NAME STRING,
    EMAIL STRING,
    PERSONAL_EMAIL STRING,
    GENDER STRING,
    DATE_OF_BIRTH STRING,
    JOIN_DATE STRING,
    LEFT_DATE STRING,
    CAMPUS_ID STRING,
    PROMOTION STRING,
    AVERAGE FLOAT
)
 ROW FORMAT DELIMITED
 FIELDS TERMINATED BY ","
 NULL DEFINED AS "\\N"
 STORED AS TEXTFILE
 LOCATION "/${hiveconf:env}/data/ERP/STUDENTS"
 tblproperties ("serialization.encoding"="UTF-8");