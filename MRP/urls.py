from django.urls import path
from .views import  *

urlpatterns = [
    path('', HomePage, name = 'home-page'),
    path('register/', Register, name = 'register-page'),
    path('file/', FileUpLoad, name = 'file-up-load'),
    path('material/', Material, name = 'material-page'),
    path('addmaterial/', AddMaterial, name = 'add-material'),
    path('3wkloading/', WeekLoad, name = 'week-loading'),
    path('planning/', Planning, name = 'planning-page'),
    path('actualusage/', ActualUsage, name = 'actual-page'),
    path('eoqboq/', EoqBoq, name = 'eoqboq-page'),
    path('dashboard/', DashBoard, name = 'dashboard-page'),
    path('material/update/<str:part_num>/', UpdateMaterial, name = 'update-page')

    

]