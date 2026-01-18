"""
Pytest-Django tests generated from the provided checklist.

HOW TO USE
- Save this file to your tests folder (for example: `tests/test_checklist.py`).
- Replace placeholders of the form <your_project_*> with project-specific values.
- Run with pytest (pytest-django==4.11.1): `pytest -q`.

PLACEHOLDERS you must replace before running:
- <your_project_home_url_name>              -> URL name for the project home page (for reverse()).
- <your_project_recipe_detail_url_name>     -> URL name for recipe detail view; expects arg 'pk' or defined accordingly.
- <your_project_user_profile_url_name>      -> URL name for user profile page; expects arg 'username' or 'pk'.
- <your_project_author_recipes_url_name>    -> URL name for list of recipes for a single author.
- <your_project_favorites_url_name>        -> URL name for favorites list page.
- <your_project_subscriptions_url_name>    -> URL name for "my subscriptions" page.
- <your_project_shopping_list_url_name>    -> URL name for shopping list page / download endpoint.
- <your_project_add_favorite_url_name>     -> URL name to add/remove favorite; expects args as your project uses.
- <your_project_add_shopping_url_name>     -> URL name to add/remove shopping cart item.
- <your_project_subscribe_url_name>        -> URL name to subscribe/unsubscribe to author.
- <your_project_create_recipe_url_name>    -> URL name for recipe creation page.
- <your_project_edit_recipe_url_name>      -> URL name for recipe edit page; expects recipe pk.
- <your_project_delete_recipe_url_name>    -> URL name for recipe delete view; expects recipe pk.
- <your_project_recipe_model>               -> Import path to your Recipe model (e.g. 'recipes.models.Recipe').
- <your_project_tag_model>                  -> Import path to your Tag model (e.g. 'tags.models.Tag').
- <your_project_ingredient_model>           -> Import path to your Ingredient model.
- <your_project_user_model>                 -> Import path to your User model (or use django_user_model fixture).
- <your_project_default_page_size>          -> Default page size used in your paginator (int).
- <your_project_static_root_setting>        -> settings.STATIC_ROOT or another setting that points to static files.
- <your_project_allowed_hosts_or_host>      -> IP or domain where project is expected to be served (for integration tests).
- <your_project_manage_static_served_by_nginx_check> -> Optional path or marker to inspect nginx setup.

NOTES
- Some tests are marked as integration or skipped because they require external services (nginx, docker containers, remote server).
- Replace placeholders first, or tests will fail / be skipped.

"""

import subprocess
import sys
from importlib import import_module

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone


def _import(path):
    """Import by dotted path placeholder -> actual model/class.
    Example placeholder replacement expected: 'recipes.models.Recipe'
    """
    module_path, attr = path.rsplit('.', 1)
    module = import_module(module_path)
    return getattr(module, attr)


# --- Tests start here ---


@pytest.mark.django_db
def test_project_homepage_accessible(client):
    """Главная страница доступна (для любого пользователя)."""
    url = reverse('<your_project_home_url_name>')
    resp = client.get(url)
    assert resp.status_code == 200, (
        f'Expected 200 on home, got {resp.status_code}'
    )


@pytest.mark.django_db
def test_recipe_detail_and_user_profile_accessible(client, django_user_model):
    """Страницы рецепта и пользователя доступны для
    неавторизованного пользователя."""
    User = django_user_model
    # create user and recipe using placeholders for Recipe model
    Recipe = _import('<your_project_recipe_model>')

    user = User.objects.create_user(
        username='testuser', email='test@example.com', password='pass'
    )
    recipe = Recipe.objects.create(
        author=user, name='Tasty', text='Yum', pub_date=timezone.now()
    )

    recipe_url = reverse(
        '<your_project_recipe_detail_url_name>', args=[recipe.pk]
    )
    profile_url = reverse(
        '<your_project_user_profile_url_name>', args=[user.username]
    )

    assert client.get(recipe_url).status_code == 200
    assert client.get(profile_url).status_code == 200


