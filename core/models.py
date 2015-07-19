from django.db import models,transaction
from django_countries.fields import CountryField
from django.contrib.auth.models import User
from guardian.shortcuts import assign_perm
from utilities import ModelDiffMixin
import random
import networkx as netx
# Create your models here.

#

class RefereeUserProfile(models.Model):
    user = models.OneToOneField(User,related_name="ref_profile")
    picture = models.ImageField(upload_to='referees',default='referees/default.png')
    def __unicode__(self):
        return u'{} {}'.format(self.user.first_name, self.user.last_name)
    

class Participant(models.Model):
    #Max length Based on UK Government Data Standards Catalogue
    full_name = models.CharField(max_length=70)
    country = CountryField()
    elo_rating = models.PositiveIntegerField()
    picture = models.ImageField(upload_to='participants',default='participants/default.png')
    
    def __unicode__(self):
        return u'{} - {} [{:,}]'.format(self.full_name, self.country, self.elo_rating)

class TournamentOptions(models.Model):
    numOfRounds = models.PositiveIntegerField()
    winPoints = models.FloatField(default=1)
    drawPoints = models.FloatField(default=0.5)
    byePoints = models.FloatField(default=1)
        
class Tournament(models.Model):
    name = models.TextField()
    country = CountryField()
    referee = models.ForeignKey(RefereeUserProfile)
    participants = models.ManyToManyField(Participant)
    date = models.DateField()
    options = models.ForeignKey(TournamentOptions)
    def __unicode__(self):
        toString = u'{} {} - {}. REF: {}'.format(self.name,self.date,self.country,self.referee)
        return toString

@transaction.atomic        
def create_first_round(instance, created, raw, **kwargs):
    if instance.participants.count() == 0:
        return
    if instance.round_set.count() == 0:
        #Create 0 score for all participants
        for participant in instance.participants.all():
            Score.objects.create(tournament = instance, participant = participant, score=0, rating_delta=0)
        generateNextRound(instance, 0)
        instance.save()

models.signals.post_save.connect(create_first_round, sender=Tournament, dispatch_uid='create_first_round')


class Round(models.Model):
    tournament = models.ForeignKey(Tournament)
    round_number = models.PositiveIntegerField()
    is_current = models.BooleanField(default=False)
    def __unicode__(self):
        toString = u'Round {} of {} :'.format(self.round_number,self.tournament)
        toString += u'\n'.join([str(match) for match in self.match_set.all()])
        return toString
    
