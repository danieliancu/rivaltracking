from django.shortcuts import render


def index(request):
    return render(request, "stub.html", {"page_title": "Reports"})


def detail(request, report_id):
    return render(request, "stub.html", {"page_title": "Report details"})
