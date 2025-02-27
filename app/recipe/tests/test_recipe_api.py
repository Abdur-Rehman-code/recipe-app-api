"""
Test for recipe API.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer)

RECIPES_URL = reverse('recipe:recipe-list')  # /api/recipe/recipes/


def detail_url(recipe_id):
    """Return recipe detail URL"""

    print(reverse('recipe:recipe-detail', args=[recipe_id]))
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_user(**params):
    """Create and return a sample user"""
    return get_user_model().objects.create_user(**params)


def create_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': Decimal('5.00'),
        'description': 'Sample description',
        'link': 'URL_ADDRESS.com/recipe.pdf',
    }
    defaults.update(params)
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""

        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='testpass123')
        self.client.force_authenticate(self.user)

    def test_retrieve_recepie(self):
        """Test retrieving a list of recepies"""

        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipe = Recipe.objects.all().order_by('-id')  # latest recipe first
        serializer = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_limited_to_user(self):
        """Test retrieving recipes for user"""

        user2 = create_user(
            email='user2@example.com',
            password='test123'
        )

        create_recipe(user=user2)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""

        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)  # /api/recipe/recipes/1/
        res = self.client.get(url)  # GET /api/recipe/recipes/1/

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating recipe"""

        payload = {
            'title': 'Sample recipe',
            'time_minutes': 10,
            'price': Decimal('5.00'),
        }

        # POST /api/recipe/recipes/
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        self.assertEqual(recipe.user, self.user)

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""

        original_link = 'URL_ADDRESS.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe',
            link=original_link
        )

        payload = {'title': 'New Recipe title'}
        url = detail_url(recipe.id)  # /api/recipe/recipes/1/
        res = self.client.patch(url, payload)  # PATCH /api/recipe/recipes/1/

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()  # refresh the object from the database
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update_recipe(self):
        """Test updating a recipe with put"""

        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link='URL_ADDRESS.com/recipe.pdf',
            description='Sample description'
            )
        payload = {
            'title': 'New recipe title',
            'link': 'URL_ADDRESS.com/new_recipe.pdf',
            'description': 'New description',
            'time_minutes': 25,
            'price': Decimal('10.00')
        }

        url = detail_url(recipe.id)  # /api/recipe/recipes/1/
        res = self.client.put(url, payload)  # PUT /api/recipe/recipes/1/
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()  # refresh the object from the database
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the recipe user results in an error"""

        new_user = create_user(
            email='user2@example.com',
            password='test123'
        )
        recipe = create_recipe(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(recipe.id)  # /api/recipe/recipes/1/
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe"""

        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)  # /api/recipe/recipes/1/
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_users_recipe_error(self):
        """Test that user cannot delete other user's recipe"""

        new_user = create_user(
            email='user2@example.com',
            password='test123'
        )
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.id)  # /api/recipe/recipes/1/
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())
