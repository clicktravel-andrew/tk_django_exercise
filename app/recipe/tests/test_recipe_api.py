from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe

from recipe.serializers import RecipeSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def sample_recipe(**params):
    """Create and return a sample recipe"""
    defaults = {
        'name': 'test name',
        'description': 'A long form, test description',
    }
    defaults.update(params)

    return Recipe.objects.create(**defaults)


class RecipeApiTests(TestCase):
    """Test recipe API"""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        sample_recipe()
        sample_recipe()

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_recipe_successful(self):
        """Test creating a new recipe"""
        payload = {
            'name': 'Pizza',
            'description': 'Put it in the oven',
        }
        self.client.post(RECIPES_URL, payload)

        exists = Recipe.objects.filter(
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_recipe_invalid(self):
        """Test that a recipe payload must be valid"""
        payload = {
            'name': '',
        }
        response = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
