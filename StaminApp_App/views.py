from django.shortcuts import render, redirect
from .models import Usuario
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .forms import UsuarioForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from .models import Usuario, Producto, Pago, Disciplina, Monitor, Clase, Inscripcion, Ejercicio, Marca
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.db.models import Sum, Count, F
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta

# Create your views here.

class UsuarioListView(ListView): # Vista solo para los clientes
    model = Usuario
    template_name = 'cliente/usuario_list.html'
    context_object_name = 'usuario'

    def get_queryset(self):
        return Usuario.objects.filter(id=self.request.user.id)

class UsuarioUpdateView(UpdateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'cliente/usuario_form.html'
    success_url = '/usuario/'

class UsuarioDeleteView(DeleteView):
    model = Usuario
    template_name = 'cliente/usuario_confirm_delete.html'
    success_url = '/usuario/'

# Vistas solo para los gestores: ver, editar y eliminar clientes
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

# Esto intenta importar modelos Producto y Pago (si existen)
try:
    from .models import Producto, Pago
except Exception:
    Producto = None
    Pago = None

# Productos para los clientes
class ProductoListView(ListView):
    model = Producto
    template_name = 'productos/producto_list.html'
    context_object_name = 'productos'

    def get_queryset(self):
        if Producto is None:
            return []
        return Producto.objects.all()

class ProductoDetailView(DetailView):
    model = Producto
    template_name = 'productos/producto_detail.html'
    context_object_name = 'producto'

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


class GestorProductoListView(GestorRequiredMixin, ListView):
    model = Producto
    template_name = 'gestor/producto_list.html'
    context_object_name = 'productos'

    def get_queryset(self):
        if Producto is None:
            return []
        return Producto.objects.all()

class GestorProductoCreateView(GestorRequiredMixin, CreateView):
    model = Producto # ProductoForm está declarado en el formulario (forms.py)
    try:
        from .forms import ProductoForm
        form_class = ProductoForm
    except Exception:
        form_class = None
    template_name = 'gestor/producto_form.html'
    success_url = reverse_lazy('gestor-producto-list')

class GestorProductoUpdateView(GestorRequiredMixin, UpdateView):
    model = Producto
    try:
        from .forms import ProductoForm
        form_class = ProductoForm
    except Exception:
        form_class = None
    template_name = 'gestor/producto_form.html'
    success_url = reverse_lazy('gestor-producto-list')

class GestorProductoDeleteView(GestorRequiredMixin, DeleteView):
    model = Producto
    template_name = 'gestor/producto_confirm_delete.html'
    success_url = reverse_lazy('gestor-producto-list')

# Gestor: lista de pagos
class GestorPagoListView(GestorRequiredMixin, ListView):
    model = Pago
    template_name = 'gestor/pago_list.html'
    context_object_name = 'pagos'

    def get_queryset(self):
        if Pago is None:
            return []
        return Pago.objects.select_related('usuario', 'producto').all()

# Gestor: ventas por producto
class GestorProductoVentasView(GestorRequiredMixin, ListView):
    template_name = 'gestor/producto_ventas.html'
    context_object_name = 'ventas'

    def get_queryset(self):
        if Producto is None:
            return []
        return Producto.objects.annotate(
            total_vendido=Sum('pago__monto'),
            ventas_cantidad=Count('pago')
        ).order_by('-ventas_cantidad')

@login_required
def dashboard(request):
    user = request.user
    today = timezone.now().date()
    context = {}

    # Datos para los gestores y admin
    if user.rol in ('GESTOR', 'ADMIN'):
        total_clientes = Usuario.objects.filter(rol='CLIENTE', fin_bono__gte=today).count()
        clases_hoy = Clase.objects.filter(fecha=today).count()
        bonos_proximos = Usuario.objects.filter(fin_bono__gt=today, fin_bono__lte=today + timedelta(days=7)).count()
        ingresos_mes = Pago.objects.filter(fecha__year=today.year, fecha__month=today.month).aggregate(total=Sum('monto'))['total'] or 0
        proximas_clases = Clase.objects.filter(fecha__gte=today).order_by('fecha', 'hora_inicio')[:5]
        ultimos_pagos = Pago.objects.select_related('usuario', 'producto').order_by('-fecha')[:5]
        bonos_vencer = Usuario.objects.filter(fin_bono__gt=today, fin_bono__lte=today + timedelta(days=7)).order_by('fin_bono')[:10]

        context.update({
            'total_clientes': total_clientes,
            'clases_hoy': clases_hoy,
            'bonos_proximos': bonos_proximos,
            'ingresos_mes': ingresos_mes,
            'proximas_clases': proximas_clases,
            'ultimos_pagos': ultimos_pagos,
            'bonos_vencer': bonos_vencer,
        })

    # Datos para los clientes
    if user.rol == 'CLIENTE':
        mis_clases = Inscripcion.objects.filter(usuario=user, activo=True, clase__fecha__gte=today).count()
        mis_marcas = Marca.objects.filter(usuario=user).count()
        mis_proximas_clases = Inscripcion.objects.filter(usuario=user, activo=True, clase__fecha__gte=today).select_related('clase').order_by('clase__fecha')[:5]
        ultimas_marcas = Marca.objects.filter(usuario=user).order_by('-fecha')[:5]

        dias_restantes = 0
        bono_porcentaje = 0
        if user.fin_bono and user.fin_bono >= today:
            dias_restantes = (user.fin_bono - today).days
            # Estimación del porcentaje respecto a 30 días (si no se conoce la duración original)
            bono_porcentaje = min(100, max(0, int((dias_restantes / 30.0) * 100)))

        context.update({
            'mis_clases': mis_clases,
            'mis_marcas': mis_marcas,
            'mis_proximas_clases': mis_proximas_clases,
            'ultimas_marcas': ultimas_marcas,
            'dias_restantes': dias_restantes,
            'bono_porcentaje': bono_porcentaje,
        })

    return render(request, 'dashboard.html', context)

class GestorClaseListView(GestorRequiredMixin, ListView):
    model = Clase
    template_name = 'gestor/clase_list.html'
    context_object_name = 'clases'

    def get_queryset(self):
        return Clase.objects.select_related('disciplina', 'monitor').order_by('-fecha', 'hora_inicio')

class GestorClaseCreateView(GestorRequiredMixin, CreateView):
    model = Clase
    fields = ['fecha', 'hora_inicio', 'hora_fin', 'disciplina', 'monitor', 'aforo']
    template_name = 'gestor/clase_form.html'
    success_url = reverse_lazy('gestor-clase-list')

class GestorClaseUpdateView(GestorRequiredMixin, UpdateView):
    model = Clase
    fields = ['fecha', 'hora_inicio', 'hora_fin', 'disciplina', 'monitor', 'aforo']
    template_name = 'gestor/clase_form.html'
    success_url = reverse_lazy('gestor-clase-list')

class GestorClaseDeleteView(GestorRequiredMixin, DeleteView):
    model = Clase
    template_name = 'gestor/clase_confirm_delete.html'
    success_url = reverse_lazy('gestor-clase-list')

@login_required
def clases_disponibles(request):
    today = timezone.now().date()
    clases = Clase.objects.filter(fecha__gte=today).order_by('fecha', 'hora_inicio')
    return render(request, 'cliente/clases_disponibles.html', {'clases': clases})

@login_required
def inscribir_clase(request, clase_id):
    clase = get_object_or_404(Clase, id=clase_id)
    # comprobar plazas
    plazas = clase.plazas_disponibles()
    if plazas <= 0:
        messages.error(request, 'No hay plazas disponibles en esta clase.')
        return redirect('clases_disponibles')

    # esto es para evitar duplicados
    insc, created = Inscripcion.objects.get_or_create(clase=clase, usuario=request.user, defaults={'activo': True})
    if not created and insc.activo:
        messages.info(request, 'Ya estás inscrito en esta clase.')
    else:
        insc.activo = True
        insc.save()
        messages.success(request, 'Inscripción realizada.')

    return redirect('clases_disponibles')

@login_required
def cancelar_inscripcion(request, inscripcion_id):
    insc = get_object_or_404(Inscripcion, id=inscripcion_id)
    if request.method == 'POST':
        if insc.usuario == request.user or request.user.rol in ('GESTOR', 'ADMIN'):
            insc.activo = False
            insc.save()
            messages.success(request, 'Inscripción cancelada.')
        else:
            messages.error(request, 'No tienes permiso para cancelar esta inscripción.')
    return redirect('dashboard')

class GestorDisciplinaListView(GestorRequiredMixin, ListView):
    model = Disciplina
    template_name = 'gestor/disciplina_list.html'
    context_object_name = 'disciplinas'

class GestorDisciplinaCreateView(GestorRequiredMixin, CreateView):
    model = Disciplina
    fields = ['nombre']
    template_name = 'gestor/disciplina_form.html'
    success_url = reverse_lazy('gestor-disciplina-list')

class GestorDisciplinaUpdateView(GestorRequiredMixin, UpdateView):
    model = Disciplina
    fields = ['nombre']
    template_name = 'gestor/disciplina_form.html'
    success_url = reverse_lazy('gestor-disciplina-list')

class GestorDisciplinaDeleteView(GestorRequiredMixin, DeleteView):
    model = Disciplina
    template_name = 'gestor/disciplina_confirm_delete.html'
    success_url = reverse_lazy('gestor-disciplina-list')

class GestorMonitorListView(GestorRequiredMixin, ListView):
    model = Monitor
    template_name = 'gestor/monitor_list.html'
    context_object_name = 'monitores'

class GestorMonitorCreateView(GestorRequiredMixin, CreateView):
    model = Monitor
    fields = ['nombre']
    template_name = 'gestor/monitor_form.html'
    success_url = reverse_lazy('gestor-monitor-list')

class GestorMonitorUpdateView(GestorRequiredMixin, UpdateView):
    model = Monitor
    fields = ['nombre']
    template_name = 'gestor/monitor_form.html'
    success_url = reverse_lazy('gestor-monitor-list')

class GestorMonitorDeleteView(GestorRequiredMixin, DeleteView):
    model = Monitor
    template_name = 'gestor/monitor_confirm_delete.html'
    success_url = reverse_lazy('gestor-monitor-list')

class GestorEjercicioListView(GestorRequiredMixin, ListView):
    model = Ejercicio
    template_name = 'gestor/ejercicio_list.html'
    context_object_name = 'ejercicios'

class GestorEjercicioCreateView(GestorRequiredMixin, CreateView):
    model = Ejercicio
    fields = ['nombre']
    template_name = 'gestor/ejercicio_form.html'
    success_url = reverse_lazy('gestor-ejercicio-list')

class GestorEjercicioUpdateView(GestorRequiredMixin, UpdateView):
    model = Ejercicio
    fields = ['nombre']
    template_name = 'gestor/ejercicio_form.html'
    success_url = reverse_lazy('gestor-ejercicio-list')

class GestorEjercicioDeleteView(GestorRequiredMixin, DeleteView):
    model = Ejercicio
    template_name = 'gestor/ejercicio_confirm_delete.html'
    success_url = reverse_lazy('gestor-ejercicio-list')

class MarcaCreateView(LoginRequiredMixin, CreateView):
    model = Marca
    fields = ['ejercicio', 'peso', 'tiempo', 'repeticiones', 'observaciones']
    template_name = 'cliente/marca_form.html'
    success_url = reverse_lazy('mis_marcas')

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)

@login_required
def mis_marcas(request):
    marcas = Marca.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'cliente/mis_marcas.html', {'marcas': marcas})