
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
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
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from django.conf import settings
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from django.utils.dateparse import parse_date


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
            booking.save()        
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
            
            messages.success(request, 'Reserva creada con éxito.')
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
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=0.75*inch)
    styles = getSampleStyleSheet()

    # Definir estilo de párrafo para el título principal
    title_style = ParagraphStyle(name='Title', fontSize=24, textColor='grey', alignment=1)

    # Contenido del PDF
    content = []

    logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'img_new', 'logo_glammping.jpg')  # Utiliza el primer directorio de archivos estáticos
    logo = Image(logo_path)
    logo.drawWidth = 1.5 * inch  # Ajusta el ancho de la imagen según sea necesario
    logo.drawHeight = 1.5 * inch  # Ajusta el alto de la imagen según sea necesario
    content.append(Spacer(1, 24))  # Espacio entre el texto y la imagen
    content.append(logo)

    content.append(Spacer(1, 24))
    # Agregar título principal al PDF
    content.append(Paragraph('REPORTE DE RESERVA', title_style))

    # Agregar espacios entre el título y el primer párrafo
    content.append(Spacer(1, 24))  # Ajusta el espacio según sea necesario

    # Agregar contenido al PDF
    content.append(Paragraph('Detalles de la reserva:', styles['Heading1']))
    content.append(Paragraph(f'ID de la reserva: {booking.id}', styles['Normal']))
    content.append(Paragraph(f'Fecha de inicio: {booking.date_start}', styles['Normal']))
    content.append(Paragraph(f'Fecha de fin: {booking.date_end}', styles['Normal']))
    content.append(Paragraph(f'Valor: {booking.value}', styles['Normal']))
    content.append(Paragraph(f'Estado: {booking.status}', styles['Normal']))

    # Agregar espacios entre cada párrafo
    for _ in range(2):
        content.append(Spacer(1, 12))  # Ajusta el espacio según sea necesario

    # Agregar detalles de las cabañas reservadas
    content.append(Paragraph('Cabañas reservadas:', styles['Heading1']))
    for booking_cabin in booking_cabins:
        cabin = booking_cabin.cabin
        cabin_details = f'Nombre: {cabin.name}<br/>Descripción: {cabin.description}<br/>Valor: {booking_cabin.value}'
        content.append(Paragraph(cabin_details, styles['Normal']))

    # Agregar espacios entre cada párrafo
    for _ in range(2):
        content.append(Spacer(1, 12))  # Ajusta el espacio según sea necesario

    # Agregar detalles de los servicios reservados
    content.append(Paragraph('Servicios reservados:', styles['Heading1']))
    for booking_service in booking_services:
        service = booking_service.service
        service_details = f'Nombre: {service.name}<br/>Valor: {booking_service.value}'
        content.append(Paragraph(service_details, styles['Normal']))

    # Construir el PDF
    doc.build(content)

    # Configurar la respuesta HTTP
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


def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    cabins = Cabin.objects.filter(booking_cabin__booking=booking)
    services = Service.objects.filter(booking_service__booking=booking)

    customers_list = Customer.objects.all()
    cabins_list = Cabin.objects.all()
    services_list = Service.objects.all()

    total = sum(cabin.value for cabin in cabins) + sum(service.value for service in services)

    # Sumar los valores de las nuevas cabañas seleccionadas
    for cabin_id in request.POST.getlist('cabinId[]'):
        cabin_value = request.POST.get(f'cabinValue[{cabin_id}]', '')
        try:
            cabin_value = float(cabin_value)
            total += cabin_value
        except ValueError:
            pass

    # Sumar los valores de los nuevos servicios seleccionados
    for service_id in request.POST.getlist('serviceId[]'):
        service_value = request.POST.get(f'serviceValue[{service_id}]', '')
        try:
            service_value = float(service_value)
            total += service_value
        except ValueError:
            pass

    # Restar los valores de las cabañas eliminadas
    cabins_to_delete = request.POST.getlist('cabinToDelete[]')
    for cabin_id in cabins_to_delete:
        cabin = get_object_or_404(Cabin, pk=cabin_id)
        total -= cabin.value

    # Restar los valores de los servicios eliminados
    services_to_delete = request.POST.getlist('serviceToDelete[]')
    for service_id in services_to_delete:
        service = get_object_or_404(Service, pk=service_id)
        total -= service.value

    # Crear nuevas asociaciones para cabañas y servicios antes de actualizar el valor total
    for cabin_id in request.POST.getlist('cabinId[]'):
        if not Booking_cabin.objects.filter(booking=booking, cabin_id=cabin_id).exists():
            cabin = get_object_or_404(Cabin, pk=cabin_id)
            cabin_value = request.POST.get(f'cabinValue[{cabin_id}]', '')
            try:
                cabin_value = float(cabin_value)
            except ValueError:
                cabin_value = 0

            Booking_cabin.objects.create(
                booking=booking,
                cabin=cabin,
                value=cabin_value
            )

    for service_id in request.POST.getlist('serviceId[]'):
        if not Booking_service.objects.filter(booking=booking, service_id=service_id).exists():
            service = get_object_or_404(Service, pk=service_id)
            service_value = request.POST.get(f'serviceValue[{service_id}]', '')
            try:
                service_value = float(service_value)
            except ValueError:
                service_value = 0

            Booking_service.objects.create(
                booking=booking,
                service=service,
                value=service_value
            )

    # Recalcular el valor total después de crear las nuevas asociaciones

    # Actualizar el campo de valor total en la reserva con el nuevo valor calculado
    booking.value = int(total)
    booking.save()

    # Eliminar cabañas y servicios seleccionados para eliminación
    for cabin_id in cabins_to_delete:
        Booking_cabin.objects.filter(booking=booking, cabin_id=cabin_id).delete()

    for service_id in services_to_delete:
        Booking_service.objects.filter(booking=booking, service_id=service_id).delete()


    cabins = Cabin.objects.filter(booking_cabin__booking=booking)
    services = Service.objects.filter(booking_service__booking=booking)
    total = sum(cabin.value for cabin in cabins) + sum(service.value for service in services)

    # Actualizar el campo de valor total en la reserva con el nuevo valor calculado
    booking.value = int(total)
    booking.save()
    messages.success(request, 'Reserva editada con éxito.')

    # Comprobamos si se realizó alguna edición
    if any([cabins_to_delete, services_to_delete, request.POST.getlist('cabinId[]'), request.POST.getlist('serviceId[]')]):
        return redirect('bookings')
    else:
        return render(request, 'bookings/edit.html', {'booking': booking, 'customers_list': customers_list, 'cabins_list': cabins_list, 'services_list': services_list, 'cabins': cabins, 'services': services, 'total': total})