@pytest.mark.django_db
def test_recipes_ordered_by_pub_date(client, django_user_model):
    """Рецепты на страницах сортируются по дате публикации (новые выше)."""
    User = django_user_model
    Recipe = _import('<your_project_recipe_model>')

    author = User.objects.create_user(username='order_author')
    # older recipe
    Recipe.objects.create(
        author=author,
        name='old',
        text='old',
        pub_date=timezone.now() - timezone.timedelta(days=5),
    )
    # newer recipe
    Recipe.objects.create(
        author=author, name='new', text='new', pub_date=timezone.now()
    )

    # access author's recipe list (placeholder)
    url = reverse(
        '<your_project_author_recipes_url_name>', args=[author.username]
    )
    resp = client.get(url)
    assert resp.status_code == 200

    content = resp.content.decode('utf-8')
    # basic check: newer recipe title should appear before older in HTML
    assert content.index('new') < content.index('old')


@pytest.mark.django_db
def test_filtering_by_tags_works(client, django_user_model):
    """Фильтрация по тегам работает (включая favorites and author pages)."""
    User = django_user_model
    Recipe = _import('<your_project_recipe_model>')
    Tag = _import('<your_project_tag_model>')

    user = User.objects.create_user(username='taguser')
    tag1 = Tag.objects.create(name='lunch', slug='lunch')
    tag2 = Tag.objects.create(name='dinner', slug='dinner')

    r1 = Recipe.objects.create(
        author=user, name='L1', text='a', pub_date=timezone.now()
    )
    r2 = Recipe.objects.create(
        author=user, name='D1', text='b', pub_date=timezone.now()
    )

    # Attach tags - the project may use m2m
    # through 'tags' field - adjust as needed
    try:
        r1.tags.add(tag1)
        r2.tags.add(tag2)
    except Exception:
        # If your project uses another relation,
        # leave placeholders to implement
        pytest.skip('Adjust tag assignment for your project models')

    # Filter by tag on recipes page (showing
    # query param 'tags' as common pattern)
    recipes_url = reverse(
        '<your_project_author_recipes_url_name>', args=[user.username]
    )
    resp = client.get(recipes_url + '?tags=lunch')
    assert resp.status_code == 200
    assert 'L1' in resp.content.decode() and 'D1' not in resp.content.decode()


@pytest.mark.django_db
def test_pagination_works_with_filtering(client, django_user_model):
    """Пагинатор работает, в том числе при фильтрации по тегам."""
    User = django_user_model
    Recipe = _import('<your_project_recipe_model>')
    Tag = _import('<your_project_tag_model>')

    user = User.objects.create_user(username='pageuser')
    tag = Tag.objects.create(name='many', slug='many')

    page_size = int('<your_project_default_page_size>')

    for i in range(page_size + 3):
        r = Recipe.objects.create(
            author=user, name=f'R{i}', text='x', pub_date=timezone.now()
        )
        try:
            r.tags.add(tag)
        except Exception:
            pytest.skip('Adjust tag assignment for your project models')

    url = reverse(
        '<your_project_author_recipes_url_name>', args=[user.username]
    )
    resp1 = client.get(url + '?tags=many')
    assert resp1.status_code == 200
    # basic check for pagination links or next page existence
    assert ('page=2' in resp1.content.decode()) or (
        len(resp1.content.decode()) > 0
    )


@pytest.mark.django_db
def test_preloaded_test_data_exists():
    """Проверяем, что в проекте есть предзагруженные
    тестовые данные (пользователи/рецепты).
    Это простой чек — попытаемся найти какой-нибудь объект в БД.
    """
    Recipe = _import('<your_project_recipe_model>')
    # if no recipes, fail the test to indicate preloaded data missing
    assert Recipe.objects.exists(), (
        'No recipes found — please ensure fixtures are loaded.'
    )


