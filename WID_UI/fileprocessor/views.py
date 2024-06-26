import json
import urllib.parse
from django.shortcuts import render
from django.http import HttpResponse
from .forms import UploadFileForm
from backend_scripts.file_operations import file_ops
from backend_scripts.reports import WID_Reports
from backend_scripts.dataLoad import Data_Load
from backend_scripts.web_crawler_select_course import GWUCourseCrawler
from backend_scripts.sql_connection import SQLConnection
from rest_framework.decorators import api_view
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import urllib

def upload_file(request):
    file_ops_obj = file_ops()
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_path = handle_uploaded_file(request.FILES['file'])
            df, cols = file_ops_obj.registrar_file(file_path)
            print(df.head())
            print(cols)
            return render(request, 'upload_complete.html', {'df' : df.head().to_html()})
        else:
            return render(request, 'upload.html', {'form': form})
    else:
        form = UploadFileForm()
        return render(request, 'upload.html', {'form': form})

def handle_uploaded_file(f):
    file_path = 'uploaded_files/' + f.name
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path

def course_leaf_scraper(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        return HttpResponse(f"You entered: {user_input}")
    return render(request, 'course_leaf_scraper.html')

@swagger_auto_schema(
    tags=['Reports'],
    method='get',
    manual_parameters=[
        openapi.Parameter(
            name='year',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=True,
            description='Year for which the report is to be generated. Ex: 2022',
        ),
    ]
)
@api_view(['GET'])
def wid_annual_report(request):
    year = urllib.parse.unquote(request.query_params['year'])
    output = WID_Reports().fetch_annual_report(year)
    return HttpResponse(json.dumps(output), content_type='application/json')

@swagger_auto_schema(
    tags=['Reports'],
    method='get',
    manual_parameters=[
        openapi.Parameter(
            name='year',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=True,
            description='Year for which the report is to be generated. Ex: 2022',
        ),
    ]
)
@api_view(['GET'])
def wid_5y_report(request):
    year = urllib.parse.unquote(request.query_params['year'])
    output = WID_Reports().fetch_five_year_report(year)
    return HttpResponse(json.dumps(output), content_type='application/json')

@swagger_auto_schema(
    tags=['Data Load'],
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'course_numbers': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
        },
        default={'course_numbers': ["AH 2001W","AH 2109W"]},
        required=['course_numbers'],
    )
)
@api_view(['POST'])
def scrape_course_leaf(request):
    body = json.loads(request.body)
    web_scraper = GWUCourseCrawler()
    web_scraper.get_selected_courses(body['course_numbers'])
    return HttpResponse(json.dumps({"Body":"Data Loaded Successfully in DB for given Course Numbers."}), content_type='application/json')

@swagger_auto_schema(
    tags=['Data Load'],
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'file_path': openapi.Schema(type=openapi.TYPE_STRING),
        },
        default={'file_path': 'uploaded_files/WID courses Fall 2014-Spr 2024 all fields REGISTRAR.xlsx'},
        required=['file_path'],
    )
)
@api_view(['POST'])
def load_registrar(request):
    body = json.loads(request.body)
    data_loader = Data_Load()
    data_loader.load_registerar_data(body['file_path'])
    return HttpResponse(json.dumps({"Body":"Data Loaded Successfully in DB."}), content_type='application/json')

@swagger_auto_schema(
    tags=['Get Data'],
    method='get',
    manual_parameters=[
        openapi.Parameter(
            name='course_number',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=True,
            description='Course number of the course. Ex: AH 2001W',
        ),
    ]
)
@api_view(['GET'])
def get_course_details(request):
    course_number = urllib.parse.unquote(request.query_params['course_number'])
    sql_conn = SQLConnection()
    result = sql_conn.get_course_details(course_number)
    return HttpResponse(json.dumps(result), content_type='application/json')

@swagger_auto_schema(
    tags=['Get Data'],
    method='get',
    manual_parameters=[
        openapi.Parameter(
            name='course_id',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=True,
            description='Course ID of the section. Ex: 201403_82243',
        ),
    ]
)
@api_view(['GET'])
def get_section_details(request):
    course_id = urllib.parse.unquote(request.query_params['course_id'])
    sql_conn = SQLConnection()
    result = sql_conn.get_section_details(course_id)
    return HttpResponse(json.dumps(result), content_type='application/json')


@swagger_auto_schema(
    tags=['Get Data'],
    method='get',
    manual_parameters=[
        openapi.Parameter(
            name='crosslist_id',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=True,
            description='Crosslist ID of the course. Ex: 201403_GI',
        ),
    ]
)
@api_view(['GET'])
def get_cross_listed(request):
    crosslist_id = urllib.parse.unquote(request.query_params['crosslist_id'])
    sql_conn = SQLConnection()
    result = sql_conn.get_cross_listed_courses(crosslist_id)
    return HttpResponse(json.dumps(result), content_type='application/json')

@swagger_auto_schema(
    tags=['Get Data'],
    method='get',
    manual_parameters=[
        openapi.Parameter(
            name='course_number',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=True,
            description='Course number of the course. Ex: HIST 3364W',
        ),
    ]
)
@api_view(['GET'])
def get_internal_tracker(request):
    course_number = urllib.parse.unquote(request.query_params['course_number'])
    sql_conn = SQLConnection()
    result = sql_conn.get_courseleaf_tracker_details(course_number)
    return HttpResponse(json.dumps(result), content_type='application/json')

