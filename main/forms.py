from django import forms
from .models import Post, Profile
from django_select2 import forms as s2forms
from .models import Comment


class TagWigget(s2forms.ModelSelect2Widget):
    search_fields = [
        "name__icontains", 
    ]

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'tags', 'image', 'status']
        # widgets = {
        #     "tags": TagWigget,
        # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control mb-2', })



class ProfileForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        label="Нікнейм",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Profile
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Напишіть коментар...',
            'autocomplete': 'off'  # не зберігати текст при натисканні "назад"
        }),
        max_length=500,
        required=True,
        error_messages={
            'required': 'Коментар не може бути порожнім!',
            'max_length': 'Коментар не може бути довшим за 500 символів.'
        }
    )

    class Meta:
        model = Comment
        fields = ['content']