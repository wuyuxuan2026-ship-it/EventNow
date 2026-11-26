#ChatGPT was used to provide ideas for debugging.
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from django.conf import settings
import markdown
from django.utils.safestring import mark_safe
from .models import Event, Session, Registration, UserDetail, Qualification, WorkExperience

class BioSuggestions(BaseModel):
    
    suggestions: List[str] = Field(description="List of improved resume bio alternatives")

def home_view(request):
    return render(request, "home.html")

def add_capacity_info_to_session(session):
    registered_count = Registration.objects.filter(
        session=session
    ).exclude(status="Cancelled").count()

    session.registered_count = registered_count
    session.remaining_capacity = session.capacity - registered_count

    return session


def event_view(request):
    events = Event.objects.filter(is_archived=False).order_by("-created_at")
    return render(request, "event.html", {"events": events})


def detail_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    sessions = Session.objects.filter(event=event).order_by("start_time")

    for session in sessions:
        add_capacity_info_to_session(session)

    return render(request, "detail.html", {
        "event": event,
        "sessions": sessions,
    })

@login_required(login_url='login')
def edit_event_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    
    if event.organiser != request.user and not request.user.is_superuser:
     messages.error(request, 'You not edit this event.')
     return redirect('detail', event_id=event.id)
    session = event.session_set.first()

    if request.method == 'POST':
        event.title = request.POST.get('title')
        event.description = request.POST.get('description')
        event.date = request.POST.get('date')
        event.location = request.POST.get('location')
        event.category = request.POST.get('category')
        event.capacity = request.POST.get('capacity')
        event.save()

        session_title = request.POST.get('session_title')
        session_start_time = request.POST.get('session_start_time')
        session_end_time = request.POST.get('session_end_time')
        session_speaker = request.POST.get('session_speaker')
        session_capacity = request.POST.get('session_capacity')
        session_room = request.POST.get('session_room')

        if session:
            session.title = session_title
            session.start_time = session_start_time
            session.end_time = session_end_time
            session.speaker = session_speaker
            session.capacity = session_capacity
            session.room = session_room
            session.save()
        else:
            Session.objects.create(
                event=event,
                title=session_title,
                start_time=session_start_time,
                end_time=session_end_time,
                speaker=session_speaker,
                capacity=session_capacity,
                room=session_room
            )

        messages.success(request, 'Event updated successfully!')
        return redirect('detail', event_id=event.id)

    return render(request, 'edit_event.html', {
        'event': event,
        'session': session,
    })


@login_required(login_url="login")
def create_event(request):
    if request.method == "POST":
        event = Event.objects.create(
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            date=request.POST.get("date"),
            location=request.POST.get("location"),
            category=request.POST.get("category"),
            capacity=request.POST.get("capacity"),
            organiser=request.user,
        )

        session_titles = request.POST.getlist("session_title")
        session_start_times = request.POST.getlist("session_start_time")
        session_end_times = request.POST.getlist("session_end_time")
        session_speakers = request.POST.getlist("session_speaker")
        session_capacities = request.POST.getlist("session_capacity")
        session_rooms = request.POST.getlist("session_room")

       

        for i in range(len(session_titles)):
            Session.objects.create(
                event=event,
                title=session_titles[i],
                start_time=session_start_times[i],
                end_time=session_end_times[i],
                speaker=session_speakers[i],
                capacity=session_capacities[i],
                room=session_rooms[i],
            )

        messages.success(request, f"Event created successfully. {len(session_titles)} sessions created.")
        return redirect("detail", event_id=event.id)

    return render(request, "creat_event.html")

@login_required(login_url="login")
def track_view(request):
    registrations = Registration.objects.filter(
        user=request.user
    ).select_related("event", "session").order_by("-registration_date")

    for reg in registrations:
        if reg.session:
            add_capacity_info_to_session(reg.session)

    return render(request, "track.html", {
        "registrations": registrations,
    })


@login_required(login_url="login")
def register_event_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    registration, created = Registration.objects.get_or_create(
        user=request.user,
        event=event,
        defaults={"status": "Registered"},
    )

    if created:
        messages.success(request, "You have successfully registered for this event.")
    else:
        messages.info(request, "You have already registered for this event.")

    return redirect("track")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password,
        )
        
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html")

