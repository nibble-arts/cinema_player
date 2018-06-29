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
function init(url) {

	set_stop();

	uri = "http://semmering.local:8000";

	buttons = $(".button");


	// set video navigation events
	$.each(buttons, function () {

		if ($(this).attr("file") != "") {

			$(this).bind("click", function () {

				cmd = $(this).attr("cmd");
				file = $(this).attr("file");

				if (file)
					send_command(cmd, file);
				else
					send_command(cmd, current_file);

			});
		}

	});

	send_command("status");
	send_command("list");

	start_timer(500);
}


/*********************************************************
 * send command to server
 *		call update_display on answer
 *********************************************************/
function send_command(cmd, file) {

	// add command
	query = '/api?cmd='+cmd;

	// add file to play
	if ((file != undefined) && file != "") { query += '&file='+file; }


	// send command
	$.ajax({
		url: uri+query,
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
	display_file_name(data.file);
	display_length(data.length);
	list_dirs(data);
	list_files(data);

}


/*********************************************************
 * draw video navigation
 *********************************************************/
function nav_buttons(data) {

	// switch stati of buttons on server status
	switch (data.status) {

		case "stop":
			set_stop();
			set_position(0);
			break;

		case "pause":
			set_pause();
			break;

		case "play":
			current_file = data.file;
			set_play();
			break;
	}


	// show play button if file is selected
	if (current_file == "") {
		$(".nav[cmd='play']")
			.addClass("disabled");
	}
	else {
		$(".nav[cmd='play']")
			.removeClass("disabled");
	}
}


// set stop
function set_stop() {

	$(".nav")
		.addClass("off");

	$("#b_play")
		.attr("cmd", "play");

	$("#b_pause")
		.addClass("disabled");

	$("#b_stop")
		.removeClass("off");

}


// set pause
function set_pause() {

	$(".nav")
		.addClass("off");

	$("#b_pause")
		.removeClass("off");

	$("#b_stop")
		.addClass("off");

	$("#b_play")
		.attr("cmd", "pause");

}


// set play
function set_play() {

	$(".nav")
		.addClass("off");

	$("#b_play")
		.removeClass("off")
		.attr("cmd", "pause");

	$("#b_pause")
		.removeClass("disabled");

}


/*********************************************************
 * draw online/offline icon
 *********************************************************/
function set_online() {
	$(".online").show();
	$(".offline").hide();
}


function set_offline() {
	$(".online").hide();
	$(".offline").show();
}



/*********************************************************
 * draw video position bar
 *********************************************************/
function position_bar(data) {

	if (data.time !== undefined) {

		set_position(data.time);

	}
}


function set_position (pos) {

	// get position div
	position = $(".position");

	// create position bar if not exists
	if (!$(".position_bar").length) {
		$(position).append('<div class="position_bar"></div>');
	}

	// get max size
	width = $(position).width();
	height = $(position).height();

	// set bar height
	bar = $(".position_bar");
	$(bar).height(height);

	// update progression bar
	if (pos) {
		$(bar).css("width",(width / 100) * pos);
	}
	else {
		$(bar).css("width",0);
	}
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
 * list files
 *********************************************************/
function list_files(data) {

	files = data.files;

	if (files) {
		$("#files").empty();

		ul = $('<ul class="file_list"></ul>');
		$("#files").append(ul);

		// list of files
		if (files != undefined) {

			// ul = $('<ul class="file_list"></ul>');
			// $("#directory").append(ul);


			$.each(files, function () {

				li = $('<li class="file" name="' + this + '">' + this + '</li>');
				li
					.css("cursor", "pointer")
					.bind("click", function () {

						// send_command("play", $(this).attr("name"));
						if ($(this).attr("name")) {
							current_file = $(this).attr("name");
						}

					});

				ul.append(li);
			});

		}
		$("#files").append(ul);
	}
}


/*********************************************************
 * list directories
 *********************************************************/
function list_dirs(data) {

	dir = data.dir;
	dirs = data.dirs;

	// get current dir
	olddir = $(".dir_name").text();

	// if chanched write new directory name and list files
	if (dir != undefined && olddir != dir) {

		$("#directory").empty();
		$("#directory").append('<div class="dir_name">'+dir+'</div>');

		ul = $('<ul class="dir_list"></ul>');
		$("#directory").append(ul);

		// add dir up
		li = $('<li class="dir" name="up">..</li>');
		li
			.css("cursor", "pointer")
			.bind("click", function () {

				current_file = "";
				send_command("up", $(this).attr("name"));

			});

		ul.append(li);


		// list of directories
		if (dirs != undefined) {

			$.each(dirs, function () {

				li = $('<li class="dir" name="' + this + '">' + this + '</li>');
				li
					.css("cursor", "pointer")
					.bind("click", function () {

						send_command("cd", $(this).attr("name"));

					});

				ul.append(li);
			});
		}

		$(".dir_list").append(ul);
	}
}

/*********************************************************
 * timed poll function
 *********************************************************/
function start_timer(duration) {

	setTimeout(function() {

		send_command("position", "");
		send_command("status");
		start_timer(duration);

	}, duration);
}
