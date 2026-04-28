"""
URL configuration for StaminApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from StaminApp_App.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('dashboard/', home, name='dashboard'),

    # Rutas cliente
    path('usuario/', UsuarioListView.as_view(), name='usuario-list'),
    path('usuario/nuevo/', UsuarioCreateView.as_view(), name='usuario-create'),
    path('usuario/<int:pk>/editar/', UsuarioUpdateView.as_view(), name='usuario-update'),
    path('usuario/<int:pk>/eliminar/', UsuarioDeleteView.as_view(), name='usuario-delete'),

    # Autenticación (única para cliente y gestor)
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),

    # Rutas para gestores: listar, ver detalle, crear, editar y eliminar clientes
    path('gestor/usuarios/', GestorUsuarioListView.as_view(), name='gestor-usuario-list'),
    path('gestor/usuario/nuevo/', GestorUsuarioCreateView.as_view(), name='gestor-usuario-create'),
    path('gestor/usuario/<int:pk>/', GestorUsuarioDetailView.as_view(), name='gestor-usuario-detail'),
    path('gestor/usuario/<int:pk>/editar/', GestorUsuarioUpdateView.as_view(), name='gestor-usuario-update'),
    path('gestor/usuario/<int:pk>/eliminar/', GestorUsuarioDeleteView.as_view(), name='gestor-usuario-delete'),

]
