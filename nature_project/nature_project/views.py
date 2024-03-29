import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from urllib.parse import quote_plus, urlencode
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.contrib.auth.models import Group
from .forms import RegisterForm
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from customers.models import Customer
import requests
from cabins.models import Cabin
from bookings.models import Booking
from services.models import Service
from customers.models import Customer
from payments.models import Payment
from django.db.models import Sum
import calendar
from django.db.models.functions import ExtractMonth
import locale

def index(request):

    # --- Inicio grafica dashboard ---
    ingresos_por_mes = Payment.objects.filter(status=True).annotate(
    mes=ExtractMonth('date')
    ).values('mes').annotate(total_ingresos=Sum('value'))
    meses = range(1, 13)

    # Agregar cada mes y su valor a la lista de datos
    data = [["Mes", "Ingresos"]]
    for mes in meses:
        total_mes = 0
        nombre_mes = calendar.month_name[mes]
        for ingreso_mes in ingresos_por_mes:
            if ingreso_mes['mes'] == mes:
                total_mes = ingreso_mes['total_ingresos']
                break
        data.append([nombre_mes, total_mes])


    # --- Fin grafica dashboard ---
    total_pagos = Payment.objects.aggregate(total=Sum('value'))
    count = Cabin.objects.count()
    customer = Customer.objects.count()
    count_booking = Booking.objects.filter(status="Reservado").count()
    count_booking2 = Booking.objects.filter(status="En ejecución").count()
    total_reservas = count_booking + count_booking2
    
    return render(request, 'index.html', {
        "count": count,
        "count_booking": count_booking,
        "count_booking2": count_booking2,
        "total_reservas": total_reservas,
        "customer": customer,'total_pagos': total_pagos['total'],
        'data': json.dumps(data)
    })

def landing(request):
    return render(request, 'landing.html')

oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)

def loginn(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )

def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token
    return redirect(request.build_absolute_uri(reverse("index")))

def logout(request):
    request.session.clear()

    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("logi")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )

def logi(request):
    # Obtenemos la sesión del usuario
    session_data = request.session.get("user")
    pretty_session_data = json.dumps(session_data, indent=4)

    # Obtenemos todas las cabañas y servicios
    cabins = Cabin.objects.filter(status=True) 
    services = Service.objects.filter(status=True)

    # Renderizamos la plantilla con ambos conjuntos de datos
    return render(
        request,
        "logi.html",
        {
            "session": session_data,
            "pretty": pretty_session_data,
            "cabins": cabins,
            "services": services,
        },
    )


def register(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST or None)
        if form.is_valid():
            name = form.cleaned_data['name']
            last_name = form.cleaned_data['last_name']
            document = form.cleaned_data['document']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            password = form.cleaned_data['password']
            
            # Crear usuario en Django
            user = User.objects.create_user(username=email, email=email, password=password, first_name=name, last_name=last_name)
            user.save()

            # Crear cliente en tu tabla Customer si el número de teléfono no existe
            full_name = f"{name} {last_name}"
            customer, created = Customer.objects.get_or_create(
                phone=phone,
                defaults={'full_name': full_name, 'document': document, 'email': email}
            )

            if not created:
                # Si el cliente ya existe, muestra un mensaje de error
                return HttpResponse("Error: Ya existe un cliente con este número de teléfono.")

            # Intentar registrar el usuario en Auth0
            auth0_data = {
                "client_id": settings.AUTH0_CLIENT_ID,
                "client_secret": settings.AUTH0_CLIENT_SECRET,
                "email": email,
                "password": password,
                "connection": "Username-Password-Authentication",
                "user_metadata": {
                    "name": name,
                    "last_name": last_name,
                    "document": document,
                    "phone": phone
                }
            }
            response = requests.post(f"https://{settings.AUTH0_DOMAIN}/dbconnections/signup", json=auth0_data)

            # Verificar el estado de la respuesta de Auth0
            if response.status_code == 200:
                # Iniciar sesión automáticamente después del registro en Django
                user = authenticate(request, username=email, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('index')
                else:
                    # No se pudo autenticar al usuario después del registro en Django
                    return HttpResponse("Error: No se pudo iniciar sesión después del registro en Django")
            else:
                # Eliminar el usuario recién creado en Django si el registro en Auth0 falla
                user.delete()
                # Mostrar un mensaje de error
                return HttpResponse("Error: No se pudo registrar en Auth0")

    return render(request, 'register.html', {'form': form})