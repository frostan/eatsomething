from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import (
    TagViewSet,
    RecipeViewSet,
    IngredientViewSet,
    UserViewSet
)

app_name = 'api'

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls),),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
