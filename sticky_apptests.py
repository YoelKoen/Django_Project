# sticky_app/tests.py

from django.test import TestCase
from .models import Note
from django.urls import reverse # Useful for functional/view testing

class NoteModelTest(TestCase):
    def test_note_creation(self):
        note = Note.objects.create(title="Grocery", content="Milk, eggs, bread")
        self.assertEqual(note.title, "Grocery")
        self.assertTrue(Note.objects.exists())

    def test_note_content_update(self):
        note = Note.objects.create(title="Old Task", content="Original content")
        note.content = "New content"
        note.save()
        updated_note = Note.objects.get(pk=note.pk)
        self.assertEqual(updated_note.content, "New content")

    def test_note_deletion(self):
        note = Note.objects.create(title="Delete Me", content="Temp")
        note_pk = note.pk
        note.delete()
        with self.assertRaises(Note.DoesNotExist):
            Note.objects.get(pk=note_pk)