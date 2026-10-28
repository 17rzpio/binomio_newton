from django.db import models
from django.core.exceptions import ValidationError

class Usuario(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
# Create your models here.

class RegistroNumeros(models.Model):
    quantidade = models.PositiveIntegerField()
    numeros = models.JSONField(default=list)
    pares = models.PositiveIntegerField(default=0)
    impares = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not isinstance(self.numeros, list):
            raise ValidationError({"numeros": "Envie uma lista de números inteiros."})

        if len(self.numeros) != self.quantidade:
            raise ValidationError({
                "quantidade": "A quantidade deve corresponder ao número de itens enviados."
            })

        if any(not isinstance(numero, int) or isinstance(numero, bool)
               for numero in self.numeros):
            raise ValidationError({"numeros": "Todos os itens devem ser números inteiros."})

    def atualizar_contagem(self):
        self.pares = sum(numero % 2 == 0 for numero in self.numeros)
        self.impares = len(self.numeros) - self.pares

    def save(self, *args, **kwargs):
        self.atualizar_contagem()
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Registro {self.id}: {self.quantidade} números"


class CalculoBhaskara(models.Model):
    numero_calculo = models.BigAutoField(primary_key=True)
    a = models.IntegerField()
    b = models.IntegerField()
    c = models.IntegerField()
    delta = models.BigIntegerField()
    raiz1_real = models.FloatField()
    raiz1_imag = models.FloatField()
    raiz2_real = models.FloatField()
    raiz2_imag = models.FloatField()
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cálculo {self.numero_calculo}"