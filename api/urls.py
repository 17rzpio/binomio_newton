from django.urls import path
from .views import hello_world
from .views import usuarios
from .views import registro_por_id, registros

urlpatterns = [
    path("hello/", hello_world),
    path("usuarios/", usuarios),
    path("numeros/", registros, name="registros"),
    path("numeros/<int:registro_id>/", registro_por_id, name="registro_por_id"),
]