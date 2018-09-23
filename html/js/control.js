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
var status = "stop";
var current_file = "";
var current_playlist = "";
var current_play = false;

var current_seek = false;

var playerData = new Data();



/*********************************************************
 * data section
 *********************************************************/
function Data() {

	var data = {};

	var set = function (key, val) {
		data[key] = val;
	};

	var remove = function (key) {
		if (data.hasOwnProperty(key)) {
			delete data[key];
		}
	};

	return {

		// get property by key
		// no key: get data object
		get: function (key) {

			if (key != undefined) {
				if (data.hasOwnProperty(key))
					return data[key];
				else
					return false;
			}

			else
				return data;
		},

		// get array of keys
		keys: function () {
			var keys = [];

			$.each(data, function (k,v) {
				keys.push(k);
			});

			return keys;
		},

		// update data
		update: function (data) {

			$.each(data, function (k, v) {
				set(k,v);
			});
		},

		// clear data object
		// if keys is []: reset only these keys
		reset: function (keys) {

			// reset fields
			if (keys) {
				$.each(keys, function (k, v) {
					remove(this);
				})
			}

			// reset all
			else {
				data = {};
			}
		}

	}
};



/*********************************************************
 * init control window
 *********************************************************/
function init() {

	set_stop();

	uri = window.location.origin;

	buttons = $(".button");


	// set video navigation events
	$.each(buttons, function () {

		if ($(this).attr("file") != "") {

			$(this).bind("click", function () {

				cmd = $(this).attr("cmd");
				file = $(this).attr("file");
				params = $(this).attr("params");

				paramList = [];

				// add file
				if (file != undefined)
					paramList.push("file="+file);
				else
					paramList.push("file="+current_file);

				// add parameters
				if (params)
					paramList.push(params);

				// send command
				send_command(cmd, paramList.join("&"));

			});
		}

	});

	send_command("list");
	send_command("playlist");
	send_command("stop");

	start_timer(250);
}


/*********************************************************
 * send command to server
 *		call update_display on answer
 *********************************************************/