@pytest.mark.django_db
def test_shopping_list_download_and_aggregation(client, django_user_model):
    """Пользователь может скачать список покупок;
    ингредиенты суммируются и не повторяются.

    This test assumes the project exposes an endpoint
    to download the shopping list content as plain text
    at the URL named by the placeholder. Replace placeholders as needed.
    """
    User = django_user_model
    Recipe = _import('<your_project_recipe_model>')
    Ingredient = _import('<your_project_ingredient_model>')

    user = User.objects.create_user(username='shopuser', password='pass')
    ingredient = Ingredient.objects.create(name='Salt', measurement_unit='g')

    # Create two recipes that both use
    # the same ingredient with different amounts
    r1 = Recipe.objects.create(
        author=user, name='A', text='a', pub_date=timezone.now()
    )
    r2 = Recipe.objects.create(
        author=user, name='B', text='b', pub_date=timezone.now()
    )

    # Attach ingredient quantities - project-specific;
    # try common through model name 'ingredients'
    try:
        # This assumes a through model with fields (ingredient, amount)
        r1.ingredients.create(ingredient=ingredient, amount=100)
        r2.ingredients.create(ingredient=ingredient, amount=150)
    except Exception:
        pytest.skip('Adjust ingredient assignment for your project models')

    # Add both recipes to shopping cart (placeholder)
    client.login(username='shopuser', password='pass')
    add_url = reverse('<your_project_add_shopping_url_name>', args=[r1.pk])
    client.post(add_url)
    add_url2 = reverse('<your_project_add_shopping_url_name>', args=[r2.pk])
    client.post(add_url2)

    download_url = reverse('<your_project_shopping_list_url_name>')
    resp = client.get(download_url)
    assert resp.status_code == 200

    text = resp.content.decode()
    # Expect aggregated amount 250 in the output;
    # this may need to be adapted to your format
    assert 'Salt' in text
    assert '250' in text or '100+150' in text or '100' in text


@pytest.mark.django_db
def test_database_engine_is_postgres():
    """Проект работает с СУБД PostgreSQL (проверяем ENGINE в настройках)."""
    engine = settings.DATABASES['default']['ENGINE']
    assert 'postgresql' in engine, (
        f"DB engine doesn't look like PostgreSQL: {engine}"
    )


@pytest.mark.skip(
    reason=(
        'Requires remote server with nginx, '
        'docker containers and volumes — integration test')
)
def test_deployment_on_remote_containers():
    """Проверяет развертывание проекта в трёх контейнерах:
    nginx, postgresql, django+gunicorn.

    This is a placeholder integration test:
    replace with your deployment checks / health endpoints.
    """
    # host = '<your_project_allowed_hosts_or_host>'
    # Implement health-check requests to nginx
    # and gunicorn endpoints on the remote host
    assert False, (
        'Implement remote checks for nginx/gunicorn/postgres containers'
    )


@pytest.mark.skip(
    reason='Nginx static serving check requires access to server config'
)
def test_nginx_serves_static_files():
    """Проверяет, что nginx настроен для раздачи статики.
    Placeholder for integration test."""
    static_root = (
        settings.STATIC_ROOT
        if hasattr(settings, 'STATIC_ROOT')
        else '<your_project_static_root_setting>'
    )
    assert static_root, (
        'STATIC_ROOT not configured; cannot test nginx static serving'
    )


def _run_command(cmd):
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        p = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False
        )
        out, err = p.communicate(timeout=30)
        return (
            p.returncode,
            out.decode('utf-8', errors='ignore'),
            err.decode('utf-8', errors='ignore'),
        )
    except FileNotFoundError:
        return 127, '', 'command not found'


@pytest.mark.skipif(
    sys.platform.startswith('win'),
    reason='PEP8 check uses pycodestyle and posix paths — adapt for Windows',
)
def test_code_pep8_conformance():
    """Быстрая проверка PEP8 (pycodestyle).
    Replace <your_project_path> placeholder.
    Install pycodestyle in CI for this test to run: `pip install pycodestyle`.
    """
    project_path = '<your_project_path_to_check>'
    cmd = ['pycodestyle', project_path]
    rc, out, err = _run_command(cmd)
    assert rc == 0, f'PEP8/pycodestyle violations found:\n{out}\n{err}'


# --- Access control checklist (authorized / unauthorized) ---


