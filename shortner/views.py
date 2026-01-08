from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError, transaction
from .forms import URLForm
from .models import ShortURL
from .utils import generate_short_code

def home(request):
    """
    Show form, accept POSTed URL, return short code.
    If the URL was shortened before, return the existing code.
    Handles race condition when saving by retrying on IntegrityError.
    """
    if request.method == "POST":
        form = URLForm(request.POST)
        if form.is_valid():
            original = form.cleaned_data["original_url"]

            # If the original URL was already shortened, return that short code.
            existing = ShortURL.objects.filter(original_url=original).first()
            if existing:
                return render(request, "home.html", {"form": form, "short_code": existing.short_code})

            # Try to create a unique short_code, handling possible race conditions.
            for attempt in range(5):  # try a few times before failing
                code = generate_short_code()
                try:
                    with transaction.atomic():
                        obj = ShortURL.objects.create(original_url=original, short_code=code)
                    # success
                    return render(request, "home.html", {"form": URLForm(), "short_code": obj.short_code})
                except IntegrityError:
                    # short_code collision (another process wrote same code). Retry.
                    continue

            # If we reach here, something went wrong (very unlikely).
            form.add_error(None, "Could not generate a unique short code. Please try again.")
    else:
        form = URLForm()

    return render(request, "home.html", {"form": form})


def redirect_url(request, short_code):
    """
    Lookup a ShortURL by code and redirect to the original URL.
    Returns 404 if not found.
    """
    url_obj = get_object_or_404(ShortURL, short_code=short_code)
    return redirect(url_obj.original_url)