import json

from django.core.management.base import BaseCommand, CommandError


class BaseImportCommand(BaseCommand):
    """
    Базовая команда для импорта данных из JSON фикстур.
    Наследники должны указать:
        - model: модель для импорта
        - help: описание команды
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
                    f'{self.path} импортирован успешно: '
                    f'создано {created_count}, пропущено {skipped_count}'
                )
            )

        except Exception as err:
            raise CommandError(f'Ошибка импорта {self.path}: {err}') from err
