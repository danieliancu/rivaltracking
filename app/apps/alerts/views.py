from django.shortcuts import render


def index(request):
    return render(request, "stub.html", {"page_title": "Alerts"})
