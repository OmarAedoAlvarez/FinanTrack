from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'), 
    path('register/', views.register, name='register'),  
    path('login/', views.login_view, name='login'),  
    path('home/', views.home, name='home'),  
    path('gastos/', views.lista_gastos, name='lista_gastos'),  
    path('gastos/registrar/', views.registrar_gasto, name='registrar_gasto'),  
    path('gastos/deshacer/', views.deshacer_gasto, name='deshacer_gasto'),
    path('gastos/editar/<int:gasto_id>/', views.editar_gasto, name='editar_gasto'),
    path('gastos/eliminar/<int:gasto_id>/', views.eliminar_gasto, name='eliminar_gasto'),
    path('gastos/reporte/', views.generar_reporte, name='generar_reporte')
]