from http.client import responses
from django.shortcuts import render
from .serializers import RegisterUserSerializer, UserProfileSerializer
from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .tokens import create_jwt_pair
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from .throttles import LoginRateThrottle
from rest_framework.throttling import ScopedRateThrottle


class RegisterUserView(generics.CreateAPIView):
    serializer_class = RegisterUserSerializer
    permission_classes = [AllowAny]

    def post(self, request: Request):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "message": "User registered successfully",
                "data": serializer.data,
            }
            return Response(data=response, status=status.HTTP_201_CREATED)

        else:
            response = {
                "message": "User registration failed",
                "data": serializer.errors,
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)

        if user is not None:
            tokens = create_jwt_pair(user)
            response = {
                "message": "User Logged In Successfully",
                "data": {"email": user.email, "tokens": tokens},
            }
            return Response(data=response, status=status.HTTP_200_OK)
        response = {"message": "Invalid Credentials"}
        return Response(data=response, status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request: Request):
        content = {"user": str(request.user), "auth": str(request.auth)}
        return Response(data=content, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        user = request.user
        serializer = UserProfileSerializer(user, context={"request": request})
        response_data = dict(serializer.data)

        # Format the balance if it exists in the response
        if 'balance' in response_data and response_data['balance'] is not None:
            response_data['balance'] = f"₦{float(response_data['balance']):,.2f}"

        response = {
            "message": "User profile fetched successfully",
            "data": response_data,
        }
        return Response(data=response, status=status.HTTP_200_OK)