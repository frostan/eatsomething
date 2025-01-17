from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from api.filters import IngredientSearchFilter, RecipeFilter
from api.pagination import PageLimitPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    AvatarSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeReadSerializer,
    SetPasswordSerializer,
    SubscriptionsSerializer,
    TagSerializer,
    UserCreateSerializer,
    UserReadSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer
)
from api.utils import util_for_favorite_shopping_cart
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Follow, User

# -------------------------ПОЛЬЗОВАТЕЛЬ--------------------------------------


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для пользователя."""

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = PageLimitPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserReadSerializer
        return UserCreateSerializer

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UserReadSerializer(request.user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['get', 'delete', 'put'],
            permission_classes=(IsAuthenticated,),
            url_path='me/avatar',
            url_name='me/avatar')
    def avatar(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = AvatarSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            user.avatar.delete()
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = AvatarSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = SetPasswordSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Пароль успешно изменен!'},
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,),
            pagination_class=PageLimitPagination)
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(page, many=True,
                                             context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, pk):
        author = get_object_or_404(User, id=pk)

        if request.method == 'POST':
            serializer = FollowSerializer(
                data=dict(user=request.user.id, author=author.id),
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if Follow.objects.filter(user=request.user, author=author).exists():
            Follow.objects.filter(user=request.user, author=author).delete()
            return Response(
                {'detail': 'Успешная отписка'},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'detail': 'Подписка не найдена'},
            status=status.HTTP_400_BAD_REQUEST
            )


# -------------------------ТЕГИ--------------------------------------

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для Тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


# -------------------------ИНГРЕДИЕНТЫ--------------------------------


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для Ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


# -------------------------РЕЦЕПТЫ--------------------------------------


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для Рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = PageLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        return util_for_favorite_shopping_cart(
            request, kwargs['pk'], FavoriteSerializer, Favorite)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),
            pagination_class=None)
    def shopping_cart(self, request, **kwargs):
        return util_for_favorite_shopping_cart(
            request, kwargs['pk'], ShoppingCartSerializer, ShoppingCart)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request, **kwargs):
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shopping_recipe__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount')))

        file_content = '\n'.join(
            f'{ingredient["ingredient__name"]} - {ingredient["total_amount"]}'
            f' {ingredient["ingredient__measurement_unit"]}.'
            for ingredient in ingredients)

        response = HttpResponse(
            f'Список покупок:\n{file_content}', content_type='text/plain'
        )
        shopping_list = "shopping_cart.txt"
        response['Content-Disposition'] = (f'attachment; '
                                           f'filename={shopping_list}')

        return response

    @action(
        detail=True,
        methods=['get'],
        permission_classes=(AllowAny,),
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        url = request.build_absolute_uri(f'/recipes/{recipe.id}')
        return Response({'short-link': url}, status=status.HTTP_200_OK)
