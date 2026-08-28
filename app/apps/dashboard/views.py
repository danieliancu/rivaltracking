from django.shortcuts import render


def overview(request):
    return render(request, "stub.html", {"page_title": "Overview"})