#OpenAI provide idea for register form
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "register.html")

        User.objects.create_user(
            username=username,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

        messages.success(request, "Registration successful. Please log in.")
        return redirect("login")

    return render(request, "register.html")


def logout_view(request):
    logout(request)
    return redirect("home")

@login_required(login_url="login")
def dashboard_view(request):
    return render(request, "dashboard.html")

def feedback_view(request):
    return render(request, "feedback.html")

@login_required(login_url='login')
def delete_session_view(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    event = session.event

    if event.organiser != request.user and not request.user.is_superuser:
        messages.error(request, 'You are not allowed to delete this session.')
        return redirect('detail', event_id=event.id)

    if request.method == 'POST':
        session.delete()
        messages.success(request, 'Session deleted successfully.')
        return redirect('detail', event_id=event.id)

    return render(request, 'delete_session.html', {
        'session': session,
        'event': event,
    })

@login_required(login_url='login')
def myresume(request):
    user_detail, created = UserDetail.objects.get_or_create(
        user=request.user,
        defaults={
            'firstname': request.user.first_name or '',
            'surname': request.user.last_name or '',
            'mobileno': '',
            'bio': 'Novice Django Developer but building unique projects.'
        }
    )

    qualifications = Qualification.objects.filter(user_detail=user_detail)
    work_experience = WorkExperience.objects.filter(user_detail=user_detail)

    return render(request, 'resume.html', {
        'user_detail': user_detail,
        'name': f"{user_detail.firstname} {user_detail.surname}",
        'mobileno': user_detail.mobileno,
        'bio': user_detail.bio,
        'user_id': user_detail.id,
        'qualifications': qualifications,
        'work_experience': work_experience,
    })


def suggest_bio(request, user_id):
    user_detail = get_object_or_404(UserDetail, id=user_id)
    bio = user_detail.bio or "Experienced professional in the tech industry."

    parser = JsonOutputParser(pydantic_object=BioSuggestions)

    prompt = PromptTemplate(
        template=(
            "You are a professional resume writer.\n"
            "Rewrite the following summary to improve its impact and clarity. "
            "Provide 5 alternative versions.\n\n"
            "{format_instructions}\n\n"
            "Bio: {bio}"
        ),
        input_variables=["bio"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    llm = ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model="gpt-5.4-mini",
        temperature=0.7,
    )

    chain = prompt | llm | parser

    try:
        result = chain.invoke({"bio": bio})
        suggestions = result["suggestions"]
    except Exception:
        suggestions = []

    return render(request, "partials/_bio_suggestions.html", {
        "suggestions": suggestions,
        "user_id": user_detail.id,
    })

def select_bio(request, user_id):
    new_bio = request.POST.get("newbio")

    user_detail = get_object_or_404(UserDetail, id=user_id)
    user_detail.bio = new_bio
    user_detail.save()

    return render(request, "partials/_bio_section.html", {
        "bio": user_detail.bio,
        "user_id": user_detail.id,
    })

@login_required(login_url='login')
def chatui(request, user_id):
    user_detail = get_object_or_404(UserDetail, id=user_id)

    request.session['chat_history'] = []
    request.session['chat_bio'] = user_detail.bio or "No bio provided"

    return render(request, "chatui.html", {
        "name": f"{user_detail.firstname} {user_detail.surname}",
        "user_id": user_detail.id,
    })

#ChatGPT offer idea for AI deploied.
@login_required(login_url='login')
def chatbot(request):
    if request.method != "POST":
        return HttpResponse("", status=405)

    user_message = request.POST.get("message", "").strip()

    if not user_message:
        return HttpResponse("")

    system_prompt = build_general_system_prompt()

    history = request.session.get('chat_history', [])

    if not history or history[0].get("role") != "system":
        history.insert(0, {"role": "system", "content": system_prompt})
    else:
        history[0] = {"role": "system", "content": system_prompt}

    history.append({"role": "human", "content": user_message})

    langchain_messages = []

    for msg in history:
        role = msg["role"]

        if role == "system":
            langchain_messages.append(("system", msg["content"]))
        elif role in ("human", "user"):
            langchain_messages.append(("human", msg["content"]))
        elif role == "assistant":
            langchain_messages.append(("assistant", msg["content"]))

    try:
        llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-5.4-mini",
            temperature=0.7,
        )

        response = llm.invoke(langchain_messages)
        bot_reply = response.content

    except Exception as e:
        bot_reply = f"Sorry, an error occurred: {e}"

    history.append({"role": "assistant", "content": bot_reply})
    request.session['chat_history'] = history
    request.session.modified = True

    return render(request, "partials/_chat_exchange.html", {
        "user_message": user_message,
        "bot_message": mark_safe(markdown.markdown(bot_reply)),
    })


@login_required(login_url='login')
def chatbot_init(request):
    system_prompt = build_general_system_prompt()

    bot_reply = (
        "Hi, I’m your EventNow AI assistant. "
        "You can ask me about events, sessions, recommendations, or general questions."
    )

    request.session['chat_history'] = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": bot_reply},
    ]
    request.session.modified = True

    return render(request, "partials/_chat_message.html", {
        "message": mark_safe(markdown.markdown(bot_reply)),
        "is_user": False,
    })

def build_event_context():
    events = Event.objects.prefetch_related('session_set').order_by('date')

    event_text = ""

    for event in events:
        event_text += f"""
Event ID: {event.id}
Title: {event.title}
Description: {event.description}
Date: {event.date}
Location: {event.location}
Category: {event.category}
Capacity: {event.capacity}
"""

        sessions = event.session_set.all()

        if sessions:
            event_text += "Sessions:\n"
            for session in sessions:
                event_text += f"- {session.title}, {session.start_time} to {session.end_time}, Speaker: {session.speaker}\n"

        event_text += "\n"

    return event_text

@login_required(login_url='login')
def my_events_view(request):
    events = Event.objects.filter(organiser=request.user)

    for event in events:
        active_registrations = Registration.objects.filter(event=event).exclude(status='Cancelled')

        event.registration_count = active_registrations.count()
        event.remaining_capacity = event.capacity - event.registration_count
        event.active_registrations = active_registrations

    return render(request, 'my_events.html', {
        'events': events
    })

def build_general_system_prompt():
    event_context = build_event_context()

    return f"""
You are a helpful general AI assistant inside the EventNow website.

You can answer general questions, casual conversation, study questions, coding questions, and EventNow-related questions.

When the user asks about EventNow events, sessions, speakers, dates, locations, or recommendations, use the EventNow event data below.

When the user asks a general question that is not related to EventNow, answer normally using your general knowledge.

If the user asks about EventNow information and the answer is not in the EventNow data, say that the EventNow information is not currently available.

Do not invent fake EventNow events, sessions, speakers, dates, or locations.

EventNow data:
{event_context}
"""

@login_required(login_url='login')
def change_mydetial(request):
    return  render(request, 'mydetial.html', {
   
    })

@login_required(login_url='login')
def edit_session_view(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    event = session.event

    if event.organiser != request.user and not request.user.is_superuser:
        messages.error(request, 'You are not allowed to edit this session.')
        return redirect('detail', event_id=event.id)

    if request.method == 'POST':
        session.title = request.POST.get('session_title')
        session.speaker = request.POST.get('session_speaker')
        session.room = request.POST.get('session_room')
        session.start_time = request.POST.get('session_start_time')
        session.end_time = request.POST.get('session_end_time')
        session.capacity = request.POST.get('session_capacity')
        session.save()

        messages.success(request, 'Session updated successfully.')
        return redirect('detail', event_id=event.id)

    return render(request, 'edit_session.html', {
        'session': session,
        'event': event,
    })
@login_required(login_url="login")
def register_session_view(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    event = session.event

    active_count = Registration.objects.filter(
        session=session
    ).exclude(status="Cancelled").count()

    if active_count >= session.capacity:
        messages.error(request, "This session is already full.")
        return redirect("detail", event_id=event.id)

    registration, created = Registration.objects.get_or_create(
        user=request.user,
        session=session,
        defaults={
            "event": event,
            "status": "Registered",
        }
    )

    if created:
        messages.success(request, "You have successfully registered for this session.")
    else:
        messages.info(request, "You have already registered for this session.")

    return redirect("track")

@login_required(login_url='login')
def archive_subscription_view(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id)

    if request.method == "POST":
        subscription.is_archived = True
        subscription.save()
        messages.success(request, "Subscription archived successfully.")
        return redirect("subscription_list")

    return redirect("subscription_list")
@login_required(login_url='login')
def delete_event_view(request, event_id):
    session = get_object_or_404(event, id=event_id)
    event = session.event

    if event.organiser != request.user and not request.user.is_superuser:
        messages.error(request, 'You are not allowed to delete this session.')
        return redirect('detail', event_id=event.id)

    if request.method == 'POST':
        session.delete()
        messages.success(request, 'Session deleted successfully.')
        return redirect('detail', event_id=event.id)

    return render(request, 'delete_session.html', {
        'session': session,
        'event': event,
    })
@login_required(login_url='login')
def archive_event_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if event.organiser != request.user and not request.user.is_superuser:
        messages.error(request, 'You are not allowed to archive this event.')
        return redirect('detail', event_id=event.id)

    if request.method == 'POST':
        event.is_archived = True
        event.save()
        messages.success(request, 'Event archived successfully.')
        return redirect('my_events')

    return redirect('detail', event_id=event.id)