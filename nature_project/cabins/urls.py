from . import views
from django.urls import path

urlpatterns = [      
    path('', views.cabins, name='cabins'),  
    path('cabin_status_/<int:cabin_id>/', views.change_status_cabin, name='cabin_status'),        
    path('create/', views.create_cabin, name='create_cabin'),     
    path('detail/<int:cabin_id>/', views.detail_cabin, name='detail_cabin'),  
    path('delete/<int:cabin_id>/', views.delete_cabin, name='delete_cabin'),  
    path('edit/<int:cabin_id>/', views.edit_cabin, name='edit_cabin'), 
]

