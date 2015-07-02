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
        queryset = Round.objects.all()
        allowed_methods = ['get']
        resource_name = 'participant'

#If there is already a result it cannot be changed via this interface
class MatchResource(ModelResource):
    class Meta:
        always_return_data = True
        queryset = Match.objects.all()
        authentication = AnonymousGetAuthentication()
        authorization = AnonymousGetAuthorization()
        allowed_methods = ['get','put']
        resource_name = 'match'
        
class RoundResource(ModelResource):
    class Meta:
        always_return_data = True
        queryset = Round.objects.all()
        allowed_methods = ['get']
        resource_name = 'round'
        
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
    participant = fields.ToOneField(ParticipantResource, 'participant')
    class Meta:
        always_return_data = True
        queryset = Score.objects.all()
        allowed_methods = ['get']
        resource_name = 'score'
        filtering = {
            'tournament': ALL_WITH_RELATIONS,
        }
        

        

        
