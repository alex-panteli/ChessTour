
from core.models import Participant,Score,Tournament,RefereeUserProfile
from django.contrib.auth.models import User
import datetime

one = Participant.objects.create(full_name='Magnus Carlsen', country="NO", elo_rating=2853)
two = Participant.objects.create(full_name='Viswanathan Anand', country="IN", elo_rating=2816)
three = Participant.objects.create(full_name='Veselin Topalov', country="BG", elo_rating=2816)
four = Participant.objects.create(full_name='Hikaru Nakamura', country="US", elo_rating=2814)
five = Participant.objects.create(full_name='Fabiano Caruana', country="US", elo_rating=2797)
referee_user = User.objects.create(username='ScoreRef',password='1234',email='scoreref@yahoo.com',first_name='Score',last_name='Ref')
referee_user.set_password('1234')
referee_user.save()
referee = RefereeUserProfile.objects.create(user=referee_user)
newtour = Tournament.objects.create(name="Scoreboard test tournament" , country="CY", referee=referee, date=datetime.datetime.strptime('2015-07-02', "%Y-%m-%d"))
Score.objects.create(tournament = newtour, participant = one, score=7.5, rating_delta=0)
Score.objects.create(tournament = newtour, participant = two, score=6.5, rating_delta=0)
Score.objects.create(tournament = newtour, participant = three, score=5.5, rating_delta=0)
Score.objects.create(tournament = newtour, participant = four, score=4.5, rating_delta=0)
Score.objects.create(tournament = newtour, participant = five, score=2.5, rating_delta=0)
newtour2 = Tournament.objects.create(name="Scoreboard second test" , country="NZ", referee=referee, date=datetime.datetime.strptime('2015-07-02', "%Y-%m-%d"))
Score.objects.create(tournament = newtour2, participant = one, score=10.5, rating_delta=0)
Score.objects.create(tournament = newtour2, participant = two, score=9.5, rating_delta=0)
Score.objects.create(tournament = newtour2, participant = three, score=8.5, rating_delta=0)
Score.objects.create(tournament = newtour2, participant = four, score=7.5, rating_delta=0)