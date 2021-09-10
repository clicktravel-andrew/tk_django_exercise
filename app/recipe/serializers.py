from rest_framework import serializers

from core.models import Recipe, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredient objects"""

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe objects"""
    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'description', 'ingredients')
        read_only_fields = ('id',)

    def create(self, validated_data):
        """create the recipe and ingredients"""
        ingredient_map = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data)

        for ingredient in ingredient_map:
            Ingredient.objects.create(**ingredient, recipe=recipe)

        return recipe


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe objects"""
    ingredients = IngredientSerializer(many=True, read_only=True)
