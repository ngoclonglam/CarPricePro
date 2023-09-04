import django_filters
from .models import Car

class CarFilter(django_filters.FilterSet):
    class Meta:
        model = Car
        fields = ['Model_Xe', 'Nam_San_Xuat', 'Dong_Xe', 'Hop_So', 'Dan_Dong']
