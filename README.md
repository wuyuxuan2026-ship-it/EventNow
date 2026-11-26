# EventNow

EventNow is a Django event management and registration platform built for a course project at The University of Queensland. It uses Django, Bootstrap, and HTMX.

- Create events with multiple sessions, manage registrations, and archive events.
- Browse events and register for individual sessions.
- Generate résumé bio suggestions and practise interviews with an AI coach.

## Run locally

Use Python 3.12 or newer. In Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Open [EventNow](http://127.0.0.1:8000/eventnow/) and create an account. For the admin dashboard, run `manage.py createsuperuser` with the same virtual environment. Add your own `OPENAI_API_KEY` to `.env` to use the AI features. SQLite is the default local database.

For a MySQL deployment, install `mysqlclient` and set `MYSQL_DATABASE`, `MYSQL_USER`, and `MYSQL_PASSWORD`. Set `DJANGO_DEBUG=false`, a private `DJANGO_SECRET_KEY`, and your deployment hosts and trusted origins in the environment.

## AI collaboration

ChatGPT helped brainstorm the registration flow, debug multiple-session form submissions, plan the AI integrations, and generate event artwork. The multi-session form uses Django's `request.POST.getlist()` to read repeated fields.

EventNow was originally deployed to UQCloud as part of the course project.
