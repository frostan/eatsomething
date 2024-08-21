from django.contrib import admin

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag


@admin.register(Ingredient)
class IngridientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author',)
    search_fields = ('name',)
    filter_fields = ('tags',)


@admin.register(RecipeIngredient)
class RecipeIngridientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')
    filter_fields = ('recipe', 'ingredient')
