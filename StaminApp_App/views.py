from django.shortcuts import render, redirect
from .models import Usuario
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import UsuarioForm
from django.contrib.auth.decorators import login_required

# Create your views here.

# ---------- Ficha socio ----------

class UsuarioListView(ListView): # Vista solo para los clientes
    model = Usuario
    template_name = 'cliente/usuario_list.html'
    context_object_name = 'usuarios'

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
'''
class UsuarioDeleteView(DeleteView):
    model = Usuario
    template_name = 'cliente/usuario_confirm_delete.html'
    success_url = '/usuario/'
'''