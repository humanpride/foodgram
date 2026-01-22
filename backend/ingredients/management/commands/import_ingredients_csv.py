import csv
import os
from typing import Iterable, Tuple

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ingredients.models import Ingredient


class Command(BaseCommand):
    help = (
        'Import ingredients from a CSV file. '
        'Usage: python manage.py import_ingredient_csv /path/to/file.csv'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help=(
                'Path to the CSV file to import. '
                'Expected columns: name, measurement_unit (header optional).'
            ),
        )

    def _iter_rows(self, file) -> Iterable[Tuple[str, str]]:
        """Yield (name, measurement_unit) pairs.
        Supports files with header and without header.
        Skips empty lines and invalid rows.
        """
        sample = file.read(2048)
        file.seek(0)

        try:
            has_header = csv.Sniffer().has_header(sample)
        except Exception:
            has_header = False

        if has_header:
            reader = csv.DictReader(file)
            for row in reader:
                name = row['name'].strip()
                measurement_unit = row['measurement_unit'].strip()
                if not name:
                    continue
                yield name, (measurement_unit or 'шт.')
        else:
            reader = csv.reader(file)
            for row in reader:
                row = [col.strip() for col in row]
                if len(row) < 2:
                    continue
                yield row[0], row[1]

    def handle(self, *args, **options):
        path = options.get('csv_file')
        if not path:
            raise CommandError('Path to CSV file is required.')

        if not os.path.exists(path):
            raise CommandError(f'File not found: {path}')

        if not path.lower().endswith('.csv'):
            raise CommandError('File must have .csv extension')

        created = 0
        skipped_existing = 0

        unique_rows = {}
        with open(path, encoding='utf-8') as f:
            for name, measurement_unit in self._iter_rows(f):
                if name not in unique_rows:
                    unique_rows[name] = measurement_unit

        names = list(unique_rows.keys())

        with transaction.atomic():
            existing = set(
                Ingredient.objects.filter(name__in=names).values_list(
                    'name', flat=True
                )
            )
            to_create = [
                Ingredient(name=name, measurement_unit=unique_rows[name])
                for name in names
                if name not in existing
            ]

            if to_create:
                Ingredient.objects.bulk_create(to_create)
                created = len(to_create)

            skipped_existing = len(names) - created

        self.stdout.write(
            self.style.SUCCESS(
                f'Import finished: created {created}, '
                f'skipped_existing {skipped_existing}'
            )
        )
