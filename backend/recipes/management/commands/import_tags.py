from recipes.management.commands.base_import import BaseImportCommand
from recipes.models import Tag


class Command(BaseImportCommand):
    help = (
        'Импорт тегов из JSON фикстуры. '
        'Пример: python manage.py import_tags /path/to/file'
    )
    model = Tag
    path = 'data/tags.json'
