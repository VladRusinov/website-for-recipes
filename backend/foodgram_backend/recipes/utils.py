from django.http import HttpResponse


def download(shop_list):
    file_name = 'shopping_cart.txt'
    ingredients = {}
    for recipe in shop_list:
        for ing in recipe:
            name = ing.ingredient.name
            if name not in ingredients:
                ingredients[name] = {
                    'amount': ing.amount,
                    'measurement_unit': ing.ingredient.measurement_unit
                }
            else:
                ingredients[name]['amount'] += ing.amount
    file_data = []
    for ingredient in ingredients:
        data = ''
        data += str(ingredient)
        for j in ingredients[ingredient]:
            data += f' {str(ingredients[ingredient][j])}'
        file_data.append(data)
    content = '\n'.join(file_data)
    content_type = 'text/plain,charset=utf8'
    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    return response


def is_number(string):
    """Проверка того, можно ли перобразовать строку в число."""
    try:
        int(string)
        return True
    except ValueError:
        return False
