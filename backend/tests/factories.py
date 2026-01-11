import factory
from django.contrib.auth import get_user_model

from ingredients.models import Ingredient
from recipes.models import Recipe, RecipeIngredient
from tags.models import Tag
from users.models import Favorite, ShoppingCartItem, Subscription


User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.test')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    is_staff = False
    is_superuser = False
    avatar = None


class IngredientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ingredient
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: f'ingredient{n}')
    measurement_unit = 'g'


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag
        django_get_or_create = ('slug',)

    name = factory.Sequence(lambda n: f'tag{n}')
    slug = factory.LazyAttribute(lambda o: o.name.lower())


class RecipeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Recipe

    name = factory.Sequence(lambda n: f'recipe{n}')
    author = factory.SubFactory(UserFactory)
    text = 'Test recipe'
    cooking_time = 10

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for tag in extracted:
                self.tags.add(tag)
        else:
            self.tags.add(TagFactory())

    @factory.post_generation
    def ingredients(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for ing, amount in extracted:
                RecipeIngredient.objects.create(
                    recipe=self, ingredient=ing, amount=amount
                )
        else:
            ing = IngredientFactory()
            RecipeIngredient.objects.create(
                recipe=self, ingredient=ing, amount=100
            )


class RecipeIngredientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RecipeIngredient

    recipe = factory.SubFactory(RecipeFactory)
    ingredient = factory.SubFactory(IngredientFactory)
    amount = 1


class FavoriteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Favorite

    user = factory.SubFactory(UserFactory)
    recipe = factory.SubFactory(RecipeFactory)


class ShoppingCartItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ShoppingCartItem

    user = factory.SubFactory(UserFactory)
    recipe = factory.SubFactory(RecipeFactory)


class SubscriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Subscription

    from_user = factory.SubFactory(UserFactory)
    to_user = factory.SubFactory(UserFactory)
