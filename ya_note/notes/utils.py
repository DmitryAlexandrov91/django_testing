from notes.models import Note


def note_counter():
    notes_count = Note.objects.count()
    return notes_count
