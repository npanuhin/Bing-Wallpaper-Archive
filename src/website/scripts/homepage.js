const year_api_path = year => `US/en.${year}.json`,
	image_url_prefix = "https://storage.googleapis.com/npanuhin-bing-wallpaper-archive/US/en/";

const start_date = new Date(2017, 2, 1), // 2017-03-01: 1080p images start here
	end_date = (d => new Date(d.setDate(d.getDate() - 1)))(new Date), // Yesterday
	previous_year = end_date.getFullYear() - 1; // Previous year to avoid having only one image on January 1st

const background = document.getElementById("background"),
	foreground = document.getElementById("foreground"),
	title = document.getElementById("title"),
	// timer = document.getElementById("timer"),
	timer_path = document.getElementById("timer_path"),
	transition_delay_initial = 200, // Initial delay before showing first image
	transition_delay_true = 1000,
	delay = 5000,
	hold_delay = 3000;

const timer_duration = delay - transition_delay_true;
timer_path.style.animationDuration = `${(timer_duration) / 1000}s`;

var transition_delay = transition_delay_initial

var cur_image = foreground;

var api;

var first_image_loaded = false,
	hold = false;


// =====================================================================================================================

function random(min, max) {
	return Math.random() * (max - min) + min;
}

function randomDate(from, to) {
	return new Date(random(from.getTime(), to.getTime()));
}

function leadingZeros(s, totalDigits) {
	s = s.toString();
	let res = "";
	for (i = 0; i < (totalDigits - s.length); ++i) res += "0";
	return res + s.toString();
}

function date2str(date) {
	return leadingZeros(date.getFullYear(), 4) +
		"-" + leadingZeros(date.getMonth() + 1, 2) +
		"-" + leadingZeros(date.getDate(), 2);
}

function reflow(element) {
	void(element.offsetHeight);
}

// function wait_func(func, callback, interval = 20) {
//     (async _ => {
//         while (!func()) await new Promise(resolve => setTimeout(resolve, interval));
//         callback();
//     })();
// }

function waitFor(conditionFunction, interval = 20) {
	const poll = resolve => {
		if (conditionFunction()) resolve();
		else setTimeout(_ => poll(resolve), interval);
	}
	return new Promise(poll);
}

function fetchYear(year, callback, alert_error = false) {
	fetch(year_api_path(year), {
			method: "GET",
			headers: {
				"Content-Type": "application/json"
			},
			mode: "same-origin"
		})
		.then(response => {
			if (response.ok) {
				return response.json();
			} else {
				throw new Error(`Error: can not load API file: ${year_api_path(year)}`);
			}
		})
		.then(data => {
			// let result = {};
			// data.forEach(image => {
			//     result[image["date"]] = image;
			// });
			callback(data);
		})
		.catch(error => {
			console.log(error);
			if (alert_error) alert(`Error: can not load API file for year ${year}`);
		});
}


// =====================================================================================================================

let hold_release_timeout;

title.addEventListener('mouseenter', _ => {
	clearTimeout(hold_release_timeout);
	hold = true;
	// console.log("Hold activated");

	timer_path.getAnimations().map(animation => {
		animation.pause();
		// if (animation.currentTime > timer_duration - hold_delay) {
		animation.currentTime = timer_duration - hold_delay;
		// }
	});
});
title.addEventListener('mouseleave', _ => {
	clearTimeout(hold_release_timeout);
	hold_release_timeout = setTimeout(_ => {
		hold = false;
	}, hold_delay);
	// console.log(`Hold will be deactivated in ${hold_delay / 1000}s`);

	timer_path.getAnimations().map(animation => animation.play());
});

function changeBackground() {
	const chosen_image = api[Math.floor(Math.random() * api.length)];

	const image_path = image_url_prefix + chosen_image["date"] + ".jpg";
	const image_title = chosen_image["title"];

	cur_image.src = image_path;

	setTimeout(_ => {
		waitFor(
			_ => cur_image.complete && !hold,
		).then(_ => {

			// Restart timer animation
			console.log("Starting");
			setTimeout(_ => {
				timer_path.classList.remove("play");
				setTimeout(_ => {
					timer_path.classList.add("play");
				}, transition_delay / 2);
			}, transition_delay / 2);

			// Showing new image
			foreground.style.opacity = (cur_image === foreground ? 1 : 0);

			cur_image = (cur_image === foreground ? background : foreground);

			setTimeout(changeBackground, transition_delay + 50); // 50 just to be safe that animation has finished

			if (document.body.classList.contains("shown")) {

				title.style.opacity = 0;

				setTimeout(_ => {
					title.textContent = image_title;
					title.href = image_path;
					title.style.opacity = 1;
				}, transition_delay / 2);

			} else {
				title.textContent = image_title;
				title.href = image_path;
				document.body.classList.add("shown");
				first_image_loaded = true;

				setTimeout(_ => {
					transition_delay = transition_delay_true;
				}, transition_delay / 2);
			}

		});
	}, (document.body.classList.contains("shown") ? delay - transition_delay - 50 : 0));
}

fetchYear(previous_year, year_api => {
	console.log("Loaded year:", previous_year);
	api = year_api;

	changeBackground();
	// waitFor(
	// 	_ => document.readyState === "complete"
	// ).then(changeBackground);

	waitFor(
		_ => first_image_loaded
	).then(_ => {
		''
		console.log("Loading other years:");

		for (let year = start_date.getFullYear(); year <= end_date.getFullYear(); ++year) {
			if (year === previous_year) continue;
			console.log("Loaded year:", year);

			fetchYear(year, year_api => {
				year_api.forEach(item => {
					if (item["date"] >= date2str(start_date)) api.push(item);
				});
			});
		}

	});
}, alert_error = true);
