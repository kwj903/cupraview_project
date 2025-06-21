from django.urls import path
from django.urls import path
from ramen import views as ramen_views


urlpatterns = [
    path("", ramen_views.main_page, name="main_page"),
    path("ramen/<int:ramen_id>/", ramen_views.ramen_detail, name="ramen_detail"),
    path("login/", ramen_views.user_login, name="ramen_login"),
    path("signup/", ramen_views.user_signup, name="ramen_signup"),
    path("logout/", ramen_views.logout, name="logout"),
    path("delete/", ramen_views.delete_account, name="delete_account"),
    path("search/", ramen_views.search, name="search"),
]
