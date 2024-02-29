from . import views
from django.urls import path

urlpatterns = [      
    path('', views.services, name='services'),
    path('service_status_/<int:service_id>/', views.change_status_service, name='service_status'),        
    path('create/', views.create_service, name='create_service'),
    path('detail/<int:service_id>/', views.detail_service, name='detail_service'),  
    path('delete/<int:service_id>/', views.delete_service, name='delete_service'),
    path('edit/<int:service_id>/', views.edit_service, name='edit_service'),   
]
