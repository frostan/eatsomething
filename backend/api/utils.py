from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import RecipeIngredient, Recipe


def recipe_ingredients(recipe, ingredients):
    recipe_ingredients = [
        RecipeIngredient(
            recipe=recipe,
            ingredient_id=ingredient['id'],
            amount=ingredient['amount']
        )
        for ingredient in ingredients
    ]
    RecipeIngredient.objects.bulk_create(recipe_ingredients)


def util_for_favorite_shopping_cart(request, pk, serializer_name, model):
    recipe = get_object_or_404(Recipe, id=pk)
    if request.method == 'POST':
        serializer = serializer_name(
            data=dict(user=request.user.id, recipe=recipe.id),
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if not model.objects.filter(user=request.user, recipe=recipe).exists():
        return Response(
            {'detail': 'Рецепт не найден в избранном.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    return Response(
        {'detail': 'Рецепт успешно удален из избранного.'},
        status=status.HTTP_204_NO_CONTENT
    )
