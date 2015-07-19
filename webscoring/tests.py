from django.test import TestCase
from tastypie.test import ResourceTestCase
from core.models import Participant,Score,Tournament,RefereeUserProfile,TournamentOptions,Round,Match
from django.contrib.auth.models import User
import datetime
import random
    
class TournamentCreationTests(ResourceTestCase):
    fixtures = ['test_initdata.json']

    def setUp(self):
        super(TournamentCreationTests, self).setUp()
        options = TournamentOptions.objects.create(numOfRounds=5,winPoints=1,drawPoints=0.5,byePoints=1)
        referee = RefereeUserProfile.objects.get(id=1)
        newtour = Tournament.objects.create(name="Scoreboard test tournament" , country="CY", referee=referee, date=datetime.datetime.strptime('2015-07-02', "%Y-%m-%d"), options = options)
        newtour.participants = Participant.objects.all()
        newtour.save()
        
    def test_scores_created(self):
        self.assertEqual(Score.objects.count(), Participant.objects.count())
        
    def test_first_round_created(self):
        self.assertEqual(Round.objects.count(), 1)
		

        
   
class APITests(ResourceTestCase):
    fixtures = ['test_initdata.json']

    def setUp(self):
        super(APITests, self).setUp()
        options = TournamentOptions.objects.create(numOfRounds=5,winPoints=1,drawPoints=0.5,byePoints=1)
        referee = RefereeUserProfile.objects.get(id=1)
        self.tour = Tournament.objects.create(name="Scoreboard test tournament" , country="CY", referee=referee, date=datetime.datetime.strptime('2015-07-02', "%Y-%m-%d"), options = options)
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
        self.assertEqual(matchSum, 25)
        
        
class BusinessLogicChecks(ResourceTestCase):
    fixtures = ['test_initdata.json']
    
    def setUp(self):
        super(BusinessLogicChecks, self).setUp()
        options = TournamentOptions.objects.create(numOfRounds=5,winPoints=1,drawPoints=0.5,byePoints=1)
        referee = RefereeUserProfile.objects.get(id=1)
        self.tour = Tournament.objects.create(name="Scoreboard test tournament" , country="CY", referee=referee, date=datetime.datetime.strptime('2015-07-02', "%Y-%m-%d"), options = options)
        self.tour.participants = Participant.objects.all()
        self.tour.save()
        for i in range(1,5):
            for match in Match.objects.filter(round__round_number = i):
                match.result = '1'
                match.save()
        self.currentRound = Round.objects.filter(tournament=self.tour, round_number = 5)[0]
        self.matchToScore = Match.objects.filter(result = "")[0]

        self.put_data = {
                'result': '1',
            }
            
        self.post_data = {
            'participant_one': { 'picture': '/media/participants/fabiano_caruana.jpg', 
                                 'country': 'US', u'full_name': u'Fabiano Caruana', 
                                 'elo_rating': 2797, 
                                 'id':5, 
                                 'resource_uri': '/api/scoring/participant/5/'}, 
            'id': 25, 
            'participant_two': { 'picture': '/media/participants/vladimir_kramnik.jpg', 
                                 'country': 'RU',
                                 'full_name': 'Vladimir Kramnik', 
                                 'elo_rating': 2783, 
                                 'id': 7, 
                                 'resource_uri': '/api/scoring/participant/7/'}, 
            'result': '1', 
            'round': '/api/scoring/round/5/', 
            'resource_uri': '/api/scoring/match/25/'
        }
        
 
    def test_read_scores(self):
        resp = self.api_client.get('/api/scoring/score/?tournament__id='+str(self.tour.id), format='json')
        self.assertValidJSONResponse(resp)
        scores = self.deserialize(resp)['objects']
        currentScores = {'Magnus Carlsen' : 4.0 , 'Viswanathan Anand' : 3.0, 'Veselin Topalov' : 3.0, 'Hikaru Nakamura' : 2.0, 'Fabiano Caruana' : 1.0, 'Anish Giri' : 1.0, 'Vladimir Kramnik' : 1.0, 'Wesley So' : 2.0 , 'Alexander Grischuk' : 2.0 , 'Levon Aronian' : 1.0 }
        for score in scores:
            currentScore = currentScores[score['participant']['full_name']]
            self.assertEqual(currentScore, score['score'])
        
    def test_score_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.put('/api/scoring/match/{}/'.format(self.matchToScore.pk), format='json', data=self.put_data))
        
    def test_create_match_not_allowed(self):
        self.assertHttpMethodNotAllowed(self.api_client.post('/api/scoring/match/{}/'.format(self.matchToScore.pk), format='json', data=self.post_data))
        
