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
	},
	
	changeTournament : function(tournId){
		console.log('displaying scoreboard for' + tournId);
		app.scores = new ScoreList({tournament_id : tournId});
		app.matches = new RoundMatchList({round_id : 1})
		this.scoreview = new ScoreBoardView({collection : app.scores});
		this.roundview = new RoundView({collection : app.matches});
	}
})

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
	
	initialize: function(){
			this.listenTo(this.collection,'update', this.render);
			//this.listenTo(this.collection,'sync', this.render);
			this.collection.fetch();
	},
	
	template: _.template($("#round_template").html()),
	
	render: function(){
		var $el = $(this.el);
		console.log('rendering matchboard');
		$el.html('');
		$el.html(this.template({}));
		var matchhtml = '';
		this.collection.each(function(listItem) {
			var item;
			item = new MatchView({ model: listItem });
			$('#match-list-container').append(item.render().el);
		});
		
		return this;
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
		console.log('rendering' + this.model.toJSON());
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