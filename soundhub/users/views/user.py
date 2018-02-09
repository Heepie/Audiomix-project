import json

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_GET

from users.forms import SignInForm
from users.models import Relationship


User = get_user_model()


@require_GET
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)

    user_posts = user.post_set.all()[:5]
    user_comments = user.commenttrack_set.all()[:5]

    context = {
        "sign_in": SignInForm,
        "user": user,
        "user_posts": user_posts,
        "user_comments": user_comments
    }
    return render(request, 'profile/profile.html', context)


def follow_toggle(request, pk):
    from_user = request.user
    to_user = User.objects.get(pk=pk)

    if request.method == 'GET' and request.user.is_authenticated:
        response = Relationship.objects \
            .filter(from_user_id=from_user.pk) \
            .filter(to_user_id=to_user.pk) \
            .exists()
        return HttpResponse(response)

    elif request.method == 'POST' and request.user.is_authenticated:
        if Relationship.objects\
                .filter(from_user_id=from_user.pk)\
                .filter(to_user_id=to_user.pk)\
                .exists():

            relation = Relationship.objects.get(
                from_user_id=from_user.pk,
                to_user_id=to_user.pk
            )
            relation.delete()
            response = {
                "status": 204
            }

        else:
            Relationship.objects.create(
                from_user_id=from_user.pk,
                to_user_id=to_user.pk
            )
            response = {
                "status": 201
            }

        response["count"] = f"{to_user.followers.count()}"
        json_response = json.dumps(response)
        header = {
            "Content-Type": "application/json",
            "charset": "utf-8"
        }

        return HttpResponse(json_response,
                            content_type=header["Content-Type"],
                            charset=header["charset"],
                            status=response["status"])
