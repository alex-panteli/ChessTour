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
	urlRoot = '/api/tournament',
	defaults: {
		name: 'New tournament',
		country: 'US'
	}
});

var TournamentList = TastypieCollection.extend({
	model: Tournament,
	url: '/api/tournament/'
	initialize: function(){
		this.fetch();
	})
})

var Match = TastypieModel.extend({
	urlRoot: '/api/match',
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
		return '/api/match/?round=' + this.options.round_id;
	}
	initialize: function(){
		this.fetch();
	})
	
})
		
var Score = TastypieModel.extend({
	urlRoot: '/api/score',
	defaults: {
		participant : '',
		tournament: '',
		score: ''
	}
})

var ScoreList = TastypieCollection.extend({
	model: Score,
		url: function() {
		return '/api/score/?tournament=' + this.options.tournament_id;
	}
	initialize: function(){
		this.fetch();
	})
})

