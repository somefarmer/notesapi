from rest_framework import permissions
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .models import Note
from .serializers import NoteSerializer

from notesapi.permissions import IsOwner
from .renderers import NoteRenderer

class NotesAPIView(ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    renderer_classes = (NoteRenderer,)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
class NoteAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated, IsOwner,)
    queryset = Note.objects.all()
    lookup_field = "id"
    serializer_class = NoteSerializer
    renderer_classes = (NoteRenderer,)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
