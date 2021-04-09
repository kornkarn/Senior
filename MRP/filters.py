import django_filters 

from .models import *

class ChemicalFilter(django_filters.FilterSet):
    class Meta :
        model = Chemical
        fields = '__all__'
        exclude = ['leadtime','std_packing','onhand','chem_price','chem_class','uom','STD_BOM']
class WeekFilter(django_filters.FilterSet):
    class Meta :
        model = WeekLoading
        fields = ['week']
        