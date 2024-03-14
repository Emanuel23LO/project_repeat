from django.shortcuts import render, redirect
from cabin_types.models import Cabin_type
from .forms import Cabin_typeForm
from django.http import JsonResponse
from django.contrib import messages


def cabin_types(request):    
    cabin_types_list = Cabin_type.objects.all()    
    return render(request, 'cabin_types/index.html', {'cabin_types_list': cabin_types_list})

def change_status_cabin_type(request, cabin_type_id):
    cabin_type = Cabin_type.objects.get(pk=cabin_type_id)
    cabin_type.status = not cabin_type.status
    cabin_type.save()
    return redirect('cabin_types')

def create_cabin_type(request):
    if request.method == 'POST':
        form = Cabin_typeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'El tipo de la cabaña se ha creado correctamente.')
            return redirect('cabin_types')
    else:
        form = Cabin_typeForm()
    return render(request, 'cabin_types/create.html', {'form': form})

def detail_cabin_type(request, cabin_type_id):
    cabin_type = Cabin_type.objects.get(pk=cabin_type_id)
    data = { 'name': cabin_type.name}    
    return JsonResponse(data)


def cabin_type_delete(request, cabin_type_id):
    cabin_type = Cabin_type.objects.get(pk=cabin_type_id)
    try:
        cabin_type.delete()        
        messages.success(request, 'El tipo de la cabaña se eliminado correctamente.')
    except:
        messages.error(request, 'No se puede eliminar el tipo de la cabaña porque está asociado a una cabaña.')
    return redirect('cabin_types')

def edit_cabin_types(request, cabin_type_id):
    cabin_type = Cabin_type.objects.get(pk=cabin_type_id)
    form = Cabin_typeForm(request.POST or None, instance=cabin_type)
    if form.is_valid() and request.method == 'POST':
        try:
            form.save()
            messages.success(request, 'Tipo Cabaña actualizada correctamente.')
        except:
            messages.error(request, 'Ocurrió un error al editar el Tipo de Cabaña.')        
        return redirect('cabin_types')    
    return render(request, 'cabin_types/editar.html', {'form': form})