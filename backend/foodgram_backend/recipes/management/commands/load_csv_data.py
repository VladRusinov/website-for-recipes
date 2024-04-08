import csv
from django.core.management import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = "Loads data from csv files"

    def handle(self, *args, **options):
        print("Loading data")
        for row in csv.reader(
            open('data/ingredients.csv', encoding='utf-8')
        ):
            ingredient = Ingredient(
                name=row[0], measurement_unit=row[1]
            )
            ingredient.save()

        for row in csv.reader(
            open('data/tags.csv', encoding='utf-8')
        ):
            tag = Tag(
                name=row[0], color=row[1], slug=row[2]
            )
            tag.save()
