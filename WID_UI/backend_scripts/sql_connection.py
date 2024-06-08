from sqlalchemy import create_engine
import pymysql
import os
import json
import pandas as pd
import numpy as np

class SQLConnection():
    def __init__(self):
        try:
            with open('/home/ubuntu/WID_Project/secrets.json') as secrets_file:
                secrets = json.load(secrets_file)
        except:
            try:
                with open('WID_UI/local_secrets.json') as secrets_file:
                    secrets = json.load(secrets_file)
            except: 
                raise Exception("Secrets file not found.")
        host = secrets['host']
        user = secrets['user']
        password = secrets['password']
        port = int(secrets['port'])
        db = secrets['database']
        self.engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{db}')
        self.conn = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db)
        self.cur = self.conn.cursor()

    def sql_query(self, query, params=None):
        if params is None:
            return self.cur.execute(query)
        else:
            return self.cur.execute(query, params)

    def df_to_sql(self, df, table_name, delete_records=False, deletion_col=None):
        if delete_records:
            self.delete_records(df, deletion_col, table_name)
        self.upsert_df(df, table_name)

    def delete_records(self, df, deletion_col, table_name):
        # Step 1: Extract unique values from the specified deletion column and format them for SQL
        unique_values = list(df[deletion_col].astype(str).unique())
        formatted_values = ', '.join([f"'{value}'" for value in unique_values])

        # Step 2: Construct and execute the deletion query using the dynamic column name
        deletion_query = f"DELETE FROM {table_name} WHERE {deletion_col} IN ({formatted_values});"
        self.sql_query(deletion_query)


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

    def get_courseleaf_tracker_details(self, course_number):
        headers = ["Course_Number", "CIM_Email_Date", "Course_Title", "Request_Type", "Status", "WID_Director_Approval_Date", "WID_approval_process_notes", "Faculty_Name", "Faculty_Email", "Semester_Approved", "Syllabus_in_Drive", "Proposal_form_in_Drive", "Home_Dept", "Dept_Admin", "Dept_Admin_Email", "Cross_listed", "Academic_Year", "WID_Director"]
        query = f"""
        SELECT {','.join(headers)}
        FROM Courseleaf_Tracker
        WHERE Course_Number = %s
        """
        self.sql_query(query, (course_number,))
        result = self.cur.fetchone()
        if result is None:
            return {}
        result = {k: v for k, v in zip(headers, result)}
        return result


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
        result['Similar_Courses'] = self.get_similar_courses(course_number)
        result['Syllabus'] = self.get_syllabus(course_number)
        result['Courseleaf_Tracker'] = self.get_courseleaf_tracker_details(course_number)
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
    
    def get_similar_courses(self, course_number):
        query = """
        SELECT Similar_Course_Number, Similarity_Type
        FROM Similar_Course_Details
        WHERE Course_Number = %s
        """
        self.sql_query(query, (course_number,))
        result = self.cur.fetchall()
        if len(result) == 0:
            return []
        result = [list(x) for x in result]
        return result
    
    def get_syllabus(self, course_number):
        query = """
        SELECT Course_Syllabus_Links
        FROM Course_Syllabus
        WHERE Course_Number = %s
        """
        self.sql_query(query, (course_number,))
        result = self.cur.fetchall()
        if len(result) == 0:
            return []
        result = [x[0] for x in result]
        return result
    
    def get_instrctor_details(self, netid):
        headers = ["Instructor_netid", "Instructor_Last_Name", "Instructor_First_Name", "Instructor_Banner_Home_Org", "Instructor_College_Group", "Instructor_Department", "Instructor_Email_Address", "Instructor_Faculty_Status"]
        query = f"""
        SELECT {','.join(headers)}
        FROM Instructor_Details
        WHERE Instructor_netid = %s
        """
        self.sql_query(query, (netid,))
        result = self.cur.fetchone()
        if result is None:
            return {}
        result = {k: v for k, v in zip(headers, result)}
        return result

    def get_section_details(self, course_id):
        headers = ["COURSE_ID", "Course_Term_Code", "Course_Number", "CRN", "Course", "Section_Title", "Section_Number", "Schedule_Type_Desc", "Section_Credit_Hours", "Max_Enrollment", "Instructor_netid", "Variable_Credits", "Course_Status_Desc", "Section_Status_Desc", "Course_College_Desc", "Actual_Enrollment", "Seats_Available", "CrossList_ID", "Cross_List_Max", "Cross_List_Actual", "Course_Link_Identifier"]
        query = f"""
        SELECT {','.join(headers)}
        FROM Course_Section_Information
        WHERE COURSE_ID = %s
        """
        self.sql_query(query, (course_id,))
        result = self.cur.fetchone()
        result = {k: v for k, v in zip(headers, result)}
        result['CrossListed_Courses'] = self.get_cross_listed_courses(result['CrossList_ID'])
        result['Instructor_Details'] = self.get_instrctor_details(result['Instructor_netid'])
        result['GA_Details'] = self.get_GA_details(course_id)
        result['PWP_Details'] = self.get_PWP_info(course_id)
        return result
    
    def get_GA_info(self, netid):
        headers = ["GA_First_Name", "GA_Last_Name", "GA_Net_ID"]
        query = f"""
        SELECT {','.join(headers)}
        FROM GA_Details
        WHERE GA_Net_ID = %s
        """
        self.sql_query(query, (netid,))
        result = self.cur.fetchone()
        result = {k: v for k, v in zip(headers, result)}
        return result
    
    def get_GA_details(self, course_id):
        headers = ["COURSE_ID", "Course_Term_Code", "CRN", "GA_Type", "GA_Net_ID", "Home_School", "Home_Dept", "Hour_Assignment"]
        query = f"""
        SELECT {','.join(headers)}
        FROM GA_Registration
        WHERE COURSE_ID = %s
        """
        self.sql_query(query, (course_id,))
        result = self.cur.fetchone()
        print(result)
        if result is None:
            return {}
        result = {k: v for k, v in zip(headers, result)}
        GA_deatils = self.get_GA_info(result['GA_Net_ID'])
        GA_deatils.update(result)
        return GA_deatils
    
    def update_record(self, table_name, primary_column, primary_value, change_field, changed_value):
        query = f"""
        UPDATE {table_name}
        SET {change_field} = %s
        WHERE {primary_column} = %s
        """
        self.sql_query(query, (changed_value, primary_value))
        self.conn.commit()

    def get_GA_history(self, ga_netid="", name=""):
        headers = ["COURSE_ID", "GA_Net_ID", "Course_Term_Code", "CRN", "GA_Type", "Home_School", "Home_Dept", "Hour_Assignment"]
        if ga_netid:
            query = f"""
            SELECT {','.join(headers)}
            FROM GA_Registration
            WHERE GA_Net_ID = %s
            """
            print(query)
            self.sql_query(query, (ga_netid,))
        elif name:
            name = f"%{name}%"
            query = f"""
            SELECT {','.join(headers)}
            FROM GA_Registration
            WHERE GA_Net_ID IN (SELECT GA_Net_ID
                FROM GA_Details 
                WHERE CONCAT(GA_First_Name, ' ', GA_Last_Name) LIKE %s OR 
                    CONCAT(GA_Last_Name, ' ', GA_First_Name) LIKE %s)
            """
            print(query)
            self.sql_query(query, (name, name))
        result = self.cur.fetchall()
        result = [{k: v for k, v in zip(headers, x)} for x in result]
        for i in range(len(result)):
            GA_deatils = self.get_GA_info(result[i]['GA_Net_ID'])
            GA_deatils.update(result[i])
            result[i] = GA_deatils
        return result
    
    def get_PWP_info(self, course_id):
        headers = ["PWP_Hours"]
        query = f"""
        SELECT {','.join(headers)}
        FROM PWP_Registration
        WHERE COURSE_ID = %s
        """
        self.sql_query(query, (course_id,))
        result = self.cur.fetchone()
        if result is None:
            return {}
        result = {k: v for k, v in zip(headers, result)}
        result_set = {}
        result_set['PWP_Assigned'] = True
        result_set.update(result)
        return result_set

        
if __name__=="__main__":
    sql = SQLConnection()
    # print(sql.fetch_total_enrollment(2023))
    # print(sql.fetch_total_seats(2023))
    # print(sql.fetch_total_courses(2023))
    # print(sql.fetch_total_sections(2023))
    # print(sql.get_course_details('AH 2132W'))
    # print(sql.get_cross_listed_courses('201403_GI'))
    # df = pd.read_csv('/Users/amitshendge/Downloads/Writing In Decipline Sheets/web crawler/acourse_leaf_data.csv')
    # print(df[['Equivalent Courses','Formerly Known']])
    # print(df.columns)
    # sql.delete_records(df, 'Course Number', 'Similar_Course_Details')
    # print(sql.get_section_details('201403_82243'))
    # sql.update_record('Course_Information', 'Course_Number', 'AH 2001W', 'Course_Title', 'Short Course Title')
    print(sql.get_GA_history(name='Alice'))
    sql.close_conn()