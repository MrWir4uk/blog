from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()



class Profile(models.Model):
    ROLE_CHOICES = (
        ('user', 'Користувач'),
        ('author', 'Автор'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Subscription(models.Model):
    from_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="followers")
    to_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="subscriptions")
    created_at = models.DateTimeField(auto_now_add=True)



class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50)
   

    def __str__(self):
        return self.name


class Post(models.Model):

    STATUS_CHOICES = (
        ('draft', 'Чернетка'),
        ('published', 'Опубліковано'),
    )

    title = models.CharField(max_length=200)
    

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )

    content = models.TextField()

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='posts'
    )

    tags = models.ManyToManyField(Tag, blank=True)

    image = models.ImageField(
        upload_to='post_images/',
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(r.value for r in ratings) / ratings.count(), 1)
        return 0

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    is_approved = models.BooleanField(default=True)

    def __str__(self):
        return f"Коментар від {self.author.username}"


class Rating(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='ratings'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    value = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.post.title} - {self.value}"
    

