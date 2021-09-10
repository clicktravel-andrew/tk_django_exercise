from rest_framework import viewsets, mixins

from core.models import Recipe
from recipe import serializers


class RecipeViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Manage recipes in the database"""
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer

    def get_queryset(self):
        """Returns recipes ordered by ID"""
        return self.queryset.order_by('-id')
