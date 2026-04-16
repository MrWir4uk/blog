import os
import django
import random

# --- DJANGO SETUP ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blog.settings")
django.setup()



import random
from django.contrib.auth.models import User
from main.models import Category, Tag, Post, Comment, Rating

# --- USERS ---
users = []
for i in range(10):
    user, _ = User.objects.get_or_create(username=f"user{i}")
    user.set_password("1234")
    user.save()
    users.append(user)

print("Users ready")

# --- CATEGORIES (EN) ---
category_names = [
    "Programming",
    "Technology",
    "Gaming",
    "Movies",
    "Self Development"
]

categories = []
for name in category_names:
    category, _ = Category.objects.get_or_create(name=name)
    categories.append(category)

print("Categories ready")

# --- TAGS (EN) ---
tag_names = [
    "python", "django", "ai", "frontend", "backend",
    "gaming", "marvel", "fast-furious", "motivation", "life",
    "javascript", "react", "coding", "tutorial", "tips"
]

tags = []
for name in tag_names:
    category = random.choice(categories)

    tag, _ = Tag.objects.get_or_create(
        name=name,
        defaults={"category": category}
    )

    tags.append(tag)

print("Tags ready")

# --- ГЕНЕРАЦІЯ КОНТЕНТУ (UA) ---
def generate_content(topic):
    return f"""
    <h2>Гайд по {topic}</h2>
    <p>У цій статті розглянемо тему <b>{topic}</b> більш детально.</p>

    <p>Це приклад контенту для заповнення блогу. Тут може бути будь-яка корисна інформація,
    поради, досвід або пояснення складних речей простими словами.</p>

    <h3>Основні моменти:</h3>
    <ul>
        <li>База та основи {topic}</li>
        <li>Як це використовувати на практиці</li>
        <li>Типові помилки новачків</li>
    </ul>

    <p>Висновок: вивчення теми <b>{topic}</b> допоможе прокачати твої навички 🚀</p>
    """

# --- POSTS (UA) ---
posts = []

for i in range(40):
    topic = random.choice(tag_names)

    post = Post.objects.create(
        title=f"Поради по {topic} #{i}",
        author=random.choice(users),
        content=generate_content(topic),
        category=random.choice(categories),
        status="published"
    )

    post.tags.set(random.sample(tags, k=random.randint(2, 5)))
    posts.append(post)

print("Posts created")

# --- COMMENTS (UA) ---
comments_samples = [
    "Крутий пост 🔥",
    "Дуже корисно, дякую!",
    "Дізнався щось нове 👍",
    "Гарно пояснено",
    "Було б круто більше таких статей",
    "Цікава думка 🤔"
]

for post in posts:
    for _ in range(random.randint(3, 10)):
        Comment.objects.create(
            post=post,
            author=random.choice(users),
            content=random.choice(comments_samples),
            is_approved=True
        )

print("Comments created")

# --- RATINGS ---
for post in posts:
    used_users = random.sample(users, k=random.randint(4, 9))
    for user in used_users:
        Rating.objects.get_or_create(
            post=post,
            user=user,
            defaults={"value": random.randint(5, 10)}
        )

print("Ratings created")

print("🔥 База заповнена: EN теги/категорії + UA контент!")