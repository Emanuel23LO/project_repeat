from django.shortcuts import render, redirect
from payments.models import Payment
from django.http import JsonResponse
from django.contrib import messages
from .forms import PaymentForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from bookings.models import Booking




@receiver(post_save, sender=Payment)
def status_reservation(sender, instance, created, **kwargs):
    booking = Booking.objects.get(pk=instance.booking_id)
    valor_reserva = booking.value
    if instance.value > 0.5 * valor_reserva:
        texto = 'pagado'
    elif instance.value >= 0.5:
        texto = 'confirmado'
    elif instance.value <= 0:
        texto = 'cancelado'
    else:
        texto= 'reservado'

    Booking.objects.filter(id=instance.booking_id).update(status=texto)

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