
$(document).ready(
function(){

	// var heat = simpleheat('canvas');
	// var c = document.getElementById("canvas");
	// var ctx = c.getContext("2d");
	// var img = document.getElementById("court_im");
	// ctx.drawImage(img,0,0);
	// $('canvas').drawImage($('#court_im'), 0, 0);
	var sd = 2.5;
	var games = [];
	var unselected_player_list = [];
	var selected_player_list = [];
	var td = [];
	
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

	update_heatmap_img = function(){
		$.get("gen_heatmap_img",
			  {"player_id": selected_player_list,
			   "sd": sd},
			function(data){
				$('#heatmapdiv').html(data);
			}
		);
	};

	// update_heatmap_img = function(){
	// 	$.getJSON("get_shot_data",
	// 		  {"player_id": selected_player_list,
	// 		   "sd": sd},
	// 		function(data){
	// 			heat.data(data);
	// 			heat.radius(5,1);
	// 			heat.draw(0.2);
	// 			}
	// 	);
	// };
});




