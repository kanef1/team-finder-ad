from django.conf import settings
from django.db import models


class Project(models.Model):
    STATUS_CHOICES = [
        ('open', 'Открыт'),
        ('closed', 'Закрыт'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    github_url = models.URLField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='participating_projects',
        blank=True,
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
