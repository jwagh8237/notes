from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Category, Note


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = [
            'title',
            'body',
            'category',
            'tags',
            'priority',
            'color',
            'is_pinned',
            'is_archived',
        ]
        widgets = {
            'body': forms.Textarea(attrs={'rows': 10}),
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.none()
        self.fields['category'].required = False

        if user is not None:
            self.fields['category'].queryset = Category.objects.filter(owner=user)

        for field in self.fields.values():
            css_class = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{css_class} form-control'.strip()
