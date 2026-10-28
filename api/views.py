import json
import cmath

from django.shortcuts import render
from django.http import JsonResponse
from .models import Usuario

from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import RegistroNumeros
from .models import CalculoBhaskara

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


def formatar_calculo(calculo):
    return {
        "numero_calculo": calculo.numero_calculo,
        "a": calculo.a,
        "b": calculo.b,
        "c": calculo.c,
        "delta": calculo.delta,
        "raiz1": {
            "real": calculo.raiz1_real,
            "imaginaria": calculo.raiz1_imag,
        },
        "raiz2": {
            "real": calculo.raiz2_real,
            "imaginaria": calculo.raiz2_imag,
        },
        "criado_em": calculo.criado_em.isoformat(),
    }


@csrf_exempt
@require_http_methods(["POST", "GET"])
def calculos(request):
    if request.method == "GET":
        resultados = CalculoBhaskara.objects.all().order_by("numero_calculo")
        return JsonResponse(
            [formatar_calculo(item) for item in resultados],
            safe=False,
        )

    try:
        dados = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"erro": "Envie um JSON válido."}, status=400)

    if not isinstance(dados, dict):
        return JsonResponse({"erro": "O corpo deve ser um objeto JSON."}, status=400)

    valores = [dados.get("a"), dados.get("b"), dados.get("c")]

    if any(not isinstance(valor, int) or isinstance(valor, bool) for valor in valores):
        return JsonResponse(
            {"erro": "Envie a, b e c como números inteiros."},
            status=400,
        )

    a, b, c = valores

    if a == 0:
        return JsonResponse(
            {"erro": "O valor de a não pode ser zero."},
            status=400,
        )

    delta = b**2 - 4 * a * c
    raiz_delta = cmath.sqrt(delta)

    raiz1 = (-b + raiz_delta) / (2 * a)
    raiz2 = (-b - raiz_delta) / (2 * a)

    calculo = CalculoBhaskara.objects.create(
        a=a,
        b=b,
        c=c,
        delta=delta,
        raiz1_real=raiz1.real,
        raiz1_imag=raiz1.imag,
        raiz2_real=raiz2.real,
        raiz2_imag=raiz2.imag,
    )

    return JsonResponse(formatar_calculo(calculo), status=201)


@require_http_methods(["GET"])
def calculo_por_numero(request, numero_calculo):
    try:
        calculo = CalculoBhaskara.objects.get(numero_calculo=numero_calculo)
    except CalculoBhaskara.DoesNotExist:
        return JsonResponse({"erro": "Cálculo não encontrado."}, status=404)

    return JsonResponse(formatar_calculo(calculo))