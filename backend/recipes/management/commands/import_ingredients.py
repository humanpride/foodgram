from recipes.management.commands.base_import import BaseImportCommand
from recipes.models import Ingredient


class Command(BaseImportCommand):
    help = (
        'Импорт ингредиентов из JSON фикстуры. '
        'Пример: python manage.py import_ingredients /path/to/file'
    )
    model = Ingredient
    path = 'data/ingredients.json'
