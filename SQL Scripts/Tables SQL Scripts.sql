DROP DATABASE IF EXISTS WID;

CREATE DATABASE IF NOT EXISTS WID;

USE WID;

-- Table `GA_Details`
CREATE TABLE GA_Details (
    GA_Net_ID VARCHAR(255) PRIMARY KEY,
    GA_First_Name VARCHAR(255),
    GA_Last_Name VARCHAR(255)
);

CREATE TABLE Instructor_Details (
    Instructor_netid VARCHAR(255) PRIMARY KEY,
    Instructor_Last_Name VARCHAR(255),
    Instructor_First_Name VARCHAR(255),
    Instructor_Banner_Home_Org VARCHAR(255),
    Instructor_College_Group VARCHAR(255),
    Instructor_Department VARCHAR(255),
    Instructor_Email_Address VARCHAR(255),
    Instructor_Faculty_Status VARCHAR(255)
);


CREATE TABLE Cross_Listed_Course_Details (
    COURSE_ID VARCHAR(255) PRIMARY KEY,
    CrossList_ID VARCHAR(255),
    Cross_List_Group VARCHAR(255)
);

CREATE INDEX idx_CLCD_crosslist_id ON Cross_Listed_Course_Details(CrossList_ID);

CREATE TABLE Similar_Course_Details (
    Course_Number VARCHAR(255),
    Similar_Course_Number VARCHAR(255),
    Similarity_Type VARCHAR(255)
);

CREATE INDEX idx_SCD_course_number ON Similar_Course_Details(Course_Number);

CREATE TABLE Course_Syllabus (
    Course_Number VARCHAR(255),
    Course_Syllabus_Links TEXT
);
CREATE INDEX idx_CS_course_number ON Course_Syllabus(Course_Number);


CREATE TABLE Course_Information (
    Course_Number VARCHAR(255) PRIMARY KEY,
    Course_Title VARCHAR(255),
    Last_Approved_Date VARCHAR(255),
    Last_Edit_Date VARCHAR(255),
    Long_Course_Title VARCHAR(255),
    Short_Course_Title VARCHAR(255),
    Effective_Term VARCHAR(50),
    Comments TEXT,
    Reviewer_Comments TEXT,
    Status_Head VARCHAR(255),
    University_general_education VARCHAR(255),
    CCAS_general_education VARCHAR(255),
    Honors VARCHAR(255),
    Elliott_School_of_International_Affairs VARCHAR(255),
    Other VARCHAR(255)
);

CREATE TABLE Course_Section_Information (
    COURSE_ID VARCHAR(255) PRIMARY KEY,
    Course_Term_Code VARCHAR(50),
    Course_Number VARCHAR(50),
    CRN VARCHAR(255),
    Course VARCHAR(255),
    Section_Title VARCHAR(255),
    Section_Number VARCHAR(50),
    Schedule_Type_Desc VARCHAR(255),
    Section_Credit_Hours VARCHAR(255),
    Max_Enrollment VARCHAR(255),
    Instructor_netid VARCHAR(255),
    Variable_Credits VARCHAR(255),
    Course_Status_Desc VARCHAR(255),
    Section_Status_Desc VARCHAR(255),
    Course_College_Desc VARCHAR(255),
    Actual_Enrollment VARCHAR(255),
    Seats_Available VARCHAR(255),
    CrossList_ID VARCHAR(255),
    Cross_List_Max VARCHAR(255),
    Cross_List_Actual VARCHAR(255),
    Course_Link_Identifier VARCHAR(255)
);

-- Table `GA_Registration`
CREATE TABLE GA_Registration (
    COURSE_ID VARCHAR(255),
    Course_Term_Code VARCHAR(255),
    CRN VARCHAR(255),
    GA_Net_ID VARCHAR(255),
    GA_Type VARCHAR(255),
    Home_School VARCHAR(255),
    Home_Dept VARCHAR(255),
    Hour_Assignment VARCHAR(255)
);

-- Table `PWP_Registration`
CREATE TABLE PWP_Registration (
    COURSE_ID VARCHAR(255) PRIMARY KEY,
    Course_Term_Code VARCHAR(255),
    CRN VARCHAR(255),
    PWP_Hours VARCHAR(255)
);

-- Table `Courseleaf_Tracker`
CREATE TABLE Courseleaf_Tracker (
    Course_Number VARCHAR(255) PRIMARY KEY,
    CIM_Email_Date VARCHAR(255),
    Course_Title VARCHAR(255),
    Request_Type VARCHAR(255),
    Status VARCHAR(255),
    WID_Director_Approval_Date VARCHAR(255),
    WID_approval_process_notes TEXT,
    Faculty_Name VARCHAR(255),
    Faculty_Email VARCHAR(255),
    Semester_Approved VARCHAR(255),
    Syllabus_in_Drive VARCHAR(255),
    Proposal_form_in_Drive VARCHAR(255),
    Home_Dept VARCHAR(255),
    Dept_Admin VARCHAR(255),
    Dept_Admin_Email VARCHAR(255),
    Cross_listed VARCHAR(255),
    Academic_Year VARCHAR(255),
    WID_Director VARCHAR(255)
);