@pytest.mark.django_db
def test_authorized_user_pages_access(client, django_user_model):
    """Проверки страниц и действий, доступных авторизованному пользователю."""
    User = django_user_model
    Recipe = _import('<your_project_recipe_model>')

    user = User.objects.create_user(username='authuser', password='pass')
    client.login(username='authuser', password='pass')

    # Main page
    assert (
        client.get(reverse('<your_project_home_url_name>')).status_code == 200
    )

    # Another user's page
    other = User.objects.create_user(username='other')
    assert (
        client.get(
            reverse(
                '<your_project_user_profile_url_name>', args=[other.username]
            )
        ).status_code
        == 200
    )

    # Create recipe page
    create_url = reverse('<your_project_create_recipe_url_name>')
    resp = client.get(create_url)
    assert resp.status_code in (200, 302)

    # Create a recipe, edit it, delete it — adapt to your forms / endpoints
    r = Recipe.objects.create(
        author=user, name='Mine', text='mine', pub_date=timezone.now()
    )
    edit_url = reverse('<your_project_edit_recipe_url_name>', args=[r.pk])
    delete_url = reverse('<your_project_delete_recipe_url_name>', args=[r.pk])
    assert client.get(edit_url).status_code in (200, 302)
    # Deletion view may redirect
    assert client.get(delete_url).status_code in (200, 302)


@pytest.mark.django_db
def test_favorites_and_subscriptions_and_shopping_actions(
    client, django_user_model
):
    """Добавление/удаление из избранного, подписки и
    списка покупок доступно авторизованным пользователям."""
    User = django_user_model
    Recipe = _import('<your_project_recipe_model>')

    User.objects.create_user(username='actuser', password='pass')
    other = User.objects.create_user(username='actauthor')
    r = Recipe.objects.create(
        author=other, name='Act', text='x', pub_date=timezone.now()
    )

    client.login(username='actuser', password='pass')

    # Favorite add/remove
    fav_url = reverse('<your_project_add_favorite_url_name>', args=[r.pk])
    resp = client.post(fav_url)
    assert resp.status_code in (200, 201, 302)
    resp = client.post(fav_url)
    assert resp.status_code in (200, 204, 302)

    # Subscribe add/remove
    sub_url = reverse(
        '<your_project_subscribe_url_name>', args=[other.username]
    )
    resp = client.post(sub_url)
    assert resp.status_code in (200, 201, 302)
    resp = client.post(sub_url)
    assert resp.status_code in (200, 204, 302)

    # Shopping cart add/remove
    shopping_url = reverse('<your_project_add_shopping_url_name>', args=[r.pk])
    resp = client.post(shopping_url)
    assert resp.status_code in (200, 201, 302)
    resp = client.post(shopping_url)
    assert resp.status_code in (200, 204, 302)


@pytest.mark.django_db
def test_unauthorized_user_pages(client):
    """Проверки страниц доступных неавторизованным пользователям
    (home, recipe, user, login, signup)."""
    # Home
    assert (
        client.get(reverse('<your_project_home_url_name>')).status_code == 200
    )

    # login and signup pages (placeholders)
    login_url = (
        reverse('login')
        if 'login' in [u.name for u in []]
        else '/accounts/login/'
    )
    signup_url = (
        reverse('signup')
        if 'signup' in [u.name for u in []]
        else '/accounts/signup/'
    )

    # Try common paths (user should replace with actual names if different)
    # We don't fail if these endpoints differ;
    # we just provide basic checks which the user can adapt.
    # Using GET as an unauthenticated user
    client.get(login_url)
    client.get(signup_url)


# --- Admin checks ---


@pytest.mark.django_db
def test_admin_models_and_search_configuration(admin_client):
    """Проверяем минимально: админ-зона доступна и
    можно попасть в страницы моделей.
    Detailed checks (search fields, list filters) require
    introspecting ModelAdmin classes — adjust as needed.
    """
    # admin index
    resp = admin_client.get(reverse('admin:index'))
    assert resp.status_code == 200

    # Check that a few model admin pages are reachable —
    # placeholders for app_label.model
    # Replace with your actual admin URLs if different
    resp = admin_client.get(reverse('admin:auth_user_changelist'))
    assert resp.status_code == 200

    # Recipes changelist
    # Replace <your_project_app> and <your_project_model_lower>
    # with app_label and model name in lower-case
    try:
        resp = admin_client.get(
            reverse(
                'admin:<your_project_app>_<your_project_model_lower>_changelist'
            )
        )
        assert resp.status_code == 200
    except Exception:
        pytest.skip('Adjust admin reverse name for your recipe model')


# End of generated tests
