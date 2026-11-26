from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    location = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    capacity = models.IntegerField()
    organiser = models.ForeignKey(User, on_delete=models.CASCADE)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Session(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    start_time = models.TimeField()
    end_time = models.TimeField()
    speaker = models.CharField(max_length=100)
    capacity = models.IntegerField()
    room = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Registration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True, blank=True)

    registration_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=50, default="Registered")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "session")

    def __str__(self):
        if self.session:
            return f"{self.user.username} - {self.session.title}"
        return f"{self.user.username} - {self.event.title}"

class UserDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    mobileno = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(blank=False, default="Novice Django Developer but building unique portfolio")  # <-- NEW FIELD

    def __str__(self):
        return f"Details for {self.user.username}"



class Qualification(models.Model):
    user_detail = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    year = models.CharField(max_length=20)

    def __str__(self):
        return self.title


class WorkExperience(models.Model):
    user_detail = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.position


class Subscription(models.Model):
    PLAN_CHOICES = [
        ("Free", "Free"),
        ("Basic", "Basic"),
        ("Premium", "Premium"),
    ]

    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=50, choices=PLAN_CHOICES, default="Free")
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    is_archived = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.plan}"