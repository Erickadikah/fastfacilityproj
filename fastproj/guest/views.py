from django.shortcuts import render
from host.models import Client
from .models import UploadedDocument
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse
from .forms import DocumentUploadForm
from django.contrib.auth.models import User
from django.http import JsonResponse
import boto3
from botocore.exceptions import NoCredentialsError
from django.contrib import messages
# from django_auth.decorators import login_not_required


# Create your views here.
# this is the client dashboard
@csrf_exempt
def index(request):
    # Check if the client is authenticated
    if 'client_id' in request.session:
        # Retrieve the client ID from the session
        client_id = request.session['client_id']
        
        # Retrieve the client based on the client ID
        try:
            client = Client.objects.get(id=client_id)
            return render(request, 'guest.html', {'client': client, 'authenticated': True, 'client_id': client_id})
        except Client.DoesNotExist:
            return HttpResponse("Client not found")
    else:
        return HttpResponse("You must be as our client logged in to view this page.")


@csrf_exempt
def upload_document(request, client_id):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            client = Client.objects.get(id=client_id)
            description = form.cleaned_data['description']
            file = form.cleaned_data['file']
            
            # Get the creator of the client
            creator_id = client.creator_id
            
            try:
                recipient_user = User.objects.get(id=creator_id)
            except User.DoesNotExist:
                return JsonResponse({"error": "User who created the client not found"}, status=404)
            
            # Upload file to S3
            s3 = boto3.client('s3')
            try:
                s3.upload_fileobj(file, '23129522-fastproj1', file.name)
            except NoCredentialsError:
                return JsonResponse({"error": "AWS credentials not found"}, status=500)
            
            # Once uploaded to S3, you might want to save the S3 URL in your database instead of the file itself
            s3_url = f"https://23129522-fastproj1.s3.amazonaws.com/{file.name}"
            
            # Save the document details in your database
            uploaded_document = UploadedDocument(
                sender=client,
                recipient_user=recipient_user,
                description=description,
                file_s3_url=s3_url  # Save the S3 URL
            )
            uploaded_document.save()
            
            return JsonResponse({'succes': True, 'message': 'uploaded'})
        else:
            errors = form.errors.as_json()
            return JsonResponse({"error": "Form validation failed", "errors": errors}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)