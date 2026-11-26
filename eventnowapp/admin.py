from django.contrib import admin
from .models import Event, Session, Registration, Subscription


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'date', 'location', 'category', 'capacity', 'organiser')
    search_fields = ('title', 'description', 'location', 'category')
    list_filter = ('category', 'date')
    ordering = ('-date',)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'title', 'start_time', 'end_time', 'speaker', 'capacity', 'room')
    search_fields = ('title', 'speaker', 'room')
    list_filter = ('event',)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'event', 'registration_date', 'status')
    search_fields = ('user__username', 'event__title', 'status')
    list_filter = ('status', 'registration_date')




@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "owner",
        "plan",
        "start_date",
        "end_date",
        "is_archived",
        "created_at",
    )

    search_fields = (
        "name",
        "owner__username",
        "owner__email",
    )

    list_filter = (
        "plan",
        "is_archived",
        "start_date",
    )

    list_per_page = 10

    actions = [
        "archive_subscriptions",
        "restore_subscriptions",
    ]
    def archive_subscriptions(self, request, queryset):
        queryset.update(is_archived=True)
    archive_subscriptions.short_description = "Archive selected subscriptions"

    def restore_subscriptions(self, request, queryset):
        queryset.update(is_archived=False)

    restore_subscriptions.short_description = "Restore selected subscriptions"

    def has_delete_permission(self, request, obj=None):
        return False