from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from accounts.models import User
from api.serializers.users import UserSerializer
from accounts.permissions import (
    IsOwnerOrReadOnly,
    IsNotOwner,
    IsEmployeeOfRestaurant,
    IsOwnerOfUser,
    IsOwnerCreatingUser,
    IsOwnerOfUserToDelete,
)


class UserView(APIView):
    permission_classes = [
        IsOwnerOrReadOnly,
        IsNotOwner,
        IsEmployeeOfRestaurant,
        IsOwnerOfUser,
        IsOwnerCreatingUser,
        IsOwnerOfUserToDelete,
    ]

    def get(self, request, pk=None):
        print(request.user.role)
        print(request.user)
        if pk:
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        else:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        user = User.objects.get(pk=pk)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = User.objects.get(pk=pk)
        if user.role == "owner":
            return Response(
                {"error": "Cannot delete owner"}, status=status.HTTP_403_FORBIDDEN
            )
        if request.user.role == "owner" and user.owner == request.user:
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "Only owner can delete users"}, status=status.HTTP_403_FORBIDDEN
        )
