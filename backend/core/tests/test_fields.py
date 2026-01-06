from django.core.files.base import ContentFile
from django.test import SimpleTestCase
from rest_framework import serializers

from core.fields import Base64ImageField

# 1x1 PNG encoded in base64 (data URI)
SAMPLE_BASE64_PNG = (
    'data:image/png;base64,'
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S'
    '0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJ'
    'RU5ErkJggg=='
)


class TestSerializer(serializers.Serializer):
    image = Base64ImageField()


class Base64ImageFieldTest(SimpleTestCase):
    def test_base64_to_contentfile(self):
        serializer = TestSerializer(data={'image': SAMPLE_BASE64_PNG})
        assert serializer.is_valid(), f'Serializer errors: {serializer.errors}'
        image = serializer.validated_data['image']

        self.assertIsInstance(image, ContentFile)

        self.assertTrue(str(image.name).lower().endswith('.png'))

        image.seek(0)
        content = image.read()
        self.assertTrue(content.startswith(b'\x89PNG\r\n\x1a\n'))
        self.assertGreater(len(content), 0)
