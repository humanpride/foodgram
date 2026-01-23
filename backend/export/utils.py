from typing import Any, Dict, List, Optional

from django.db.models import Sum
from django.http import HttpResponse

from recipes.models import RecipeIngredient


def build_aggregated_ingredients(user):
    return list(
        RecipeIngredient.objects.filter(
            recipe__id__in=user.shopping_cart.all().values_list(
                'recipe__id', flat=True
            )
        )
        .values(
            'ingredient__id',
            'ingredient__name',
            'ingredient__measurement_unit',
        )
        .annotate(total_amount=Sum('amount'))
        .order_by('ingredient__name')
    )


def build_text_response(aggregated: List[Dict[str, Any]]) -> HttpResponse:
    response = HttpResponse(
        '\n'.join(
            [
                (
                    f'{row["ingredient__name"]} — '
                    f'{row["total_amount"]} '
                    f'{row["ingredient__measurement_unit"]}'
                )
                for row in aggregated
            ]
        ),
        content_type='text/plain',
    )
    response['Content-Disposition'] = (
        'attachment; filename="shopping_list.txt"'
    )
    return response


def build_csv_response(aggregated: List[Dict[str, Any]]) -> HttpResponse:
    import csv
    from io import StringIO

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ingredient', 'amount', 'unit'])
    for row in aggregated:
        writer.writerow(
            [
                row['ingredient__name'],
                row['total_amount'],
                row['ingredient__measurement_unit'],
            ]
        )
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename="shopping_list.csv"'
    )
    return response


def build_pdf_response(
    aggregated: List[Dict[str, Any]],
    request: Optional[Any] = None,
    filename: str = 'shopping_list.pdf',
    template_name: str = 'export/shopping_list.html',
    css_text: Optional[str] = None,
) -> HttpResponse:
    """
    Возвращает pdf, собранный с помощью Weasyprint.
    """
    from django.template.loader import render_to_string
    from weasyprint import CSS, HTML

    html = HTML(
        string=render_to_string(
            template_name, context={'items': aggregated}, request=request
        ),
        base_url=None if not request else request.build_absolute_uri('/'),
    )

    pdf_bytes = html.write_pdf(
        stylesheets=[CSS(string=css_text)] if css_text else None
    )

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
