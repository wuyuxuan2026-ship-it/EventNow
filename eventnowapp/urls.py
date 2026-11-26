from django.urls import path
from . import views

urlpatterns = [

    path("", views.home_view, name="home"),
    path("events/", views.event_view, name="events"),
    path("event/<int:event_id>/", views.detail_view, name="detail"),
    path("create/", views.create_event, name="create_event"),
    path("track/", views.track_view, name="track"),
    path("register-event/<int:event_id>/", views.register_event_view, name="register_event"),

    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("register-session/<int:session_id>/", views.register_session_view, name="register_session"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("feedback/", views.feedback_view, name="feedback"),
    
    path('event/<int:event_id>/edit/', views.edit_event_view, name='edit_event'),
   
    path('session/<int:session_id>/delete/', views.delete_session_view, name='delete_session'),
    path("suggest_bio/<int:user_id>/", views.suggest_bio, name="suggest_bio"),
    path("select_bio/<int:user_id>/", views.select_bio, name="select_bio"),
    
    
    path('resume/', views.myresume, name='myresume'),
    path('resume/', views.myresume, name='myresume'),
    path('event/<int:event_id>/archive/', views.archive_event_view, name='archive_event'),
    path("chatui/<int:user_id>/", views.chatui, name="chatui"),
    path("chatbot/", views.chatbot, name="chatbot"),
    path("chatbot_init/", views.chatbot_init, name="chatbot_init"),

    path('my-events/', views.my_events_view, name='my_events'),
    path('change_mydetial', views.change_mydetial, name='change_mydetial'),

    path('session/<int:session_id>/edit/', views.edit_session_view, name='edit_session'),
    path("subscriptions/<int:subscription_id>/archive/",views.archive_subscription_view,name="archive_subscription"),
    path('event/<int:event_id>/delete/', views.delete_event_view, name='delete_event'),
]