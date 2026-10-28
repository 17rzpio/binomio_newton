from django.urls import path
from .views import hello_world
from .views import usuarios
from .views import registro_por_id, registros
from .views import calculo_por_numero, calculos

urlpatterns = [
    path("hello/", hello_world),
    path("usuarios/", usuarios),
    path("numeros/", registros, name="registros"),
    path("numeros/<int:registro_id>/", registro_por_id, name="registro_por_id"),
    path("calculos/", calculos, name="calculos"),
    path(
        "calculos/<int:numero_calculo>/",
        calculo_por_numero,
        name="calculo_por_numero",
    ),
]