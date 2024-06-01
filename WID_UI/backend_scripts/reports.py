from .sql_connection import SQLConnection

class WID_Reports():
    def __init__(self):
        self.sql_opertions = SQLConnection()
    
    def fetch_annual_report(self, year):
        year = int(year)
        # Fetch current year data
        total_seats = self.sql_opertions.fetch_total_seats(year)
        total_enrollment = self.sql_opertions.fetch_total_enrollment(year)
        total_sections = self.sql_opertions.fetch_total_sections(year)
        total_courses = self.sql_opertions.fetch_total_courses(year)
        
        # Fetch previous year data
        prev_total_seats = self.sql_opertions.fetch_total_seats(year - 1)
        prev_total_enrollment = self.sql_opertions.fetch_total_enrollment(year - 1)
        prev_total_sections = self.sql_opertions.fetch_total_sections(year - 1)
        prev_total_courses = self.sql_opertions.fetch_total_courses(year - 1)
        
        # Calculate differences
        diff_seats = total_seats - prev_total_seats
        diff_enrollment = total_enrollment - prev_total_enrollment
        diff_sections = total_sections - prev_total_sections
        diff_courses = total_courses - prev_total_courses
        
        # Calculate percentage differences and round to nearest integer
        percent_seats = round((diff_seats / prev_total_seats) * 100) if prev_total_seats else 0
        percent_enrollment = round((diff_enrollment / prev_total_enrollment) * 100) if prev_total_enrollment else 0
        percent_sections = round((diff_sections / prev_total_sections) * 100) if prev_total_sections else 0
        percent_courses = round((diff_courses / prev_total_courses) * 100) if prev_total_courses else 0
        
        return {
            f'Total Seats Available for academic year {year}-{year+1}': total_seats,
            f'Total Enrolled Seats for academic year {year}-{year+1}': total_enrollment,
            f'Total Sections Available for academic year {year}-{year+1}': total_sections,
            f'Total Courses Available for academic year {year}-{year+1}': total_courses,
            f'Difference in Seats compared to previous year ({year-1}-{year})': diff_seats,
            f'Percentage change in Seats compared to previous year ({year-1}-{year})': percent_seats,
            f'Difference in Enrolled Seats compared to previous year ({year-1}-{year})': diff_enrollment,
            f'Percentage change in Enrolled Seats compared to previous year ({year-1}-{year})': percent_enrollment,
            f'Difference in Sections compared to previous year ({year-1}-{year})': diff_sections,
            f'Percentage change in Sections compared to previous year ({year-1}-{year})': percent_sections,
            f'Difference in Courses compared to previous year ({year-1}-{year})': diff_courses,
            f'Percentage change in Courses compared to previous year ({year-1}-{year})': percent_courses
        }
    
    def fetch_five_year_report(self, year):
        year = int(year)
        # Initialize dictionaries to store data for the two 5-year periods
        current_period_data = {
            'total_seats': 0,
            'total_enrollment': 0,
            'total_sections': 0,
            'total_courses': 0
        }
        previous_period_data = {
            'total_seats': 0,
            'total_enrollment': 0,
            'total_sections': 0,
            'total_courses': 0
        }
        
        # Fetch data for the current 5-year period
        for i in range(5):
            current_year = year - i
            current_period_data['total_seats'] += self.sql_opertions.fetch_total_seats(current_year)
            current_period_data['total_enrollment'] += self.sql_opertions.fetch_total_enrollment(current_year)
            current_period_data['total_sections'] += self.sql_opertions.fetch_total_sections(current_year)
            current_period_data['total_courses'] += self.sql_opertions.fetch_total_courses(current_year)
        
        # Fetch data for the previous 5-year period
        for i in range(5, 10):
            previous_year = year - i
            previous_period_data['total_seats'] += self.sql_opertions.fetch_total_seats(previous_year)
            previous_period_data['total_enrollment'] += self.sql_opertions.fetch_total_enrollment(previous_year)
            previous_period_data['total_sections'] += self.sql_opertions.fetch_total_sections(previous_year)
            previous_period_data['total_courses'] += self.sql_opertions.fetch_total_courses(previous_year)
        
        # Calculate differences
        diff_seats = current_period_data['total_seats'] - previous_period_data['total_seats']
        diff_enrollment = current_period_data['total_enrollment'] - previous_period_data['total_enrollment']
        diff_sections = current_period_data['total_sections'] - previous_period_data['total_sections']
        diff_courses = current_period_data['total_courses'] - previous_period_data['total_courses']
        
        # Calculate percentage differences and round to nearest integer
        percent_seats = round((diff_seats / previous_period_data['total_seats']) * 100) if previous_period_data['total_seats'] else 0
        percent_enrollment = round((diff_enrollment / previous_period_data['total_enrollment']) * 100) if previous_period_data['total_enrollment'] else 0
        percent_sections = round((diff_sections / previous_period_data['total_sections']) * 100) if previous_period_data['total_sections'] else 0
        percent_courses = round((diff_courses / previous_period_data['total_courses']) * 100) if previous_period_data['total_courses'] else 0
        
        return {
            f'Total Seats Available for last 5 years ({year-4}-{year})': current_period_data['total_seats'],
            f'Total Enrolled Seats for last 5 years ({year-4}-{year})': current_period_data['total_enrollment'],
            f'Total Sections Available for last 5 years ({year-4}-{year})': current_period_data['total_sections'],
            f'Total Courses Available for last 5 years ({year-4}-{year})': current_period_data['total_courses'],
            f'Difference in Seats compared to previous 5 years ({year-9}-{year-5})': diff_seats,
            f'Percentage change in Seats compared to previous 5 years ({year-9}-{year-5})': percent_seats,
            f'Difference in Enrolled Seats compared to previous 5 years ({year-9}-{year-5})': diff_enrollment,
            f'Percentage change in Enrolled Seats compared to previous 5 years ({year-9}-{year-5})': percent_enrollment,
            f'Difference in Sections compared to previous 5 years ({year-9}-{year-5})': diff_sections,
            f'Percentage change in Sections compared to previous 5 years ({year-9}-{year-5})': percent_sections,
            f'Difference in Courses compared to previous 5 years ({year-9}-{year-5})': diff_courses,
            f'Percentage change in Courses compared to previous 5 years ({year-9}-{year-5})': percent_courses
        }



if __name__=="__main__":
    reports = WID_Reports()
    print(reports.fetch_five_year_report(2023))