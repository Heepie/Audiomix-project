import filecmp
import os
from random import randint

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import resolve, reverse
from rest_framework import status
from rest_framework.test import APILiveServerTestCase, APIRequestFactory, force_authenticate

from posts.models import Post, CommentTrack
from posts.apis import PostList, PostDetail, CommentTrackList, CommentTrackDetail, PostLikeToggle

User = get_user_model()


# 포스트 리스트 API 테스트 - 포스트 생성, 리스트 조회
class PostListAPIViewTest(APILiveServerTestCase):
    API_VIEW_URL = '/post/'
    API_VIEW_URL_NAME = 'post:list'
    VIEW_CLASS = PostList

    # 테스트 유저 생성
    @staticmethod
    def create_user(email='testuser@test.co.kr', nickname='testuser'):
        return User.objects.create_user(
            email=email,
            nickname=nickname,
            password='testpassword'
        )

    # 테스트 포스트 생성
    def create_post(self, user):
        # 포스트 생성
        factory = APIRequestFactory()
        track_dir = os.path.join(settings.MEDIA_ROOT, 'author_tracks/The_Shortest_Straw_-_Guitar.mp3')
        with open(track_dir, 'rb') as author_track:
            data = {
                'title': 'test_title',
                'author_track': author_track,
                'instrument': 'Guitar',
                'genre': 'Heavy Metal',
            }
            request = factory.post(self.API_VIEW_URL, data)
        force_authenticate(request, user=user)

        view = PostList.as_view()
        response = view(request)
        return response

    # /post/로 접속했을 때 PostList 뷰를 사용하고 있는지 테스트
    def test_post_list_url_resolve(self):
        resolve_match = resolve(self.API_VIEW_URL)
        self.assertEqual(resolve_match.view_name, self.API_VIEW_URL_NAME)
        self.assertEqual(resolve_match.func.view_class, self.VIEW_CLASS)

    # post:list 을 호출했을 때 /post/ url으로 연결되는지 테스트
    def test_post_list_url_name_reverse(self):
        url = reverse(self.API_VIEW_URL_NAME)
        self.assertEqual(url, self.API_VIEW_URL)

    # Post Create 테스트
    def test_post_create(self):
        # 포스트 생성
        user = self.create_user()
        response = self.create_post(user=user)

        test_user = User.objects.first()
        post = Post.objects.get(pk=response.data['id'])

        # 제목 테스트
        self.assertEqual(response.data['title'], 'test_title')
        # 작성자 테스트
        self.assertEqual(response.data['author']['id'], test_user.pk)
        # 상태 코드 테스트
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 생성된 포스트 갯수 테스트
        self.assertEqual(Post.objects.count(), 1)
        # 파일 일치 테스트
        # self.assertTrue(filecmp.cmp(track_dir, post.author_track.file.name))

    # 포스트 리스트 조회 테스트
    def test_post_list_retrieve(self):
        # 랜덤 갯수의 포스트 생성
        num = randint(0, 10)
        user = self.create_user()
        for i in range(num):
            self.create_post(user=user)

        # /post/ 에 GET 요청
        response = self.client.get(self.API_VIEW_URL)

        # 결과 테스트
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.count(), num)


