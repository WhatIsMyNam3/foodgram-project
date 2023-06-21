from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet

router = SimpleRouter()
router.register(
    'recipes',
    RecipeViewSet,
    basename='recipes'
)
router.register(
    'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
router.register(
    'tags',
    TagViewSet,
    basename='tags'
)
router.register(
    'users',
    UserViewSet,
    basename='users'
)
urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),

]
