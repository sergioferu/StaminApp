from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

class Usuario(AbstractUser):
    ROLES = (
        ('ADMIN', 'Administrador'),
        ('GESTOR', 'Gestor'),
        ('CLIENTE', 'Cliente'),
    )

    rol = models.CharField(max_length=10, choices=ROLES)
    fin_bono = models.DateField(null=True, blank=True)

    def bono_activo(self):
        if self.fin_bono:
            return self.fin_bono >= timezone.now().date()
        return False

    def __str__(self):
        return f"{self.username} ({self.rol})"


class Disciplina(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Monitor(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Clase(models.Model):
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    monitor = models.ForeignKey(Monitor, on_delete=models.SET_NULL, null=True)
    aforo = models.PositiveIntegerField()

    def plazas_disponibles(self):
        return self.aforo - self.inscripcion_set.filter(activo=True).count()

    def __str__(self):
        return f"{self.disciplina} - {self.fecha}"


class Inscripcion(models.Model):
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ('clase', 'usuario')

    def __str__(self):
        return f"{self.usuario} en {self.clase}"


class Producto(models.Model):
    TIPOS = (
        (1, 'Tienda'),
        (2, 'Bono'),
    )

    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    tipo = models.IntegerField(choices=TIPOS)
    duracion = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.nombre


class Pago(models.Model):
    METODOS = (
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta'),
        ('TRANSFERENCIA', 'Transferencia'),
    )

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=20, choices=METODOS)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.producto and self.producto.tipo == 2:  # comprueba objeto sea producto y objeto sea producto tipo 2
            if self.producto.duracion:  # comprueba objeto producto tenga duración
                hoy = timezone.now().date()  

                if self.usuario.fin_bono and self.usuario.fin_bono > hoy:  # comprueba que el objeto usuario tenga fin_bono y que fin_bono sea su fecha mayor al dia actual
                    nueva_fecha = self.usuario.fin_bono + timedelta(days=self.producto.duracion) # si es mayor, al finbono le añade el tiempo del bono pagado
                else:
                    nueva_fecha = hoy + timedelta(days=self.producto.duracion) # sino a la fecha actual "hoy" se lo añade

                self.usuario.fin_bono = nueva_fecha # registra la fecha
                self.usuario.save() # guarda el cambio

    def __str__(self):
        return f"Pago de {self.usuario} - {self.monto}€"


class Ejercicio(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Marca(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    peso = models.FloatField(null=True, blank=True)
    tiempo = models.DurationField(null=True, blank=True)
    repeticiones = models.PositiveIntegerField(null=True, blank=True)
    observaciones = models.TextField(blank=True)
    fecha = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - {self.ejercicio}"