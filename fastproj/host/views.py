from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, get_user_model
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .forms import ClientForm, GuestLoginForm
from .models import Client
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib.auth.models import User
import json
import requests
import random
import string
from django.contrib.auth.models import User, Permission
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import logging
from django.contrib.auth.hashers import make_password
# from .permisions import remove_duplicate_permissions
from django.contrib.auth.hashers import check_password
# from .forms import MessageForm
from django.contrib import messages
from .models import Message
from django.views.decorators.http import require_POST
from django.contrib.auth.hashers import check_password
from guest.models import UploadedDocument
from django.contrib.auth import logout as django_logout
from django.contrib.auth import logout
from django.urls import reverse
from django.core.mail import send_mail
import postmark
from django.conf import settings
from postmarker.core import PostmarkClient
import logging
from .models import UploadClients
from .forms import UploadForm
from django.shortcuts import get_object_or_404
import boto3
from .utils import delete_file_from_s3
# from django.shorts import redirect


CustomUser = get_user_model()
@login_required
def index(request):
    clients = Client.objects.filter(creator_id=request.user.id)
    return render(request, "host.html", {'clients': clients})

def generate_random_password():
    # Generate a random password of length 8
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

logger = logging.getLogger(__name__)

@csrf_exempt
@login_required      
def create_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.creator_id = request.user.id

            # Save the client instance to trigger the save() met

            # Generate a random password
            raw_password = generate_random_password()
            print("password:", raw_password)

            # Hash the raw password and save
            client.password = make_password(raw_password)
            # client.password.save()
            # print("saved:", password)hod
            client.save()

            # Log the details
            logger.info("Client created: username=%s, email=%s, phoneNumber=%s, rentPayDate=%s, rentEndDate=%s, creator_id=%s",
                        client.username, client.email, client.phoneNumber, client.rentPayDate, client.rentEndDate, client.creator_id)
            
            # esending email
            send_email_to_client(client.email, raw_password)

            return JsonResponse({'success': True, 'message': 'Client created successfully', 'password': raw_password})
        else:
            # Return a JSON response with form errors
            return JsonResponse({'success': False, 'message': 'Form validation failed', 'errors': form.errors})
    else:
        # Return a JSON response for invalid request method
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
logger = logging.getLogger(__name__)

def send_email_to_client(email, password):
    subject = 'Your Account Information'
    message = f'Your account has been created. Your password is: {password}'
    from_email = 'x23129522@student.ncirl.ie'  # Replace with your email
    recipient_list = [email]
    
    # Using Postmark for sending emails
    try:
        postmark = PostmarkClient(server_token=settings.POSTMARK_API_TOKEN)
        postmark.emails.send(
            From=from_email,
            To=recipient_list,
            Subject=subject,
            HtmlBody=message
        )
        logger.info("Email sent successfully to %s", email)
        print('email sent succesfully', email)
        return True  # Email sent successfully
    except Exception as e:
        logger.error("Error sending email to %s: %s", email, e)
        return False  # Email sending failed

#update client
@csrf_exempt
def update_client(request, client_id):
    if request.method == 'POST':
        client = get_object_or_404(Client, id=client_id)  # Corrected 'id' to 'client_id'
        form = ClientForm(request.POST, instance=client)
        print("Password:", client.password)
        if form.is_valid():
            client = form.save(commit=False)
            client.creator_id = request.user.id  # or however you want to track the creator
            client.save()  # Make sure to save the client instance to trigger the save() method
            # return JsonResponse({'success': True, 'message': 'Client updated successfully'})
            messages.success(request, 'Client updated successfully!')
            return redirect(reverse('host'))
        else:
            return JsonResponse({'success': False, 'message': 'Form validation failed', 'errors': form.errors})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

#this is the login view as a guest
@csrf_exempt
def guest_login(request):
    if request.method == 'POST':
        form = GuestLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            # Authenticate the guest user
            client = Client.objects.filter(email=email).first()

            if client is not None:
                if check_password(password, client.password):
                    # Log in the guest client
                    request.session['client_id'] = client.id
                    logger.info("Guest login successful: email=%s", email)
                    return redirect('/guest/')  # Redirect to guest area
                else:
                    # Incorrect password
                    logger.error("Incorrect password for client: %s", client.username)
                    return JsonResponse({'success': False, 'message': 'Invalid email or password'})
            else:
                # Client not found
                logger.error("Client with email %s not found.", email)
                return JsonResponse({'success': False, 'message': 'Client not found'})
        else:
            # Form validation failed
            logger.error("Form validation failed: %s", form.errors)
            return JsonResponse({'success': False, 'message': 'Form validation failed', 'errors': form.errors})
    else:
        # Render the guest login form
        form = GuestLoginForm()
        return render(request, 'guest_login.html', {'form': form})

