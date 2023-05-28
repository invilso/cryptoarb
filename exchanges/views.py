from django.shortcuts import render
from exchanges.tasks import *
from .services.parser import main

# Create your views here.
def BinanceView(request):
    main()
    return render(request, 'main/item.html', {})