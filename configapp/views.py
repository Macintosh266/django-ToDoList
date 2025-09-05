from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import render,get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from configapp.serializers import *
from .make_token import *


class LoginUser(APIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self,request):
        serialize=LoginSerializer(data=request.data)
        serialize.is_valid(raise_exception=True)
        user=get_object_or_404(User,username=serialize.validated_data.get('username'))
        token=get_tokens_for_user(user)
        return Response(data=token)


class Todolist(APIView):
    permission_classes = []
    @swagger_auto_schema(request_body=ToDoListSerializer)
    def post(self,request):
        serializer=ToDoListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data,status=status.HTTP_201_CREATED)

    def get(self, request, pk):
        todo_item = get_object_or_404(ToDoList, pk=pk)

        data = {
            "item": ToDoListSerializer(todo_item).data
        }
        if request.data.is_admin==False:
            if not todo_item.is_completed:
                incomplete_items = ToDoList.objects.filter(is_completed=True).exclude(pk=pk)
                data["incomplete_items"] = ToDoListSerializer(incomplete_items, many=True).data
            
        else:
            all_items = ToDoList.objects.all()
            data["all_items"] = ToDoListSerializer(all_items, many=True).data

        return Response(data=data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=LoginSerializer)
    def patch(self,request,pk):
        response = {'success': True}
        comment = get_object_or_404(ToDoList, pk=pk)
        serializer = LoginSerializer(comment, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            response['date'] = serializer.data
            return Response(data=response, status=status.HTTP_201_CREATED)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


    def delete(self,request,pk):
        commen=ToDoList.objects.filter(pk=pk,is_completed=False)
        commen.is_completed=True
        commen.save()

        return  Response(data={"massage":"O'chirildi"},status=status.HTTP_200_OK)

