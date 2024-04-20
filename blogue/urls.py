from django.urls import path

from blogue import views
urlpatterns = [
    path("", views.post_list, name="post_list"),
    path("<slug>/", views.detail_list, name="post_detail")
]
