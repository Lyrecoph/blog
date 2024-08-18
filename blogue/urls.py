from django.urls import path

from blogue import views
urlpatterns = [
    path("", views.post_list, name="post_list"),
    path("category/<slug:category>/", views.post_list, name="category_post_list"),
    path("tag/<slug:tag_slug>/", views.post_list, name="tag_post_list"),
    path("<int:year>/<int:month>/<int:day>/<slug>/", views.post_detail, name="post_detail"),
    path("<int:year>/<int:month>/<int:day>/<slug>/update/", 
         views.post_update, name="post_update"),
    path("<int:year>/<int:month>/<int:day>/<slug>/", views.post_delete, name="post_delete"),
    path('<int:year>/<int:month>/<int:day>/<str:slug>/delete/', views.post_delete_ajax, name='post_delete_ajax'),
    path("add_post/", views.post_add, name="post_add"),
    # vue generic
    # path("add/", views.AddPost.as_view(), name="post_add"),
    
    path('<int:post_id>/stream/', views.stream_comment_view, name='stream_comment'),
    path('<int:post_id>/post_email/', views.email_post, name='post_email'),
    path('ajax_comment/', views.ajax_comment, name='ajax_comment'),
    
    path("search/", views.post_search, name="post_search"),
]
