"""
URL configuration for WID_UI project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path
from fileprocessor import views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="API Documentation",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@yourapi.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # path('upload/', views.upload_file, name='upload_file'),
    path('scrape_course_leaf/', views.scrape_course_leaf, name='scrape_course_leaf'),
    path('annual_report/', views.wid_annual_report, name='annual_report'),
    path('wid_5y_report/', views.wid_5y_report, name='wid_5y_report'),
    path('load_registrar/', views.load_registrar, name='load_registrar'),
    path('get_course_details/', views.get_course_details, name='get_course_details'),
    path('get_cross_listed/', views.get_cross_listed, name='get_cross_listed'),
    path('get_section_details/', views.get_section_details, name='get_section_details'),
    path('run_shello/', views.run_shell_command, name='run_shell_command'),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]
