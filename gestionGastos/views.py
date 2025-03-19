# Importaciones de Django
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponse

# Utilidades y Fechas
from datetime import datetime, timedelta
from django.utils.timezone import now

# Modelos
from .models import Gasto, Categoria

# Pila global para almacenar los últimos gastos
pila_gastos = []


def index(request):
    # Vista de la página principal
    return render(request, 'index.html')


def register(request):
    # Vista para registrar un nuevo usuario
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # Guardar al nuevo usuario
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            login(request, user)  # Iniciar sesión del nuevo usuario
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    # Vista para iniciar sesión de un usuario
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)  # Iniciar sesión
                return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


@login_required
def home(request):
    # Vista de inicio para mostrar los gastos del usuario
    gastos = Gasto.objects.filter(user=request.user).order_by('-fecha')

    # Agrupar los gastos por categoría
    gastos_por_categoria = {}
    for gasto in gastos:
        categoria_nombre = gasto.categoria.nombre
        if categoria_nombre not in gastos_por_categoria:
            gastos_por_categoria[categoria_nombre] = []
        gastos_por_categoria[categoria_nombre].append(gasto)

    # Calcular totales
    total_gastos = sum(g.monto for g in gastos)
    categoria_mayor_gasto = None
    mayor_gasto = 0
    for categoria, gastos_categoria in gastos_por_categoria.items():
        total_categoria = sum(g.monto for g in gastos_categoria)
        if total_categoria > mayor_gasto:
            mayor_gasto = total_categoria
            categoria_mayor_gasto = categoria

    gasto_mas_fuerte = max(gastos, key=lambda g: g.monto) if gastos.exists() else None

    return render(request, "home.html", {
        "gastos_por_categoria": gastos_por_categoria,
        "total_gastos": total_gastos,
        "categoria_mayor_gasto": categoria_mayor_gasto,
        "mayor_gasto": mayor_gasto,
        "gasto_mas_fuerte": gasto_mas_fuerte
    })


def obtener_filtro_fecha(filtro):
    # Retorna la fecha límite para los filtros predefinidos
    filtros_fecha = {
        "ultimo_mes": now().date() - timedelta(days=30),
        "ultimos_3_meses": now().date() - timedelta(days=90),
        "este_anio": now().date().replace(month=1, day=1),
    }
    return filtros_fecha.get(filtro)


def generar_reporte(request):
    # Generar un reporte de gastos filtrados en formato CSV
    filtro = request.GET.get('filtro_tiempo', 'todos')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    gastos = Gasto.objects.filter(user=request.user).order_by('-fecha')

    # Aplicar filtro por fecha
    fecha_limite = obtener_filtro_fecha(filtro)
    if fecha_limite:
        gastos = gastos.filter(fecha__gte=fecha_limite)

    elif filtro == "personalizado":
        try:
            if fecha_inicio and fecha_fin:
                fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
                if fecha_inicio > fecha_fin:
                    gastos = Gasto.objects.none()  # No mostrar si la fecha inicio es mayor que la fecha fin
                else:
                    gastos = gastos.filter(fecha__range=[fecha_inicio, fecha_fin])
        except ValueError:
            gastos = Gasto.objects.none()  # Si las fechas no son válidas, no mostrar gastos

    # Crear archivo CSV con los gastos filtrados
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
    # Vista que muestra los gastos según el filtro seleccionado
    filtro = request.GET.get('filtro_tiempo', 'todos')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    gastos = Gasto.objects.filter(user=request.user).order_by('-fecha')

    fecha_limite = obtener_filtro_fecha(filtro)

    if filtro == "este_anio":
        # Filtrar los gastos del año actual
        gastos = gastos.filter(fecha__year=now().year)
    
    elif fecha_limite:
        # Filtra los gastos entre la fecha límite y la fecha actual
        gastos = gastos.filter(fecha__gte=fecha_limite, fecha__lte=now().date())  # Asegura que no haya fechas futuras

    elif filtro == "personalizado":
        try:
            if fecha_inicio and fecha_fin:
                fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
                
                if fecha_inicio > fecha_fin:
                    gastos = Gasto.objects.none()  # Si la fecha inicio es mayor que la fecha fin, no mostrar nada
                else:
                    gastos = gastos.filter(fecha__range=[fecha_inicio, fecha_fin])
        except ValueError:
            gastos = Gasto.objects.none()  # Si las fechas no son válidas, no mostrar gastos

    return render(request, "lista_gastos.html", {
        "gastos": gastos,
        "filtro": filtro,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin
    })


@login_required
def registrar_gasto(request):
    # Vista para registrar un nuevo gasto
    categorias = Categoria.objects.all()

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        categoria_nombre = request.POST.get('categoria')
        monto = request.POST.get('monto')
        fecha_str = request.POST.get('fecha')
        descripcion = request.POST.get('descripcion')

        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date() if fecha_str else None

        # Usar la categoría seleccionada
        categoria, created = Categoria.objects.get_or_create(nombre=categoria_nombre)

        # Crear y guardar el gasto
        gasto = Gasto.objects.create(
            user=request.user,
            categoria=categoria,
            titulo=titulo,
            monto=monto,
            fecha=fecha,
            descripcion=descripcion
        )

        # Asegurarse de que la pila esté inicializada
        if "pila_gastos" not in request.session:
            request.session["pila_gastos"] = []

        # Agregar el ID del gasto a la pila
        request.session["pila_gastos"].append(gasto.id)
        request.session.modified = True 

        return redirect('lista_gastos')

    return render(request, 'registrar_gasto.html', {"categorias": categorias})


@login_required
def deshacer_gasto(request):
    # Vista para deshacer el último gasto registrado
    if "pila_gastos" in request.session and request.session["pila_gastos"]:
        ultimo_gasto_id = request.session["pila_gastos"].pop()  # Elimina el último gasto de la pila
        request.session.modified = True

        # Eliminar el gasto de la base de datos
        try:
            ultimo_gasto = Gasto.objects.get(id=ultimo_gasto_id)
            ultimo_gasto.delete()
        except Gasto.DoesNotExist:
            pass  # Si el gasto no existe, ignoramos el error

    return redirect('lista_gastos')


@login_required
def editar_gasto(request, gasto_id):
    # Vista para editar un gasto
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
    # Vista para eliminar un gasto
    gasto = get_object_or_404(Gasto, id=gasto_id)

    if gasto.user == request.user:
        if "pila_gastos" in request.session:
            if gasto.id in request.session["pila_gastos"]:
                request.session["pila_gastos"].remove(gasto.id)
                request.session.modified = True 

        gasto.delete()

    return redirect('lista_gastos')
