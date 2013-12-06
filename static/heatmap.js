$(document).ready(
function(){

	var sd = 2.5;
	var games = [];
	var unselected_player_list = [];
	var selected_player_list = [];
	var td = [];


	list_remove = function(a, k){
		newa = [];
		for(var i in a){
			if(a[i] != k){
				newa.push(a[i]);
			}
		}
		return newa;
	}

	update_players = function(){
		alert(selected_players.length);
		sdivs = "";
		for(i = 0; i < selected_players.length; i++){
			player = selected_players[i];
			link = "<a href=\"#\">" + player.name + "</a>";
			sdivs += make_simple_div("player" + player.id,
									"playerlink", link );
		}
		$("#selectedplayers").html(sdivs);
	}

	make_simple_div = function(id, divclass, content){
		tag =  "<div id='" + id + "' class='" + divclass + "'>";
		tag += content + "</div>";
		return tag;
	}

	$.getJSON("get_teams", {}, function(data){
		divs = [];
		teams = data["teams"];
		for(i=0; i < teams.length; i++){
			team = teams[i];
			link = "<a href=\"#\">" + team.name + "</a>";
			divs += make_simple_div("team" + team.id,
									"teamlink", link );
		}
		$('#teamselect').append(divs);
		activate_tselect();
	});

	activate_tselect = function(){
		$('div.teamlink').click(function(){
			$.getJSON("get_players", {"team_id": this.id}, function(data){
				divs = [];
				players = data["players"];
				for(i=0; i < players.length; i++){
					player = players[i];
					link = "<a href=\"#\">" + player.name + "</a>";
					divs += make_simple_div("player" + player.id,
											"playerlink", link );
				}
				selected_player_list = [];
				$('#heatmapdiv').html("");
				$('#selectedplayers').html("");
				$('#unselectedplayers').html(data["teamname"] + divs);
				activate_pselect();
			});
		});

	};

	strip_id = function(idstr, index){
		justid = "";
		for(i=index; i < idstr.length; i++){
			justid += idstr[i];
		}
		return justid;
	};

	inlist = function(list, item){
		for(i=0; i < list.length; i++){
			if(list[i] == item){ return true;}
		}
		return false;
	};

	activate_pselect = function(){
		$('div.playerlink').click(function(){
			name = "#" + this.id;
			pid = strip_id(this.id, 6);
			link = $(name).html();
			div = make_simple_div("player" + pid,
								  "playerlink", link);
			if(inlist(selected_player_list, pid)){
				selected_player_list = list_remove(selected_player_list, parseInt(pid));

				$(name).remove();
				$("#unselectedplayers").append(div);
				activate_pselect();
			}
			else{
				selected_player_list.push(parseInt(pid));

				$(name).remove();
				$("#selectedplayers").append(div);
				activate_pselect();
			}
			update_heatmap_img();
 		});
	};

	update_heatmap_img = function(){
		$.get("gen_heatmap_img/",
			  {"player_ids": selected_player_list,
			   "sd": sd},
			function(data){
				$('#heatmapdiv').html(data);
			}
		);
	};
});




