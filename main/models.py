from django.db import models

class Article (models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publication_date = models.DateField(auto_now_add=True)
    tags = models.JSONField()
    content = models.TextField()
    free = models.BooleanField(default=False)

    def __str__(self):
        return self.title 
