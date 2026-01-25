import csv
import json

from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient


class Command(BaseCommand):
    help = (
        'Import ingredients from a CSV or JSON file. '
        'Usage: python manage.py import_ingredients /path/to/file'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help=(
                'Path to CSV/JSON file to import. '
                'Expected columns: name, measurement_unit (header optional).'
            ),
        )

    def handle(self, *args, **options):
        try:
            path: str = options['file_path']

            with open(path, encoding='utf-8') as f:
                if path.endswith('.csv'):
                    ingredients = [
                        Ingredient(name=row[0], measurement_unit=row[1])
                        for row in csv.reader(f)
                    ]
                elif path.endswith('.json'):
                    ingredients = [
                        Ingredient(
                            name=item['name'],
                            measurement_unit=item['measurement_unit'],
                        )
                        for item in json.load(f)
                    ]
                else:
                    raise CommandError('File must have csv/json extension')
            created = Ingredient.objects.bulk_create(
                ingredients, ignore_conflicts=True
            )

            created_count = len(created)
            skipped_existing_count = len(ingredients) - created_count

            self.stdout.write(
                self.style.SUCCESS(
                    f'{path} imported successfully: '
                    f'created {created_count}, '
                    f'skipped_existing {skipped_existing_count}'
                )
            )
        except KeyError as err:
            raise CommandError('Path to CSV file is required.') from err
