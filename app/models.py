from django.db import models

class Model(models.Model):  # Corrigido para a convenção de nomenclatura
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
