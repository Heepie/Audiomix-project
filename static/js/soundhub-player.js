var player_play_btn = $("#player-play-btn");

function getCurrentPlaying(self) {
    var target_id = $(self).data("target");
    var audios = $(".audio-file");
    var player_total_duration = $("#player-total-duration");
    var player_current_time = $("#player-current-time");

    audios.each(function(index, item){
        if($(item).attr("data-isPlaying") === "true") {
            $(item).on("play", function() {
                player_total_duration.text(format_time(item.duration))
            });
            $(item).on("timeupdate", function() {
                player_current_time.text(format_time(item.currentTime));
            });

            player_play_btn.attr("data-target", target_id);
        }
    });
}

// player_play_btn.on("click", function() {
//     var target_audio = $("#" + $(this).data("target"));
//     target_audio[0].pause();
//     console.log(target_audio)
// });

function playerBtn(self) {
    var target_audio = $("#" + $(self).attr("data-target"));
    if (target_audio.attr("data-isPlaying") === "false") {
        target_audio[0].play();
        target_audio.attr("data-isPlaying", "true")
    }
    else {
        target_audio[0].pause();
        target_audio.attr("data-isPlaying", "false")
    }
}