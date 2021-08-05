from rest_framework.routers import SimpleRouter
from django.urls import path
from loans.views import lend, UsersView

router = SimpleRouter()
router.register(r'users', UsersView)


urlpatterns = [
    path('lend/', lend, name='lend')
]

urlpatterns += router.urls
