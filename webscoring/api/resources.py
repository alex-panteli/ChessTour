from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie import fields, utils
from core.models import Participant,Match,Round,Tournament,Score

class AnonymousGetAuthentication(BasicAuthentication):
    def is_authenticated(self, request, **kwargs):
        """ If GET, don't check auth, otherwise fall back to parent """

        if request.method == "GET":
            return True
        else:
            return super(AnonymousGetAuthentication, self).is_authenticated(request, **kwargs)
            
class AnonymousGetAuthorization(DjangoAuthorization):
    """
    Authorizes every authenticated user to perform GET, for all others
    performs DjangoAuthorization.
    """

    def is_authorized(self, request, object=None):
        if request.method == 'GET':
            return True
        else:
            return super(AnonymousGetAuthorization, self).is_authorized(request, object)


class ParticipantResource(ModelResource):
    class Meta:
        always_return_data = True
        queryset = Participant.objects.all()
        allowed_methods = ['get']
        resource_name = 'participant'
		
class RoundResource(ModelResource):
    class Meta:
        always_return_data = True
        queryset = Round.objects.all()
        allowed_methods = ['get']
        resource_name = 'round'
        filtering = {
            'id': ['exact'],
        }

#If there is already a result it cannot be changed via this interface
class MatchResource(ModelResource):
    round = fields.ToOneField(RoundResource, 'round')
    participant_one = fields.ToOneField(ParticipantResource, 'participant_one',full=True)
    participant_two = fields.ToOneField(ParticipantResource, 'participant_two',full=True)
    class Meta:
        always_return_data = True
        queryset = Match.objects.all()
        authentication = AnonymousGetAuthentication()
        authorization = AnonymousGetAuthorization()
        allowed_methods = ['get','put']
        resource_name = 'match'
        filtering = {
            'round': ALL_WITH_RELATIONS,
        }
        
        
class TournamentResource(ModelResource):
    class Meta:
        always_return_data = True
        queryset = Tournament.objects.all()
        allowed_methods = ['get']
        resource_name = 'tournament'
        filtering = {
            'id': ['exact'],
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
        

        

        
