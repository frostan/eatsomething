from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.fields import Base64ImageField
from api.utils import recipe_ingredients
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)
from users.models import Follow, User

# -------------------------ПОЛЬЗОВАТЕЛЬ--------------------------------------


class UserReadSerializer(UserSerializer):
    """Cписок пользователей."""
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
           and self.context['request'].user.is_authenticated):
            return Follow.objects.filter(user=self.context['request'].user,
                                         author=obj).exists()
        return False


class UserCreateSerializer(UserCreateSerializer):
    """Создание создания пользователя."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'password')


class SetPasswordSerializer(serializers.Serializer):
    """Изменение пароля пользователя."""

    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, obj):
        try:
            validate_password(obj['new_password'])
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError(
                {'new_password': list(e.messages)}
            )
        return super().validate(obj)

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['current_password']):
            raise serializers.ValidationError(
                {'current_password': 'Неправильный пароль.'}
            )
        if (validated_data['current_password']
           == validated_data['new_password']):
            raise serializers.ValidationError(
                {'new_password': 'Новый пароль должен отличаться от текущего.'}
            )
        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор аватара."""

    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class RecipeSerializer(serializers.ModelSerializer):
    """Список рецептов без ингридиентов."""
    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class SubscriptionsSerializer(UserReadSerializer):
    """Сериализатор для просмотра подписок."""
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar'
        ]

    def get_recipes(self, obj):
        """Получить рецепты авторов из подписки."""
        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]

        return RecipeSerializer(
            recipes, many=True
        ).data

    def get_recipes_count(self, obj):
        """Получить количество рецептов автора."""

        return obj.recipes.count()


class CreateSubscribeSerializer(SubscriptionsSerializer):
    """Сериализатор для подписки и отписки от автора."""
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    avatar = Base64ImageField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar'
        )

# -------------------------ИНГРЕДИЕНТЫ----------------------------------


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')

# -------------------------ТЕГИ----------------------------------------


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


# -------------------------РЕЦЕПТЫ---------------------------------------


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Краткая информация о рецепте."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Список ингредиентов с количеством для рецепта."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name',
                  'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Получить список рецептов."""

    author = UserReadSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, read_only=True, source='recipes')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags',
                  'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image',
                  'text', 'cooking_time')

    def get_is_favorited(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Favorite.objects.filter(user=self.context['request'].user,
                                        recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and ShoppingCart.objects.filter(
                user=self.context['request'].user,
                recipe=obj).exists()
        )


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Ингредиент и количество для RecipeCreateSerializer."""

    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Создать / Измененить / Удалить / рецепт."""

    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    author = UserReadSerializer(read_only=True)
    id = serializers.ReadOnlyField()
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients',
                  'tags', 'image',
                  'name', 'text',
                  'cooking_time', 'author')

    def validate(self, obj):
        tags = obj.get('tags', [])
        if not obj.get('ingredients', []):
            raise serializers.ValidationError(
                'Ингредиенты не могут быть пустыми'
            )
        ingredient_id_list = [
            item['id'] for item in obj.get('ingredients', [])
        ]
        if len(ingredient_id_list) != len(set(ingredient_id_list)):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальны.'
            )
        ingredient_obj = Ingredient.objects.filter(id__in=ingredient_id_list)
        if len(ingredient_obj) != len(obj.get('ingredients')):
            raise serializers.ValidationError('Такого ингредиента нет')
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('Теги не могут повторяться')
        if not tags:
            raise serializers.ValidationError('Теги не могут быть пустыми.')
        return obj

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data
        )
        recipe.tags.set(tags)
        recipe_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        RecipeIngredient.objects.filter(recipe=instance).delete()
        recipe_ingredients(instance, ingredients)
        instance.save()
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance,
                                    context=self.context).data

# -------------------------ИЗБРАННОЕ----------------------------------------


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с избранными рецептами."""
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в список покупок'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSerializer(
            instance.recipe,
            context={'request': request}
        ).data

# -------------------------КОРЗИНА----------------------------------------


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для работы со списком покупок."""
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в список покупок'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSerializer(
            instance.recipe,
            context={'request': request}
        ).data

# -------------------------ПОДПИСКА----------------------------------------


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('user', 'author')

    def validate(self, data):
        user = data.get('user')
        author = data.get('author')
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя.'
            )
        if Follow.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на данного автора.'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')

        return CreateSubscribeSerializer(
            instance.author, context={'request': request}
        ).data
