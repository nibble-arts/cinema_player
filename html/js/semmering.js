/****************************************************
 * This file is part of the Cinema Player scripts
 *
 * It is provided as is unter the
 * GNU GENERAL PUBLIC LICENSE Version 3
 *
 * @author	  Thomas Winkler <thomas.winkler__at__iggmp.net>
 * @Version   1.0
 * @copyright 2018
 ****************************************************/


var uri = "";
var current_file = "";


/*********************************************************
 * init control window
 *********************************************************/
function init() {

	set_stop();

	uri = window.location.origin;

	buttons = $(".button, .home_button");


	// set video navigation events
	$.each(buttons, function () {

		if ($(this).attr("file") != "") {

			$(this).bind("click", function () {

				cmd = $(this).attr("cmd");
				file = $(this).attr("file");

				send_command(cmd, {file: file});

			});
		}

	});

//	send_command("list");

	start_timer(500);
}


/*********************************************************
 * send command to server
 *		call update_display on answer
 *********************************************************/
function send_command(cmd, data) {

	// add command
	query = '/api?cmd='+cmd;

	// add file to play
//	if ((file != undefined) && file != "") { query += '&file='+file; }


	// send command
	$.ajax({
		url: uri+query,
		data: data,
		dataType: "json",
		contentType: "multipart/form-data",

		success: function (data) {
			update_display(data);
		},

		error: function (xhr, ajaxOptions, thrownError) {

			set_offline();
			// console.log("error");
			// console.log(xhr);
			// console.log(thrownError);
		}
	});
}


/*********************************************************
 * update all display items
 *********************************************************/
function update_display(data) {

	set_online();
	nav_buttons(data);
	position_bar(data);
	// display_file_name(data.file);
	// display_length(data.length);

}


/*********************************************************
 * draw video navigation
 *********************************************************/
function nav_buttons(data) {

	// switch stati of buttons on server status
	switch (data.status) {

		case "stop":
			current_file = null;
			clear_position();
			set_stop();
			break;

		case "play":
			current_file = data.file;
			set_play(data.screensaver);
			break;
	}

}


// set stop
function set_stop() {

	$(".button[file != '"+current_file+"']")
		.fadeIn(500);

	$(".home_button")
		.fadeOut(500);
}


// set play
function set_play(screensaver) {

	if (!screensaver) {

		$(".button[file != '"+current_file+"']")
			.fadeOut(500);

		$(".button[file = '"+current_file+"']")
			.fadeIn(500);
	}

	else {
		$(".button[file != '"+current_file+"']")
			.fadeIn(500);

		// remove all position displays
		$(".position").empty();
	}


	$(".home_button")
		.fadeIn(500);

}


/*********************************************************
 * draw online/offline icon
 *********************************************************/
function set_online() {
//	$(".online").show();
//	$(".offline").hide();

    $(".button").css("opacity", 1);
}


function set_offline() {
//	$(".online").hide();
//	$(".offline").show();

    $(".button").css("opacity", 0.4);
}



/*********************************************************
 * draw video position bar
 *********************************************************/
function position_bar(data) {

	if ((data.time !== undefined) && data.time !== null) {
		set_position(data.time);
	}
}


function set_position (pos) {

	// get position div
	position = $(".position[file='"+current_file+"']");

	// create position bar if not exists
	if (position.children().length == 0) {
		$(position).append('<div file="' + current_file + '" class="position_bar"></div>');
	}

	// get max size
	width = $(position).width();
	height = $(position).height();

	// set bar height
	bar = $(".position_bar[file='" + current_file + "']");
	$(bar).height(height);

	// update progression bar
	if (pos) {
		$(bar).css("width",(width / 100) * pos);
	}
	else {
		$(bar).css("width",0);
	}
}


function clear_position () {
	$(".position").empty();
}


/*********************************************************
 * mark current filename
 *********************************************************/
function display_file_name() {

	// update file played
	if (current_file != undefined) {
		$(".current_file").text(current_file);

		$(".file").removeClass("active");
		$("[name='"+current_file+"']").addClass("active");
	}

	// file stopped
	else {
		$(".current_file").empty();

		$(".file").removeClass("active");
		$(".filename").empty();
	}

}


/*********************************************************
 * mark current filename
 *********************************************************/
function display_length(length) {

	if (length != undefined) {
		$(".length").text(length);
	}
	else {
		$(".length").empty();
	}
}



/*********************************************************
 * timed poll function
 *********************************************************/
function start_timer(duration) {

	setTimeout(function() {

		send_command("position");
		start_timer(duration);

	}, duration);
}
