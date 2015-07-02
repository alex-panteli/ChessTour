<script type="text/template" id="scoreboard_template">
  <ul>
  </ul>
</script>

<script type="text/template" id="match_template">
  <label>Search</label>
  <input type="text" id="search_input" />
  <input type="button" id="search_button" value="Search" />
</script>

<script type="text/template" id="round_template">
  <label>Search</label>
  <input type="text" id="search_input" />
  <input type="button" id="search_button" value="Search" />
</script>

<script type="text/template" id="tournament_select_template">
	<select id="tournament-selector">
		 <% _.each(tournaments, function(tournament) {%>
			<option value="<%= tournament.id %>"><%= tournament.name %> <%= tournament.date %></option>
		<% }); %>
	</select>
</script>