$(document).ready(
function(){

	var sd = 2.5;
	var games = [];
	var unselected_player_list = [];
	var selected_player_list = [];
	var td = [];

	$.getJSON("get_teams", {}, function(data){
		teams = data["teams"];
		for(i=0; i < teams.length; i++){
			team = teams[i];
			$('#teamselect').append('<option value="' + 'team' + team.id + '">' + team.name + '</option>');
		}
	});
	
	get_players = function(){
		$.getJSON("get_players", {"team_id": $("#teamselect option:selected").val()}, 
			function(data){
				$("#playerselect").html('<option value="None"> Choose a player: </option>');
				players = data["players"];
				for(i=0; i < players.length; i++){
					player = players[i];
					$("#playerselect").append('<option value="' + player.id + '">' + player.name + '</option>');
				}
				selected_player_list = [];
				$('#heatmapdiv').html("");
				$("#playerselect").show();
			});
	};

	choose_player = function(){
		selected_player_list.push($("#playerselect option:selected").val())
		update_heatmap_img();
	};

	strip_id = function(idstr, index){
		justid = "";
		for(i=index; i < idstr.length; i++){
			justid += idstr[i];
		}
		return justid;
	};

	update_heatmap_img = function(){
		$.get("gen_heatmap_img",
			  {"player_id": selected_player_list,
			   "sd": sd},
			function(data){
				$('#heatmapdiv').html(data);
			}
		);
	};
});




