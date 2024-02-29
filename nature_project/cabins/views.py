from django.shortcuts import render, redirect
from cabins.models import Cabin
from .forms import CabinForm
from django.http import JsonResponse
from django.contrib import messages
from django.contrib import messages

def cabins(request):    
    cabins_list = Cabin.objects.all()    
    return render(request, 'cabins/index.html', {'cabins_list': cabins_list})

def change_status_cabin(request, cabin_id):
    cabin = Cabin.objects.get(pk=cabin_id)
    cabin.status = not cabin.status
    cabin.save()
    return redirect('cabins')

def create_cabin(request):
    form = CabinForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('cabins')    
    return render(request, 'cabins/create.html', {'form': form})

def detail_cabin(request, cabin_id):
    cabin = Cabin.objects.get(pk=cabin_id)
    data = { 'name': cabin.name, 'capacity': cabin.capacity, 'description': cabin.description, 'value': cabin.value, 'cabin_type': str(cabin.cabin_type) }    
    return JsonResponse(data)

def delete_cabin(request, cabin_id):
    cabin = Cabin.objects.get(pk=cabin_id)
    try:
        cabin.delete()        
        messages.success(request, 'Cabaña eliminado correctamente.')
    except:
        messages.error(request, 'No se puede eliminar la cabaña porque está asociado a ...')
    return redirect('cabins')


def edit_cabin(request, cabin_id):
    cabin = Cabin.objects.get(pk=cabin_id)
    form = CabinForm(request.POST or None, request.FILES or None, instance=cabin)
    if form.is_valid() and request.method == 'POST':
        try:
            form.save()
            messages.success(request, 'Cabaña actualizada correctamente.')
        except:
            messages.error(request, 'Ocurrió un error al editar la cabaña.')
        return redirect('cabins')    
    return render(request, 'cabins/edit.html', {'form': form})