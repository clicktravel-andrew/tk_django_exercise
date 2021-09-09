from django.db import models


class Recipe(models.Model):
    """Recipe object"""
    name = models.CharField(max_length=31)
    description = models.TextField()

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient object"""
    name = models.CharField(max_length=31)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
