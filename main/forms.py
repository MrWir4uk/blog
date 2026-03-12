from django import forms
from .models import Post, Profile
from django_select2 import forms as s2forms
from .models import Comment


class TagWigget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        "name__icontains",
    ]
    dependent_fields = {
        "category": "category"
    }
    
    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs['data-minimum-input-length'] = 0
        return attrs

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'tags', 'image', 'status']
        widgets = {
            "tags": TagWigget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control mb-2', })

            


class ProfileForm(forms.ModelForm):
    # Нікнейм як окреме поле, не через Meta, бо це поле User
    username = forms.CharField(
        max_length=150,
        label="Нікнейм",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введіть ваш нікнейм'
        })
    )

    class Meta:
        model = Profile
        fields = ['avatar']  # аватар беремо з моделі Profile
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'  # обмеження на тип файлу
            }),
        }

    def __init__(self, *args, **kwargs):
        # Можемо передати початковий username
        initial_username = kwargs.pop('initial_username', None)
        super().__init__(*args, **kwargs)
        if initial_username:
            self.fields['username'].initial = initial_username

    def save(self, commit=True):
        profile = super().save(commit=False)
        # username зберігаємо окремо в User
        if self.cleaned_data.get('username'):
            profile.user.username = self.cleaned_data['username']
            profile.user.save()
        if commit:
            profile.save()
        return profile


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