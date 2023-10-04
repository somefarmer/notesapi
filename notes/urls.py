from django.urls import path

from .views import NotesAPIView, NoteAPIView

urlpatterns = [
    path("", NotesAPIView.as_view(), name="notes"),
    path("<int:id>/", NoteAPIView.as_view(), name="note")
]