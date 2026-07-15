from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Note


class NotesAccessTests(TestCase):
    def setUp(self):
        self.alex = User.objects.create_user(username='alex', password='pass12345')
        self.sam = User.objects.create_user(username='sam', password='pass12345')
        self.category = Category.objects.create(owner=self.alex, name='Work')
        self.alex_note = Note.objects.create(
            owner=self.alex,
            category=self.category,
            title='Alex private note',
            body='Only Alex should see this.',
            tags='private, work',
        )
        self.sam_note = Note.objects.create(
            owner=self.sam,
            title='Sam private note',
            body='Only Sam should see this.',
        )

    def test_note_list_requires_login(self):
        response = self.client.get(reverse('note_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_user_only_sees_their_own_notes(self):
        self.client.login(username='alex', password='pass12345')
        response = self.client.get(reverse('note_list'))
        self.assertContains(response, self.alex_note.title)
        self.assertNotContains(response, self.sam_note.title)

    def test_user_cannot_edit_another_users_note(self):
        self.client.login(username='alex', password='pass12345')
        response = self.client.get(reverse('note_update', args=[self.sam_note.id]))
        self.assertEqual(response.status_code, 404)

    def test_create_note_assigns_logged_in_owner(self):
        self.client.login(username='sam', password='pass12345')
        response = self.client.post(
            reverse('note_create'),
            {
                'title': 'New Sam note',
                'body': 'Created from the form.',
                'category': '',
                'tags': 'ideas',
                'priority': Note.HIGH,
                'color': '#ffffff',
            },
        )
        self.assertRedirects(response, reverse('note_list'))
        self.assertTrue(Note.objects.filter(owner=self.sam, title='New Sam note').exists())
