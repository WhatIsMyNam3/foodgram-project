import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient

csv_files = {
    Ingredient: './data/ingredients.json'
}


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open(csv_files[Ingredient], encoding='utf-8') as f:
            jsondata = json.load(f)
            for line in jsondata:
                if not Ingredient.objects.filter(
                    name=line['name'],
                    measurement_unit=line['measurement_unit']).exists():
                    Ingredient.objects.create(
                        name=line['name'],
                        measurement_unit=line['measurement_unit']
                    )
