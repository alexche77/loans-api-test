from django.contrib.auth import get_user_model
from django.db.models import Sum, F

from rest_framework import serializers
from loans.models import Transaction

User = get_user_model()


class TransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    owned = serializers.SerializerMethodField(read_only=True)
    owns = serializers.SerializerMethodField(read_only=True)
    balance = serializers.IntegerField(
        source='balance.balance',
        read_only=True
    )

    class Meta:
        model = User
        fields = [
            'pk',
            'username',
            'email',
            'balance',
            'owned',
            'owns'
        ]
        read_only_fields = ['pk']
        related_fields = ['balance']

    def get_owned(self, user):
        return Transaction.objects.filter(lender=user).order_by('recipient')\
                .annotate(
                    total=Sum('quantity'),
                    user=F('recipient__username')
                )\
                .values('user', 'total')

    def get_owns(self, user):
        return Transaction.objects.filter(recipient=user).order_by('lender')\
                .annotate(total=Sum('quantity'), user=F('lender__username'))\
                .values('user', 'total')
