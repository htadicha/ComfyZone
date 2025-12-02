from django.shortcuts import render


def custom_404(request, exception):
    """Render a branded 404 page with helpful links."""
    return render(request, "404.html", status=404)
