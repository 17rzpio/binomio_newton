import json

from django.shortcuts import render
from django.http import JsonResponse
from .models import Usuario

from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import RegistroNumeros

def hello_world(request):
    return HttpResponse("Hello World!")
# Create your views here.

def usuarios(request):
    usuarios = Usuario.objects.all()

    dados = []

    for usuario in usuarios:
        dados.append({
            "id": usuario.id,
            "nome": usuario.nome
        })

    return JsonResponse(dados, safe=False)

def serializar(registro):
    return {
        "id": registro.id,
        "quantidade": registro.quantidade,
        "numeros": registro.numeros,
        "pares": registro.pares,
        "impares": registro.impares,
        "criado_em": registro.criado_em.isoformat(),
    }


def ler_json(request):
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


@csrf_exempt
@require_http_methods(["GET", "POST"])
def registros(request):
    if request.method == "GET":
        dados = [serializar(item) for item in RegistroNumeros.objects.all()]
        return JsonResponse(dados, safe=False)

    dados = ler_json(request)
    if not isinstance(dados, dict):
        return JsonResponse({"erro": "Envie um JSON válido."}, status=400)

    quantidade = dados.get("quantidade")
    numeros = dados.get("numeros")

    if not isinstance(quantidade, int) or isinstance(quantidade, bool):
        return JsonResponse({"erro": "quantidade deve ser um número inteiro."}, status=400)

    if not isinstance(numeros, list):
        return JsonResponse({"erro": "numeros deve ser uma lista de inteiros."}, status=400)

    try:
        registro = RegistroNumeros.objects.create(
            quantidade=quantidade,
            numeros=numeros,
        )
    except ValidationError as erro:
        return JsonResponse({"erro": erro.message_dict}, status=400)

    return JsonResponse(serializar(registro), status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def registro_por_id(request, registro_id):
    try:
        registro = RegistroNumeros.objects.get(id=registro_id)
    except RegistroNumeros.DoesNotExist:
        return JsonResponse({"erro": "Registro não encontrado."}, status=404)

    if request.method == "GET":
        return JsonResponse(serializar(registro))

    if request.method == "DELETE":
        registro.delete()
        return JsonResponse({"mensagem": "Registro excluído."})

    dados = ler_json(request)
    if not isinstance(dados, dict):
        return JsonResponse({"erro": "Envie um JSON válido."}, status=400)

    if request.method == "PUT" and not {"quantidade", "numeros"}.issubset(dados):
        return JsonResponse({
            "erro": "PUT exige os campos quantidade e numeros."
        }, status=400)

    quantidade = dados.get("quantidade", registro.quantidade)
    numeros = dados.get("numeros", registro.numeros)

    if not isinstance(quantidade, int) or isinstance(quantidade, bool):
        return JsonResponse({"erro": "quantidade deve ser um número inteiro."}, status=400)

    if not isinstance(numeros, list):
        return JsonResponse({"erro": "numeros deve ser uma lista de inteiros."}, status=400)

    registro.quantidade = quantidade
    registro.numeros = numeros

    try:
        registro.save()
    except ValidationError as erro:
        return JsonResponse({"erro": erro.message_dict}, status=400)

    return JsonResponse(serializar(registro))