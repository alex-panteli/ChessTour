from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from core.models import Participant,Match,Round,Tournament

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

class MatchResource(ModelResource):
	class Meta:
        always_return_data = True
        queryset = Match.objects.all()
		authentication = AnonymousGetAuthentication()
		authorization = AnonymousGetAuthorization()
        allowed_methods = ['get','put']
		
class RoundResource(ModelResource):
	class Meta:
        always_return_data = True
        queryset = Round.objects.all()
        allowed_methods = ['get']
		
class TournamentResource(ModelResource):
	class Meta:
        always_return_data = True
        queryset = Tournament.objects.all()
        allowed_methods = ['get']
		

		
