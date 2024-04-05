from django.db import models
from django.contrib.auth.models import User
from host.models import Client

class UploadedDocument(models.Model):
    sender = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='sent_documents', default=None)
    recipient_user = models.ForeignKey(User, related_name='received_documents', null=True, blank=True, on_delete=models.CASCADE)
    recipient_client = models.ForeignKey(Client, related_name='received_documents', null=True, blank=True, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, default='No description provided')
    file = models.FileField(upload_to='uploads/', default='default/file.pdf')
    file_s3_url = models.URLField(blank=True)

    def __str__(self):
        return f"Document uploaded by {self.sender.username}"
