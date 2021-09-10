from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_ingredient(recipe, name='love'):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(recipe=recipe, name=name)


def sample_recipe(**params):
    """Create and return a sample recipe"""
    defaults = {
        'name': 'Unicorn cakes',
        'description': 'Sparkly, swirly and bright',
    }
    defaults.update(params)
    recipe = Recipe.objects.create(**defaults)
    sample_ingredient(recipe=recipe)
    return recipe


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

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = sample_recipe()

        url = detail_url(recipe.id)

        response = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(response.data, serializer.data)

    def test_create_recipe_successful(self):
        """Test creating a new recipe"""
        ingredient1 = {'name': 'flour'}
        ingredient2 = {'name': 'yeast'}
        ingredient3 = {'name': 'water'}
        payload = {
            'name': 'Bread',
            'description': 'Ideal for toast',
            'ingredients': [
                ingredient1,
                ingredient2,
                ingredient3,
            ],
        }

        response = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=response.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 3)
        self.assertEqual(len(ingredients.filter(name=ingredient1['name'])), 1)
        self.assertEqual(len(ingredients.filter(name=ingredient2['name'])), 1)
        self.assertEqual(len(ingredients.filter(name=ingredient3['name'])), 1)

    def test_create_recipe_invalid(self):
        """Test that a recipe payload must be valid"""
        payload = {
            'name': '',
        }
        response = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recipes_by_name(self):
        """Test retrieving a list of recipes"""
        recipe_name = 'Kitten cakes'
        recipe1 = sample_recipe()
        recipe2 = sample_recipe(name=recipe_name)

        query_params = {'name': recipe_name[0:5]}
        
        response = self.client.get(RECIPES_URL, query_params)

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)

        self.assertNotIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
