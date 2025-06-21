from django.db import models

# Create your models here.


class User(models.Model):
    id = models.AutoField(primary_key=True)  # PK, INT
    email = models.CharField(max_length=40, unique=True)  # VARCHAR(40)
    password = models.CharField(max_length=255)  # VARCHAR(255), NOTNULL
    nickname = models.CharField(max_length=15)  # VARCHAR(15)

    def __str__(self):
        return self.nickname


class Ramen(models.Model):
    ramen_name = models.CharField(max_length=40)  # VARCHAR(40)
    image_url = models.CharField(max_length=255)  # VARCHAR(255)
    like_number = models.IntegerField(default=0)  # INT

    def __str__(self):
        return self.ramen_nam


class Review(models.Model):
    id = models.AutoField(primary_key=True)  # PK, INT
    content = models.CharField(max_length=400)  # VARCHAR(400)
    created_at = models.DateTimeField(auto_now_add=True)  # DATETIME
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)  # FK
    ramen_id = models.ForeignKey(Ramen, on_delete=models.CASCADE)  # FK

    def __str__(self):
        return f"Review by {self.user_id.nickname} on {self.ramen_id.ramen_name}"
