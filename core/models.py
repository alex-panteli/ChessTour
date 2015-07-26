from django.db import models,transaction
from django_countries.fields import CountryField
from django.contrib.auth.models import User
from django.utils import timezone
from guardian.shortcuts import assign_perm
from utilities import ModelDiffMixin
from django.template.defaultfilters import escape
from django.core.urlresolvers import reverse
import random
import math
import networkx as netx
from itertools import chain
from operator import eq

class RefereeUserProfile(models.Model):
    user = models.OneToOneField(User,related_name="ref_profile")
    picture = models.ImageField(upload_to='referees',default='referees/default.png')
    def __unicode__(self):
        return u'{} {}'.format(self.user.first_name, self.user.last_name)
    

class Participant(models.Model):
    #Max length Based on UK Government Data Standards Catalogue
    full_name = models.CharField(max_length=70,blank=False)
    country = CountryField()
    elo_rating = models.PositiveIntegerField()
    picture = models.ImageField(upload_to='participants',default='participants/default.png')
    
    def __unicode__(self):
        return u'{} - {} [{:,}]'.format(self.full_name, self.country, self.elo_rating)

class TournamentRuleset(models.Model):
    name = models.CharField(max_length=250,blank=False)
    numOfRounds = models.PositiveIntegerField(verbose_name='Number of rounds')
    winPoints = models.FloatField(default=1, verbose_name='Points per win')
    drawPoints = models.FloatField(default=0.5, verbose_name='Points per draw')
    byePoints = models.FloatField(default=1, verbose_name='Points per bye')
    def __unicode__(self):
        toString = u'{}'.format(self.name)
        return toString
        
class Tournament(models.Model):
    name = models.CharField(max_length=250,blank=False)
    country = CountryField()
    referee = models.OneToOneField(RefereeUserProfile)
    participants = models.ManyToManyField(Participant)
    date = models.DateField()
    ruleset = models.OneToOneField(TournamentRuleset)
    def __unicode__(self):
        toString = u'{} {} {}'.format(self.name,self.country.name,self.date.year)
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
    completed_on = models.DateTimeField(null=True)
    def __unicode__(self):
        toString = u'Round #{} of {}'.format(self.round_number,self.tournament)
        return toString
        
    
class Match(models.Model,ModelDiffMixin):

    class Meta:
            permissions = (
                ('set_result', 'Set result'),
                ('view_result', 'View result'),
            )
            
    RESULT_CHOICES = (
        ('1' , 'White won'),
        ('X' , 'Draw'),
        ('2' , 'Black won'),
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
                score.score += self.round.tournament.ruleset.byePoints
                score.save()
        #Result can be set only once
        if ('result' in self.changed_fields): 
            if self.get_field_diff('result')[0] != '':
                return
            
            updateStandings(self.participant_one,self.participant_two,self.round.tournament,self.result)
        
            if self.pk is not None and self.round.round_number + 1 <= self.round.tournament.ruleset.numOfRounds:
                remainingMatches = Match.objects.filter(round = self.round, result = "")
                if remainingMatches.count() == 1 and remainingMatches[0] == self and self.result:
                    generateNextRound(self.round.tournament, self.round.round_number)
                    self.round.is_current = False
                    self.round.completed_on = timezone.now()
                    self.round.save()
                    
        super(Match, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return u'{} vs {} : {}'.format(self.participant_one, self.participant_two, self.result)
        
                    
def assign_rights(instance, created, raw, **kwargs):
    if created:
        anonymous_user = User.objects.get(id=-1)
        assign_perm('view_result', anonymous_user, instance) 
        referee_user = instance.round.tournament.referee.user
        assign_perm('set_result', referee_user, instance)
        assign_perm('view_result', referee_user, instance)
        

models.signals.post_save.connect(assign_rights, sender=Match, dispatch_uid='assign_read_rights')

@transaction.atomic     
def updateStandings(participant_one,participant_two,tournament, result):
    winPoints = tournament.ruleset.winPoints
    drawPoints = tournament.ruleset.drawPoints
    
    score_one = Score.objects.filter(tournament = tournament,participant = participant_one)[0]
    score_two = Score.objects.filter(tournament = tournament,participant = participant_two)[0]
    p1rating = participant_one.elo_rating + score_one.rating_delta
    p2rating = participant_two.elo_rating + score_two.rating_delta
    r1 = math.pow(10,p1rating/400.0)
    r2 = math.pow(10,p2rating/400.0)
    rt = r1+r2
    e1 = r1 / rt
    e2 = r2 / rt
    
    points = ()
    if result == '1':
        points = (winPoints,0,1,0)
    if result == 'X':
        points = (drawPoints,drawPoints,0.5,0.5)
    if result == '2':
        points = (0,winPoints,0,1)
    
    score_one.score += points[0]
    score_two.score += points[1]
    score_one.rating_delta += round(32 * (points[2] - e1),0)
    score_two.rating_delta += round(32 * (points[3] - e2),0)
    score_one.save()
    score_two.save()
    

        
class Score(models.Model):
    participant = models.ForeignKey(Participant)
    tournament = models.ForeignKey(Tournament)
    score = models.FloatField()
    rating_delta = models.IntegerField()
    def __unicode__(self):
        return u'{} : {}\n , elo delta: {}'.format(self.participant, self.score,self.rating_delta)
    
def getColors(player_one,player_two,tournament):

    prevColors = []
    rounds = tournament.round_set.prefetch_related('match_set').order_by('-round_number')[1:]
    numRoundsPlayed = rounds.count()
    
    #First round
    if  numRoundsPlayed == 0:
        return (player_one, player_two)
    #We only need to check last two rounds      
    for round in rounds[:min(numRoundsPlayed,2)]:
        matches = round.match_set
        roundColors = ['white' if matches.filter(participant_one=player_one).exists() else  'black' , 'white' if matches.filter(participant_one=player_two).exists() else  'black']
        #Alternate colours if possible
        if roundColors[0] != roundColors[1]:
            if roundColors[0] == 'white':
                return (player_two, player_one)
            return (player_one, player_two)
        
        #Cannot have the same color three times in a row
        consecColors = map(eq,roundColors,prevColors)
        if True in consecColors:
            player = consecColors.index(True)
            color = invColor(roundColors[player])
            if color == 'white' and player == 1:
                return (player_two, player_one)
            if color == 'white' and player == 0:
                return (player_one, player_two)
            if color == 'black' and player == 1:
                return (player_one, player_two)
            if color == 'black' and player == 0:
                return (player_two, player_one)
        prevColors = roundColors    
    
    #Only one round played and in both matches both players had the same colour, return the original pairing  
    return (player_one,player_two)

def invColor(color):
    return 'black' if color is 'white' else 'white'
    
''' 
This license applies to all files in this repository that do not have 
another license otherwise indicated.

Copyright (c) 2014, Jeff Hoogland
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the <organization> nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
'''
Modified version of main pairing function from PyPair (https://github.com/JeffHoogland/pypair)
'''
def generateNextRound(tournament,current_round_number):
    currentStandings = Score.objects.filter(tournament=tournament).select_related('participant')
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
        playerScore = currentStandings.filter(participant = player)[0].score
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
                (white,black) = getColors(p,pairings[p],tournament)
                Match.objects.create(participant_one=white, participant_two=black, round=newRound)
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
                    
    