import pandas as pd
import os
import json

class file_ops():

    def __init__(self):
        lookup = self.read_lookup_file()
        self.registrar_cols = lookup['registrar_cols']
        self.course_leaf_cols = lookup['course_leaf_cols']
        
    def read_lookup_file(self):
        with open('lookup_file.json', 'r') as file:
            data = json.load(file)
        return data

    def read_file(self, file_path):
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        return df

    def registrar_file(self, file_path):
        self.file_path = file_path
        df = self.read_file(file_path)
        unknown_cols = self.reg_col_validations(df)
        return df, unknown_cols


    def reg_col_validations(self, df):
        col_list = df.columns
        unknown_cols = []
        for col in self.registrar_cols:
            if col not in col_list:
                unknown_cols.append(col)
        return unknown_cols
    
    def course_leaf_col_validations(self, df):
        col_list = df.columns
        unknown_cols = []
        for col in self.course_leaf_cols:
            if col not in col_list:
                unknown_cols.append(col)
        return unknown_cols

if __name__ == '__main__':
    file_path = 'data_files/test.xlsx'
    file_ops_obj = file_ops(file_path)
    df, unknown_cols = file_ops_obj.registrar_file()
    print(df.head())
    print(unknown_cols)

