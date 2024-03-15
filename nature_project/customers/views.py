from django.shortcuts import render, redirect

from customers.models import Customer

from .forms import CustomerForm

from django.http import JsonResponse

from django.contrib import messages


def customers(request):    
    customers_list = Customer.objects.all()    
    return render(request, 'customers/index.html', {'customers_list': customers_list})

def change_status_customer(request, customer_id):
    customer = Customer.objects.get(pk=customer_id)
    customer.status = not customer.status
    customer.save()
    return redirect('customers')

def create_customer(request):
    form = CustomerForm(request.POST or None)
    if form.is_valid() and request.method == 'POST':
        try:
            form.save()
            messages.success(request, 'Cliente creado correctamente.')
        except:
            messages.error(request, 'Ocurrió un error al crear el cliente.')        
        return redirect('customers')    
    return render(request, 'customers/create.html', {'form': form})

def detail_customer(request, customer_id):
    customer = Customer.objects.get(pk=customer_id)
    data = { 'full_name': customer.full_name, 'document': customer.document, 'phone': customer.phone, 'email': customer.email  }    
    return JsonResponse(data)

def delete_customer(request, customer_id):
    customer = Customer.objects.get(pk=customer_id)
    try:
        customer.delete()
        messages.success(request, 'Cliente eliminado correctamente.')
    except:
        messages.error(request, 'No se puede eliminar el Cliente porque está asociado a un libro.')
    return redirect('customers')

def edit_customer(request, customer_id):
    author = Customer.objects.get(pk=customer_id)
    form = CustomerForm(request.POST or None, instance=author)
    if form.is_valid() and request.method == 'POST':
        try:
            form.save()
            messages.success(request, 'Cliente actualizado correctamente.')
        except:
            messages.error(request, 'Ocurrió un error al editar el Cliente.')        
        return redirect('customers')    
    return render(request, 'customers/editar.html', {'form': form})
