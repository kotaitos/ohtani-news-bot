from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def hello(request):
    return HttpResponse('''
    ver 1.1
    試合結果
    時差&AMPM考慮
    ''')