# 포스트 디테일 API 테스트 - 포스트 디테일 조회, 수정, 삭제
class PostDetailAPIViewTest(APILiveServerTestCase):
    API_VIEW_URL = '/post/'

    # 테스트 유저 생성
    @staticmethod
    def create_user(email='testuser@test.co.kr', nickname='testuser'):
        return User.objects.create_user(
            email=email,
            nickname=nickname,
            password='testpassword'
        )

    # 테스트 포스트 생성
    def create_post(self):
        # 유저 생성
        user = self.create_user()
        # 포스트 생성
        factory = APIRequestFactory()
        track_dir = os.path.join(settings.MEDIA_ROOT, 'author_tracks/The_Shortest_Straw_-_Guitar.mp3')
        with open(track_dir, 'rb') as author_track:
            data = {
                'title': 'test_title',
                'author_track': author_track,
                'instrument': 'Guitar',
                'genre': 'Heavy Metal',
            }
            request = factory.post(self.API_VIEW_URL, data)
        force_authenticate(request, user=user)

        view = PostList.as_view()
        response = view(request)
        return response

    # 포스트 조회 테스트
    def test_post_retrieve(self):
        # 포스트 생성
        pk = self.create_post().data['id']

        # 비교대상 포스트
        post = Post.objects.get(pk=pk)

        # 생성한 포스트 가져오기 - /post/pk/ 로 GET 요청
        response = self.client.get(f'http://testserver/post/{pk}/')

        # 데이터베이스에서 꺼내온 포스트와 /post/pk/의 응답으로 받은 포스트를 비교
        self.assertEqual(response.data['id'], post.pk)
        self.assertEqual(response.data['title'], post.title)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['author_track'], post.author_track)

    # 포스트 수정 테스트
    def test_post_update(self):
        # 포스트 생성
        pk = self.create_post().data['id']

        # /post/pk/으로 PATCH 요청을 보냄
        factory = APIRequestFactory()
        data = {
            'title': 'updated_title',
        }
        request = factory.patch(f'/post/{pk}/', data)
        view = PostDetail.as_view()
        response = view(request, pk=pk)

        # 인증 정보가 없는 경우 포스트 수정 불가인지 확인
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # 작성자가 아닌 경우 포스트 수정 불가능한지 확인
        user = self.create_user('testuser2@test.co.kr', 'testuser2')
        force_authenticate(request, user=user)
        response = view(request, pk=pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 작성자인 경우 포스트 수정 성공 확인
        user = User.objects.get(email='testuser@test.co.kr')
        force_authenticate(request, user=user)
        response = view(request, pk=pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'updated_title')

    # 포스트 삭제 테스트
    def test_post_destroy(self):
        # 포스트 생성
        pk = self.create_post().data['id']

        # /post/pk/으로 DELETE 요청을 보냄
        factory = APIRequestFactory()
        request = factory.delete(f'/post/{pk}/')
        view = PostDetail.as_view()
        response = view(request, pk=pk)

        # 인증 데이터가 없을 경우 포스트 삭제 불가 테스트
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # 작성자가 아닌 경우 포스트 삭제 불가능한지 테스트
        user = self.create_user('testuser2@test.co.kr', 'testuser2')
        force_authenticate(request, user=user)
        response = view(request, pk=pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 작성자인 경우 삭제 가능
        user = User.objects.get(email='testuser@test.co.kr')
        force_authenticate(request, user=user)
        response = view(request, pk=pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 포스트가 삭제되었는지 확인
        request = factory.get(f'/post/{pk}/')
        view = PostDetail.as_view()
        response = view(request, pk=pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# 커멘트 목록 API 테스트 - 커멘트 목록 조회, 커맨트 생성
class CommentListAPIViewTest(APILiveServerTestCase):
    POST_API_VIEW_URL = '/post/'

    # 테스트 유저 생성
    @staticmethod
    def create_user(email='testuser@test.co.kr', nickname='testuser'):
        return User.objects.create_user(
            email=email,
            nickname=nickname,
            password='testpassword'
        )

    # 테스트 포스트 생성
    def create_post(self, user):
        # 포스트 생성
        factory = APIRequestFactory()
        track_dir = os.path.join(settings.MEDIA_ROOT, 'author_tracks/The_Shortest_Straw_-_Guitar.mp3')
        with open(track_dir, 'rb') as author_track:
            data = {
                'title': 'test_title',
                'author_track': author_track,
                'instrument': 'Guitar',
                'genre': 'Heavy Metal',
            }
            request = factory.post(self.POST_API_VIEW_URL, data)
        force_authenticate(request, user=user)

        view = PostList.as_view()
        response = view(request)
        return response

    # 테스트 커멘트 생성
    def create_comment(self, user, post):
        # 포스트 생성
        pk = post.data['id']

        # /post/pk/comments/로 POST 요청 보냄
        factory = APIRequestFactory()
        track_dir = os.path.join(settings.MEDIA_ROOT, 'comment_tracks/The_Shortest_Straw_-_Bass.mp3')
        with open(track_dir, 'rb') as author_track:
            data = {
                'comment_track': author_track,
                'instrument': 'Bass'
            }
            request = factory.post(f'/post/{pk}/comments/', data)
        force_authenticate(request, user=user)
        view = CommentTrackList.as_view()
        response = view(request, pk=pk)
        return response

    # 코멘트 트랙 생성 테스트
    def test_comment_create(self):
        # 유저 및 포스트 생성
        user = self.create_user()
        pk = self.create_post(user=user).data['id']

        # post/pk/comment로 POST 요청 보냄
        factory = APIRequestFactory()
        track_dir = os.path.join(settings.MEDIA_ROOT, 'comment_tracks/The_Shortest_Straw_-_Bass.mp3')
        with open(track_dir, 'rb') as author_track:
            data = {
                'comment_track': author_track,
                'instrument': 'Bass'
            }
            request = factory.post(f'/post/{pk}/comments/', data)
        view = CommentTrackList.as_view()
        response = view(request, pk=pk)

        # 인증정보가 없는 경우 커맨트 트랙 생성 불가 테스트
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # 인증정보가 있으면 트랙 생성
        force_authenticate(request, user=user)
        response = view(request, pk=pk)

        # 데이터베이스에서 커맨트 트랙을 가져와서
        comment_track = CommentTrack.objects.get(pk=response.data['id'])

        # 생성된 트랙과 동일한지 비교
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['instrument'], comment_track.instrument)

    def test_comment_list_retrieve(self):
        # 유저1로 포스트를 생성
        user = self.create_user()
        post = self.create_post(user=user)
        pk = post.data["id"]

        # 유저2로 유저1이 만든 포스트에 커맨트 트랙을 무작위 갯수로 생성
        another_user = self.create_user(email='testuser2@test.co.kr', nickname='testuser2')
        num = randint(0, 10)
        for i in range(num):
            self.create_comment(user=another_user, post=post)

        # /post/pk/ 에 GET 요청
        response = self.client.get(f'http://testserver/post/{pk}/comments/')

        # 데이터베이스에서 꺼내온 포스트
        test_post = Post.objects.get(pk=pk)

        # 결과 테스트
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(test_post.comment_tracks.count(), num)


# 커멘트 디테일 API 테스트 - 커멘트 조회, 수정, 삭제
class CommentDetailAPIViewTest(APILiveServerTestCase):
    POST_API_VIEW_URL = '/post/'

    # 테스트 유저 생성
    @staticmethod
    def create_user(email='testuser@test.co.kr', nickname='testuser'):
        return User.objects.create_user(
            email=email,
            nickname=nickname,
            password='testpassword'
        )

    # 테스트 포스트 생성
    def create_post(self, user):
        # 포스트 생성
        factory = APIRequestFactory()
        track_dir = os.path.join(settings.MEDIA_ROOT, 'author_tracks/The_Shortest_Straw_-_Guitar.mp3')
        with open(track_dir, 'rb') as author_track:
            data = {
                'title': 'test_title',
                'author_track': author_track,
                'instrument': 'Guitar',
                'genre': 'Heavy Metal'
            }
            request = factory.post(self.POST_API_VIEW_URL, data)
        force_authenticate(request, user=user)

        view = PostList.as_view()
        response = view(request)
        return response

    # 테스트 커멘트 생성
    def create_comment(self, user, post):
        # 포스트 생성
        pk = post.data['id']

        # /post/pk/comments/로 POST 요청 보냄
        factory = APIRequestFactory()
        track_dir = os.path.join(settings.MEDIA_ROOT, 'comment_tracks/The_Shortest_Straw_-_Bass.mp3')
        with open(track_dir, 'rb') as author_track:
            data = {
                'comment_track': author_track,
                'instrument': 'Bass'
            }
            request = factory.post(f'/post/{pk}/comments/', data)
        force_authenticate(request, user=user)
        view = CommentTrackList.as_view()
        response = view(request, pk=pk)
        return response

    # 커멘트 트랙 조회 테스트
    def test_comment_retrieve(self):
        user1 = self.create_user()
        user2 = self.create_user(email='testuser2@test.co.kr', nickname='testuser2')
        post = self.create_post(user=user1)
        comment = self.create_comment(post=post, user=user2)
        pk = comment.data['id']

        # /post/comment/pk/ 에 GET 요청 보냄
        response = self.client.get(f'http://testserver/post/comment/{pk}/')

        self.assertEqual(response.data['author'], user2.nickname)
        self.assertEqual(response.data['instrument'], 'Bass')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # 커멘트 트랙 수정 테스트
    def test_comment_update(self):
        # 유저, 포스트, 코멘트 트랙 생성
        user1 = self.create_user()
        user2 = self.create_user(email='testuser2@test.co.kr', nickname='testuser2')
        post = self.create_post(user=user1)
        comment = self.create_comment(post=post, user=user2)
        pk = comment.data['id']

        # /post/comment/pk/ 에 PATCH 요청 보냄
        factory = APIRequestFactory()
        data = {
            'instrument': 'Vocal'
        }
        request = factory.patch(f'/post/comment/{pk}/', data=data)
        view = CommentTrackDetail.as_view()
        response = view(request, pk=pk)

        # 인증 정보 없는 경우 수정 불가능 테스트
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # 작성자가 아닌 경우 수정 불가능 테스트
        force_authenticate(request, user=user1)
        response = view(request, pk=pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 작성자인 경우 수정 가능 테스트
        force_authenticate(request, user=user2)
        response = view(request, pk=pk)

        self.assertEqual(response.data['instrument'], 'Vocal')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # 커멘트 삭제 테스트
    def test_comment_destroy(self):
        # 유저, 포스트, 코멘트 트랙 생성
        user1 = self.create_user()
        user2 = self.create_user(email='testuser2@test.co.kr', nickname='testuser2')
        post = self.create_post(user=user1)
        comment = self.create_comment(post=post, user=user2)
        pk = comment.data['id']

        # /post/comment/pk/에 DELETE 요청 보냄
        factory = APIRequestFactory()
        request = factory.delete(f'/post/comment/{pk}/')
        view = CommentTrackDetail.as_view()
        response = view(request, pk=pk)

        # 인증 정보가 없는 경우 삭제 불가능 테스트
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # 작성자가 아닌 경우 삭제 불가능 테스트
        force_authenticate(request, user=user1)
        response = view(request, pk=pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 작성자인 경우 삭제 가능 테스트
        force_authenticate(request, user=user2)
        response = view(request, pk=pk)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 코멘트가 삭제되었는지 확인
        response = self.client.get(f'http://testserver/post/comment/{pk}/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PostLikeToggleTest(APILiveServerTestCase):
    POST_API_VIEW_URL = '/post/'

    # 테스트 유저 생성
    @staticmethod
    def create_user(email='testuser@test.co.kr', nickname='testuser'):
        return User.objects.create_user(
            email=email,
            nickname=nickname,
            password='testpassword'
        )

    # 테스트 포스트 생성
    def create_post(self, user):
        # 포스트 생성
        factory = APIRequestFactory()
        track_dir = os.path.join(settings.MEDIA_ROOT, 'author_tracks/The_Shortest_Straw_-_Guitar.mp3')
        with open(track_dir, 'rb') as author_track:
            data = {
                'title': 'test_title',
                'author_track': author_track,
                'instrument': 'Guitar',
                'genre': 'Heavy Metal',
            }
            request = factory.post(self.POST_API_VIEW_URL, data)
        force_authenticate(request, user=user)

        view = PostList.as_view()
        response = view(request)
        return response

    # 포스트 좋아요 & 좋아요 취소 테스트
    def test_post_like(self):
        user1 = self.create_user()
        user2 = self.create_user(email='testuser2@test.co.kr', nickname='testuser2')
        post = self.create_post(user=user1)
        pk = post.data['id']
        test_post = Post.objects.get(pk=pk)

        # /post/pk/like/ 로 POST 요청 보냄
        factory = APIRequestFactory()
        request = factory.post(f'/post/{pk}/like/')
        view = PostLikeToggle.as_view()
        response = view(request, pk=pk)

        # 인증 데이터가 없는 경우 좋아요 불가능 테스트
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # 인증된 유저인 경우 좋아요 가능 테스트
        force_authenticate(request, user=user2)
        response = view(request, pk=pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(test_post.liked.count(), 1)

        # 또 다른 인증된 유저로 좋아요 테스트
        force_authenticate(request, user=user1)
        response = view(request, pk=pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(test_post.liked.count(), 2)

        # 동일한 POST 요청을 다시 보내면 좋아요 취소 테스트
        response = view(request, pk=pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(test_post.liked.count(), 1)
