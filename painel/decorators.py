from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


def admin_required(view_func):
    @login_required(login_url="painel:login")
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("Acesso negado.")
        return view_func(request, *args, **kwargs)

    return wrapper