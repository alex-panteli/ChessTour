
from core.models import Participant,Score,Tournament,RefereeUserProfile,Match,Round,TournamentRuleset
from django.contrib.auth.models import User
from guardian.shortcuts import assign_perm
import datetime




one = Participant.objects.create(full_name='Magnus Carlsen', country="NO", elo_rating=2853)
one.picture = "participants/magnus_carlsen.jpg"
one.save()
 
two = Participant.objects.create(full_name='Viswanathan Anand', country="IN", elo_rating=2816)
two.picture = "participants/viswanathan_anand.jpg"
two.save()

three = Participant.objects.create(full_name='Veselin Topalov', country="BG", elo_rating=2816)
three.picture = "participants/veselin_topalov.jpg"
three.save()

four = Participant.objects.create(full_name='Hikaru Nakamura', country="US", elo_rating=2814)
four.picture = "participants/hikaru_nakamura.jpg"
four.save()

five = Participant.objects.create(full_name='Fabiano Caruana', country="US", elo_rating=2797)
five.picture = "participants/fabiano_caruana.jpg"
five.save()

six = Participant.objects.create(full_name='Anish Giri', country="NL", elo_rating=2791)
six.picture = "participants/anish_giri.jpg"
six.save()

seven = Participant.objects.create(full_name='Vladimir Kramnik', country="RU", elo_rating=2783)
seven.picture = "participants/vladimir_kramnik.jpg"
seven.save()

eight = Participant.objects.create(full_name='Wesley So', country="US", elo_rating=2780)
eight.picture = "participants/wesley_so.jpg"
eight.save()

nine = Participant.objects.create(full_name='Alexander Grischuk', country="RU", elo_rating=2771)
nine.picture = "participants/alexander_grischuk.jpg"
nine.save()

ten = Participant.objects.create(full_name='Levon Aronian', country="AM", elo_rating=2765)
ten.picture = "participants/levon_aronian.jpg"
ten.save()

admin = User.objects.create_superuser(username='admin',password='password', email='')

referee_user = User.objects.create(username='jdoe',password='1234',email='jdoe@somemail.com',first_name='John',last_name='Doe')
referee_user.set_password('1234')
referee_user.save()

referee = RefereeUserProfile.objects.create(user=referee_user)
ruleset = TournamentRuleset.objects.create(name='Small tournament',numOfRounds=5,winPoints=1,drawPoints=0.5,byePoints=1)

newtour = Tournament.objects.create(name="Scoreboard test tournament" , country="CY", referee=referee, date=datetime.datetime.strptime('2015-07-02', "%Y-%m-%d"), ruleset = ruleset)

newtour.participants = Participant.objects.all()
newtour.save()

anonymous_user = User.objects.get(id=-1)
x = [assign_perm('set_result', referee_user, match) for match in Match.objects.all()]
y = [assign_perm('view_result', referee_user, match) for match in Match.objects.all()]
z = [assign_perm('view_result', anonymous_user, match) for match in Match.objects.all()]

for i in range(1,3):
    for match in Match.objects.filter(round__round_number = i):
        match.result = '1'
        match.save()


    


