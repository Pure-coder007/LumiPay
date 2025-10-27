from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'cards'

router = DefaultRouter()

urlpatterns = [
    # Create a new card
    path('create/', views.CreateCardView.as_view(), name='create-card'),
    
    # List all cards for the authenticated user
    path('my-cards/', views.UserCardsView.as_view(), name='user-cards'),
    
    # View or deactivate a specific card
    path('<uuid:id>/', views.CardDetailView.as_view(), name='card-detail'),
]

urlpatterns += router.urls