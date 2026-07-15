from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CategoryForm, NoteForm, RegisterForm
from .models import Category, Note


def register(request):
    if request.user.is_authenticated:
        return redirect('note_list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome. Your notes workspace is ready.')
            return redirect('note_list')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def note_list(request):
    notes = Note.objects.filter(owner=request.user).select_related('category')
    categories = Category.objects.filter(owner=request.user)

    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', 'active')
    category_id = request.GET.get('category', '')
    priority = request.GET.get('priority', '')

    if status == 'archived':
        notes = notes.filter(is_archived=True)
    elif status != 'all':
        notes = notes.filter(is_archived=False)

    if query:
        notes = notes.filter(
            Q(title__icontains=query)
            | Q(body__icontains=query)
            | Q(tags__icontains=query)
        )

    if category_id:
        notes = notes.filter(category_id=category_id, category__owner=request.user)

    if priority:
        notes = notes.filter(priority=priority)

    context = {
        'notes': notes,
        'categories': categories,
        'category_form': CategoryForm(),
        'query': query,
        'status': status,
        'selected_category': category_id,
        'selected_priority': priority,
        'active_count': Note.objects.filter(owner=request.user, is_archived=False).count(),
        'archived_count': Note.objects.filter(owner=request.user, is_archived=True).count(),
        'pinned_count': Note.objects.filter(owner=request.user, is_pinned=True).count(),
        'priority_choices': Note.PRIORITY_CHOICES,
    }
    return render(request, 'notes/note_list.html', context)


@login_required
def note_create(request):
    if request.method == 'POST':
        form = NoteForm(request.POST, user=request.user)
        if form.is_valid():
            note = form.save(commit=False)
            note.owner = request.user
            note.save()
            messages.success(request, 'Note created.')
            return redirect('note_list')
    else:
        form = NoteForm(user=request.user)

    return render(request, 'notes/note_form.html', {'form': form, 'title': 'New note'})


@login_required
def note_update(request, pk):
    note = get_object_or_404(Note, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Note updated.')
            return redirect('note_list')
    else:
        form = NoteForm(instance=note, user=request.user)

    return render(request, 'notes/note_form.html', {'form': form, 'title': 'Edit note'})


@login_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, owner=request.user)

    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Note deleted.')
        return redirect('note_list')

    return render(request, 'notes/note_confirm_delete.html', {'note': note})


@require_POST
@login_required
def note_toggle_pin(request, pk):
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    note.is_pinned = not note.is_pinned
    note.save(update_fields=['is_pinned', 'updated_at'])
    return redirect(request.POST.get('next') or 'note_list')


@require_POST
@login_required
def note_toggle_archive(request, pk):
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    note.is_archived = not note.is_archived
    note.save(update_fields=['is_archived', 'updated_at'])
    return redirect(request.POST.get('next') or 'note_list')


@require_POST
@login_required
def category_create(request):
    form = CategoryForm(request.POST)
    if form.is_valid():
        name = form.cleaned_data['name'].strip()
        if Category.objects.filter(owner=request.user, name__iexact=name).exists():
            messages.error(request, 'You already have a category with that name.')
        else:
            category = form.save(commit=False)
            category.owner = request.user
            category.name = name
            category.save()
            messages.success(request, 'Category added.')
    else:
        messages.error(request, 'Category could not be added.')

    return redirect('note_list')


@require_POST
@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, owner=request.user)
    category.delete()
    messages.success(request, 'Category deleted.')
    return redirect('note_list')
