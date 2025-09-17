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
		'en-US',
		'en-ROW'
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

	homepage_background = document.querySelector("#background"),
	homepage_foreground = document.querySelector("#foreground"),
	// timer_path = document.querySelector("#timer_path"),
	title = document.querySelector("#title"),
	title_background = document.querySelector("#title_background"),
	title_texts = document.querySelectorAll("#title span"),

	content_area = document.querySelector("#content"),

	markets_wrapper = document.querySelector("#markets_wrapper"),
	markets = document.querySelector("#markets"),
	markets_items = document.querySelectorAll("#markets a"),
	markets_toggle = document.querySelector("#markets_menu"),

	cur_image = document.querySelector("#cur_image"),
	cur_image_title = document.querySelector("#cur_image_title"),
	cur_image_description = document.querySelector("#cur_image_description");

// transition_delay_initial = 200, // Initial delay before showing first image
// transition_delay_true = 1000,
// delay = 5000,
// hold_delay = 3000,
// timer_duration = delay - transition_delay_true,

// homepage_image_transition_duration = parseFloat(getComputedStyle(homepage_foreground)["transitionDuration"]);

// timer_path.style.animationDuration = `${(timer_duration) / 1000}s`;

// var hold = false;

var cur_homepage = foreground, // Either background or foreground: image shown at the moment
	next_homepage = background;

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

function waitAnimations(element, property, value) { // TODO rewrite + remove .style
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

	next_homepage.src = chosen_image["url"];
	next_homepage.alt = chosen_image["title"];
	next_homepage.title = chosen_image["title"];

	waitFor(_ => !document.hidden && window.scrollY < window.innerHeight).then(_ => {
		console.log("Changing image soon");
		wait(HOMEPAGE_DELAY).then(_ => {
			waitFor(_ => next_homepage.complete).then(_ => {

				// Restart timer animation
				// setTimeout(_ => {
				// 	timer_path.classList.remove("play");
				// 	setTimeout(_ => {
				// 		timer_path.classList.add("play");
				// 	}, transition_delay / 2);
				// }, transition_delay / 2);

				waitAnimations(foreground, "opacity", (next_homepage === foreground ? 1 : 0))
					.then(_ => {
						[cur_homepage, next_homepage] = [next_homepage, cur_homepage]; // Swap images
						changeHomepage();
					});

				waitAnimations(title, "opacity", 0).then(_ => {
					title_texts.forEach(span => span.textContent = chosen_image["title"]);
					title.href = chosen_image["url"];

					title.classList.toggle("fullwidth", title.getBoundingClientRect().left == 0);

					title.style.opacity = 1;
				});
			});
		});
	});
}

api.get(HOMEPAGE_REGION).fetchYear(PREVIOUS_YEAR, () => {

	waitFor(_ => document.body.classList.contains("shown")).then(changeHomepage);

	for (let year = START_DATE.getFullYear(); year <= YESTERDAY.getFullYear(); ++year) {
		if (year === PREVIOUS_YEAR) continue;

		api.get(HOMEPAGE_REGION).fetchYear(year);
	}
}, alert_error = true);


// ===================================================== Scrolling =====================================================

let auto_scroll_timeout;
let last_scroll = window.scrollY;

const NAVIGATION_STATUS = {
	MAX_TOP: 0,
	FIXED_TOP: 1,
	FIXED_BOTTOM: 2,
	FLOATING: 3
};

let navigation_status = NAVIGATION_STATUS.MAX_TOP;

