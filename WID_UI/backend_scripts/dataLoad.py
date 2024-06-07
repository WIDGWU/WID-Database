import pandas as pd
from .sql_connection import SQLConnection
import numpy as np

class Data_Load():
    def __init__(self):
        self.sql_opertions = SQLConnection()

    def read_data(self, data):
        if isinstance(data, str):
            if data.endswith('.csv'):
                df = pd.read_csv(data)
            elif data.endswith('.xlsx'):
                df = pd.read_excel(data)
            return df
        elif isinstance(data, pd.DataFrame):
            return data
        
    def new_column_names(self, df):
        new_col = []
        for i in df.columns:
            new_col.append(i.replace(' ','_'))
        df.columns = new_col
        
    def extract_course_syllabus(self, input_df, output_df, static_column, dynamic_column):
        for i in input_df.iterrows():
            if i[1][dynamic_column] != '[]':
                if isinstance(i[1][dynamic_column], str):
                    for j in eval(i[1][dynamic_column]):
                        output_df.loc[len(output_df)] = [i[1][static_column], j]
                elif isinstance(i[1][dynamic_column], list):
                    for j in i[1][dynamic_column]:
                        output_df.loc[len(output_df)] = [i[1][static_column], j]

    def extract_similar_course_details(self, input_df, output_df, static_column):
        for i in input_df.iterrows():
            if i[1]['Formerly Known']:
                if pd.notna(i[1]['Formerly Known']):
                    for k in i[1]['Formerly Known'].split('/'):
                        output_df.loc[len(output_df)] = [i[1][static_column], k.strip(), 'Formerly Known']
            if i[1]['Equivalent Courses']:
                if pd.notna(i[1]['Equivalent Courses']):
                    for k in i[1]['Equivalent Courses'].split('\n'):
                        output_df.loc[len(output_df)] = [i[1][static_column], k.split('-')[0].strip(), 'Equivalent Course']

    def load_course_leaf(self, data):
        df = self.read_data(data)
        df.rename(columns={"Attribute 1":"University general education","Attribute 2":"CCAS general education","Attribute 3":"Honors","Attribute 4":"Elliott School of International Affairs","Attribute 5":"Other"}, inplace=True)
        Course_Information = ["Course Number","Course Title","Last Approved Date","Last Edit Date","Long Course Title","Short Course Title","Effective Term","Comments","Reviewer Comments","Status Head","University general education","CCAS general education","Honors","Elliott School of International Affairs","Other"]
        Similar_Course_Details = ["Course Number","Similar_Course_Number","Similarity_Type"]
        Course_Syllabus = ["Course Number","Course Syllabus Links"]

        df.drop_duplicates(subset=['Course Number'], keep='first', inplace=True)
        Course_Information_df = df[Course_Information]
        Course_Syllabus_df = pd.DataFrame(columns=Course_Syllabus)
        Similar_Course_Details_df = pd.DataFrame(columns=Similar_Course_Details)
        self.extract_course_syllabus(df, Course_Syllabus_df,'Course Number','Course Syllabus Links')
        self.extract_similar_course_details(df, Similar_Course_Details_df,'Course Number')
        self.new_column_names(Course_Information_df)
        self.new_column_names(Course_Syllabus_df)
        self.new_column_names(Similar_Course_Details_df)
        
        self.sql_opertions.upsert_df(Course_Information_df, 'Course_Information')
        self.sql_opertions.df_to_sql(df=Course_Syllabus_df, table_name='Course_Syllabus',delete_records=True,deletion_col='Course_Number')
        self.sql_opertions.df_to_sql(df=Similar_Course_Details_df, table_name='Similar_Course_Details', delete_records=True, deletion_col='Course_Number')
        self.sql_opertions.close_conn()
        print("Data loaded successfully")

    def load_registerar_data(self, data):
        df_registrar = self.read_data(data)
        df_registrar.rename(columns={"Course Reference Number (CRN)":"CRN"}, inplace=True)
        df_registrar.dropna(subset=['CRN'], inplace=True)
        df_registrar['Course Number'] = df_registrar['Subject Code'] + " " + df_registrar['Course Number'].astype(str)
        df_registrar['Instructor_netid'] = df_registrar['Instructor Email Address'].apply(lambda x: x.split('@')[0] if pd.notna(x) else np.NaN)
        df_registrar['CRN'] = df_registrar['CRN'].astype(int).astype(str)
        float_columns = df_registrar.select_dtypes(include=['float']).columns
        df_registrar[float_columns] = df_registrar[float_columns].fillna(0)
        df_registrar[float_columns] = df_registrar[float_columns].astype(int).astype(str)
        Course_Section_Information = ["COURSE_ID","Course Term Code","Course Number","CRN","Course","Section Title","Section Number","Schedule Type Desc","Section Credit Hours","Max Enrollment","Instructor_netid","Variable Credits","Course Status Desc","Section Status Desc","Course College Desc","Actual Enrollment","Seats Available","CrossList_ID","Cross List Max","Cross List Actual","Course Link Identifier"]
        Instructor_Details = ["Instructor Last Name","Instructor First Name","Instructor_netid", "Instructor Banner Home Org","Instructor College Group","Instructor Department","Instructor Email Address","Instructor Faculty Status"]
        Cross_Listed_Course_Details = ["CrossList_ID","COURSE_ID","Cross List Group"]

        df_registrar['COURSE_ID'] = df_registrar['Course Term Code']+'_'+df_registrar['CRN']
        df_registrar['CrossList_ID'] = df_registrar.apply(lambda x: x['Course Term Code']+'_'+x['Cross List Group'] if pd.notna(x['Cross List Group']) else np.NaN, axis=1)
        Course_Section_Information_df = df_registrar[Course_Section_Information]
        Instructor_Details_df = df_registrar[Instructor_Details].dropna(subset=['Instructor Email Address']).drop_duplicates(subset=['Instructor Email Address'])
        Cross_Listed_Course_Details_df = df_registrar[Cross_Listed_Course_Details].dropna(subset=['CrossList_ID'])

        self.new_column_names(Course_Section_Information_df)
        self.new_column_names(Instructor_Details_df)
        self.new_column_names(Cross_Listed_Course_Details_df)
        Course_Section_Information_df.drop_duplicates(keep='first', inplace=True)

        self.sql_opertions.upsert_df(Instructor_Details_df, 'Instructor_Details')
        self.sql_opertions.upsert_df(Cross_Listed_Course_Details_df, 'Cross_Listed_Course_Details')
        self.sql_opertions.upsert_df(Course_Section_Information_df, 'Course_Section_Information')
        self.sql_opertions.close_conn()
        print("Data loaded successfully")

    def load_GA_data(self, file_path):
        df = self.read_data(file_path)
        df.dropna(subset='CRN',inplace=True)
        df['COURSE_ID'] = df['Course Term Code'].astype(str) + '_' + df['CRN'].astype(str)
        self.new_column_names(df)
        self.sql_opertions.df_to_sql(df=df[['COURSE_ID', 'Course_Term_Code', 'CRN', 'GA_Type',
       'GA_Net_ID', 'Home_School', 'Home_Dept', 'Hour_Assignment']], table_name='GA_Registration', delete_records=True, deletion_col='COURSE_ID')
        
        self.sql_opertions.upsert_df(df[['GA_Net_ID', 'GA_Last_Name', 'GA_First_Name']].drop_duplicates().dropna(subset='GA_Net_ID'), 'GA_Details')
        self.sql_opertions.close_conn()

    def load_PWP_data(self, file_path):
        PWP_cols = ['Course Term Code', 'CRN', 'PWP Hours']
        df = self.read_data(file_path)[PWP_cols]
        df.dropna(subset=['Course Term Code', 'CRN'],inplace=True)
        df['COURSE_ID'] = df['Course Term Code'].astype(str) + '_' + df['CRN'].astype(str)
        self.new_column_names(df)
        self.sql_opertions.upsert_df(df, 'PWP_Registration')
        self.sql_opertions.close_conn()
        
    def load_courseleaf_tracker(self, file_path):
        df = self.read_data(file_path)
        self.new_column_names(df)
        df.rename(columns={"Course_Code":"Course_Number","Faculty_Name_(Last,_First)":"Faculty_Name",
                           "Semester_Approved_(TERM_YEAR)":"Semester_Approved", "Syllabus_in_Drive?":"Syllabus_in_Drive",
                           "Proposal_form_in_Drive?":"Proposal_form_in_Drive", "Dept._Admin":"Dept_Admin",
                           "Dept._Admin_Email":"Dept_Admin_Email", "Cross-listed_(1)":"Cross_listed","Home_Dept.":"Home_Dept",
                           "Academic_Year_(Format:_AY_YYYY-YY)":"Academic_Year"}, inplace=True)
        df.drop_duplicates(subset=['Course_Number'], keep='first', inplace=True)
        self.sql_opertions.upsert_df(df, 'Courseleaf_Tracker')
        self.sql_opertions.close_conn()


if __name__ == '__main__':
    import time
    t1 = time.time()
    data_load = Data_Load()
    data_load.load_course_leaf('/Users/amitshendge/Downloads/Writing In Decipline Sheets/data_files/courseLeaf_complete _data.csv')
    data_load = Data_Load()
    data_load.load_registerar_data('/Users/amitshendge/Downloads/Writing In Decipline Sheets/data_files/WID courses Fall 2014-Spr 2024 all fields (1).xlsx')
    data_load = Data_Load()
    data_load.load_GA_data('/Users/amitshendge/Downloads/Writing In Decipline Sheets/data_files/Copy of WID GA Database Upload Spreadsheet.xlsx')
    data_load = Data_Load()
    data_load.load_PWP_data('/Users/amitshendge/Downloads/Writing In Decipline Sheets/data_files/Copy of PWP Database Upload Spreadsheet.xlsx')
    data_load = Data_Load()
    data_load.load_courseleaf_tracker('/Users/amitshendge/Downloads/Writing In Decipline Sheets/data_files/Copy of  CourseLeaf TRACKER.xlsx')
    t2 = time.time()
    print(f"Time taken: {t2-t1} seconds")