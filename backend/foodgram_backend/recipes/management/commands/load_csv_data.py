import csv
from django.core.management import BaseCommand
from tqdm import tqdm

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = "Loads data from csv files"

    def handle(self, *args, **options):
        for row in tqdm(
            (csv.reader(open(
                'data/ingredients.csv', encoding='utf-8'
            ))), ncols=80, ascii=True, desc='Total'
        ):
            ingredient = Ingredient(
                name=row[0], measurement_unit=row[1]
            )
            ingredient.save()

        for row in tqdm(
            (csv.reader(open(
                'data/tags.csv', encoding='utf-8'
            ))), ncols=80, ascii=True, desc='Total'
        ):
            tag = Tag(
                name=row[0], color=row[1], slug=row[2]
            )
            tag.save()