function handle_scroll() {
	clearTimeout(auto_scroll_timeout);
	let scroll = window.scrollY;

	// -------------------------------- Title background --------------------------------

	title_background.classList.toggle("always_visible", scroll > 0);

	// -------------------------------- Sticky navigation -------------------------------

	let navigation_block_pos = markets.getBoundingClientRect();
	let relative_pos = navigation_block_pos.top - content_area.getBoundingClientRect().top;

	let new_position = "",
		new_top = "";
	let old_status = null,
		new_status = navigation_status;

	while (old_status != new_status) {
		old_status = new_status;

		if (scroll >= last_scroll) { // Scrolling down
			switch (old_status) {
				case NAVIGATION_STATUS.MAX_TOP:
				case NAVIGATION_STATUS.FLOATING:
					if (navigation_block_pos.top <= 86 && navigation_block_pos.bottom <= window.innerHeight) {
						// console.log("Changing navbar to FIXED_BOTTOM:",  Math.min(86, window.innerHeight - navigation_block_pos.height) + "px");
						new_status = NAVIGATION_STATUS.FIXED_BOTTOM;
						new_position = "fixed";
						new_top = Math.min(86, window.innerHeight - navigation_block_pos.height) + "px";
					}
					break;

				case NAVIGATION_STATUS.FIXED_TOP:
					// console.log("Changing navbar to FLOATING:", relative_pos + "px");
					new_status = NAVIGATION_STATUS.FLOATING;
					new_position = "absolute";
					new_top = relative_pos + "px";
					break;
			}

		} else { // Scrolling up
			switch (old_status) {
				case NAVIGATION_STATUS.FIXED_TOP:
					if (relative_pos <= 86) {
						// console.log("Changing navbar to MAX_TOP:", "86px");
						new_status = NAVIGATION_STATUS.MAX_TOP;
						new_position = "absolute";
						new_top = "86px";
					}
					break;

				case NAVIGATION_STATUS.FIXED_BOTTOM:
					// console.log("Changing navbar to FLOATING:", relative_pos + "px");
					new_status = NAVIGATION_STATUS.FLOATING;
					new_position = "absolute";
					new_top = relative_pos + "px";
					break;

				case NAVIGATION_STATUS.FLOATING:
					if (navigation_block_pos.top >= 86) {
						// console.log("Changing navbar to FIXED_TOP:", "86px");
						new_status = NAVIGATION_STATUS.FIXED_TOP;
						new_position = "fixed";
						new_top = "86px";
					}
					break;
			}
		}
	}

	if (new_status != navigation_status) {
		if (markets.style.position != new_position) {
			// console.log("Changing position to", new_position);
			markets.style.position = new_position;
		}
		if (markets.style.top != new_top) {
			// console.log("Changing top to", new_top);
			markets.style.top = new_top;
		}
	}

	navigation_status = new_status;
	last_scroll = scroll;

	// ----------------------------------- Autoscroll -----------------------------------

	if (scroll * 2 < window.innerHeight) {
		auto_scroll_timeout = setTimeout(_ => {
			window.scroll({
				top: 0,
				left: 0,
				behavior: "smooth"
			});
		}, SCROLL_DELAY);

	} else if (scroll < window.innerHeight) {
		auto_scroll_timeout = setTimeout(_ => {
			window.scroll({
				top: window.innerHeight,
				left: 0,
				behavior: "smooth"
			});
		}, SCROLL_DELAY);
	}
}

window.addEventListener("scroll", handle_scroll);
window.addEventListener("resize", handle_scroll);

// ====================================================== Markets ======================================================


function change_market(market = HOMEPAGE_REGION) {
	markets_items.forEach(selector => {
		selector.classList.toggle("active", selector.getAttribute("data-mkt") == market);
	});
}

change_market();

window.addEventListener("hashchange", _ => {
	let market = window.location.hash.slice(1);
	if (!REGIONS.includes(market)) {
		console.log(`Invalid market specified in URL hash: ${market}`);
	} else {
		change_market(market);
	}
});

// ================================================== Market selector ==================================================

function toggle_market_selector() {
	markets.classList.toggle("hidden", !markets_toggle.checked);
	markets_wrapper.classList.toggle("hidden", !markets_toggle.checked);
}

function toggle_market_selector_by_screen_size() {
	if (window.innerWidth <= 950) {
		markets_toggle.checked = false;
	} else {
		markets_toggle.checked = true;
	}
	toggle_market_selector();
}

markets_toggle.addEventListener('change', toggle_market_selector);
window.addEventListener("resize", toggle_market_selector_by_screen_size);
toggle_market_selector_by_screen_size();


// ================================================= Page fully loaded =================================================

window.addEventListener('load', _ => {
	document.body.classList.add("shown");
});
