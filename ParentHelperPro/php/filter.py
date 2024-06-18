import django_filters
from django_filters import rest_framework as filters
from .models import Post


class PostFilter(filters.FilterSet):
    tags = filters.CharFilter(method='filter_by_tags')
    title = filters.CharFilter(field_name='title', lookup_expr='icontains', required=False)

    class Meta:
        model = Post
        fields = ['tags', 'title']

    def filter_by_tags(self, queryset, name, value):
        tag_names = value.split(',')
        return queryset.filter(tags__name__in=tag_names).distinct()