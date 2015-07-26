var AppView = Backbone.View.extend({
	el: '#app_container',
	
	events: {
        "change #tournament-selector": "tournamentSelected"
	},
  
	tournamentSelected: function(event){
		var selectedTournament = event.currentTarget.value;
		this.changeTournament(selectedTournament);
	},
	
	initialize: function(){
		var self=this;
		app.refresh = this.refresh
		app.tournaments = new TournamentList();
		this.tournamentview = new TournamentsView({ collection: app.tournaments });
		app.tournaments.fetch().done(function(){
			if(app.tournaments){
				var tournId = app.tournaments.at(0).get('id');
				self.changeTournament(tournId);
			}
		});
		app.loginView = new LoginView();
	},
	
	changeTournament : function(tournId){
		this.currTour = app.tournaments.get(tournId); 
		app.scores = new ScoreList({tournament_id : tournId});
		app.rounds = new RoundList({tournament_id : tournId});
		if(this.scoreview)
			this.scoreview.clean();
		if(this.roundview)
			this.roundview.clean();
		this.scoreview = new ScoreBoardView({collection : app.scores});
		app.roundview = new RoundView({collection : app.rounds});
	},
	
	refresh : function(){
		app.scores.fetch({reset: true});
	    //Check if there's a new round
		if (app.roundview.wasLastMatch()){
			app.rounds.fetch({reset: true});
		}
	}
	
});

var LoginView = Backbone.View.extend({
	el: '#login-container',
	
	events: {
      "click button[id=login-btn]": "login"
	},
	
	initialize: function(){
		this.user = new Referee();
    },
	
	login: function(){
		
		var usernameStr = $('#username-field').val();
		var passwordStr = $('#password-field').val();
		this.user.credentials = {
			username: usernameStr,
			password: passwordStr
		};
		
		var self = this;
		this.user.fetch({success : function () {
									self.renderLogged();
									} , 
						 error : this.renderFailure});
	},
	
	isAuthenticated: function() {
		var loggedUser = this.getUser();
		var selectedTournament = app.tournaments.get(app.scores.options.tournament_id);
		if(loggedUser && (selectedTournament.get('referee').id == loggedUser.get('id')))
		{
			return true;
		}
		return false;
	},
	
	success_template : _.template($("#logged-in_template").html()),
	
	renderLogged: function() {
		var $el = $(this.el);
		var userObj = this.user.at(0);
        $el.html(this.success_template(userObj.toJSON()));
		app.roundview.render();
        return this;
	},
	
	renderFailure: function() {
		$('#error-output').addClass("col-xs-12 alert alert-danger text-center");
		$('#error-output').attr('role',"alert");
		$('#error-output').text("Login failed");

	},
	
	getUser: function() {
		if(this.user.at(0))
			return this.user.at(0);
		return undefined;
	}
	
});

var TournamentsView = Backbone.View.extend({
  el: '#tournament_container',

  initialize: function(){
    this.listenTo(app.tournaments,'update', this.render);
  },
  
  template: _.template($("#tournament_select_template").html()),
  
  render: function(){
	    var $el = $(this.el);
        $el.html(this.template({ tournaments: app.tournaments.toJSON()}));
		
        return this;
  }
});

var ScoreBoardView = Backbone.View.extend({
  el: '#scoreboard_container',
  
  initialize: function(){
	this.listenTo(this.collection,'update', this.render);
	this.listenTo(this.collection,'reset', this.render);
	this.collection.fetch();
	
  },
  
  render: function(){
	var $el = $(this.el);
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
			this.loadRound();
		}
	},
	
	initialize: function(){
			this.listenTo(this.collection,'update', this.loadCurrentRound);
			this.listenTo(this.collection,'reset', this.loadCurrentRound);
			this.collection.fetch();
	},
	
	loadCurrentRound: function()
	{
		this.current = (this.collection.where({ is_current : true }))[0];
		this.loadRound();
	},
	
	loadRound: function()
	{
		this.cleanItems();		
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
		if('items' in this && this.items.length != 0) {
			for ( var i=0,  tot=this.items.length; i < tot; i++){
					this.items[i].render();
			}
		}
		else
		{		
			var $el = $(this.el);
			$el.html('');
			$el.html(this.template(this.current.toJSON()));
			var self = this;
			this.matches.each(function(listItem) {
				var item;
				item = new MatchView({ model: listItem });
				$('#match-list-container').append(item.render().el);
				self.addMatch(item);
			});
		}
		
		return this;
	},
	
	addMatch: function(match){
		if(!('items' in this)){
			this.items = [];
		}
		this.items.push(match);
	},
	
	wasLastMatch: function(){
		var unplayedMatches = this.matches.where({ result : '' });
		if (unplayedMatches.length != 0){
			return false;
		}
		return true;
	},
	
	clean: function(){
	  this.undelegateEvents();
	  this.stopListening();
	},
	
	cleanItems: function(){
	  if(!('items' in this)) {
		  return;
	  }
	  for ( var i=0,  tot=this.items.length; i < tot; i++){
		  this.items[i].undelegateEvents();
		  this.items[i].stopListening();
	  }
	  this.items = []
	}
	
});


var MatchView = Backbone.View.extend({
  tagName: 'div',
  className: 'row',
  
  events: {
      "click button[type=save]": "saveResult"
  },

  saveResult: function( event ){
	  
	  if(app.loginView.isAuthenticated())
	  {
		    var elName = "#result-selector-" + this.model.get('id');
			this.model.credentials = app.loginView.user.credentials;
			this.model.save({ result :  $(elName).val()},{wait: true});
	  }
	  
  },
  
   initialize: function(){
		this.listenTo(this.model,'change', this.render);
		this.listenTo(this.model,"change:result", function(model){
		  app.refresh();
		});		  
   },
   
   template: _.template($("#match_template").html()),
  
   render: function(){
	  	var $el = $(this.el);
		//if logged in and referee id matches tournament referee insert referee from app.loginView 
		var isAuthenticated =  app.loginView.isAuthenticated();
		this.model.set({ logged : isAuthenticated });
        $el.html(this.template(this.model.toJSON()));
		
        return this;
  }
});