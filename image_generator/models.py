
from django.db import models
from django.contrib.auth.models import User

class GeneratedImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prompt = models.TextField()
    image_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # New fields to store additional metadata
    width = models.IntegerField(default=1024)
    height = models.IntegerField(default=1024)
    cfg_scale = models.FloatField(default=7.0)
    steps = models.IntegerField(default=30)
    seed = models.BigIntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"Image for {self.user.username}: {self.prompt[:30]}..."