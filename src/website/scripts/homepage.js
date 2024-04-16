// ===================================================== SETTINGS ======================================================
const
	REGIONS = [
		'pt-BR',
		'en-CA',
		'fr-CA',
		'fr-FR',
		'de-DE',
		'en-IN',
		'it-IT',
		'ja-JP',
		'zh-CN',
		'es-ES',
		'en-GB',
		'en-US'
	],
	HOMEPAGE_REGION = 'en-US',
	YEAR_API_PATH = (country, lang, year) => `${country.toUpperCase()}/${lang.toLowerCase()}.${year}.json`,
	START_DATE = new Date(2017, 2, 1), // 2017-03-01: 1080p images start here

	HOMEPAGE_DELAY = 5000, // Delay between homepage images, doess not include transition time

	SCROLL_THRESHOLD = 66, // Scroll to the top if less than this value
	SCROLL_DELAY = 2000; // Delay before automatic scroll

// =====================================================================================================================

const
	YESTERDAY = (d => new Date(d.setDate(d.getDate() - 1)))(new Date), // Yesterday
	PREVIOUS_YEAR = YESTERDAY.getFullYear() - 1, // Previous year to avoid having only one image on January 1st

	homepage_background = document.getElementById("background"),
	homepage_foreground = document.getElementById("foreground"),
	// timer_path = document.getElementById("timer_path"),
	title = document.getElementById("title"),
	title_background = document.querySelector("#title > div"),
	title_texts = document.querySelectorAll("#title span");

// transition_delay_initial = 200, // Initial delay before showing first image
// transition_delay_true = 1000,
// delay = 5000,
// hold_delay = 3000,
// timer_duration = delay - transition_delay_true,

// homepage_image_transition_duration = parseFloat(getComputedStyle(homepage_foreground)["transitionDuration"]);

// timer_path.style.animationDuration = `${(timer_duration) / 1000}s`;

// var hold = false;

var cur_image = foreground, // Either background or foreground: image shown at the moment
	next_image = background;

// ==================================================== Api storage ====================================================

class Region {
	constructor(region) {
		[this.lang, this.country] = region.split('-');
		this.images = new Map();
		this.dates = [];
	}

	add(date, item) {
		if (!this.images.has(date)) {
			this.dates.push(date);
		}
		this.images.set(date, item);
	}

	addAll(items) {
		items.forEach(item => this.add(item["date"], item));
	}

	get(date) {
		return this.images.get(date);
	}

	getRandom() {
		return this.images.get(this.dates[Math.floor(Math.random() * this.dates.length)]);
	}

	fetchYear(year, callback = function() {}, alert_error = false) {
		let api_path = YEAR_API_PATH(this.country, this.lang, year);
		fetch(api_path, {
				method: "GET",
				headers: {
					"Content-Type": "application/json"
				},
				mode: "same-origin"
			})
			.then(response => {
				if (response.ok) {
					console.log(`Loaded year: ${year}`);
					return response.json();
				} else {
					throw new Error(`Error: can not load API file: ${api_path}`);
				}
			})
			.then(data => {
				this.addAll(data);
				callback();
			})
			.catch(error => {
				console.log(error);
				if (alert_error) alert(`Error: can not load API file: ${api_path}`);
			});
	}

}

const api = new Map();
REGIONS.forEach(region => api.set(region, new Region(region)));

// =====================================================================================================================

// function random(min, max) {
// 	return Math.random() * (max - min) + min;
// }

// function randomDate(from, to) {
// 	return new Date(random(from.getTime(), to.getTime()));
// }

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

// function reflow(element) {
// 	void(element.offsetHeight);
// }

// function wait_func(func, callback, interval = 20) {
//     (async _ => {
//         while (!func()) await new Promise(resolve => setTimeout(resolve, interval));
//         callback();
//     })();
// }

// =============================================== Waiting functionality ===============================================

// var Timer = function(delay, callback) {
//     var timerId, start, remaining = delay;

