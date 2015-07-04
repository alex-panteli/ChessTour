var AppView = Backbone.View.extend({
	el: '#app_container',
	
	events: {
        "change #tournament-selector": "tournamentSelected"
		//change round
	},
  
	tournamentSelected: function(event){
		var selectedTournament = event.currentTarget.value;
		this.changeTournament(selectedTournament);
	},
	
	initialize: function(){
		var self=this;
		app.tournaments = new TournamentList();
		this.tournamentview = new TournamentsView({ collection: app.tournaments });
		app.tournaments.fetch().done(function(){
			if(app.tournaments){
				var selectedTournament = app.tournaments.at(0).get('id');
				self.changeTournament(selectedTournament);
			}
		});
		app.loginView = new LoginView();
	},
	
	changeTournament : function(tournId){
		console.log('displaying scoreboard for' + tournId);
		app.scores = new ScoreList({tournament_id : tournId});
		app.rounds = new RoundList({tournament_id : tournId});
		if(this.scoreview)
			this.scoreview.clean();
		if(this.roundview)
			this.roundview.clean();
		this.scoreview = new ScoreBoardView({collection : app.scores});
		this.roundview = new RoundView({collection : app.rounds});
	}
});

var LoginView = Backbone.View.extend({
	el: '#login-form',
	
	events: {
      "click button[id=login-btn]": "login"
	},
	
	login: function(){
		var user = new Referee();
		user.credentials = {
			username: 'username',
			password: 'password'
		};

		user.save({success : this.renderLogged , failure : this.renderFailure});
	}
	
});

var TournamentsView = Backbone.View.extend({
  el: '#tournament_container',

  initialize: function(){
    this.listenTo(app.tournaments,'update', this.render);
	//this.listenTo(app.tournaments,'sync', this.render);
  },
  
  template: _.template($("#tournament_select_template").html()),
  
  render: function(){
	  console.log('rendering tournaments');
	    var $el = $(this.el);
        $el.html(this.template({ tournaments: app.tournaments.toJSON()}));
		
        return this;
  }
});

var ScoreBoardView = Backbone.View.extend({
  el: '#scoreboard_container',
  
  initialize: function(){
	this.listenTo(this.collection,'update', this.render);
	//this.listenTo(this.collection,'sync', this.render);
	this.collection.fetch();
	
  },
  
  render: function(){
	var $el = $(this.el);
	console.log('rendering scoreboard');
	$el.html('');
	this.collection.each(function(listItem) {
		var item;
		item = new ScoreView({ model: listItem });
		$el.append(item.render().el);
	});

	return this;
  },
  
  clean: function(){
	  this.undelegateEvents();
	  this.stopListening();
  }
});

var ScoreView = Backbone.View.extend({
	tagName: 'li',
	className: 'media',
	template: _.template($("#score_template").html()),
	
	initialize: function(){
		this.listenTo(this.model,'change', this.render);
		//this.listenTo(this.model,'sync', this.render);
	},
	
	render: function(){
	    var $el = $(this.el);
	    $el.data('listId', this.model.get('id'));
        $el.html(this.template(this.model.toJSON()));
		
        return this;
    }
});

var RoundView =  Backbone.View.extend({
	el: '#round_container',
	
	events: {
      "click button[id=prev-round-btn]": "prevRound",
	  "click button[id=next-round-btn]": "nextRound"
	},
	
	prevRound: function(){
		this.changeRound(-1);
	},
	
	nextRound: function(){
		this.changeRound(1);
	},
	
	changeRound: function(increment)
	{
		currentRound = this.current.get("round_number");
		maxRoundNum = this.current.get("max_round");
		if ( (currentRound + increment <= maxRoundNum) && (currentRound + increment >= 1))
		{
			this.current = (this.collection.where({ round_number : currentRound + increment }))[0];
			this.current.set({max_round : maxRoundNum});
			this.loadMatches(this.current.get('id'));
		}
	},
	
	initialize: function(){
			this.listenTo(this.collection,'update', this.loadRound);
			//this.listenTo(this.collection,'sync', this.render);
			this.collection.fetch();
	},
	
	loadRound: function()
	{
		this.current = (this.collection.where({ is_current : true }))[0];
		var maxRound = this.collection.max(function(model) {
			return model.get("round_number");
		});
		this.current.set({max_round : maxRound.get('round_number')});
		this.loadMatches(this.current.get('id'));
	},
	
	loadMatches: function(roundId)
	{
		this.matches = new RoundMatchList({round_id : roundId});
		this.listenTo(this.matches,'update', this.render);
		this.matches.fetch();
	},
	
	template: _.template($("#round_template").html()),
	
	render: function(){
		var $el = $(this.el);
		console.log('rendering matchboard');
		$el.html('');
		$el.html(this.template(this.current.toJSON()));
		var matchhtml = '';
		this.matches.each(function(listItem) {
			var item;
			item = new MatchView({ model: listItem });
			$('#match-list-container').append(item.render().el);
		});
		
		return this;
	},
	
	clean: function(){
	  this.undelegateEvents();
	  this.stopListening();
	}
});


var MatchView = Backbone.View.extend({
  tagName: 'div',
  className: 'row',
  
  events: {
      "click input[type=button]": "saveResult"
  },

  saveResult: function( event ){
      // Button clicked, you can access the element that was clicked with event.currentTarget
      alert( "Search for " + $("#search_input").val() );
	  this.model.save();
  },
  
   initialize: function(){
		this.listenTo(this.model,'change', this.render);
		//this.listenTo(this.model,'sync', this.render);
		this.listenTo(this.model,"change:result", function(model){
		  model.save();
		});
   },
   
   template: _.template($("#match_template").html()),
  
   render: function(){
	  	var $el = $(this.el);
        $el.html(this.template(this.model.toJSON()));
		
        return this;
  }
});

/*
var TournamentView = Backbone.View.extend({
  tagName: 'option',
  initialize: function(){
    this.model.on('change', this.render, this);
  },
  render: function(){
	  var $el = $(this.el);
      $el.data('value', this.model.get('id'));
      
      // Load the compiled HTML into the Backbone "el"
      $el.html( this.model.get('name') );
	  return this;
  },
});
*/