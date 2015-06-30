from django.db import models
from django_countries.fields import CountryField

# Create your models here.

#

class RefereeUserProfile(models.model):
	user = models.ForeignKey(User, unique=True)
    picture = models.ImageField(upload_to='judges')
	def __unicode__(self):
        return u'{} {}'.format(user.first_name, user.last_name)
	

class Participant(models.model):
	#Max length Based on UK Government Data Standards Catalogue
	full_name = models.CharField(max_length=70)
	country = CountryField()
	elo_rating = models.IntegerField()
	picture = models.ImageField(upload_to='participants')
	
	def __unicode__(self):
        return u'{} - {} [{:,}]'.format(self.full_name, self.country, self.elo_rating)

class Tournament(models.model):
	name = models.TextField()
	country = CountryField()
	referee = models.ForeignKey(RefereeUserProfile)
	participants = models.ManyToManyField(Participant)
	date = models.DateField()
	def __unicode__(self):
		toString = u'{} {} - {}. REF: {}'.format(self.name,self.date,self.country,self.referee}

class Round(models.model):
	tournament = models.ForeignKey(Tournament)
	round_number = models.IntegerField()
	def __unicode__(self):
		toString = u'Round {} of {} :'.format(self.round_number,self.tournament)
		toString.append('\n'.join(match_set.all()))
	
class Match(models.model):
	RESULT_CHOICES = (
		('1' , 'One'),
		('X' , 'Draw'),
		('2' , 'Two'),
	)
	round = models.ForeignKey(Round)
	participant_one = models.ForeignKey(Participant,related_name='player_one')
	participant_two = models.ForeignKey(Participant,related_name='player_two')
	result = forms.ChoiceField(choices=RESULT_CHOICES,required=False)
	
	def __unicode__(self):
        return u'{} vs {} : {}'.format(participant_one, participant_two, result)
	