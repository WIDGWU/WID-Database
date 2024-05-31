from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
from .dataLoad import Data_Load

class GWUCourseCrawler:
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")

        service = Service(ChromeDriverManager().install(), options=chrome_options)
        self.driver = webdriver.Chrome(service=service)
        self.driver.get("http://next.bulletin.gwu.edu/courseadmin")

    def close(self):
        self.driver.close()
        
    # Find Element Functions
    def _element_by_id_send_keys(self, element_id, keys, enter=False):
        element = self.driver.find_element(By.ID, element_id)
        element.clear()
        element.send_keys(keys)
        if enter:
            element.send_keys(Keys.ENTER)

    def _element_by_id_click(self, element_id):
        element = self.driver.find_element(By.ID, element_id)
        time.sleep(1)
        element.click()

    def _element_by_xpath_click(self, xpath, class_name=None):
        if class_name:
            element = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{xpath}')]").find_element(By.CLASS_NAME, class_name)
        else:
            element = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{xpath}')]")
        return element

    def data_from_grid(self, xpath):
        return '\n'.join(self._element_by_xpath_click(xpath).find_element(By.XPATH,'..').find_element(By.XPATH,'..').text.split("\n")[1:]).strip()

    def log_in_page(self):
        if "Web Single Sign-on" in self.driver.page_source:
            print(self.driver.page_source)
            self._element_by_id_send_keys("username", "G26933631")
            time.sleep(1)
            self._element_by_id_send_keys("password", "GRandAMi123@", True)

    def accept_terms(self):
        if "The George Washington University Web Single Signon Terms of Use" in self.driver.page_source:
            self.driver.find_element(By.ID, "accept").click()
            time.sleep(1)
            self.driver.find_element(By.NAME, "_eventId_proceed").click()
            time.sleep(1)
            self.driver.find_element(By.NAME, "_eventId_proceed").click()

    def Please_complete_log_in(self):
        try:
            if "In order to authorize your ability to update, please click the icon to complete your log in." in self.driver.page_source:
                self.driver.find_element(By.ID, "loginuser").send_keys(Keys.ENTER)
                print("Please complete log in and press enter")
        except:
            print("Log in already completed")

    def search_for_course(self):
        if "Search, edit, add, and deactivate courses." in self.driver.page_source:
            self._element_by_id_send_keys("search_field","*W")
            time.sleep(1)
            self._element_by_id_click("search_button")

    def search_course(self, course_code):
        if "Search, edit, add, and deactivate courses." in self.driver.page_source:
            self._element_by_id_send_keys("search_field",course_code)
            time.sleep(1)
            self._element_by_id_click("search_button")

    def get_all_courses(self, sleep_time=30):
        time.sleep(sleep_time)
        my_table = self.driver.find_element(By.ID, "queryresults")
        list_of_courses = my_table.find_elements(By.TAG_NAME, "tr")
        list_of_courses = list_of_courses[1:]
        print("Total Courses:",len(list_of_courses))
        return list_of_courses

    def store_df_course_list(self, list_of_courses):
        courses_list = []
        for row in list_of_courses:
            courses_list.append([i.text for i in row.find_elements(By.TAG_NAME, "td")])
        df = pd.DataFrame(courses_list, columns=["Course Code", "Title", "Effective Term", "Workflow", "Status"])
        df.to_csv("/Users/amitshendge/Downloads/Writing In Decipline Sheets/web crawler/courses.csv", index=False)
        print("Courses stored in courses.csv")
        return df

    #data retrival
    def get_course_num_title(self):
        try:
            viewing =self._element_by_xpath_click('Viewing:', 'course_number')
            title = viewing.text
            for i in viewing.find_elements(By.TAG_NAME, "span"):
                if i.get_attribute("class") == "diffdeleted":
                    title = title.replace(" " + i.text + " ", " ")
            return title.split(" : ")
        except:
            return ['','']

    def get_formerly_known(self):
        try:
            former_name = self._element_by_xpath_click('Formerly known as:', 'course_number')
            title = former_name.text
            return title
        except:
            return ''

    def get_course_file_links(self):
        return [i.get_attribute('href') for i in self._element_by_xpath_click('Course syllabus').find_element(By.XPATH,'..').find_element(By.XPATH,'..').find_elements(By.CLASS_NAME,'uploadlink') if i.get_attribute('href')]

    def get_attribute_categories(self):
        return [i.text.split("\n")[1] if len(i.text.split("\n"))>1 else '' for i in self._element_by_xpath_click('Attribute Categories').find_element(By.XPATH,'..').find_element(By.XPATH,'..').find_element(By.XPATH,'..').find_elements(By.CLASS_NAME, 'row')[1:]]

    def get_all_fields(self):
        Course_number, Course_title = self.get_course_num_title()
        Formerly_known = self.get_formerly_known()
        try:
            Last_approved_dt = self._element_by_xpath_click('Last approved:', 'timestamp').text
        except:
            Last_approved_dt = ''
        
        try:
            Last_edit_dt = self._element_by_xpath_click('Last edit:', 'timestamp').text
        except:
            Last_edit_dt = ''
        Long_course_title = self.data_from_grid('Long course title')
        Short_course_title = self.data_from_grid('Short course title')
        Effective_term = self.data_from_grid('In which academic term will the requested action take effect?')
        Equivalent_coursses = self.data_from_grid('Is this course equivalent to any other course(s)?')
        Course_syllabus_lins = self.get_course_file_links()
        Atr1, Atr2, Atr3, Atr4, Atr5 = self.get_attribute_categories()
        Comments = self.data_from_grid('Comments')
        Reviewer_comments = self.data_from_grid('Reviewer Comments')
        statushead = '\n'.join([i.text for i in self.driver.find_elements(By.CLASS_NAME, 'statushead')])

        return [Course_number, Course_title, Formerly_known, Last_approved_dt, Last_edit_dt, Long_course_title, Short_course_title, Effective_term, 
        Equivalent_coursses, Course_syllabus_lins, Atr1, Atr2, Atr3, Atr4, Atr5, Comments, Reviewer_comments, statushead]

    def get_selected_courses(self, course_codes):
        global list_of_courses
        self.log_in_page()
        print("Logged in successfully")
        time.sleep(1)
        self.accept_terms()
        time.sleep(1)
        self.Please_complete_log_in()
        time.sleep(1)
        Course_leaf_data = []
        for course_code in course_codes:
            self.search_course(course_code)
            time.sleep(1)
            list_of_courses = self.get_all_courses(5)
            time.sleep(1)
            for course in list_of_courses:
                course.click()
                time.sleep(1)
                Course_leaf_data.append(self.get_all_fields())
        course_leaf_df = pd.DataFrame(Course_leaf_data, columns=["Course Number", "Course Title", "Formerly Known", "Last Approved Date", "Last Edit Date", "Long Course Title", "Short Course Title", "Effective Term", "Equivalent Courses", "Course Syllabus Links", "Attribute 1", "Attribute 2", "Attribute 3", "Attribute 4", "Attribute 5", "Comments", "Reviewer Comments", "Status Head"])
        Data_Load().load_course_leaf(course_leaf_df)
        # course_leaf_df.to_csv(f"/Users/amitshendge/Downloads/Writing In Decipline Sheets/web crawler/acourse_leaf_data.csv", index=False)

        print(f"Course Leaf Data stored in DB successfully")
        self.close()

if __name__ == "__main__":
    web_scraper = GWUCourseCrawler()
    web_scraper.get_selected_courses(['AH 2001W', 'AH 2109W'])