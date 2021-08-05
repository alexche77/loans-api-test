from django.db import models
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save

from logging import getLogger

logger = getLogger()


User = get_user_model()


# Create your models here.
class Transaction(models.Model):
    lender = models.ForeignKey(
        to=User,
        on_delete=models.PROTECT,
        related_name='lender'
    )
    recipient = models.ForeignKey(
        to=User,
        on_delete=models.PROTECT,
        related_name='recipient'
    )
    quantity = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.lender.username}\
            lended {self.quantity} to \
                {self.recipient}'


class Balance(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.PROTECT)
    balance = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.username} - {self.balance}'


@receiver(post_save, sender=User)
def create_balance_for_user(sender, instance, **kwargs):
    balance, _ = Balance.objects.get_or_create(user=instance)
    logger.debug(f'Balance created? {_} for {instance.username}')


@receiver(post_save, sender=Transaction)
def calculate_balance(sender, instance, **kwargs):
    # It would be best to do this in a background job
    # Maybe implementing celery
    logger.debug(f'Balance update for users \
        {instance.lender} and {instance.recipient}')

    lender_balance, _ = Balance.objects.get_or_create(
        user=instance.lender
    )
    recipient_balance, _ = Balance.objects.get_or_create(
        user=instance.recipient
    )

    lender_balance.balance -= instance.quantity
    recipient_balance.balance += instance.quantity

    lender_balance.save()
    recipient_balance.save()
