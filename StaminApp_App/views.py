from django.shortcuts import render, redirect
from .models import Usuario
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .forms import UsuarioForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView

# Create your views here.

# ---------- Ficha socio ----------

class UsuarioListView(ListView): # Vista solo para los clientes
    model = Usuario
    template_name = 'cliente/usuario_list.html'
    context_object_name = 'usuario'

    def get_queryset(self):
        return Usuario.objects.filter(id=self.request.user.id)

class UsuarioCreateView(CreateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'cliente/usuario_form.html'
    success_url = '/usuario/'

class UsuarioUpdateView(UpdateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'cliente/usuario_form.html'
    success_url = '/usuario/'

class UsuarioDeleteView(DeleteView):
    model = Usuario
    template_name = 'cliente/usuario_confirm_delete.html'
    success_url = '/usuario/'

# Vistas solo para gestores: ver, editar y eliminar clientes
class GestorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return getattr(self.request.user, 'rol', '').lower() == 'gestor'

class GestorUsuarioListView(GestorRequiredMixin, ListView):
    model = Usuario
    template_name = 'gestor/usuario_list.html'
    context_object_name = 'usuarios'

    def get_queryset(self):
        return Usuario.objects.all()

class GestorUsuarioDetailView(GestorRequiredMixin, DetailView):
    model = Usuario
    template_name = 'gestor/usuario_detail.html'
    context_object_name = 'usuario'

class GestorUsuarioCreateView(GestorRequiredMixin, CreateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'gestor/usuario_form.html'
    success_url = '/gestor/usuarios/'

class GestorUsuarioUpdateView(GestorRequiredMixin, UpdateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'gestor/usuario_form.html'
    success_url = '/gestor/usuarios/'

class GestorUsuarioDeleteView(GestorRequiredMixin, DeleteView):
    model = Usuario
    template_name = 'gestor/usuario_confirm_delete.html'
    success_url = '/gestor/usuarios/'

# Login/logout comunes
class UserLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

class UserLogoutView(LogoutView):
    next_page = '/'

def home(request):
    return render(request, 'cliente/genericos.html')