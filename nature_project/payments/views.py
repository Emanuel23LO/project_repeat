from django.shortcuts import render, redirect
from payments.models import Payment
from django.http import JsonResponse
from django.contrib import messages
from .forms import PaymentForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from bookings.models import Booking
from customers.models import Customer
from datetime import datetime
from django.db import models
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image

def generate_payment_pdf(request, payment_id):
    # Obtener el pago detallado
    payment = Payment.objects.get(pk=payment_id)
    customer = payment.booking.customer

    # Crear el PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=0.75*inch)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(name='Title', fontSize=24, textColor='grey', alignment=1)
    
    content = []
    
    content.append(Spacer(1, 24))

    content.append(Paragraph('REPORTE DE PAGOS', title_style))

    content.append(Spacer(1, 24))

    content.append(Paragraph( 'Detalles del pago:', styles['Heading1']))
    content.append(Paragraph( f'ID del pago: {payment.id}', styles['Normal']))
    content.append(Paragraph( f'Método de pago: {payment.payment_method}', styles['Normal']))
    content.append(Paragraph( f'Fecha: {payment.date}', styles['Normal']))
    content.append(Paragraph( f'Valor: {payment.value}', styles['Normal']))

    for _ in range(2):
        content.append(Spacer(1, 12))
    
    content.append(Paragraph( f'Cliente: {customer.full_name}', styles['Normal']))

    doc.build(content)

    buffer.seek(0)
    response_o = HttpResponse(buffer, content_type='application/pdf')
    response_o['Content-Disposition'] = 'attachment; filename="pago.pdf"'
    
    return response_o


def payment_booking(request, id):
    booking = Booking.objects.get(id=id)
    total_payments = Payment.objects.filter(booking_id=id).aggregate(total=models.Sum('value'))
    if total_payments['total'] is not None:
        total_payments = total_payments['total']
    else:
        total_payments = 0    
    if request.method == 'POST':
        payment_method = request.POST['payment_method']
        date = datetime.now().date()
        value = request.POST['value']
        payment_booking = request.POST['payment_booking']
        payment = Payment.objects.create(
            payment_method = payment_method,
            date=date,
            value=int(value),
            booking=booking,
            status=True
        )
        try:
            payment.save()     
            total_p = Payment.objects.filter(booking_id=id).aggregate(total=models.Sum('value'))       
            if  int(total_p['total']) >= (booking.value / 2) and int(total_p['total']) < booking.value:
                booking.status = 'Reservado'
            elif int(total_p['total']) >= booking.value:
                booking.status = 'En ejecución'        
            booking.save()
            return redirect('bookings') 
        
        except Exception as e:
            return redirect('bookings')         
    return render(request, 'payment.html', {'booking': booking, 'total_payments': total_payments})


def payments(request):    
    payments_list = Payment.objects.all()    
    return render(request, 'payments/index.html', {'payments_list': payments_list})

def change_status_payment(request, payment_id):
    payment = Payment.objects.get(pk=payment_id)
    payment.status = not payment.status
    payment.save()
    return redirect('payments')

def create_payment(request):
    form = PaymentForm(request.POST or None, request.FILES or None)
    if form.is_valid() and request.method == 'POST':
        try:
            form.save()
            messages.success(request, 'Pago creado correctamente.')
        except:
            messages.error(request, 'Ocurrió un error al crear el pago.')
        return redirect('payments')    
    return render(request, 'payments/create.html', {'form': form})

def detail_payment(request, payment_id):
    try:
        payment = Payment.objects.get(pk=payment_id)
        data = {
            'payment_method': payment.payment_method,
            'date': payment.date,
            'value': payment.value,
        }
        return JsonResponse(data)
    except Payment.DoesNotExist:
        messages.error(request, 'El pago especificado no existe.')
        return JsonResponse({'error': 'Payment not found'}, status=404)
    except Exception as e:
        messages.error(request, f'Ocurrió un error al obtener los detalles del pago: {str(e)}')
        return JsonResponse({'error': str(e)}, status=500)

def delete_payment(request, payment_id):
    payment = Payment.objects.get(pk=payment_id)
    try:
        payment.delete()
        messages.success(request, 'Pago eliminado correctamente.')
    except:
        messages.error(request, 'No se puede eliminar el pago porque está asociado a una reserva.')
    return redirect('payments')

def edit_payment(request, payment_id):
    payment = Payment.objects.get(pk=payment_id)
    form = PaymentForm(request.POST or None, request.FILES or None, instance=payment)
    if form.is_valid() and request.method == 'POST':
        try:
            form.save()
            messages.success(request, 'Pago actualizado correctamente.')
        except:
            messages.error(request, 'Ocurrió un error al editar el pago.')
        return redirect('payments')    
    return render(request, 'payments/editar.html', {'form': form})