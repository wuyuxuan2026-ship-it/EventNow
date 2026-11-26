import os
from copy import deepcopy
from datetime import time, timedelta

from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from .settings import *  # noqa: F403


render_hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if render_hostname:
    ALLOWED_HOSTS = [*ALLOWED_HOSTS, render_hostname]  # noqa: F405

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

MIDDLEWARE = [  # noqa: F405
    MIDDLEWARE[0],
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "eventnow.demo.PublicDemoMiddleware",
    *MIDDLEWARE[1:],
]
TEMPLATES = deepcopy(TEMPLATES)  # noqa: F405
TEMPLATES[0]["OPTIONS"]["context_processors"].append("eventnow.demo.demo_context")


def demo_context(request):
    return {"public_demo": True}


class PublicDemoMiddleware(MiddlewareMixin):
    """Expose the original public event pages with sample data only."""

    def process_request(self, request):
        if request.method not in {"GET", "HEAD"}:
            return HttpResponseNotAllowed(["GET", "HEAD"])
        if request.path == "/":
            return redirect("home")
        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.resolver_match.url_name not in {"home", "events", "detail"}:
            return redirect("events")
        return None


def seed_demo():
    from django.contrib.auth import get_user_model
    from django.db import transaction

    from eventnowapp.models import Event, Session

    events = [
        (
            "Brisbane Developers Meetup",
            "Meet local developers and explore how a Django app handles a request from the browser to the database.",
            "Brisbane City Library",
            "Technology",
            ("From Browser to Django", "Build an HTMX Feature"),
        ),
        (
            "Creative Design Workshop",
            "Work through a design brief and turn your ideas into a portfolio-ready prototype.",
            "South Bank Studio",
            "Design",
            ("Sketching the User Journey", "Prototype Review"),
        ),
        (
            "Campus Music Night",
            "An evening of live performances and a behind-the-scenes session for student musicians.",
            "St Lucia Arts Centre",
            "Music",
            ("Sound Check and Setup", "Live Performances"),
        ),
    ]
    with transaction.atomic():
        organiser, created = get_user_model().objects.get_or_create(username="EventNow Demo")
        if created:
            organiser.set_unusable_password()
            organiser.save(update_fields=["password"])

        for offset, (title, description, location, category, sessions) in enumerate(events, start=1):
            event, _ = Event.objects.update_or_create(
                organiser=organiser,
                title=title,
                defaults={
                    "description": description,
                    "date": timezone.localdate() + timedelta(days=7 * offset),
                    "location": location,
                    "category": category,
                    "capacity": 60,
                },
            )
            for hour, session_title in zip((10, 11), sessions, strict=True):
                Session.objects.update_or_create(
                    event=event,
                    title=session_title,
                    defaults={
                        "start_time": time(hour),
                        "end_time": time(hour, 45),
                        "speaker": "Demo host",
                        "capacity": 30,
                        "room": "Main room",
                    },
                )
