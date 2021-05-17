import random
import datetime

from essential_generators import DocumentGenerator
from django.core.management.base import BaseCommand

from core.models import Giver, Feedback


# generate random date between 2015 and 2020. Only the first 28 days of the month are used
def generate_feedback_date():
    year = random.randint(2015, 2020)
    month = random.randint(1, 12)
    day = random.randint(1, 28)

    # time is set to 0:00:00 of the given date
    return datetime.date(year, month, day)


# giver names to pull from
givers = [
    'James', 'John', 'Robert', 'William', 'Michael', 'David', 'Richard', 'Joseph'
]


# select a random giver name from predefined list
def generate_giver_name():
    index = random.randint(0, 7)
    return givers[index]


class Command(BaseCommand):
    help = 'Populates the database with randomly generated data.'

    # allow users to set the number of entries that should be generated
    def add_arguments(self, parser):
        parser.add_argument('--amount', type=int, help='The number of feedback entries that should be generated.')

    def handle(self, *args, **options):
        gen = DocumentGenerator()
        amount = options['amount'] if options['amount'] else 2500
        for i in range(0, amount):
            giver_name = generate_giver_name()

            # create a new feedback object and randomize variables
            feedback = Feedback.objects.create(
                activity=random.choice(Feedback.ACTIVITIES)[0],
                giver=Giver.objects.get(name=giver_name),
                complex=True if random.randint(1, 2) == 1 else False,
                complicated=True if random.randint(1, 2) == 1 else False,
                entrustability=random.choice(Feedback.ENTRUSTABILITY_SCORES)[0],
                done_well=gen.sentence(),
                needs_improvement=gen.sentence(),
                feedbackDate=generate_feedback_date()
            )
            feedback.save()

        self.stdout.write(self.style.SUCCESS('Successfully populated the database.'))
