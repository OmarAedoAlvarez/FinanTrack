# Importaciones de Django
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponse

#Utilidades y Fechas
from datetime import datetime, timedelta
from django.utils.timezone import now

#Modelos
from .models import Gasto, Categoria

# Pila global para almacenar los últimos gastos
pila_gastos = []


def index(request):
    return render(request, 'index.html')
# Vista de registro
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            login(request, user)
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})

# Vista de inicio de sesión
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required
def home(request):
    # Obtener los gastos del usuario ordenados por fecha
    gastos = Gasto.objects.filter(user=request.user).order_by('-fecha')

    # Crear un diccionario para agrupar los gastos por categoría
    gastos_por_categoria = {}
    for gasto in gastos:
        categoria_nombre = gasto.categoria.nombre
        if categoria_nombre not in gastos_por_categoria:
            gastos_por_categoria[categoria_nombre] = []
        gastos_por_categoria[categoria_nombre].append(gasto)

    # Calcular el total de los gastos
    total_gastos = sum(g.monto for g in gastos)

    # Calcular la categoría con el gasto mayor
    categoria_mayor_gasto = None
    mayor_gasto = 0
    for categoria, gastos_categoria in gastos_por_categoria.items():
        total_categoria = sum(g.monto for g in gastos_categoria)
        if total_categoria > mayor_gasto:
            mayor_gasto = total_categoria
            categoria_mayor_gasto = categoria

    # Obtener el gasto más alto
    if gastos.exists():
        gasto_mas_fuerte = max(gastos, key=lambda g: g.monto)  # Obtener el gasto con el monto más alto
    else:
        gasto_mas_fuerte = None

    return render(request, "home.html", {
        "gastos_por_categoria": gastos_por_categoria,  # Gastos agrupados por categoría
        "total_gastos": total_gastos,
        "categoria_mayor_gasto": categoria_mayor_gasto,
        "mayor_gasto": mayor_gasto,
        "gasto_mas_fuerte": gasto_mas_fuerte  # Pasar el gasto más fuerte
    })


def obtener_filtro_fecha(filtro):
    filtros_fecha = {
        "ultimo_mes": now().date() - timedelta(days=30),  
        "ultimos_3_meses": now().date() - timedelta(days=90),  
        "este_anio": now().date().replace(month=1, day=1),  
    }
    return filtros_fecha.get(filtro)

def generar_reporte(request):
    filtro = request.GET.get('filtro_tiempo', 'todos')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    # Filtrar los gastos según los criterios
    gastos = Gasto.objects.filter(user=request.user).order_by('-fecha')

    # Aplicar el filtro de tiempo
    fecha_limite = obtener_filtro_fecha(filtro)
    if fecha_limite:
        gastos = gastos.filter(fecha__gte=fecha_limite)

    elif filtro == "personalizado":
        try:
            if fecha_inicio and fecha_fin:
                fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
                if fecha_inicio > fecha_fin:
                    gastos = Gasto.objects.none()  
                else:
                    gastos = gastos.filter(fecha__range=[fecha_inicio, fecha_fin])
        except ValueError:
            gastos = Gasto.objects.none()

    # Crear el archivo CSV con los gastos filtrados
    import csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_gastos.csv"'
    writer = csv.writer(response)
    writer.writerow(['Título', 'Categoría', 'Monto', 'Fecha', 'Descripción'])

    for gasto in gastos:
        writer.writerow([gasto.titulo, gasto.categoria.nombre, gasto.monto, gasto.fecha, gasto.descripcion])

    return response


@login_required
def lista_gastos(request):
    filtro = request.GET.get('filtro_tiempo', 'todos')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    gastos = Gasto.objects.filter(user=request.user).order_by('-fecha')

    fecha_limite = obtener_filtro_fecha(filtro)
    
    if filtro == "este_anio":
        # Filtra los gastos del año actual, independientemente de si son antes o después de hoy
        gastos = gastos.filter(fecha__year=now().year)
    
    elif fecha_limite:
        # Filtra los gastos cuyo 'fecha' sea mayor o igual a la fecha limite y menor o igual a la fecha de hoy.
        gastos = gastos.filter(fecha__gte=fecha_limite, fecha__lte=now().date())  # Asegura que no haya fechas futuras

    elif filtro == "personalizado":
        try:
            if fecha_inicio and fecha_fin:
                fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
                
                if fecha_inicio > fecha_fin:
                    gastos = Gasto.objects.none() 
                else:
                    gastos = gastos.filter(fecha__range=[fecha_inicio, fecha_fin])
        except ValueError:
            gastos = Gasto.objects.none()  

    return render(request, "lista_gastos.html", {
        "gastos": gastos,
        "filtro": filtro,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin
    })

@login_required
def registrar_gasto(request):
    categorias = Categoria.objects.all()  # Obtener todas las categorías disponibles

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        categoria_nombre = request.POST.get('categoria')  # Categoría seleccionada
        monto = request.POST.get('monto')
        fecha_str = request.POST.get('fecha')
        descripcion = request.POST.get('descripcion')

        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date() if fecha_str else None

        # Usar la categoría seleccionada, sin la necesidad de ingresar una nueva categoría
        categoria, created = Categoria.objects.get_or_create(nombre=categoria_nombre)

        # Crear y guardar el gasto en la base de datos
        gasto = Gasto.objects.create(
            user=request.user,
            categoria=categoria,
            titulo=titulo,
            monto=monto,
            fecha=fecha,
            descripcion=descripcion
        )

        # Asegurarse de que la pila esté inicializada en la sesión
        if "pila_gastos" not in request.session:
            request.session["pila_gastos"] = []  

        # Agregar el ID del gasto a la pila
        request.session["pila_gastos"].append(gasto.id)
        request.session.modified = True 

        return redirect('lista_gastos')

    return render(request, 'registrar_gasto.html', {"categorias": categorias})


@login_required
def deshacer_gasto(request):
    if "pila_gastos" in request.session and request.session["pila_gastos"]:
        ultimo_gasto_id = request.session["pila_gastos"].pop()  # Elimina el último gasto de la pila
        request.session.modified = True  # Asegúrate de que la sesión se guarde correctamente

        # Eliminar el gasto de la base de datos
        try:
            ultimo_gasto = Gasto.objects.get(id=ultimo_gasto_id)
            ultimo_gasto.delete()
        except Gasto.DoesNotExist:
            pass  # Si el gasto no existe, simplemente ignoramos el error

    return redirect('lista_gastos')


@login_required
def editar_gasto(request, gasto_id):
    gasto = get_object_or_404(Gasto, id=gasto_id)

    if request.method == 'POST':
        gasto.titulo = request.POST.get('titulo')
        gasto.categoria, _ = Categoria.objects.get_or_create(nombre=request.POST.get('categoria'))
        gasto.monto = request.POST.get('monto')
        gasto.fecha = request.POST.get('fecha')
        gasto.descripcion = request.POST.get('descripcion')
        gasto.save()

        return redirect('lista_gastos')

    return render(request, 'editar_gasto.html', {'gasto': gasto})


@login_required
def eliminar_gasto(request, gasto_id):
    print("Pila antes de eliminar:", request.session.get('pila_gastos'))

    gasto = get_object_or_404(Gasto, id=gasto_id)

    if gasto.user == request.user:
        if "pila_gastos" in request.session:
            if gasto.id in request.session["pila_gastos"]:
                request.session["pila_gastos"].remove(gasto.id)
                request.session.modified = True 

        gasto.delete()

    return redirect('lista_gastos')



