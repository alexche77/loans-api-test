
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import serializers, status

from loans.models import Balance, Transaction
from loans.serializers import TransactionsSerializer, UserSerializer

User = get_user_model()


def create_user(payload):
    u = User.objects.create(
        **payload
    )
    if ('password' in payload):
        u.set_password(payload['password'])
        u.save()
    return u


# Create your tests here.
class LoansTests(TestCase):

    def setUp(self):
        self.user1 = create_user({
            "username": "TestUser1",
            "email": "test1@user.com",
            "password": "random"
        })

        self.user2 = create_user({
            "username": "TestUser2",
            "email": "test2@user.com",
            "password": "random"
        })

        self.client = APIClient()

    def test_transaction_model(self):
        Transaction.objects.create(
            lender=self.user1,
            recipient=self.user2,
            quantity=10
        )

        self.assertEqual(1, Transaction.objects.all().count())

    def test_create_user(self):
        res = self.client.post(reverse('user-list'), {
            "username": "TestUser3",
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            res.data['pk'],
            UserSerializer(
                instance=User.objects.get(pk=res.data['pk'])
            ).data['pk']
        )

        self.assertEqual(
            res.data['balance'],
            UserSerializer(
                instance=User.objects.get(pk=res.data['pk'])
            ).data['balance']
        )

    def test_users_list(self):
        res = self.client.get(reverse('user-list'))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = UserSerializer(
            instance=User.objects.all()[:10],
            many=True
        )
        self.assertEqual(
            res.data['results'][0]['username'],
            serializer.data[0]['username']
        )

    def test_balance_update(self):
        res = self.client.post(reverse('lend'), {
            'lender': self.user1.pk,
            'recipient': self.user2.pk,
            'quantity': 10
        })

        lender_balance = Balance.objects.get(user=self.user1)
        recipient_balance = Balance.objects.get(user=self.user2)

        self.assertEqual(
            res.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(2, Balance.objects.all().count())
        self.assertEqual(-10, lender_balance.balance)
        self.assertEqual(10, recipient_balance.balance)

    def test_user_detail_lender(self):
        res = self.client.post(reverse('lend'), {
            'lender': self.user1.pk,
            'recipient': self.user2.pk,
            'quantity': 10
        })
        res = self.client.get(
            reverse(
                'user-detail',
                args=[self.user1.pk]
            )
        )
        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK
        )

        self.assertIn("balance", res.data)
        self.assertEqual(-10, res.data['balance'])

        # If user1 lended 10 to user2
        # Then, user2 must appear in 'owned' array
        self.assertEqual(
            {
                'user': self.user2.username,
                'total': 10
            },
            res.data['owned'][0]
        )

    def test_user_detail_recipient(self):
        res = self.client.post(reverse('lend'), {
            'lender': self.user1.pk,
            'recipient': self.user2.pk,
            'quantity': 10
        })
        res = self.client.get(
            reverse(
                'user-detail',
                args=[self.user2.pk]
            )
        )
        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK
        )

        self.assertIn("balance", res.data)
        self.assertEqual(10, res.data['balance'])

        # If user1 lended 10 to user2
        # Then, user1 must appear in 'owns' array
        self.assertEqual(
            {
                'user': self.user1.username,
                'total': 10
            },
            res.data['owns'][0]
        )
