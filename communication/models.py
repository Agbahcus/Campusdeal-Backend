from django.db import models
from django.contrib.auth.models import User
from marketplace.models import ItemListing


class Chat(models.Model):
    """Conversation between two users"""
    participant_1 = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='chats_as_p1'
    )
    participant_2 = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='chats_as_p2'
    )
    
    # Context
    related_item = models.ForeignKey(
        ItemListing, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    last_message = models.TextField(blank=True)
    last_message_time = models.DateTimeField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Ensure unique chat between two users
        unique_together = [['participant_1', 'participant_2']]
        indexes = [
            models.Index(fields=['-last_message_time']),
        ]
        verbose_name_plural = "Chats"
    
    def __str__(self):
        return f"Chat: {self.participant_1.username} ↔ {self.participant_2.username}"
    
    def get_other_participant(self, user):
        """Get the other participant in the chat"""
        if self.participant_1 == user:
            return self.participant_2
        return self.participant_1


class Message(models.Model):
    """Individual chat messages"""
    chat = models.ForeignKey(
        Chat, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    
    # Moderation
    is_flagged = models.BooleanField(default=False)
    flagged_for = models.CharField(max_length=50, blank=True)  # e.g., "PHONE_NUMBER"
    is_system_warning = models.BooleanField(default=False)  # System-generated warning
    is_deleted_by_system = models.BooleanField(default=False)
    
    # Read status
    is_read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['chat', '-created_at']),
        ]
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.username}: {self.text[:50]}"


class ModeratedMessageLog(models.Model):
    """Audit trail for moderation actions"""
    original_sender = models.ForeignKey(User, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    original_text = models.TextField()
    detected_flags = models.CharField(max_length=100)
    
    ACTION_CHOICES = [
        ('flagged', 'Flagged for Review'),
        ('deleted', 'Auto-Deleted'),
    ]
    action_taken = models.CharField(max_length=20, choices=ACTION_CHOICES)
    
    strike_number = models.PositiveSmallIntegerField()  # 1, 2, or 3
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Strike {self.strike_number} - {self.original_sender.username}"