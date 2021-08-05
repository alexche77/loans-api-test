from django.contrib.auth import get_user_model

from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED

from loans.serializers import TransactionsSerializer, UserSerializer

User = get_user_model()


class UsersView(ModelViewSet):
    queryset = User.objects.filter(is_superuser=False, is_staff=False).all()
    serializer_class = UserSerializer


@api_view(['POST'])
def lend(request):
    serializer = TransactionsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=HTTP_201_CREATED)
