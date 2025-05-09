from django.shortcuts import render
from .models import * # Certifique-se de que esses modelos estejam corretamente importados

def home(request):
	# Contexto a ser passado para o template
	context = {
			"title": "Estuda Vagão | CMSM"  # Título dinâmico da página
			}
	return render(request, "index.html", context)  # Renderizar o template e passar o contexto
