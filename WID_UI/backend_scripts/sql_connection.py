from sqlalchemy import create_engine
import pymysql
import os
from dotenv import load_dotenv
load_dotenv()
import pandas as pd
import numpy as np

class SQLConnection():
    def __init__(self):
        host = os.getenv('host')
        user = os.getenv('user')
        password = os.getenv('password')
        port = int(os.getenv('port'))
        db = os.getenv('database')
        self.engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{db}')
        self.conn = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db)
        self.cur = self.conn.cursor()

    def sql_query(self, query, params=None):
        if params is None:
            return self.cur.execute(query)
        else:
            return self.cur.execute(query, params)

    def df_to_sql(self, df, table_name):
        self.sql_query(f"SELECT 1 FROM {table_name} LIMIT 1;")
        df.to_sql(table_name, con=self.engine, if_exists='append', index=False)

    def upsert_df(self, df, table_name):
        """
        Upsert DataFrame to SQL table. It updates if the primary key exists, inserts if not.
        Arguments:
        df -- pandas DataFrame
        table_name -- str, the name of the SQL table
        primary_keys -- list of str, the columns that form the primary key
        """
        df = df.where(pd.notna(df), None)
        update_columns = df.columns
        update_statement = ", ".join([f"`{col}`=VALUES(`{col}`)" for col in update_columns])
        
        value_placeholders = ", ".join(["%s"] * len(df.columns))
        insert_statement = f"INSERT INTO `{table_name}` ({', '.join(['`' + col + '`' for col in df.columns])}) VALUES ({value_placeholders}) ON DUPLICATE KEY UPDATE {update_statement};"
        data = [tuple(x) for x in df.to_records(index=False)]
        cur = self.conn.cursor()
        cur.executemany(insert_statement, data)
        self.conn.commit()

    def close_conn(self):
        self.conn.close()

    def fetch_total_enrollment(self, year):
        year = int(year)
        # Prepare the SQL query to fetch the sum of Actual_Enrollment for the specified academic year
        query = """
        SELECT SUM(CAST(Actual_Enrollment AS UNSIGNED)) AS Total_Enrollment
        FROM Course_Section_Information
        WHERE Course_Term_Code IN (%s, %s, %s)
        """

        # Set the term codes for fall of the current year and spring and summer of the next year
        summer_term_code = f'{year}02'
        fall_term_code = f'{year}03'
        spring_term_code = f'{year + 1}01'
        # Execute the query
        self.sql_query(query, (fall_term_code, spring_term_code, summer_term_code))
        result = self.cur.fetchone()
        # Check if result is not None
        total_enrollment = result[0] if result and result[0] is not None else 0
        return int(total_enrollment)

    def fetch_total_seats(self, year):
        year = int(year)
        # Prepare the SQL query to fetch the sum of Actual_Enrollment for the specified academic year
        query = """
        SELECT SUM(seats) AS Total_Seats
        FROM (
            SELECT Max_Enrollment AS seats
            FROM Course_Section_Information
            WHERE CrossList_ID IS NULL AND Course_Term_Code IN (%s, %s, %s)
            UNION ALL
            SELECT MAX(CAST(Cross_List_Max AS UNSIGNED)) AS seats
            FROM Course_Section_Information
            WHERE CrossList_ID IS NOT NULL AND Course_Term_Code IN (%s, %s, %s)
            GROUP BY CrossList_ID
        ) AS available_seats
        """

        # Set the term codes for fall of the current year and spring and summer of the next year
        summer_term_code = f'{year}02'
        fall_term_code = f'{year}03'
        spring_term_code = f'{year + 1}01'

        # Execute the query
        self.sql_query(query, (fall_term_code, spring_term_code, summer_term_code, fall_term_code, spring_term_code, summer_term_code))
        result = self.cur.fetchone()
        # Check if result is not None
        total_seats = result[0] if result and result[0] is not None else 0
        return int(total_seats)

    def fetch_total_sections(self, year):
        year = int(year)
        # Prepare the SQL query to fetch the sum of Actual_Enrollment for the specified academic year
        query = """
        SELECT COUNT(*) AS Total_Sections
        FROM Course_Section_Information
        WHERE Course_Term_Code IN (%s, %s, %s)
        """

        # Set the term codes for fall of the current year and spring and summer of the next year
        summer_term_code = f'{year}02'
        fall_term_code = f'{year}03'
        spring_term_code = f'{year + 1}01'

        # Execute the query
        self.sql_query(query, (fall_term_code, spring_term_code, summer_term_code))
        result = self.cur.fetchone()
        # Check if result is not None
        total_sections = result[0] if result and result[0] is not None else 0

        return int(total_sections)
    
    def fetch_total_courses(self, year):
        year = int(year)
        # Prepare the SQL query to fetch the sum of Actual_Enrollment for the specified academic year
        query = """
        SELECT COUNT(DISTINCT Course_Number) AS Total_Courses
        FROM Course_Section_Information
        WHERE Course_Term_Code IN (%s, %s, %s)
        """

        # Set the term codes for fall of the current year and spring and summer of the next year
        summer_term_code = f'{year}02'
        fall_term_code = f'{year}03'
        spring_term_code = f'{year + 1}01'

        # Execute the query
        self.sql_query(query, (fall_term_code, spring_term_code, summer_term_code))
        result = self.cur.fetchone()
        # Check if result is not None
        total_courses = result[0] if result and result[0] is not None else 0
        return int(total_courses)

    def get_course_details(self, course_number):
        headers = ["Course_Number","Course_Title","Last_Approved_Date","Last_Edit_Date","Long_Course_Title","Short_Course_Title",
                   "Effective_Term","Comments","Reviewer_Comments","Status_Head","University_general_education","CCAS_general_education",
                   "Honors","Elliott_School_of_International_Affairs","Other"]
        query = f"""
        SELECT {','.join(headers)}
        FROM Course_Information
        WHERE Course_Number = %s
        """
        self.sql_query(query, (course_number,))
        result = self.cur.fetchone()
        result = {k: v for k, v in zip(headers, result)}
        return result
    
    def get_cross_listed_courses(self, crosslist_id):
        query = """
        SELECT COURSE_ID
        FROM Cross_Listed_Course_Details
        WHERE CrossList_ID = %s
        """
        self.sql_query(query, (crosslist_id,))
        result = self.cur.fetchall()
        result = [x[0] for x in result]
        return result

if __name__=="__main__":
    sql = SQLConnection()
    # print(sql.fetch_total_enrollment(2023))
    # print(sql.fetch_total_seats(2023))
    # print(sql.fetch_total_courses(2023))
    # print(sql.fetch_total_sections(2023))
    # print(sql.get_course_details('AH 2132W'))
    # print(sql.get_cross_listed_courses('201403_GI'))
    sql.close_conn()