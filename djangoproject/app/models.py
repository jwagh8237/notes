from django.conf import settings
from django.db import models


class Category(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='note_categories',
    )
    name = models.CharField(max_length=80)
    color = models.CharField(max_length=20, default='#eef2ff')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'name'],
                name='unique_category_per_owner',
            )
        ]

    def __str__(self):
        return self.name


class Note(models.Model):
    LOW = 'low'
    NORMAL = 'normal'
    HIGH = 'high'

    PRIORITY_CHOICES = [
        (LOW, 'Low'),
        (NORMAL, 'Normal'),
        (HIGH, 'High'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notes',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='notes',
        blank=True,
        null=True,
    )
    title = models.CharField(max_length=160)
    body = models.TextField(blank=True)
    tags = models.CharField(
        max_length=240,
        blank=True,
        help_text='Comma-separated tags, for example: work, ideas, study',
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default=NORMAL,
    )
    color = models.CharField(max_length=20, default='#ffffff')
    is_pinned = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-updated_at']
        indexes = [
            models.Index(fields=['owner', 'is_archived', '-updated_at']),
            models.Index(fields=['owner', 'is_pinned']),
        ]

    def __str__(self):
        return self.title

    @property
    def tag_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
