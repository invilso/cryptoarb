from django.shortcuts import render
from .tasks import *

# Create your views here.
def BinanceView(request):
    x = create_queryes.delay()
    print(x)
    return render(request, 'main/item.html', {})