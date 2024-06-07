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
def internal_tracker(request):
    course_number = urllib.parse.unquote(request.query_params['course_number'])
    sql_conn = SQLConnection()
    result = sql_conn.get_courseleaf_tracker_details(course_number)
    return HttpResponse(json.dumps(result), content_type='application/json')

@api_view(['GET'])
def run_shell_command(request):
    import subprocess
    process = subprocess.Popen('sh /home/ubuntu/WID_Project/refresh_project.sh', shell=True)
    return HttpResponse(json.dumps({"Body":"Shell script executed successfully."}), content_type='application/json')