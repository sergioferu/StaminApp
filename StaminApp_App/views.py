from django.shortcuts import render, redirect
from .models import Usuario
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .forms import UsuarioForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import logout as auth_logout
from django.urls import reverse_lazy
from django.db.models import Sum, Count

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

# Productos: cliente puede ver lista y detalle
class ProductoListView(ListView):
    model = getattr(__import__('StaminApp_App.models', fromlist=['Producto']), 'Producto')
    template_name = 'productos/producto_list.html'
    context_object_name = 'productos'

class ProductoDetailView(DetailView):
    model = getattr(__import__('StaminApp_App.models', fromlist=['Producto']), 'Producto')
    template_name = 'productos/producto_detail.html'
    context_object_name = 'producto'

# Gestor: CRUD de productos
class GestorProductoListView(GestorRequiredMixin, ListView):
    model = getattr(__import__('StaminApp_App.models', fromlist=['Producto']), 'Producto')
    template_name = 'gestor/producto_list.html'
    context_object_name = 'productos'

class GestorProductoCreateView(GestorRequiredMixin, CreateView):
    model = getattr(__import__('StaminApp_App.models', fromlist=['Producto']), 'Producto')
    form_class = getattr(__import__('StaminApp_App.forms', fromlist=['ProductoForm']), 'ProductoForm')
    template_name = 'gestor/producto_form.html'
    success_url = '/gestor/productos/'

class GestorProductoUpdateView(GestorRequiredMixin, UpdateView):
    model = getattr(__import__('StaminApp_App.models', fromlist=['Producto']), 'Producto')
    form_class = getattr(__import__('StaminApp_App.forms', fromlist=['ProductoForm']), 'ProductoForm')
    template_name = 'gestor/producto_form.html'
    success_url = '/gestor/productos/'

class GestorProductoDeleteView(GestorRequiredMixin, DeleteView):
    model = getattr(__import__('StaminApp_App.models', fromlist=['Producto']), 'Producto')
    template_name = 'gestor/producto_confirm_delete.html'
    success_url = '/gestor/productos/'

# Pagos: gestor puede ver pagos y agregados por producto
class GestorPagoListView(GestorRequiredMixin, ListView):
    model = getattr(__import__('StaminApp_App.models', fromlist=['Pago']), 'Pago')
    template_name = 'gestor/pago_list.html'
    context_object_name = 'pagos'

    def get_queryset(self):
        # incluir información del producto y usuario; mostrar todos los pagos
        return self.model.objects.select_related('usuario', 'producto').all()

# Vista resumen de ventas por producto
class GestorProductoVentasView(GestorRequiredMixin, ListView):
    template_name = 'gestor/producto_ventas.html'
    context_object_name = 'ventas'

    def get_queryset(self):
        Producto = getattr(__import__('StaminApp_App.models', fromlist=['Producto']), 'Producto')
        Pago = getattr(__import__('StaminApp_App.models', fromlist=['Pago']), 'Pago')
        return Producto.objects.annotate(
            total_vendido=Sum('pago__monto'),
            ventas_cantidad=Count('pago')
        ).order_by('-ventas_cantidad')

# Login/logout comunes
class UserLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        rol = getattr(user, 'rol', '')
        if user.is_superuser:
            return reverse_lazy('dashboard')
        if rol and rol.lower() == 'gestor':
            return reverse_lazy('gestor-usuario-list')
        # default to cliente area
        return reverse_lazy('usuario-list')

class UserLogoutView(LogoutView):
    next_page = '/login/'

def logout_view(request):
    """Log out the user and redirect to login (accept any HTTP method)."""
    auth_logout(request)
    return redirect('login')

def home(request):
    return render(request, 'base.html')