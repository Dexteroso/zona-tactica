from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db.models import F, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CreatorRegistrationForm, VideoEditForm, VideoUploadForm
from .models import Video


@login_required(login_url="login")
def upload_video(request):
    if request.method == "POST":
        form = VideoUploadForm(request.POST, request.FILES)

        if form.is_valid():
            video = form.save(commit=False)
            video.creator = request.user
            video.save()
            return redirect("upload_success")
    else:
        form = VideoUploadForm()

    return render(request, "videos_app/videos_form.html", {"form": form})

@login_required(login_url="login")
def upload_success(request):
    return render(request, "videos_app/success.html")

def register(request):
    form = CreatorRegistrationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()

        creators_group = Group.objects.get(name="Creators")
        user.groups.add(creators_group)

        login(request, user)

        return redirect("index")

    return render(request, "registration/register.html", {"form": form})

def lista_videos(request):
    creator_name = request.GET.get("creator", "").strip()
    videos = Video.objects.select_related("creator").all()

    if creator_name:
        videos = videos.filter(
            Q(titulo__icontains=creator_name)
            | Q(creator__nickname__icontains=creator_name)
        )

    return render(
        request,
        "videos_app/lista_videos.html",
        {
            "videos": videos,
            "creator_name": creator_name,
            "mis_videos": False,
        },
    )


@login_required(login_url="login")
def mis_videos(request):
    creator_name = request.GET.get("creator", "").strip()
    videos = Video.objects.select_related("creator").filter(creator=request.user)

    if creator_name:
        videos = videos.filter(
            Q(titulo__icontains=creator_name)
            | Q(creator__nickname__icontains=creator_name)
        )

    return render(
        request,
        "videos_app/lista_videos.html",
        {
            "videos": videos,
            "creator_name": creator_name,
            "mis_videos": True,
        },
    )


@login_required(login_url="login")
def editar_video(request, video_id):
    video = get_object_or_404(Video, id=video_id, creator=request.user)

    if request.method == "POST":
        form = VideoEditForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            form.save()
            return redirect("mis_videos")
    else:
        form = VideoEditForm(instance=video)

    return render(
        request,
        "videos_app/videos_form.html",
        {"form": form, "editando": True},
    )


@require_POST
def registrar_vista_video(request, video_id):
    actualizados = Video.objects.filter(id=video_id).update(vistas=F("vistas") + 1)
    if not actualizados:
        raise Http404

    vistas = Video.objects.values_list("vistas", flat=True).get(id=video_id)
    return JsonResponse({"vistas": vistas})


def eliminar_video(request, video_id):
    if request.method != 'POST':
        return redirect('index')

    video = get_object_or_404(Video, id=video_id)
    if video.archivo:
        video.archivo.delete(save=False)
    video.delete()
    return redirect('index')
