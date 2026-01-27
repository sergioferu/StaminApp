from django.shortcuts import render, redirect
from .models import Usuario
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .forms import UsuarioForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from .models import Usuario, Producto, Pago
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages

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
    return render(request, 'base.html')

# ===== NUEVAS VISTAS PARA PRODUCTOS Y PAGOS =====
from .models import Producto, Pago
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils import timezone

class ProductoListView(LoginRequiredMixin, ListView):
    """Lista todos los productos disponibles para comprar"""
    model = Producto
    template_name = 'cliente/producto_list.html'
    context_object_name = 'productos'

@login_required
def pagar_producto(request, producto_id):
    """Muestra el formulario de pago y procesa la compra"""
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        metodo_pago = request.POST.get('metodo_pago')
        monto = request.POST.get('monto')
        
        # Validar que el monto coincide con el precio del producto
        if float(monto) != float(producto.precio):
            messages.error(request, 'El monto no coincide con el precio del producto.')
            return redirect('pagar_producto', producto_id=producto.id)
        
        # Crear el pago
        pago = Pago.objects.create(
            usuario=request.user,
            producto=producto,
            monto=monto,
            metodo_pago=metodo_pago
        )
        
        # Si el producto es un bono (tipo 2), el método save() de Pago ya actualiza fin_bono
        if producto.tipo == 2:
            messages.success(request, f'¡Bono activado! Tu bono es válido hasta {request.user.fin_bono}')
        else:
            messages.success(request, '¡Compra realizada con éxito!')
        
        return redirect('pago_exitoso', pago_id=pago.id)
    
    return render(request, 'cliente/producto_pagar.html', {'producto': producto})

@login_required
def pago_exitoso(request, pago_id):
    """Muestra la confirmación del pago"""
    pago = get_object_or_404(Pago, id=pago_id, usuario=request.user)
    return render(request, 'cliente/pago_exitoso.html', {'pago': pago})

@login_required
def mis_pagos(request):
    """Muestra el historial de pagos del usuario actual"""
    pagos = Pago.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'cliente/mis_pagos.html', {'pagos': pagos})


# ===== VISTAS PARA GESTOR (administrar productos) =====
class GestorProductoListView(GestorRequiredMixin, ListView):
    model = Producto
    template_name = 'gestor/producto_list.html'
    context_object_name = 'productos'

class GestorProductoCreateView(GestorRequiredMixin, CreateView):
    model = Producto
    fields = ['nombre', 'precio', 'tipo', 'duracion']
    template_name = 'gestor/producto_form.html'
    success_url = '/gestor/productos/'

class GestorProductoUpdateView(GestorRequiredMixin, UpdateView):
    model = Producto
    fields = ['nombre', 'precio', 'tipo', 'duracion']
    template_name = 'gestor/producto_form.html'
    success_url = '/gestor/productos/'

class GestorProductoDeleteView(GestorRequiredMixin, DeleteView):
    model = Producto
    template_name = 'gestor/producto_confirm_delete.html'
    success_url = '/gestor/productos/'