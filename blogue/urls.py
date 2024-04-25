from django.urls import path

from blogue import views
urlpatterns = [
    path("", views.post_list, name="post_list"),
    path("category/<slug:category>/", views.post_list, name="category_post_list"),
    path("<int:year>/<int:month>/<int:day>/<slug>/", views.detail_list, name="post_detail"),
    path("<int:year>/<int:month>/<int:day>/<slug>/update/", 
         views.post_update, name="post_update"),
    path("add/", views.post_add, name="post_add"),
    path('<int:post_id>/stream/', views.stream_comment_view, name='stream_comment'),
    path("search/", views.post_search, name="post_search"),
]
