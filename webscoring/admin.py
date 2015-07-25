from django.contrib import admin
from core.models import Participant,Tournament,RefereeUserProfile,TournamentRuleset

class RefereeAdmin(admin.ModelAdmin):
    pass

class TournamentAdmin(admin.ModelAdmin):
    pass

class ParticipantAdmin(admin.ModelAdmin):
    pass
	
class RulesetAdmin(admin.ModelAdmin):
    pass
	
	
admin.site.register(RefereeUserProfile, RefereeAdmin)
admin.site.register(Tournament, TournamentAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(TournamentRuleset, RulesetAdmin)