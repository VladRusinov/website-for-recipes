from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from recipes.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
)
from users.views import (
    SubscribeView,
    SubscriptionViewSet,
    UserViewSet
)

app_name = 'recipes'

router_v1 = DefaultRouter()
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('users/subscriptions/', SubscriptionViewSet.as_view()),
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('users/<int:pk>/subscribe/', SubscribeView.as_view())
]
