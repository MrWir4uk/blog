from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Comment, Category, Tag, Rating
from .forms import PostForm, ProfileForm
from django.contrib import messages
from django.shortcuts import redirect

from .forms import CommentForm



from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Comment, Category, Tag, Rating
from .forms import PostForm, ProfileForm
from django.contrib import messages
from django.shortcuts import redirect

from .forms import CommentForm



def post_list(request):
    category_id = request.GET.get("category")
    tag_id = request.GET.get("tag")
    
    posts = Post.objects.filter(status='published')
    categories = Category.objects.all()
    tags = None  # теги вибраної категорії

    # Фільтр по категорії
    if category_id and category_id != "all":
        posts = posts.filter(category_id=category_id)
        # отримуємо всі теги цієї категорії
        tags = Tag.objects.filter(category_id=category_id)

    # Фільтр по тегу
    if tag_id:
        posts = posts.filter(tags__id=tag_id)

    return render(request, 'post_list.html', {
        'posts': posts,
        'categories': categories,
        'tags': tags,
        'selected_category': category_id,
        'selected_tag': tag_id,
        'rating_range': range(1, 11)
        
    })



def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # беремо тільки затверджені коментарі
    comments = post.comments.filter(is_approved=True).order_by('-created_at')

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.author = request.user
                comment.post = post
                comment.save()
                return redirect('post_detail', pk=post.pk)
        else:
            return redirect('accounts/login/')
    else:
        form = CommentForm()

    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
    })


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
    posts = request.user.posts.filter(status='published').all() 
    return render(request, "profile.html", {'profile': profile, 'posts': posts})


@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            # Зміна username
            username = form.cleaned_data.get('username')
            if username:
                request.user.username = username
                request.user.save()
            profile.save()
            messages.success(request, "Профіль оновлено успішно!")
            return redirect('profile')
    else:
        # Передаємо початкові дані для username
        form = ProfileForm(instance=profile, initial={'username': request.user.username})

    return render(request, "edit_profile.html", {'form': form})



@login_required
def my_drafts(request):
    drafts = Post.objects.filter(author=request.user, status='draft')
    return render(request, 'my_drafts.html', {'drafts': drafts})


@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # щоб користувач міг редагувати тільки свій пост
    if post.author != request.user:
        messages.error(request, "Ви не можете редагувати цей пост")
        return redirect('post_list')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)

    return render(request, 'create_post.html', {'form': form})



@login_required
def edit_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk=comment.post.pk)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'edit_comment.html', {'form': form})

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user == comment.author or request.user == comment.post.author or request.user.is_staff:
        post_pk = comment.post.pk
        comment.delete()
        return redirect('post_detail', pk=post_pk)
    else:
        return redirect('post_detail', pk=comment.post.pk)
    

# Видалення поста
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        messages.error(request, "Ви можете видаляти лише свої пости!")
        return redirect('post_list')

    if request.method == "POST":
        post.delete()
        messages.success(request, "Пост успішно видалено!")
        return redirect('profile')  # просто на свій профіль

    return render(request, 'confirm_delete.html', {'object': post, 'type': 'пост'})


# Видалення чернетки
@login_required
def delete_draft(request, draft_id):
    draft = get_object_or_404(Post, id=draft_id, status='draft')  # перевіряємо статус

    if draft.author != request.user:
        messages.error(request, "Ви можете видаляти лише свої чернетки!")
        return redirect('my_drafts')

    if request.method == "POST":
        draft.delete()
        messages.success(request, "Чернетка успішно видалена!")
        return redirect('my_drafts')

    return render(request, 'confirm_delete.html', {'object': draft, 'type': 'чернетку'})




@login_required
def rate_post(request, post_id, value):
    post = get_object_or_404(Post, id=post_id)
    
    # Перевіримо, щоб оцінка була від 1 до 10
    if value < 1 or value > 10:
        return redirect('post_list')
    
    # Якщо користувач вже оцінював пост — оновимо
    rating, created = Rating.objects.update_or_create(
        post=post,
        user=request.user,
        defaults={'value': value}
    )
    
    return redirect('post_list')



def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # беремо тільки затверджені коментарі
    comments = post.comments.filter(is_approved=True).order_by('-created_at')

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.author = request.user
                comment.post = post
                comment.save()
                return redirect('post_detail', pk=post.pk)
        else:
            return redirect('accounts/login/')
    else:
        form = CommentForm()

    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
    })


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
    posts = request.user.posts.filter(status='published').all() 
    return render(request, "profile.html", {'profile': profile, 'posts': posts})


@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            # Зміна username
            username = form.cleaned_data.get('username')
            if username:
                request.user.username = username
                request.user.save()
            profile.save()
            messages.success(request, "Профіль оновлено успішно!")
            return redirect('profile')
    else:
        # Передаємо початкові дані для username
        form = ProfileForm(instance=profile, initial={'username': request.user.username})

    return render(request, "edit_profile.html", {'form': form})



@login_required
def my_drafts(request):
    drafts = Post.objects.filter(author=request.user, status='draft')
    return render(request, 'my_drafts.html', {'drafts': drafts})


@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # щоб користувач міг редагувати тільки свій пост
    if post.author != request.user:
        messages.error(request, "Ви не можете редагувати цей пост")
        return redirect('post_list')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)

    return render(request, 'create_post.html', {'form': form})



@login_required
def edit_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk=comment.post.pk)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'edit_comment.html', {'form': form})

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user == comment.author or request.user == comment.post.author or request.user.is_staff:
        post_pk = comment.post.pk
        comment.delete()
        return redirect('post_detail', pk=post_pk)
    else:
        return redirect('post_detail', pk=comment.post.pk)
    

# Видалення поста
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        messages.error(request, "Ви можете видаляти лише свої пости!")
        return redirect('post_list')

    if request.method == "POST":
        post.delete()
        messages.success(request, "Пост успішно видалено!")
        return redirect('profile')  # просто на свій профіль

    return render(request, 'confirm_delete.html', {'object': post, 'type': 'пост'})


# Видалення чернетки
@login_required
def delete_draft(request, draft_id):
    draft = get_object_or_404(Post, id=draft_id, status='draft')  # перевіряємо статус

    if draft.author != request.user:
        messages.error(request, "Ви можете видаляти лише свої чернетки!")
        return redirect('my_drafts')

    if request.method == "POST":
        draft.delete()
        messages.success(request, "Чернетка успішно видалена!")
        return redirect('my_drafts')

    return render(request, 'confirm_delete.html', {'object': draft, 'type': 'чернетку'})





@login_required
def rate_post(request, post_id, value):
    post = get_object_or_404(Post, id=post_id)
    
    # Перевіримо, щоб оцінка була від 1 до 10
    if value < 1 or value > 10:
        return redirect('post_list')
    
    # Якщо користувач вже оцінював пост — оновимо
    rating, created = Rating.objects.update_or_create(
        post=post,
        user=request.user,
        defaults={'value': value}
    )
    
    return redirect('post_list')