class Match(models.Model,ModelDiffMixin):

    class Meta:
            permissions = (
                ('set_result', 'Set result'),
                ('view_result', 'View result'),
            )
            
    RESULT_CHOICES = (
        ('1' , 'One'),
        ('X' , 'Draw'),
        ('2' , 'Two'),
    )
    round = models.ForeignKey(Round)
    participant_one = models.ForeignKey(Participant,related_name='player_one')
    participant_two = models.ForeignKey(Participant,related_name='player_two',null=True)
    result = models.CharField(max_length=1, choices=RESULT_CHOICES,blank=True)
    
    #If something goes wrong we need to not have an inconsistency between rounds/matches/scores
    @transaction.atomic
    def save(self, *args, **kwargs):
        #Created with bye
        if self.pk is None:
            if self.result:
                score = Score.objects.filter(tournament = self.round.tournament,participant = self.participant_one)[0]
                score.score += self.round.tournament.options.byePoints
                score.save()
        #Result can be set only once
        if ('result' in self.changed_fields): 
            if self.get_field_diff('result')[0] != '':
                return
            
            updateStandings(self.participant_one,self.participant_two,self.round.tournament,self.result)
        
            if self.pk is not None and self.round.round_number + 1 <= self.round.tournament.options.numOfRounds:
                remainingMatches = Match.objects.filter(round = self.round, result = "")
                if remainingMatches.count() == 1 and remainingMatches[0] == self and self.result:
                    generateNextRound(self.round.tournament, self.round.round_number)
                    self.round.is_current = False
        super(Match, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return u'{} vs {} : {}'.format(self.participant_one, self.participant_two, self.result)
        
                    
def assign_read_rights(instance, created, raw, **kwargs):
    if created:
        anonymous_user = User.objects.get(id=-1)
        assign_perm('view_result', anonymous_user, instance)        

models.signals.post_save.connect(assign_read_rights, sender=Match, dispatch_uid='assign_read_rights')

@transaction.atomic     
def updateStandings(participant_one,participant_two,tournament, result):
    score_one = Score.objects.filter(tournament = tournament,participant = participant_one)[0]
    score_two = Score.objects.filter(tournament = tournament,participant = participant_two)[0]
    winPoints = tournament.options.winPoints
    drawPoints = tournament.options.drawPoints
    if result == '1':
        score_one.score += winPoints
    if result == 'X':
        score_one.score += drawPoints
        score_two.score += drawPoints
    if result == '2':
        score_two.score += winPoints
    score_one.save()
    score_two.save()
        
class Score(models.Model):
    participant = models.ForeignKey(Participant)
    tournament = models.ForeignKey(Tournament)
    score = models.FloatField()
    rating_delta = models.IntegerField()
    def __unicode__(self):
        return u'{} : {}\n'.format(self.participant, self.score)
    
def generateNextRound(tournament,current_round_number):
    currentStandings = Score.objects.filter(tournament=tournament)
    tournamentMatches = Match.objects.filter(round__tournament = tournament)
    players = tournament.participants
    newRound = Round.objects.create(tournament = tournament, round_number=current_round_number+1,is_current=True)
    
    #Contains lists of players sorted by how many points they currently have
    pointLists = {}
    
    #Contains a list of points in the event from high to low
    pointTotals = []
    
    #Counts our groupings for each point amount
    countPoints = {}
    maxGroup = 50
    
    #Add all players to pointLists
    for player in players.all():
        playerScore = Score.objects.filter(tournament = tournament, participant = player)[0].score
        #If this point amount isn't in the list, add it
        if "%s_1"%playerScore not in pointLists:
            pointLists["%s_1"%playerScore] = []
            countPoints[playerScore] = 1
        
        #Breakers the players into groups of their current points up to the max group allowed.
        #Smaller groups mean faster calculations
        if len(pointLists["%s_%s"%(playerScore, countPoints[playerScore])]) > maxGroup:
            countPoints[playerScore] += 1
            pointLists["%s_%s"%(playerScore, countPoints[playerScore])] = []
        
        #Add our player to the correct group
        pointLists["%s_%s"%(playerScore, countPoints[playerScore])].append(player)
        
    #Add all points in use to pointTotals
    for points in pointLists:
        pointTotals.append(points)
        
        #Randomize the players in the list so the first player isn't always the first paired
        random.shuffle(pointLists[points])
        
    #Sort our point groups based on points
    pointTotals.sort(reverse=True, key=lambda s: float(s.split('_')[0]))

    #Actually pair the players utilizing graph theory networkx
    for points in pointTotals:
        
        #Create the graph object and add all players to it
        bracketGraph = netx.Graph()
        bracketGraph.add_nodes_from(pointLists[points])
        
        #Create edges between all players in the graph who haven't already played
        for player in bracketGraph.nodes():
            for opponent in bracketGraph.nodes():
                alreadyPlayed = Match.objects.filter(participant_one=player,participant_two=opponent).exists() or Match.objects.filter(participant_one=opponent,participant_two=player).exists()
                if not alreadyPlayed:
                    #Weight 1 is the default, if a person has more points, give higher weight to make sure they get paired this time
                    wgt = 1
                    if  currentStandings.filter(participant = player) > points or currentStandings.filter(participant = opponent) > points:
                        wgt = 2
                    #Create edge
                    bracketGraph.add_edge(player, opponent, weight=wgt)
        
        #Generate pairings from the created graph
        pairings = netx.max_weight_matching(bracketGraph)
        
        #Actually pair the players based on the matching we found
        for p in pairings:
            if p in pointLists[points]:
                Match.objects.create(participant_one = p, participant_two=pairings[p], round=newRound)
                pointLists[points].remove(p)
                pointLists[points].remove(pairings[p])
            
        #Check if we have an odd man out that we need to pair down
        if len(pointLists[points]) > 0:
            #Check to make sure we aren't at the last player in the event
            if pointTotals.index(points) + 1 == len(pointTotals):
                while len(pointLists[points]) > 0:
                    #If they are the last player give them a bye
                    Match.objects.create(participant_one = pointLists[points].pop(0), round=newRound, result='1')
                    
            else:
                #Add our player to the next point group down
                nextPoints = pointTotals[pointTotals.index(points) + 1]
                
                while len(pointLists[points]) > 0:
                    pointLists[nextPoints].append(pointLists[points].pop(0))
    