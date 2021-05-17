from django.db import models

# definition of activities
ACTIVITIES = [
    ('HP', 'Conducting History and Physical'),
    ('PD', 'Prioritizing a Differential Diagnosis'),
    ('RI', 'Recommending and Interpreting Tests'),
    ('PH', 'Doing a Patient Handover'),
    ('PP', 'Performing a Procedure'),
]
# definition of entrustability scores
ENTRUSTABILITY_SCORES = [
    (1, 'I did it.'),
    (2, 'I talked them through it.'),
    (3, 'I directed them from time to time.'),
    (4, 'I was available just in case.'),
]
dictACT = dict(ACTIVITIES)
dictENT = dict(ENTRUSTABILITY_SCORES)


# Giver model has the char field, name
class Giver(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name}'


# Feedback model has the following fields
class Feedback(models.Model):
    activity = models.CharField(max_length=255, default='HP', choices=ACTIVITIES)
    giver = models.ForeignKey(to=Giver, on_delete=models.CASCADE)
    complex = models.BooleanField(default=False)
    complicated = models.BooleanField(default=False)
    entrustability = models.IntegerField(default=1, choices=ENTRUSTABILITY_SCORES)
    done_well = models.TextField()
    needs_improvement = models.TextField()
    feedbackDate = models.DateTimeField()

    def __str__(self):
        return f'The giver ({self.giver}) reported an entrustability score of ({self.entrustability}) for "{dictACT[self.activity]}" on {self.feedbackDate:%m, %d, %Y}.'

    def to_month_year(self):
        return f'{self.feedbackDate:%b %Y}'

    def to_year(self):
        return f'{self.feedbackDate:%Y}'

    def to_month(self):
        return f'{self.feedbackDate:%m}'

    def to_month_day_year(self):
        return f'{self.feedbackDate:%b %d, %Y}'