# client logout view
def client_logout(request):
    if 'client_id' in request.session:
        # client_id = Client.id
        # print(client_id)
        del request.session['client_id']  # Clear client session data
    logout(request)  # Logout the user
    return redirect('/guest_login/')

# display all clients
def display_clients(request):
    clients = Client.objects.all()
    return render(request, 'host.html', {'clients': clients})

def display_clients(request):
    clients = Client.objects.all()
    return render(request, 'clients.html', {'clients': clients})
@csrf_exempt
def delete_client(request, id):
    client = Client.objects.get(id=id)
    client.delete()
    return redirect('create_client')

#get client with id
def get_client(request, client_id):
    if request.method == 'GET':
        try:
            # Retrieve the client with the specified ID
            client = get_object_or_404(Client, id=client_id)
            # Return client data in JSON format
            return JsonResponse({'id': client.id, 'username': client.username, 'email': client.email, 'phoneNumber': client.phoneNumber, 'rentPayDate': client.rentPayDate, 'rentEndDate': client.rentEndDate, 'creator_id': client.creator_id})
        except Client.DoesNotExist:
            # Return an error response if the client is not found
            return JsonResponse({'error': 'Client not found'}, status=404)
            
#user
def get_user(request, user_id):
    if request.method == 'GET':
        try:
            # Retrieve the user with the specified ID
            user = get_object_or_404(User, id=user_id)
            # Retrieve all clients associated with the user
            # clients = Client.objects.filter(user=user)
            # Return user and client data in JSON format
            user_data = {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                # 'phone': user.phone,
                # 'address': user.address,
                # 'aircode': user.eircode,
                # 'country': user.country,
                # 'client_count': clients.count(),
                # 'clients': [{'id': client.id, 'username': client.username, 'email': client.email,} for client in clients]
                }
            return JsonResponse(user_data)
        except User.DoesNotExist:
            # Return an error response if the user is not found
            return JsonResponse({'error': 'User not found'}, status=404)
        
# dispaly all users
def display_users(request):
    if request.method == 'GET':
        users = User.objects.all()
        user_list = []
        for user in users:
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                }
            user_list.append(user_data)
        return JsonResponse(user_list, safe=False)
    
def get_all_clients(request):
    if request.method == 'GET':
        # Retrieve all clients from the database
        clients = Client.objects.all()
        
        # Serialize client data into JSON format
        client_data = [{'id': client.id, 'username': client.username, 'email': client.email} for client in clients]
        
        # Return the serialized client data as JSON response
        return JsonResponse({'clients': client_data})
    
def maintenance_view(request):
    return render(request, 'maintenance.html')

#sendig message
@login_required
@csrf_exempt
def send_message(request, client_id):
    if request.method == 'POST':
        sender = request.user  # Fetch the logged-in user as the sender
        print("Sender:", sender)  # Check sender

        # Fetch the recipient user by ID
        try:
            recipient_user = User.objects.get(pk=client_id)
            recipient_client = None  # Initialize recipient_client as None
        except User.DoesNotExist:
            # If the recipient is not a User, it might be a Client
            try:
                recipient_client = Client.objects.get(pk=client_id)
                recipient_user = None  # Initialize recipient_user as None
            except Client.DoesNotExist:
                print("Recipient does not exist")  # Print error message
                return JsonResponse({'error': 'Recipient does not exist'}, status=404)

        content = request.POST.get('message_text')
        file = request.FILES.get('file')

        # Create and save the message
        message = Message.objects.create(sender=sender, recipient_user=recipient_user, recipient_client=recipient_client, content=content, file=file)
        messages.success(request, 'Message sent successfully!')
        # return JsonResponse({'success': True, 'message': 'Message sent successfully'})

    # return render(request, 'send_message.html')
    return redirect(reverse('host'))

#maintainance view
def maintainance_view(request):
    return render(request, 'maintenance.html')


# get all messages from the database
def get_messages(request, client_id):
    if request.method == 'GET':
        # Retrieve all messages sent to the specified client
        messages = Message.objects.filter(recipient_client_id=client_id)
        
        # Serialize message data into JSON format
        message_data = [{'id': message.id, 'sender': message.sender.username, 'content': message.content, 'file': message.file.url if message.file else None, 'created_at': message.created_at} for message in messages]
        # print(message_data)
        # Return the serialized message data as JSON response
        return JsonResponse({'messages': message_data})

