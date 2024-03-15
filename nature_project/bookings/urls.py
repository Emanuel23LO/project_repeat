from . import views
from django.urls import path

urlpatterns = [      
    path('', views.bookings, name='bookings'),  
    path('create/', views.create_booking, name='create_booking'),       
    path('detail/<int:booking_id>/', views.detail_booking, name='detail_booking'), 
    path('edit/<int:booking_id>/', views.edit_booking, name='edit_booking'), 
    path('bookings/generate-pdf/<int:booking_id>/', views.generate_pdf, name='generate_booking_pdf'),
    path('bookings/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
]