//     this.pause = function() {
//         clearTimeout(timerId);
//         timerId = null;
//         remaining -= Date.now() - start;
//     };

//     this.resume = function() {
//         if (timerId) {
//             return;
//         }

//         start = Date.now();
//         timerId = setTimeout(callback, remaining);
//     };

//     this.resume();
// };

function waitFor(conditionFunction, interval = 50) {
	const poll = resolve => {
		if (conditionFunction()) resolve();
		else setTimeout(_ => poll(resolve), interval);
	}
	return new Promise(poll);
}

function waitAnimations(element, property, value) {
	return new Promise(resolve => {
		element.style[property] = value;
		const transitionEnded = animation => {
			if (animation.propertyName !== property) return;
			element.removeEventListener('transitionend', transitionEnded);
			resolve();
		}
		element.addEventListener('transitionend', transitionEnded);
	});
}

function wait(delay) {
	return new Promise(resolve => setTimeout(resolve, delay));
}

// =====================================================================================================================

// let hold_release_timeout;

// title.addEventListener('mouseenter', _ => {
// 	clearTimeout(hold_release_timeout);
// 	hold = true;
// 	// console.log("Hold activated");

// 	timer_path.getAnimations().map(animation => {
// 		animation.pause();
// 		// if (animation.currentTime > timer_duration - hold_delay) {
// 		animation.currentTime = timer_duration - hold_delay;
// 		// }
// 	});
// });
// title.addEventListener('mouseleave', _ => {
// 	clearTimeout(hold_release_timeout);
// 	hold_release_timeout = setTimeout(_ => {
// 		hold = false;
// 	}, hold_delay);
// 	// console.log(`Hold will be deactivated in ${hold_delay / 1000}s`);

// 	timer_path.getAnimations().map(animation => animation.play());
// });

let homepage_change_timer;

function changeHomepage() {
	const chosen_image = api.get(HOMEPAGE_REGION).getRandom();
	// console.log(chosen_image);

	next_image.src = chosen_image["url"];

	waitFor(_ => !document.hidden).then(_ => {
		wait(HOMEPAGE_DELAY).then(_ => {
			waitFor(_ => next_image.complete).then(_ => {

				// Restart timer animation
				// setTimeout(_ => {
				// 	timer_path.classList.remove("play");
				// 	setTimeout(_ => {
				// 		timer_path.classList.add("play");
				// 	}, transition_delay / 2);
				// }, transition_delay / 2);

				waitAnimations(foreground, "opacity", (next_image === foreground ? 1 : 0))
					.then(_ => {
						[cur_image, next_image] = [next_image, cur_image]; // Swap images
						changeHomepage();
					});

				waitAnimations(title, "opacity", 0).then(_ => {
					title_texts.forEach(span => span.textContent = chosen_image["title"]);
					title.href = chosen_image["url"];
					title.style.opacity = 1;
				});
			});
		});
	});
}

window.addEventListener('load', _ => {
	document.body.classList.add("shown");
});

api.get(HOMEPAGE_REGION).fetchYear(PREVIOUS_YEAR, () => {

	waitFor(_ => document.body.classList.contains("shown")).then(changeHomepage);

	for (let year = START_DATE.getFullYear(); year <= YESTERDAY.getFullYear(); ++year) {
		if (year === PREVIOUS_YEAR) continue;

		api.get(HOMEPAGE_REGION).fetchYear(year);
	}
}, alert_error = true);


// ================================================ Automatic scrolling ================================================

let auto_scroll_timeout;

window.addEventListener("scroll", _ => {
	clearTimeout(auto_scroll_timeout);
	let scroll = window.scrollY;

	if (scroll > 0) {
		title_background.style.opacity = 1;
	} else {
		title_background.style.opacity = "";
	}

	if (scroll < 66) {
		auto_scroll_timeout = setTimeout(_ => {
			window.scroll({
				top: 0,
				left: 0,
				behavior: "smooth"
			});
		}, SCROLL_DELAY);
	}
});
