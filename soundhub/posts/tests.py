from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APILiveServerTestCase

User = get_user_model()


class PostListViewTest(APILiveServerTestCase):
    @staticmethod
    def create_user(username='testuser@test.co.kr'):
        return User.objects.create_user(username=username, nickname='testuser')
