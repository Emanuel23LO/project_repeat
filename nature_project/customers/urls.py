from . import views
from django.urls import path

urlpatterns = [      
    path('', views.customers, name='customers'),   
    path('customer_status_/<int:customer_id>/', views.change_status_customer, name='customer_status'),    
    path('create/', views.create_customer, name='create_customer'), 
    path('detail/<int:customer_id>/', views.detail_customer, name='detail_customer'), 
    path('delete/<int:customer_id>/', views.delete_customer, name='delete_customer'),       
    path('edit/<int:customer_id>/', views.edit_customer, name='edit_customer'),   
]
