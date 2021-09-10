from rest_framework import viewsets

from core.models import Recipe
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in the database"""
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer

    def get_queryset(self):
        """Returns recipes ordered by ID"""
        queryset = self.queryset
        name_filter = self.request.query_params.get('name', None)
        if name_filter:
            queryset = queryset.filter(name__contains=name_filter)

        return queryset.order_by('-id')

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save()
