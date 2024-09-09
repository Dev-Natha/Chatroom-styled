from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import *
from django.db.models import Q
# Create your views here.
def home(request):
    profile = ""
    q = request.GET.get("q")
    if q is None:
        q = ""
    rooms = Rooms.objects.filter(Q(name__icontains=q) 
                                 | Q(topic__name__icontains=q)
                                 | Q(owner__username__icontains=q)
                                 | Q(description__icontains = q)
                                 )
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
    context = {"profile":profile, "rooms":rooms}
    return render(request, "index.html", context)
\
def signup(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = UserRegisterationForm()
    if request.method == "POST":
        form = UserRegisterationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            Profile.objects.create(
                user = user
            )
            login(request, user)
            return redirect("home")
    context = {"form":form}
    return render(request, "signup.html", context)

def signin(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        uname = request.POST.get("username")
        pwd = request.POST.get("password")
        user = authenticate(username=uname, password=pwd)
        if user is not None:
            login(request, user)
            return redirect("home")
    return render(request, "signin.html")

def logoutUser(request):
    logout(request)
    return redirect("home")

@login_required(login_url="login")
def profile(request, pk):
    profile = Profile.objects.get(profile_id=pk)
    context = {"profile":profile}

    return render(request, "profile.html", context)

@login_required(login_url="login")
def settings(request, pk):
    profile = Profile.objects.get(profile_id=pk)
    if request.user != profile.user:
        return redirect("home")
    if request.method == "POST":
        name = request.POST.get("profile_name")
        picture = request.FILES.get("profile_picture")
        bio = request.POST.get("profile_bio")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        profile.name = name
        if picture:
            profile.profile_picture = picture
        profile.bio= bio
        profile.save()
        profile.user.username = username
        profile.user.email = email
        if password:
            profile.user.set_password(password)
        profile.user.save()
        return redirect("profile", pk=pk)
    context = {"profile":profile}
    return render(request, "settings.html", context)

@login_required(login_url="login")
def createRoom(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        room_name = request.POST.get("room_name")
        room_description = request.POST.get("room_description")
        topic_name = request.POST.get("topic_name").lower()
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Rooms.objects.create(
            name = room_name,
            description = room_description,
            owner = request.user,
            topic = topic

        )
        return redirect("home")
    context = {"profile":profile}
    return render(request, "create-edit.html", context)

@login_required(login_url="login")
def roomDetails(request, pk):
    profile = Profile.objects.get(user=request.user)
    room = Rooms.objects.get(id=pk)
    messages = room.messages_set.all()
    if request.method == "POST":
       room_msg = request.POST.get("room_msg")
       Messages.objects.create(
           owner = request.user,
           body = room_msg,
           room = room
       )
       return redirect("roomdetails", pk=pk)
    context = {"profile":profile, "room":room, "messages":messages}
    return render(request, "roomdetails.html", context)

@login_required(login_url="login")
def editDetails(request, pk):
    profile = Profile.objects.get(user=request.user)
    room = Rooms.objects.get(id=pk)
    if request.user != room.owner:
        return redirect("home")
    topics = Topic.objects.all()
    if request.method == "POST":
        room_name = request.POST.get("room_name")
        room_description = request.POST.get("room_description")
        topic_name = request.POST.get("topic_name").lower()
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = room_name
        room.description = room_description
        room.topic = topic
        room.save()
        return redirect("home")
    context = {"profile":profile, "room":room, "topics":topics}
    return render(request, "create-edit.html", context)

@login_required(login_url="login")
def deleteRoom(request, pk):
    room = Rooms.objects.get(id=pk)
    topic = room.topic
    if request.user != room.owner:
        return redirect("home")
    if len(topic.rooms_set.all()) == 0:
        topic.delete()

    room.delete()
    return redirect("home")

def notifications(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
    context = {"profile":profile}
    return render(request, "notifications.html", context)