@swagger_auto_schema(
    tags=['Server Operations'],
    method='get',
)
@api_view(['GET'])
def run_shell_command(request):
    import subprocess
    process = subprocess.Popen('sh /home/ubuntu/WID_Project/refresh_project.sh', shell=True)
    return HttpResponse(json.dumps({"Body":"Shell script executed successfully."}), content_type='application/json')

@swagger_auto_schema(
    tags=['Server Operations'],
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'secrets': openapi.Schema(type=openapi.TYPE_OBJECT),
        },
        default={'host': 'xx', 'port': '3306', 'database': 'WID', 'user': 'xx', 'password': 'xx', 'course_leaf_username':'xx', 'course_leaf_password':'xx'},
        required=['secrets'],
    )
)
@api_view(['POST'])
def set_secrets(request):
    body = json.loads(request.body)
    with open('/home/ubuntu/WID_Project/secrets.json', 'w') as f:
        json.dump(body, f)
    return HttpResponse(json.dumps({"Body":"Secrets saved successfully."}), content_type='application/json')

@swagger_auto_schema(
    tags=['Update Data'],
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'table_name': openapi.Schema(type=openapi.TYPE_STRING),
            'primary_column': openapi.Schema(type=openapi.TYPE_STRING),
            'primary_value': openapi.Schema(type=openapi.TYPE_STRING),
            'change_field': openapi.Schema(type=openapi.TYPE_STRING),
            'changed_value': openapi.Schema(type=openapi.TYPE_STRING),
        },
        default={'table_name': 'Course_Information', 'primary_column': 'Course_Number', 'primary_value': 'AH 2001W', 'change_field': 'Course_Title', 'changed_value': 'New Updated Course Title'},
        required=['table_name', 'primary_column', 'primary_value', 'change_field', 'changed_value'],
    )
)
@api_view(['POST'])
def update_record(request):
    try:
        body = json.loads(request.body)
        table_name, primary_column, primary_value, change_field, changed_value = body['table_name'], body['primary_column'], body['primary_value'], body['change_field'], body['changed_value']
        sql_conn = SQLConnection()
        sql_conn.update_record(table_name, primary_column, primary_value, change_field, changed_value)
    except Exception as e:
        return HttpResponse(json.dumps({"Error":str(e), "Error_details":str(e.with_traceback)}), content_type='application/json')
    return HttpResponse(json.dumps("Record Updated Sucessfully"), content_type='application/json')

@swagger_auto_schema(
    tags=['Get Data'],
    method='get',
    manual_parameters=[
        openapi.Parameter(
            name='ga_netid',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=False,
            description='GA NetID of the GA. Ex: abc123',
        ),
        openapi.Parameter(
            name='name',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=False,
            description='Name of the GA. Ex: John Doe',
        ),
    ]
)
@api_view(['GET'])
def get_GA_history(request):
    try:
        ga_netid = urllib.parse.unquote(request.query_params['ga_netid'])
    except:
        ga_netid = ""
    try:
        name = urllib.parse.unquote(request.query_params['name'])
    except:
        name = ""
    sql_conn = SQLConnection()
    result = sql_conn.get_GA_history(ga_netid=ga_netid, name=name)
    return HttpResponse(json.dumps(result), content_type='application/json')

@swagger_auto_schema(
    tags=['Data Load'],
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'file_path': openapi.Schema(type=openapi.TYPE_STRING),
        },
        default={'file_path': 'WID_UI/uploaded_files/Copy of WID GA Database Upload Spreadsheet.xlsx'},
        required=['file_path'],
    )
)
@api_view(['POST'])
def load_ga_registration(request):
    body = json.loads(request.body)
    data_loader = Data_Load()
    data_loader.load_GA_data(body['file_path'])
    return HttpResponse(json.dumps({"Body":"Data Loaded Successfully in DB."}), content_type='application/json')

@swagger_auto_schema(
    tags=['Data Load'],
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'file_path': openapi.Schema(type=openapi.TYPE_STRING),
        },
        default={'file_path': 'WID_UI/uploaded_files/Copy of PWP Database Upload Spreadsheet.xlsx'},
        required=['file_path'],
    )
)
@api_view(['POST'])
def load_pwp_registration(request):
    body = json.loads(request.body)
    data_loader = Data_Load()
    data_loader.load_PWP_data(body['file_path'])
    return HttpResponse(json.dumps({"Body":"Data Loaded Successfully in DB."}), content_type='application/json')

@swagger_auto_schema(
    tags=['Data Load'],
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'file_path': openapi.Schema(type=openapi.TYPE_STRING),
        },
        default={'file_path': 'WID_UI/uploaded_files/Copy of  CourseLeaf TRACKER.xlsx'},
        required=['file_path'],
    )
)
@api_view(['POST'])
def load_courseleaf_tracker(request):
    body = json.loads(request.body)
    data_loader = Data_Load()
    data_loader.load_courseleaf_tracker(body['file_path'])
    return HttpResponse(json.dumps({"Body":"Data Loaded Successfully in DB."}), content_type='application/json')