#delete messages
@require_POST
@csrf_exempt
def delete_message(request, message_id):
    try:
        # Check if the message exists
        message = Message.objects.get(pk=message_id)
        # Delete the message
        message.delete()
        return JsonResponse({'message': 'Message deleted successfully'}, status=200)
    except Message.DoesNotExist:
        return JsonResponse({'error': 'Message not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
        
@csrf_exempt  
def get_documents(request, user_id):
    if request.method == 'GET':
        try:
            user = User.objects.get(id=user_id)
            documents = UploadedDocument.objects.filter(recipient_user=user)
            document_list = []
            for document in documents:
                document_data = {
                    'sender': document.sender.username,
                    'id': document.id,
                    'description': document.description,
                    'file_s3_url': document.file_s3_url,  # Use file_s3_url instead of file.url
                }
                document_list.append(document_data)
            return JsonResponse({'documents': document_list})  # Return an object with 'documents' property
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
@csrf_exempt
def documents(request, user_id):
    if request.method == 'GET':
        try:
            user = User.objects.get(id=user_id)
            documents = UploadedDocument.objects.filter(recipient_user=user)
            return render(request, 'document_list.html', {'documents': documents, 'user': user})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


# delet document with id
@require_POST
@csrf_exempt
def delete_document(request, document_id):
    try:
        document = UploadedDocument.objects.get(pk=document_id)
        document.delete()
        return JsonResponse({'message': 'Document deleted successfully'}, status=200)
    except UploadedDocument.DoesNotExist:
        return JsonResponse({'error': 'Document not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
        
# upload to all clients
@csrf_exempt
def upload_file(request, user_id):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the logged-in user (sender)
            sender = get_object_or_404(User, pk=user_id)
            description = form.cleaned_data['description']
            
            # Access the file from the form data
            uploaded_file = request.FILES['file']
            original_filename = uploaded_file.name  # Get the original file name
            
            try:
                # Get all clients associated with the sender
                clients = User.objects.filter(sent_files__sender=sender)
                print(clients)
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User does not exist'}, status=404)
            
            # Create an instance of UploadClients for the sender
            upload_instance = UploadClients.objects.create(
                sender=sender,
                description=description,
                file=uploaded_file,  # Save the file object directly
            )

            # Associate the upload instance with each client
            for client in clients:
                upload_instance.clients.add(client)
            
            # Upload file to S3
            s3 = boto3.client('s3')
            bucket_name = '23129522-fastproj1'
            file_name = original_filename  # Use the original file name
            try:
                s3.upload_fileobj(uploaded_file, bucket_name, file_name)
                file_s3_url = f'https://{bucket_name}.s3.amazonaws.com/{file_name}'
            except Exception as e:
                # Log the error for debugging
                print(f"Error uploading file to S3: {e}")
                # Delete the upload instance if upload to S3 fails
                upload_instance.delete()
                return JsonResponse({'success': False, 'message': 'Error uploading file to S3'}, status=500)
            
            # Update file_s3_url in the database
            upload_instance.file_s3_url = file_s3_url
            upload_instance.save()
            
            # return JsonResponse({'success': True, 'message': 'Document uploaded successfully to clients', 'file_s3_url': file_s3_url})
            return redirect(reverse('host'))
        else:
            # Return form errors
            return JsonResponse({'success': False, 'message': 'Form data is not valid', 'errors': form.errors}, status=400)
    else:
        # Invalid request method
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

        
def get_uploaded_documents(request, client_id):
    if request.method == 'GET':
        # Retrieve the client based on the client_id
        client = get_object_or_404(Client, pk=client_id)
        
        # Retrieve uploaded documents associated with the client's creator
        uploaded_documents = UploadClients.objects.filter(sender_id=client.creator_id)
        
        # Serialize the data
        data = [{'id': doc.id, 'sender': doc.sender.username, 'description': doc.description, 'file_s3_url': doc.file_s3_url} for doc in uploaded_documents]
        
        # Return the serialized data as a JSON response
        return JsonResponse({'documents': data})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
        
def download_file(request, user_id):
    try:
        # Retrieve all files associated with the creator_id
        files = UploadClients.objects.filter(sender_id=user_id)

        # Prepare data to return
        files_data = []
        for file in files:
            file_info = {
                'id': file.id,
                'description': file.description,
                'filename': file.file.name,
                'file_s3_url': file.file_s3_url,
            }
            files_data.append(file_info)

        return JsonResponse({'success': True, 'files': files_data})
    except Exception as e:
        # Handle exceptions
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
def delete_file(request, file_id):
    try:
        # Retrieve the file object
        file_instance = UploadClients.objects.get(pk=file_id)
        
        # Delete the file from S3 and database
        if file_instance:
            # Delete the file from S3
            if file_instance.file_s3_url:
                success = delete_file_from_s3('23129522-fastproj1', file_instance.file_s3_url)
                if success:
                    # Delete the file instance from the database
                    file_instance.delete()
                    return JsonResponse({'success': True, 'message': 'File deleted successfully'})
                else:
                    return JsonResponse({'success': False, 'message': 'Failed to delete file from S3'}, status=500)
            else:
                return JsonResponse({'success': False, 'message': 'S3 URL missing for the file'}, status=400)
        else:
            return JsonResponse({'success': False, 'message': 'File not found'}, status=404)
    except UploadClients.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'File not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
