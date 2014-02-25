$(document).ready(->
    sd = 2.5
    games = []
    unselected_player_list = []
    selected_player_list = []
    td = []
    $("img.loading").hide()

    get_players = ->
        if $("#teamselect option:selected").val() != "None"
            $.getJSON(
                "get_players", 
                {"team_id": $("#teamselect option:selected").val()},
                (data) ->
                    $("#playerselect").html('<option value="None"> Choose a player: </option>')
                    for player in data['players']
                        $("#playerselect").append('<option value="' + player.id + '">' + player.name + '</option>')
                    selected_player_list = []
                    $("#playerselect").show()
            )

    choose_player = ->
        if $("#playerselect option:selected").val() != "None"
            selected_player_list.push($("#playerselect option:selected").val())
            $("img.loading").show()
            $("#heatmapdiv").html($("img.loading"))                
            update_heatmap_img()

    update_heatmap_img = ->
        $.get(
            "gen_heatmap_img", 
            {"player_id": selected_player_list, "sd": sd},
            (data) -> 
                $("img.loading").hide()
                $('#heatmapdiv').append(data)

        )
    $("#teamselect").change(-> get_players())
    $("#playerselect").change(-> choose_player())

)