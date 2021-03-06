from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization,Authorization
from tastypie import fields, utils
from core.models import Participant,Match,Round,Tournament,Score,RefereeUserProfile,TournamentRuleset
from core.authorization import GuardianAuthorization
from django.contrib.auth.models import User


class AnonymousGetAuthentication(BasicAuthentication):
    def is_authenticated(self, request, **kwargs):
        """ If GET, don't check auth, otherwise fall back to parent """

        if request.method == "GET":
            return True
        else:
            return super(AnonymousGetAuthentication, self).is_authenticated(request, **kwargs)

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user/login'
        excludes = ['email', 'password', 'is_superuser']
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()
        allowed_methods = ['get']
            
class RefereeLoginResource(ModelResource):
    user = fields.ToOneField(UserResource, 'user', full=True)
    class Meta:
        queryset = RefereeUserProfile.objects.all()
        resource_name = 'referee/login'
        allowed_methods = ['get']
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()
        
class RefereeResource(ModelResource):
    class Meta:
        always_return_data = True
        queryset = RefereeUserProfile.objects.all()
        allowed_methods = ['get']
        resource_name = 'referee'
        
class TournamentRulesetResource(ModelResource):
    class Meta:
        always_return_data = True
        queryset = TournamentRuleset.objects.all()
        allowed_methods = ['get']
        resource_name = 'ruleset'
      
class TournamentResource(ModelResource):
    referee = fields.ToOneField(RefereeResource, 'referee', full=True)
    ruleset = fields.ToOneField(TournamentRulesetResource, 'ruleset', full=True)
    class Meta:
        always_return_data = True
        queryset = Tournament.objects.all()
        allowed_methods = ['get']
        resource_name = 'tournament'
        filtering = {
            'id': ['exact'],
        }           

class ParticipantResource(ModelResource):
    class Meta:
        always_return_data = True
        queryset = Participant.objects.all()
        authorization = Authorization()
        allowed_methods = ['get']
        resource_name = 'participant'
        
class RoundResource(ModelResource):
    tournament = fields.ToOneField(TournamentResource, 'tournament')
    class Meta:
        always_return_data = True
        queryset = Round.objects.all()
        allowed_methods = ['get']
        resource_name = 'round'
        filtering = {
            'id': ['exact'],
            'round_number': ['exact'],
            'is_current': ['exact'],
            'tournament': ALL_WITH_RELATIONS,
        }

#If there is already a result it cannot be changed via this interface
class MatchResource(ModelResource):
    round = fields.ToOneField(RoundResource, 'round')
    participant_one = fields.ToOneField(ParticipantResource, 'participant_one',full=True)
    participant_two = fields.ToOneField(ParticipantResource, 'participant_two',full=True,null=True)
    class Meta:
        always_return_data = True
        queryset = Match.objects.all()
        authentication = AnonymousGetAuthentication()
        authorization = GuardianAuthorization(
            view_permission_code = 'view_result', 
            update_permission_code = 'set_result' 
            )
        allowed_methods = ['get','put']
        resource_name = 'match'
        filtering = {
            'round': ALL_WITH_RELATIONS,
        }
        
        
class ScoreResource(ModelResource):
    tournament = fields.ToOneField(TournamentResource, 'tournament')
    participant = fields.ToOneField(ParticipantResource, 'participant',full=True)
    class Meta:
        always_return_data = True
        queryset = Score.objects.all()
        allowed_methods = ['get']
        resource_name = 'score'
        filtering = {
            'tournament': ALL_WITH_RELATIONS,
        }
        

        

        
