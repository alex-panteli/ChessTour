window.TastypieModel = Backbone.Model.extend({
    base_url: function() {
      var temp_url = Backbone.Model.prototype.url.call(this);
      return (temp_url.charAt(temp_url.length - 1) == '/' ? temp_url : temp_url+'/');
    },

    url: function() {
      return this.base_url();
    }
});

window.TastypieCollection = Backbone.Collection.extend({
    parse: function(response) {
        this.recent_meta = response.meta || {};
        return response.objects || response;
    }
});

var Tournament = TastypieModel.extend({
	urlRoot : '/api/scoring/tournament'
});

var TournamentList = TastypieCollection.extend({
	model: Tournament,
	url: '/api/scoring/tournament/'
});


var Score = TastypieModel.extend({
	urlRoot: '/api/scoring/score'
});

var ScoreList = TastypieCollection.extend({
	model: Score,
	url: function() {
		return '/api/scoring/score/?tournament__id=' + this.options.tournament_id;
	},
	
	initialize: function(options) {
		this.options = options;
	}
});
/*
var Match = TastypieModel.extend({
	urlRoot: '/api/scoring/match',
	defaults: {
		round: '',
		participant_one: '',
		participant_two: '',
		result: ''
	},
	initialize: function(){
		this.on("change:result", function(model){
		  model.save();
		});
	}
});

var RoundMatchList = TastypieCollection.extend({
	model : Match,
	url: function() {
		return '/api/scoring/match/?round=' + this.options.round_id;
	}
	initialize: function(){
		this.fetch();
	})
	
})

*/