function send_command(cmd, data) {

	// add command
	query = '/api?cmd='+cmd;

/*	if (data !== undefined) {

		// add file to play
		if ((data.file != undefined) && data.file != "") { query += '&file='+data.file; }

	}*/


	// send command
	$.ajax({
		url: uri+query,
		data: data,
		dataType: "json",
		contentType: "multipart/form-data",

		success: function (data) {
			set_data(data);
			update_display();
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
 * save loaded data
 *	reset data that is not updated periodically
 *********************************************************/
function set_data(data) {

	playerData.reset(["dirinfo", "volume"]);
	playerData.update(data);

}


/*********************************************************
 * update all display items
 *********************************************************/
function update_display() {

	set_online();
	nav_buttons();
	position_bar();

	display_file_name();
	display_length();

	display_volume(playerData.get("volume"));

	if (data = playerData.get("fileinfo")) {
		display_info(data);
	}


	if (data = playerData.get("dirinfo")) {
		display_dirinfo(data);
	}

	display_playlist();

}


function display_dirinfo(data) {

	list_dirs(data["dir"], data["dirs"]);
	list_files(data["dir"], data["files"]);
	list_pl_files(data["dir"], data["pl_files"]);

}


/*********************************************************
 * draw video navigation
 *********************************************************/
function nav_buttons() {

	// switch stati of buttons on server status
	switch (playerData.get("status")) {

		case "stop":
			set_stop();
			set_position(0);
			status = "stop";
			break;

		case "pause":
			set_pause();
			status = "pause";
			break;

		case "play":
			current_file = playerData.get("file");
			set_play();
			status = "play";
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

	/* halting */
	if ($("#b_stop").hasClass("off") && status != "stop") {
		set_next_play();
	}

	$("#b_stop")
		.removeClass("off");

	$("#files .file_list")
		.removeClass("inactive");

	$("#position")
		.addClass("inactive");

	$("#b_voldown")
		.addClass("disabled")

	$("#b_volup")
		.addClass("disabled")
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

/*	$("#b_voldown")
		.addClass("disabled")

	$("#b_volup")
		.addClass("disabled")
*/

//	$("#files .file_list")
//		.removeClass("inactive");
}


// set play
function set_play() {

	$(".nav")
		.addClass("off");

	$("#b_play")
		.removeClass("off")
		.attr("cmd", "pause");

	$("#b_voldown")
		.removeClass("disabled")

	$("#b_volup")
		.removeClass("disabled")

	$("#b_pause")
		.removeClass("disabled");

	$("#position")
		.removeClass("inactive");

//	$("#files .file_list")
//		.addClass("inactive");

}


// set seek
function set_seek() {

	$(".seek").remove();

	$("#position").append("<div class='seek'></div>");
	$(".seek").css("left", (current_seek / 100) * width);

	$("#b_end")
		.removeClass("disabled")
		.bind("click", function () {
			$(this).addClass("disabled")

			if (current_seek !== false) {
				send_command("seek", {position: current_seek});
			}

			$(".seek").remove();
			current_seek = false;
		});
} 


// set new play position of playlist
function set_next_play() {

}



/*********************************************************
 * draw online/offline icon
 *********************************************************/
function set_online() {

	$(".offline")
		.addClass("online")
		.removeClass("offline");
}


function set_offline() {

	$(".online")
		.addClass("offline")
		.removeClass("online");
}



/*********************************************************
 * draw video position bar
 *********************************************************/
function position_bar() {

	if (playerData.get("time") !== undefined) {

		// seek operation: reset seek marker
		if (playerData.get["cmd"] == "seek") {
			current_seek = false;
		}

		set_position(playerData.get("time"));

	}
}


function set_position (pos) {

	// get position div
	position = $(".position");

	// get max size
	width = $(position).width();
	height = $(position).height();


	if (current_seek === false) {
//		$(".seek").remove();
	}


	// add seek event
	position
		.unbind("click")
		.bind("click", function (e) {

			var parentOffset = $(this).offset();
			var relX = e.pageX - parentOffset.left;
			current_seek = (relX / width) * 100;

			set_seek();
		});


	// create position bar if not exists
	if (!$(".position_bar").length) {
		$(position)
			.append('<div class="position_bar"></div>');
	}

	// set bar height
	bar = $(".position_bar");
	$(bar).height(height);


	// update progression bar
	if (pos) {
		$(bar)
			.attr("pos", pos)
			.css("width",(width / 100) * pos);
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
		$(".current_file").text(filename(current_file));

		$(".file").removeClass("active");
		$(".playlist").removeClass("active");
		$("[name='"+current_file+"']").addClass("active");
	}

	// no current file
	else {
		$(".current_file").empty();
		$(".file").removeClass("active");
	}


	// film info selected
	if ($("div[name='file']").text() != "") {
		$("#info").removeClass("inactive");
	}
	else {
		$("#info").addClass("inactive");
	}


	// update active playlist
	if (current_playlist != undefined) {
		$(".current_playlist").text(filename(current_playlist));

		$(".playlistfile").removeClass("active");
		$("[name='"+current_playlist+"']").addClass("active");
	}

	else {
		$(".current_playlist").empty();

		$(".playlistfile").removeClass("active");
	}


	// update screensaver
	if (scr = playerData.get("screensaver")) {

		// screensaver file
		$(".screensaver")
			.text(filename(scr["screensaver_file"]))
			.attr("file", scr["screensaver_file"])
			.unbind("click");


		if (scr["screensaver_file"] != "") {

			if (scr["enable_screensaver"] == true)
				$(".screensaver").removeClass("lightened");
			else
				$(".screensaver").addClass("lightened");


			$(".screensaver")
				.removeClass("inactive")
				.bind("click", function () {

					if (scr["enable_screensaver"] == true)
						send_command("disable_screensaver");
					else
						send_command("enable_screensaver");
				});
		}

		// no screensaver file: inactivate field
		else {
			$(".screensaver")
				.text("")
				.addClass("inactive");
		}
	}


}


/*********************************************************
 * display video file configuration data
 *********************************************************/
function display_volume(volume) {

	if (volume) {

		if (!$(".current_volume").length)
			$("#volume").append("<div class='current_volume'></div>");

		// get max size
		height = $("#volume").height();

		$(".current_volume")
			.css("top", height - ((volume / 100) * height))
			.css("height", (volume / 100) * height);
	}

	else
		$("#volume").empty();

}


/*********************************************************
 * display video file configuration data
 *********************************************************/
function display_info(data) {

	fileName = data["file"];

	if (filename != undefined) {

		$("div[name='file']")
			.text(fileName);


		// add event to set as screensaver
		$("[name='screensaver_check']")
			.prop("checked", false)
			.unbind("click")
			.bind("click", function () {

				// switched on
				if ($(this).is(":checked")) {
					send_command("set_screensaver", {file: fileName});
				}

				// switched off
				else {
					$(".screensaver").removeAttr("file");
					send_command("set_screensaver", {file: ""});
				}

			});


		// get current screensaver
		screensaver = $(".screensaver").attr("file");

		// mark if file is screensaver
		if (screensaver == data["file"]) {

			$("[name='screensaver_check']")
				.prop("checked", true);
		}
	}


	// clear fields
	$("[edit]").find(".value").text("");


	// bind edit events
	$("div[edit]")
		.unbind("click")
		.bind("click", function () {

			$(this).unbind("click");

			edit_field = $(this).children(".value");
			edit_value = edit_field.text();

			edit_field
				.empty()
				.append("<input type='text' value='" + edit_value + "'>")
				.bind("keyup", function (e) {

					switch (e.which) {

						// enter value
						case 13:
							write_config(fileName);
							break;

						// escape
						case 27:
// DOTO is chanched data loaded correctly? 
							update_display();
							break;
					}

				});

			edit_field.find("input")
				.focus();
		});


	/* insert informations */
	$.each(data["audio"], function (k, v) {
		$("*[name='audio"+k+"']").find(".value").text(v);
	});

	$.each(data["video"], function (k, v) {
		$("*[name='video_"+k+"']").find(".value").text(v);
	});
}



/*********************************************************
 * send video info data to be written
 *********************************************************/
function write_config(file) {

	data = {};
	data["file"] = file;

	// get key: values from divs
	$.each($("div[edit]"), function () {

		label = $(this).attr("name");
		val = $(this).children(".value").text();
		input_val = $(this).find("input").val();

		if (input_val != undefined)
			val = input_val;

		data[label] = val;
	});


	/* send to player */
	send_command("writeinfo", data);
}


/*********************************************************
 * display video length
 *********************************************************/
function display_length() {

	if (playerData.get("length") != undefined) {
		$(".length").text(playerData.get("length"));
	}
	else {
		$(".length").empty();
	}
}


/*********************************************************
 * list files
 *********************************************************/
function list_files(dir, files) {


	if (files) {
		$("#files").empty();

		ul = $('<ul class="file_list"></ul>');
		$("#files").append(ul);

		// list of files
		if (files != undefined) {

			$.each(files, function () {

				li = $('<li class="file" name="' + joinpath([dir, this]) + '">' + this + '</li>');
				li
					.css("cursor", "pointer")
					.bind("click", function () {

						if ($(this).attr("name")) {
							current_file = $(this).attr("name");
						}

						send_command("fileinfo", {file: current_file});

					});

				ul.append(li);
			});

		}
		$("#files").append(ul);
	}
}


/*********************************************************
 * list playlist files
 *********************************************************/
function list_pl_files(dir, files) {


	if (files) {
		$("#pl_files").empty();

		ul = $('<ul class="file_list"></ul>');
		$("#pl_files").append(ul);

		// list of files
		if (files != undefined) {

			// ul = $('<ul class="file_list"></ul>');
			// $("#directory").append(ul);

			$.each(files, function () {

				li = $('<li class="playlistfile" name="' + this + '">' + this + '</li>');
				li
					.css("cursor", "pointer")
					.bind("click", function () {

						if ($(this).attr("name")) {

							send_command("playlist", {file: joinpath([dir, $(this).attr("name")])});
							current_playlist = $(this).attr("name");
						}

/*						send_command("fileinfo", {file: current_file});*/

					});

				ul.append(li);
			});

		}
		$("#pl_files").append(ul);
	}
}


/*********************************************************
 * list directories
 *********************************************************/
function list_dirs(dir, dirs) {

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
				send_command("up", {file: $(this).attr("name")});
//				display_filename();

			});

		ul.append(li);


		// list of directories
		if (dirs != undefined) {

			$.each(dirs, function () {

				li = $('<li class="dir" name="' + this + '">' + this + '</li>');
				li
					.css("cursor", "pointer")
					.bind("click", function () {

						send_command("cd", {file: $(this).attr("name")});

					});

				ul.append(li);
			});
		}

		$(".dir_list").append(ul);
	}
}


/*********************************************************
 * display playlist
 *********************************************************/
function display_playlist() {

	if (playerData.get("cmd") == "playlist") {

		files = playerData.get("playlist");
		pl_options = playerData.get("options");

		$("#playlist_content").empty();

		ol = $('<ol class="playlist"></ol>');
		$("#playlist_content").append(ol);

		// list of files
		if (files != undefined) {

			$.each(files, function () {

				li = $('<li class="playlist" name="' + this + '">' + this + '</li>');
				li
					.css("cursor", "pointer")
					.bind("click", function () {

						if ($(this).attr("name")) {
							current_file = $(this).attr("name");
						}

						send_command("fileinfo", {file: current_file});

					});

				ol.append(li);
			});

		}
		$("#playlist_content").append(ol);
	}
}




/*********************************************************
 * display filename with shortened path
 *********************************************************/
function filename(name) {

	if (name != undefined)
		return name.split("/").pop();

}


/*********************************************************
 * join an array of path snippets togeather
 *********************************************************/
function joinpath(pathArray) {

	var retArray = [];
	var root = false;

	// split all path elements
	$.each(pathArray, function () {
		retArray = retArray.concat(this.split("/"));
	});

	// check for root /
	if ((retArray[0]) == "") root = true;

	// remove empty elements
	retArray = retArray.filter(function (v) { return v != "" });

	// add root /
	if (root)
		retArray.unshift("");

	return retArray.join("/");
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
