from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe, Ingredient

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

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = sample_recipe()

        url = detail_url(recipe.id)

        response = self.client.get(url)

        self.assertEqual(response.data['id'], recipe.id)
        self.assertEqual(response.data['name'], recipe.name)
        self.assertEqual(response.data['description'], recipe.description)

        self.assertEqual(len(response.data['ingredients']), 1)
        self.assertEqual(response.data['ingredients'][0]['name'], 'love')

    def test_view_unknown_recipe_detail(self):
        """Test viewing a recipe detail"""
        url = detail_url('1')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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
        self.assertEqual(
            ingredients.filter(name=ingredient1['name']).count(), 1)
        self.assertEqual(
            ingredients.filter(name=ingredient2['name']).count(), 1)
        self.assertEqual(
            ingredients.filter(name=ingredient3['name']).count(), 1)

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
        recipe = sample_recipe(name=recipe_name)

        query_params = {'name': recipe_name[0:5]}

        response = self.client.get(RECIPES_URL, query_params)

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], recipe.id)
        self.assertEqual(response.data[0]['name'], recipe_name)
        self.assertEqual(response.data[0]['description'], recipe.description)

        self.assertEqual(len(response.data[0]['ingredients']), 1)

    def test_delete_recipe(self):
        """Tests deleting a recipe by id"""
        recipe = sample_recipe()

        url = detail_url(recipe.id)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check no recipe left in the DB
        db_recipes = Recipe.objects.all()
        self.assertEqual(db_recipes.count(), 0)

        # Check no ingredient left in the DB
        db_ingredients = Ingredient.objects.all()
        self.assertEqual(db_ingredients.count(), 0)

    def test_delete_unknown_recipe(self):
        """Tests call to delete a recipe that doesn't exist"""
        url = detail_url('1')

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_update_existing_recipe(self):
        """Tests a PATCH of an existing recipe"""
        recipe = sample_recipe()

        ingredient = {'name': 'flour'}
        update_payload = {
            'name': 'Bread',
            'description': 'Ideal for toast',
            'ingredients': [
                ingredient,
            ],
        }
        url = detail_url(recipe.id)
        self.client.patch(url, update_payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.name, update_payload['name'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(len(ingredients), 1)

        self.assertEqual(
            ingredients.filter(name=ingredient['name']).count(), 1)
