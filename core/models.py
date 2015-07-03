from django.db import models
from django_countries.fields import CountryField
from django.contrib.auth.models import User

# Create your models here.

#

class RefereeUserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    picture = models.ImageField(upload_to='referees',default='referees/default.png')
    def __unicode__(self):
        return u'{} {}'.format(user.first_name, user.last_name)
    

class Participant(models.Model):
    #Max length Based on UK Government Data Standards Catalogue
    full_name = models.CharField(max_length=70)
    country = CountryField()
    elo_rating = models.IntegerField()
    picture = models.ImageField(upload_to='participants',default='participants/default.png')
    
    def __unicode__(self):
        return u'{} - {} [{:,}]'.format(self.full_name, self.country, self.elo_rating)

class Tournament(models.Model):
    name = models.TextField()
    country = CountryField()
    referee = models.ForeignKey(RefereeUserProfile)
    participants = models.ManyToManyField(Participant)
    date = models.DateField()
    def __unicode__(self):
        toString = u'{} {} - {}. REF: {}'.format(self.name,self.date,self.country,self.referee)

class Round(models.Model):
    tournament = models.ForeignKey(Tournament)
    round_number = models.IntegerField()
    def __unicode__(self):
        toString = u'Round {} of {} :'.format(self.round_number,self.tournament)
        toString.append('\n'.join(match_set.all()))
    
class Match(models.Model):
    RESULT_CHOICES = (
        ('1' , 'One'),
        ('X' , 'Draw'),
        ('2' , 'Two'),
    )
    round = models.ForeignKey(Round)
    participant_one = models.ForeignKey(Participant,related_name='player_one')
    participant_two = models.ForeignKey(Participant,related_name='player_two')
    result = models.CharField(max_length=1, choices=RESULT_CHOICES,blank=True)
    
    def __unicode__(self):
        return u'{} vs {} : {}'.format(self.participant_one, self.participant_two, self.result)
        
class Score(models.Model):
    participant = models.ForeignKey(Participant)
    tournament = models.ForeignKey(Tournament)
    score = models.FloatField()
    rating_delta = models.IntegerField()
    