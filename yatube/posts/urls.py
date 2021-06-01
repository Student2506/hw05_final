from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.new_post, name="new_post"),
    path("about/", include('about.urls', namespace='about')),
    path("<str:username>/", views.profile, name='profile'),
    path("<str:username>/<int:post_id>/", views.post_view, name='post'),
    path("<str:username>/<int:post_id>/edit/",
         views.post_edit,
         name='post_edit'),
    path("<str:username>/<int:post_id>/comment",
         views.add_comment,
         name="add_comment"),
]
