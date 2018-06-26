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

function init(url) {

	uri = url;

	buttons = $(".button");

	$.each(buttons, function () {

		if ($(this).attr("file") != "") {

			$(this).bind("click", function () {

				cmd = $(this).attr("cmd");
				file = $(this).attr("file");

				send_command(cmd, file);

			});
		}

	});

	start_timer(1000);
}


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
			set_online();
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


function update_display(data) {

	position_bar(data.time);
	display_file_name(data.file);
	list_files(data.dir, data.files);

}


function set_online() {
	$(".online").show();
	$(".offline").hide();
}


function set_offline() {
	$(".online").hide();
	$(".offline").show();
}


function position_bar(pos) {

	if (pos !== false) {
	
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

	// no time -> set width to 0
	else {
		$(".position_bar").css("width",0);
	}
}


function display_file_name(name) {

	// update file played
	if (name != undefined) {

		$(".file").removeClass("active");
		$("[name='"+name+"']").addClass("active");

		$(".filename").text(name);
		$(".playing")
			.css("color", "#000");
	}
	else {
		$(".file").removeClass("active");

		$(".filename").empty();
		$(".playing").css("color", "#a0a0a0");
	}

}


function list_files(dir, files) {

	if (files != undefined) {

		$("#directory").empty();

		$("#directory").append('<div class="dir_name">'+dir+'</div>');

		ul = $('<ul class="file_list"></ul>');
		$("#directory").append(ul);


		$.each(files, function () {

			li = $('<li class="file" name="' + this + '">' + this + '</li>');
			li
				.css("cursor", "pointer")
				.bind("click", function () {

					send_command("play", $(this).attr("name"));

				});

			ul.append(li);
		});

		$(".file_list").append(ul);
	}
}


function start_timer(duration) {

	setTimeout(function() {

		send_command("position", "");
		start_timer(duration);

	}, duration);
}