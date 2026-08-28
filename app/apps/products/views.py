from django.shortcuts import render


def index(request):
    return render(request, "stub.html", {"page_title": "Products"})


def detail(request, slug):
    return render(request, "stub.html", {"page_title": "Product details"})
