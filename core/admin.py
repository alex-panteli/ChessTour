from django.contrib.admin import AdminSite, TabularInline, StackedInline
from django.contrib import admin
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from admin_enhancer import admin as enhanced_admin
from core.models import Participant,Tournament,RefereeUserProfile,TournamentRuleset,Round,Match
from django.template.defaultfilters import escape
from django.core.urlresolvers import reverse
from django.utils.html import format_html

class ModelAdminPlus(enhanced_admin.EnhancedModelAdminMixin, NestedModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj and hasattr(self, 'noneditable_fields'): #If editing
            return self.readonly_fields + self.noneditable_fields
        return self.readonly_fields

class MatchInline(enhanced_admin.EnhancedAdminMixin, NestedStackedInline):
    model = Match
    can_delete = False
    verbose_name_plural = "Matches"
    extra = 0
    max_num=0   
        
class RoundInline(enhanced_admin.EnhancedAdminMixin, StackedInline):
    model = Round
    can_delete = False
    extra = 0
    max_num=0
    template = 'admin/core/Round/stackedinline.html'

    def actions(self, instance):

        url = reverse('admin:%s_%s_change' % (instance._meta.app_label, instance._meta.module_name),
                      args=(instance.pk,))
        return format_html(u'<a href="{}">Detailed view</a>', url)

    readonly_fields = ('is_current','completed_on','actions', )
    fields = ('is_current', 'actions', 'completed_on')
        
class TournamentAdmin(ModelAdminPlus):
    fields= ('name','date','country','referee','ruleset','participants')
    noneditable_fields = ('participants','date','country','ruleset')
    inlines= [RoundInline]

class RoundAdmin(ModelAdminPlus):
    inlines = [MatchInline]
    noneditable_fields = ('round_number','tournament','is_current', 'completed_on')
    
class ParticipantAdmin(ModelAdminPlus):
    pass
    
class RulesetAdmin(ModelAdminPlus):
    fields= ('numOfRounds','winPoints','drawPoints','byePoints')
    noneditable_fields = ('numOfRounds','winPoints','drawPoints','byePoints',)

class RefereeAdmin(ModelAdminPlus):
    noneditable_fields = ('user',)   
    
admin.site.register(RefereeUserProfile, RefereeAdmin)
admin.site.register(Tournament, TournamentAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(TournamentRuleset, RulesetAdmin)
admin.site.register(Round, RoundAdmin)


