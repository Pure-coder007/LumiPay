from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Card
from .serializers import CreateCard


class CreateCardView(generics.CreateAPIView):
    """
    API endpoint that allows authenticated users to create a new card.
    The card will be automatically linked to the authenticated user.
    """
    serializer_class = CreateCard
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        # The serializer's create method will handle the card creation
        serializer.save()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED, 
            headers=headers
        )


class UserCardsView(generics.ListAPIView):
    """
    API endpoint that lists all cards for the authenticated user.
    """
    serializer_class = CreateCard
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only return active cards for the current user
        return Card.objects.filter(user=self.request.user, is_active=True)


class CardDetailView(generics.RetrieveDestroyAPIView):
    """
    API endpoint to view or deactivate a specific card.
    Cards are soft-deleted (marked as inactive) rather than actually deleted.
    """
    serializer_class = CreateCard
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        # Only allow users to see their own cards
        return Card.objects.filter(user=self.request.user)
    
    def perform_destroy(self, instance):
        # Instead of deleting, mark the card as inactive
        instance.is_active = False
        instance.save()
