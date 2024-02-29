from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from customers.models import Customer
from cabins.models import Cabin
from services.models import Service
from bookings.models import Booking
from booking_cabins.models import Booking_cabin
from datetime import datetime
from booking_services.models import Booking_service
from payments.models import Payment
from django.db import IntegrityError
from django.utils import timezone
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse

def bookings(request):    
    bookings_list = Booking.objects.all()    
    return render(request, 'bookings/index.html', {'bookings_list': bookings_list})

def create_booking(request):
    customers_list = Customer.objects.all()
    cabins_list = Cabin.objects.all()
    services_list = Service.objects.all()    
    
    if request.method == 'POST':
        # Verificar si las fechas ingresadas son válidas
        date_start_str = request.POST.get('date_start', '')
        date_end_str = request.POST.get('date_end', '')

        if not date_start_str or not date_end_str:
            error_message = 'Todos los campos son obligatorios'
            return render(request, 'bookings/create.html', {'error_message': error_message, 'customers_list': customers_list , 'cabins_list': cabins_list, 'services_list': services_list})

        try:
            date_start = datetime.strptime(date_start_str, '%Y-%m-%d')
            date_end = datetime.strptime(date_end_str, '%Y-%m-%d')

            if date_start.date() < timezone.now().date() or date_end.date() < timezone.now().date():
                error_message = 'Las fechas deben ser vigentes'
                return render(request, 'bookings/create.html', {'error_message': error_message, 'customers_list': customers_list , 'cabins_list': cabins_list, 'services_list': services_list})

            if date_start.date() > date_end.date():
                error_message = 'La fecha de inicio debe ser anterior a la fecha de finalización'
                return render(request, 'bookings/create.html', {'error_message': error_message, 'customers_list': customers_list , 'cabins_list': cabins_list, 'services_list': services_list})

            # Crear la reserva si las fechas son válidas
            booking = Booking.objects.create(                        
                date_booking=datetime.now().date(),                                   
                date_start=date_start,
                date_end=date_end,
                value=request.POST['totalValue'],
                status='Reservado',
                customer_id=request.POST['customer']
            )
            
            cabins_Id = request.POST.getlist('cabinId[]')
            cabins_value = request.POST.getlist('cabinValue[]')
            services_Id = request.POST.getlist('serviceId[]')
            services_value = request.POST.getlist('serviceValue[]')       
                    
            for i in range(len(cabins_Id)):            
                cabin = Cabin.objects.get(pk=int(cabins_Id[i]))
                booking_cabins = Booking_cabin.objects.create(
                    booking=booking,
                    cabin=cabin,
                    value=cabins_value[i]
                )
                booking_cabins.save()
            
            for i in range(len(services_Id)):
                service = Service.objects.get(pk=int(services_Id[i]))
                booking_service = Booking_service.objects.create(
                    booking=booking,
                    service=service,
                    value=services_value[i]
                )
                booking_service.save()

            # Redirigir primero a 'bookings'
            return redirect('bookings')
            
        except ValueError:
            error_message = 'Las fechas ingresadas no son válidas.'
            return render(request, 'bookings/create.html', {'error_message': error_message, 'customers_list': customers_list , 'cabins_list': cabins_list, 'services_list': services_list})

    return render(request, 'bookings/create.html', {'customers_list': customers_list , 'cabins_list': cabins_list, 'services_list': services_list})

def generate_pdf(request, booking_id):
   # Obtener la reserva detallada
    booking = Booking.objects.get(pk=booking_id)
    booking_cabins = Booking_cabin.objects.filter(booking=booking)
    booking_services = Booking_service.objects.filter(booking=booking)

    # Crear el PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    # Agregar contenido al PDF
    p.drawString(100, 750, 'Detalles de la reserva:')
    p.drawString(100, 730, f'ID de la reserva: {booking.id}')
    p.drawString(100, 710, f'Fecha de inicio: {booking.date_start}')
    p.drawString(100, 690, f'Fecha de fin: {booking.date_end}')
    p.drawString(100, 670, f'Valor: {booking.value}')
    p.drawString(100, 650, f'Estado: {booking.status}')

    # Obtener y agregar detalles de las cabañas reservadas
    p.drawString(100, 630, 'Cabañas reservadas:')
    y_position = 610
    for booking_cabin in booking_cabins:
        cabin = booking_cabin.cabin
        p.drawString(120, y_position, f'Nombre: {cabin.name}')
        p.drawString(120, y_position - 20, f'Descripción: {cabin.description}')
        p.drawString(120, y_position - 40, f'Valor: {booking_cabin.value}')
        y_position -= 80

    # Obtener y agregar detalles de los servicios reservados
    p.drawString(100, y_position - 20, 'Servicios reservados:')
    y_position -= 40
    for booking_service in booking_services:
        service = booking_service.service
        p.drawString(120, y_position, f'Nombre: {service.name}')
        p.drawString(120, y_position - 20, f'Valor: {booking_service.value}')
        y_position -= 40

    # Cierra el lienzo
    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reserva.pdf"'
    
    return response

def detail_booking(request, booking_id):
    booking = Booking.objects.get(pk=booking_id)
    booking_cabins = Booking_cabin.objects.filter(booking=booking)
    booking_services = Booking_service.objects.filter(booking=booking)
    payments = Payment.objects.filter(booking=booking)
    return render(request, 'bookings/detail.html', {'booking': booking, 'booking_cabins': booking_cabins, 'booking_services': booking_services, 'payments': payments})



def delete_booking(request, booking_id):
    booking = Booking.objects.get(pk=booking_id)
    try:
        booking.delete()        
        messages.success(request, 'Reserva eliminada correctamente.')
    except:
        messages.error(request, 'No se puede eliminar la reserva porque está asociado a otra tabla.')
    return redirect('bookings')

def edit_booking(request, booking_id):
    booking = Booking.objects.get(pk=booking_id)
    customers_list = Customer.objects.all()  # Obtener la lista de clientes
    cabins_list = Cabin.objects.all()  # Obtener la lista de cabañas
    services_list = Service.objects.all()  # Obtener la lista de servicios

    if request.method == 'POST':
        # Actualizar los campos de la reserva con los datos enviados en la solicitud POST
        try:
            date_start_str = request.POST['date_start']
            date_end_str = request.POST['date_end']        
            date_start = datetime.strptime(date_start_str, '%Y-%m-%d')
            date_end = datetime.strptime(date_end_str, '%Y-%m-%d')
            
            booking.date_start = date_start
            booking.date_end = date_end
            booking.value = request.POST['totalValue']
            booking.status = 'Reservado'  # Siempre lo establecemos a 'Reservado' en esta vista
            
            # Guardar los cambios en la reserva
            booking.save()
            
            messages.success(request, 'Reserva actualizada correctamente.')  # Mensaje de éxito
            return redirect('bookings')  # Redirigir a la página de listado de reservas después de la actualización
        except Exception as e:
            messages.error(request, f'Ocurrió un error al editar la reserva: {e}')  # Mensaje de error
            return redirect('edit_booking', booking_id=booking_id)
        
    # Si la solicitud no es POST, renderiza la página de edición con los datos de la reserva
    return render(request, 'bookings/create.html', {'booking': booking, 'customers_list': customers_list, 'cabins_list': cabins_list, 'services_list': services_list})
