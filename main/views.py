from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import PostForm
from django.contrib import messages
from django.shortcuts import redirect


def post_list(request):
    posts = Post.objects.filter(status='published')
    return render(request, 'post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'post_detail.html', {'post': post})


@login_required
def create_post(request):
    # Перевірка ролі або адміна
    if request.user.profile.role != 'author' and not request.user.is_superuser:
        messages.error(request, "Тільки автори та адміни можуть створювати пости.")
        return redirect('post_list')

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            return redirect('post_detail', pk=post.pk)
        else:
            print(form.errors)
    else:
        form = PostForm()

    return render(request, 'create_post.html', {'form': form})
    


@login_required
def profile_view(request):
    profile = request.user.profile
    return render(request, "profile.html", {'profile': profile})


