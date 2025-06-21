from django.contrib import admin
from .models import User, Ramen, Review

# Register your models here.



@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "nickname")  # 목록에 보여줄 필드
    search_fields = ("email", "nickname")  # 검색 가능 필드
    list_filter = ()  # 필터 없으면 생략
    ordering = ("id",)  # 정렬 기준


@admin.register(Ramen)
class RamenAdmin(admin.ModelAdmin):
    list_display = ("id", "ramen_name", "like_number")  # 보여줄 컬럼
    search_fields = ("ramen_name",)
    list_filter = ()
    ordering = ("-like_number",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "user_id", "ramen_id", "created_at")
    search_fields = ("user_id__nickname", "ramen_id__ramen_name")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
