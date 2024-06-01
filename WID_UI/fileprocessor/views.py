import json
from django.shortcuts import render
from django.http import HttpResponse
from .forms import UploadFileForm
from backend_scripts.file_operations import file_ops
from backend_scripts.reports import WID_Reports
from backend_scripts.dataLoad import Data_Load
from backend_scripts.web_crawler_select_course import GWUCourseCrawler
from backend_scripts.sql_connection import SQLConnection
from rest_framework.decorators import api_view

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

@api_view(['POST'])
def wid_annual_report(request):
    body = json.loads(request.body)
    output = WID_Reports().fetch_annual_report(body['year'])
    return HttpResponse(json.dumps(output), content_type='application/json')

@api_view(['POST'])
def wid_5y_report(request):
    body = json.loads(request.body)
    output = WID_Reports().fetch_five_year_report(body['year'])
    return HttpResponse(json.dumps(output), content_type='application/json')

@api_view(['POST'])
def scrape_course_leaf(request):
    body = json.loads(request.body)
    web_scraper = GWUCourseCrawler()
    web_scraper.get_selected_courses(body['Course_Numbers'])
    return HttpResponse(json.dumps({"Body":"Data Loaded Successfully in DB for given Course Numbers."}), content_type='application/json')

@api_view(['POST'])
def load_registrar(request):
    body = json.loads(request.body)
    data_loader = Data_Load()
    data_loader.load_registerar_data(body['file_path'])
    return HttpResponse(json.dumps({"Body":"Data Loaded Successfully in DB."}), content_type='application/json')

@api_view(['POST'])
def get_course_details(request):
    body = json.loads(request.body)
    sql_conn = SQLConnection()
    result = sql_conn.get_course_details(body['course_number'])
    return HttpResponse(json.dumps(result), content_type='application/json')

@api_view(['POST'])
def get_cross_listed(request):
    body = json.loads(request.body)
    sql_conn = SQLConnection()
    result = sql_conn.get_cross_listed_courses(body['crosslist_id'])
    return HttpResponse(json.dumps(result), content_type='application/json')


