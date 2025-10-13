from http.client import responses
from django.shortcuts import render
from .serializers import RegisterUserSerializer
from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
# from .tokens import create_jwt_pair
from rest_framework.permissions import AllowAny


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
                "data": serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)

        else:
            response = {
                "message": "User registration failed",
                "data": serializer.errors
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)



