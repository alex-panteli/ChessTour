from django.test import TestCase
from django.db.models import Q
from tastypie.test import ResourceTestCase
from core.models import Participant,Score,Tournament,RefereeUserProfile,TournamentRuleset,Round,Match,updateStandings
from django.contrib.auth.models import User
import datetime
import random
                  
class APITests(ResourceTestCase):
    fixtures = ['test_initdata.json']

    def setUp(self):
        super(APITests, self).setUp()
        ruleset = TournamentRuleset.objects.create(numOfRounds=5,winPoints=1,drawPoints=0.5,byePoints=1)
        referee = RefereeUserProfile.objects.get(id=1)
        self.tour = Tournament.objects.create(name="Scoreboard test tournament" , country="CY", referee=referee, date=datetime.datetime.strptime('2015-07-02', "%Y-%m-%d"), ruleset = ruleset)
        self.tour.participants = Participant.objects.all()
        self.tour.save()
        for i in range(1,6):
            for match in Match.objects.filter(round__round_number = i):
                match.result = '1'
                match.save()

    def test_read_scores(self):
        resp = self.api_client.get('/api/scoring/score/?tournament__id='+str(self.tour.id), format='json')
        self.assertValidJSONResponse(resp)
        scores = self.deserialize(resp)['objects']
        self.assertEqual(len(scores), 10)
        
    def test_read_random_match(self):
        randomMatch = random.choice(Match.objects.all())
        resp = self.api_client.get('/api/scoring/match/{}/'.format(randomMatch.id), format='json')
        self.assertValidJSONResponse(resp)
        self.assertEqual(self.deserialize(resp)['id'], randomMatch.id)
               
    def test_read_rounds(self):
        resp = self.api_client.get('/api/scoring/round/?tournament__id='+str(self.tour.id), format='json')
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 5)
        
    def test_read_matches(self):
        matchSum = 0
        for round in Round.objects.filter(tournament = self.tour):
            resp = self.api_client.get('/api/scoring/match/?round__id='+str(round.id), format='json')
            self.assertValidJSONResponse(resp)
            matches = self.deserialize(resp)['objects']
            matchSum+=len(matches)
        #Two players got bye as they cannot play against each other twice.
        self.assertEqual(matchSum, 26)
