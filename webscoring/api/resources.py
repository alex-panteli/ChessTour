from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.http import HttpUnauthorized, HttpForbidden
from tastypie import fields, utils
from tastypie.utils import trailing_slash
from core.models import Participant,Match,Round,Tournament,Score
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.conf.urls import url


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

class RefereeLoginResource(ModelResource):

    class Meta:
        queryset = RefereeUserProfile.objects.all()
        resource_name = 'referee'
        allowed_methods = ['post']

    def prepend_urls(self):
        return [
            url(r"^referee/login/$", self.wrap_view('login'), name="api_login"),
            url(r"^referee/logout/$", self.wrap_view('logout'), name='api_logout'),
        ]

    def login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        data = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))

        username = data.get('username', '')
        password = data.get('password', '')

        user = authenticate(username=username, password=password)
		try:
			if user and user.ref_profile:
				if user.is_active:
					login(request, user)
					return self.create_response(request, {
						'success': True
					})
				else:
					return self.create_response(request, {
						'success': False,
						'reason': 'disabled',
					}, HttpForbidden )
			else:
				return self.create_response(request, {
					'success': False,
					'reason': 'incorrect',
					}, HttpUnauthorized )
		except:
			return self.create_response(request, {
					'success': False,
					'reason': 'no referee profile',
					}, HttpUnauthorized )

    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request, { 'success': True })
        else:
            return self.create_response(request, { 'success': False }, HttpUnauthorized)
			
class TournamentResource(ModelResource):
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
        

        

        
