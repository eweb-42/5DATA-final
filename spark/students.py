import argparse
import logging
from operator import add
from random import random

from pyspark.sql import SparkSession

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def students(partitions, students, grades, output_uri):
    
    with SparkSession.builder.appName("Students").getOrCreate() as spark:
        logger.info("Launching spark job")
        students_df = spark.read.csv(students).toDF('id', 'first_name', 'last_name', 'mail', 'personal_mail', 'gender', 'date_of_birth', 'joind_date', 'left_date', 'campus_id', 'promotion')
        grades_df = spark.read.csv(grades).toDF('id', 'student_id', 'subject', 'date', 'grade')
        float_grades_df = grades_df.select('student_id', grades_df.grade.cast('float'))
        avg_df = float_grades_df.groupBy('student_id').avg('grade')
        students_df_with_avg_grades = students_df.join(avg_df, students_df.id == avg_df.student_id, 'inner')
        if output_uri is not None:
            students_df_with_avg_grades.write.mode('overwrite').csv(output_uri)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--partitions', default=2, type=int, help="The number of parallel partitions to use when calculating averages.")
    parser.add_argument('--students', help="The URI where the students input file is located")
    parser.add_argument('--grades', help="The URI where the grades input file is located")
    # parser.add_argument('--lessons', help="The URI where the lessons input file is located")
    parser.add_argument('--output_uri', help="The URI where output is saved, typically an S3 bucket.")
    args = parser.parse_args()

    students(args.partitions, args.students, args.grades, args.output_uri)