from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.

class AppMainPageView(TemplateView):
    template_name="webscoring.html"
