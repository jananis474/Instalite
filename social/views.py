from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Post, Comment, UserProfile
from django.db.models import Count
from django.views.decorators.http import require_POST

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        mobile_number = request.POST.get('mobile_number')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')
        
        user = User.objects.create_user(username=username, password=password)
        profile = UserProfile.objects.create(
            user=user,
            full_name=full_name,
            mobile_number=mobile_number
        )
        
        login(request, user)
        return redirect('home')
    return render(request, 'social/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    return render(request, 'social/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')

@login_required
def home_view(request):
    posts = Post.objects.all().order_by('-timestamp')
    return render(request, 'social/home.html', {'posts': posts})

@login_required
def upload_view(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        caption = request.POST.get('caption', '')
        if image:
            post = Post.objects.create(user=request.user, image=image, caption=caption)
            return redirect('home')
    return render(request, 'social/post.html')

@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        text = request.POST['comment']
        Comment.objects.create(
            post=post,
            user=request.user,
            text=text
        )
        messages.success(request, 'Comment added successfully!')
    return redirect('home')

@login_required
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': post.likes.count()})

@login_required
def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=user).order_by('-timestamp')
    return render(request, 'social/profile.html', {'user': user, 'posts': posts})

@login_required
def edit_profile_view(request):
    # Create profile if it doesn't exist
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        if 'bio' in request.POST:
            profile.bio = request.POST['bio']
        profile.save()
        return redirect('profile', username=request.user.username)
    return render(request, 'social/edit_profile.html')

@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.user == request.user:
        post.delete()
    return redirect('home')
