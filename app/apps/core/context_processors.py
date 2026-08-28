"""Context shared by the application shell (sidebar + header) on every page."""


def shell(request):
    return {
        "date_range": request.session.get("date_range", "30d"),
    }
