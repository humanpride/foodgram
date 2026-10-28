import json

from django.core.management.base import BaseCommand, CommandError


class BaseImportCommand(BaseCommand):
    """
    Base command for importing data from JSON fixtures.
    Subclasses must specify:
        - model: model to import data into
        - help: command description
    """

    model = None
    path = None

    def handle(self, *args, **options):
        try:
            with open(self.path, encoding='utf-8') as f:
                instances = [self.model(**item) for item in json.load(f)]

            created_objects = self.model.objects.bulk_create(
                instances, ignore_conflicts=True
            )

            created_count = len(created_objects)
            skipped_count = len(instances) - created_count

            self.stdout.write(
                self.style.SUCCESS(
                    f'{self.path} imported successfully: '
                    f'created {created_count}, skipped {skipped_count}'
                )
            )

        except Exception as err:
            raise CommandError(f'Failed to import {self.path}: {err}') from err
