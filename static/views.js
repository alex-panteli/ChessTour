// On launch show the last round of the most recent tournament, selecting tournament => get latest round, if modifiable show buttons
//############# Views ###############

var ScoreBoardView = Backbone.View.extend({
  el: '#scoreboard_container',
  tagName: 'ul',
  className: 'nav nav-list lists-nav',
  events: {
    },
  initialize: function(){
    this.collection.on('add', this.render, this);
  },
  render: function(){
	var $el = $(this.el)

	this.collection.each(function(listItem) {
		var item, sidebarItem;
		item = new SingleScoreView({ model: listItem });
		$el.append(item.render().el);
	});

	return this;
  }
});

var RoundView =  Backbone.View.extend({
  initialize: function(){
    this.render();
	this.collection = round matches?
  }
  render: function(){
      // Compile the template using underscore
      var template = _.template( $("#round_template").html(), {} );
      // Load the compiled HTML into the Backbone "el"
      this.$el.html( template );
  }
});

var SingleMatchView = Backbone.View.extend({
	tagName: 'li',
    className: 'list-menu-item',
  initialize: function(){
    this.model.on('change', this.render, this);
  },
  render: function(){
	  var $el = $(this.el);
      $el.data('listId', this.model.get('id'));
      var template = _.template( $("#match_template").html(), this.model.toJSON() );
      // Load the compiled HTML into the Backbone "el"
      $el.html( template );
	  return this;
  },
  events: {
      "click input[type=button]": "saveResult"
  },
  saveResult: function( event ){
      // Button clicked, you can access the element that was clicked with event.currentTarget
      alert( "Search for " + $("#search_input").val() );
  }
});
