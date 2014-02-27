// Generated by CoffeeScript 1.7.1
(function() {
  $(document).ready(function() {
    var choose_player, games, get_players, layer, sd, selected_player_list, stage, td, unselected_player_list, update_heatmap_canvas, update_heatmap_img;
    if ($('#heatmap_stage').length) {
      stage = new Kinetic.Stage({
        width: 300,
        height: 282,
        container: "heatmap_stage"
      });
      layer = new Kinetic.Layer();
      stage.add(layer);
    }
    sd = 2.5;
    games = [];
    unselected_player_list = [];
    selected_player_list = [];
    td = [];
    $("img.loading").hide();
    get_players = function() {
      if ($("#teamselect option:selected").val() !== "None") {
        return $.getJSON("get_players", {
          "team_id": $("#teamselect option:selected").val()
        }, function(data) {
          var player, _i, _len, _ref;
          $("#playerselect").html('<option value="None"> Choose a player: </option>');
          _ref = data['players'];
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            player = _ref[_i];
            $("#playerselect").append('<option value="' + player.id + '">' + player.name + '</option>');
          }
          selected_player_list = [];
          return $("#playerselect").show();
        });
      }
    };
    choose_player = function() {
      if ($("#playerselect option:selected").val() !== "None") {
        selected_player_list.push($("#playerselect option:selected").val());
        $("img.loading").show();
        $("#heatmapdiv").html($("img.loading"));
        if ($("#heatmap_stage").length) {
          return update_heatmap_canvas();
        } else {
          return update_heatmap_img();
        }
      }
    };
    update_heatmap_img = function() {
      return $.get("gen_heatmap_img", {
        "player_id": selected_player_list,
        "sd": sd
      }, function(data) {
        $("img.loading").hide();
        return $('#heatmapdiv').append(data);
      });
    };
    $("#teamselect").change(function() {
      return get_players();
    });
    $("#playerselect").change(function() {
      return choose_player();
    });
    return update_heatmap_canvas = function() {
      return $.getJSON('get_shot_data', {
        'player_id': selected_player_list
      }, function(data) {
        var c, color, opacity, x, y, _i, _len, _ref, _ref1;
        layer.removeChildren();
        _ref = data['local_shot_data'];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          _ref1 = _ref[_i], x = _ref1[0], y = _ref1[1], opacity = _ref1[2], color = _ref1[3];
          c = new Kinetic.Circle({
            x: Math.round(x),
            y: Math.round(y),
            radius: 10,
            opacity: opacity / 2,
            fill: color
          });
          layer.add(c);
        }
        return layer.draw();
      });
    };
  });

}).call(this);
