// ===================================================== SETTINGS ======================================================
const
	REGIONS: string[] = [
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
	HOMEPAGE_REGION: string = 'en-US',
	YEAR_API_PATH = (country: string, lang: string, year: number): string => `${country.toUpperCase()}/${lang.toLowerCase()}.${year}.json`,
	START_DATE: Date = new Date(2017, 2, 1), // 2017-03-01: 1080p images start here

	HOMEPAGE_DELAY: number = 5000, // Delay between homepage images does not include transition time

	SCROLL_THRESHOLD: number = 66, // Scroll to the top if less than this value
	SCROLL_DELAY: number = 2000; // Delay before automatic scroll

// =====================================================================================================================

interface ImageEntry {
	date: string;
	url: string;
	title: string;

	[key: string]: any;
}

const
	YESTERDAY: Date = (d => new Date(d.setDate(d.getDate() - 1)))(new Date), // Yesterday
	PREVIOUS_YEAR: number = YESTERDAY.getFullYear() - 1, // Previous year to avoid having only one image on January 1st

	homepage_background = document.querySelector<HTMLImageElement>("#background")!,
	homepage_foreground = document.querySelector<HTMLImageElement>("#foreground")!,
	// timer_path = document.querySelector("#timer_path"),
	title = document.querySelector<HTMLAnchorElement>("#title")!,
	title_background = document.querySelector<HTMLElement>("#title_background")!,
	title_texts = document.querySelectorAll<HTMLSpanElement>("#title span"),

	content_area = document.querySelector<HTMLElement>("#content")!,

	markets_wrapper = document.querySelector<HTMLElement>("#markets_wrapper")!,
	markets = document.querySelector<HTMLElement>("#markets")!,
	markets_items = document.querySelectorAll<HTMLAnchorElement>("#markets a"),
	markets_toggle = document.querySelector<HTMLInputElement>("#markets_menu")!,

	cur_image = document.querySelector<HTMLElement>("#cur_image")!,
	cur_image_title = document.querySelector<HTMLElement>("#cur_image_title")!,
	cur_image_description = document.querySelector<HTMLElement>("#cur_image_description")!;

// transition_delay_initial = 200, // Initial delay before showing the first image
// transition_delay_true = 1000,
// delay = 5000,
// hold_delay = 3000,
// timer_duration = delay - transition_delay_true,

// homepage_image_transition_duration = parseFloat(getComputedStyle(homepage_foreground)["transitionDuration"]);

// timer_path.style.animationDuration = `${(timer_duration) / 1000}s`;

// let hold = false;

let cur_homepage: HTMLImageElement | null = homepage_foreground, // Either background or foreground: image shown at the moment
	next_homepage: HTMLImageElement | null = homepage_background;

// ==================================================== Api storage ====================================================

class Region {
	lang: string;
	country: string;
	images: Map<string, ImageEntry>;
	dates: string[];

	constructor(region: string) {
		[this.lang, this.country] = region.split('-');
		this.images = new Map<string, ImageEntry>();
		this.dates = [];
	}

	add(date: string, item: ImageEntry) {
		if (!this.images.has(date)) {
			this.dates.push(date);
		}
		this.images.set(date, item);
	}

	addAll(items: ImageEntry[]) {
		items.forEach(item => this.add(item["date"], item));
	}

	get(date: string): ImageEntry | undefined {
		return this.images.get(date);
	}

	getRandom(): ImageEntry | undefined {
		return this.images.get(this.dates[Math.floor(Math.random() * this.dates.length)]);
	}

	fetchYear(year: number, callback: () => void = function () {}, alert_error: boolean = false) {
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
			.then((data: ImageEntry[]) => {
				this.addAll(data);
				callback();
			})
			.catch(error => {
				console.log(error);
				if (alert_error) alert(`Error: can not load API file: ${api_path}`);
			});
	}

}

const api = new Map<string, Region>();
REGIONS.forEach(region => api.set(region, new Region(region)));

// =====================================================================================================================

// function random(min, max) {
// 	return Math.random() * (max - min) + min;
// }

// function randomDate(from, to) {
// 	return new Date (random(from.getTime(), to.getTime()));
// }

function leadingZeros(s: string | number, totalDigits: number): string {
	s = s.toString();
	let res = "";
	for (let i = 0; i < (totalDigits - s.length); ++i) res += "0";
	return res + s.toString();
}

function date2str(date: Date): string {
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

// const Timer = function(delay, callback) {
//     let timerId, start, remaining = delay;

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

function waitFor(conditionFunction: () => boolean, interval: number = 50): Promise<void> {
	const poll = (resolve: (value: void | PromiseLike<void>) => void) => {
		if (conditionFunction()) resolve();
		else setTimeout(() => poll(resolve), interval);
	}
	return new Promise(poll);
}

function waitAnimations(element: HTMLElement, property: string, value: string | number): Promise<void> { // TODO rewrite + remove .style
	return new Promise(resolve => {
		(element.style as any)[property] = value;
		const transitionEnded = (animation: TransitionEvent) => {
			if (animation.propertyName !== property) return;
			element.removeEventListener('transitionend', transitionEnded);
			resolve();
		}
		element.addEventListener('transitionend', transitionEnded);
	});
}

function wait(delay: number): Promise<void> {
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

let homepage_change_timer: any;

function changeHomepage() {
	const chosen_image = api.get(HOMEPAGE_REGION)!.getRandom()!;
	// console.log(chosen_image);

	next_homepage!.src = chosen_image["url"];
	next_homepage!.alt = chosen_image["title"];
	next_homepage!.title = chosen_image["title"];

	waitFor(() => !document.hidden && window.scrollY < window.innerHeight).then(_ => {
		console.log("Changing image soon");
		wait(HOMEPAGE_DELAY).then(_ => {
			waitFor(() => next_homepage!.complete).then(_ => {

				// Restart timer animation
				// setTimeout(_ => {
				// 	timer_path.classList.remove("play");
				// 	setTimeout(_ => {
				// 		timer_path.classList.add("play");
				// 	}, transition_delay / 2);
				// }, transition_delay / 2);

				waitAnimations(homepage_foreground, "opacity", (next_homepage === homepage_foreground ? 1 : 0))
					.then(_ => {
						[cur_homepage, next_homepage] = [next_homepage, cur_homepage]; // Swap images
						changeHomepage();
					});

				waitAnimations(title, "opacity", 0).then(_ => {
					title_texts.forEach(span => span.textContent = chosen_image["title"]);
					title.href = chosen_image["url"];

					title.classList.toggle("fullwidth", title.getBoundingClientRect().left == 0);

					title.style.opacity = '1';
				});
			});
		});
	});
}

api.get(HOMEPAGE_REGION)!.fetchYear(PREVIOUS_YEAR, () => {

	waitFor(() => document.body.classList.contains("shown")).then(changeHomepage);

	for (let year = START_DATE.getFullYear(); year <= YESTERDAY.getFullYear(); ++year) {
		if (year === PREVIOUS_YEAR) continue;

		api.get(HOMEPAGE_REGION)!.fetchYear(year);
	}
}, true);


// ===================================================== Scrolling =====================================================

let auto_scroll_timeout: any;
let last_scroll: number = window.scrollY;

enum NAVIGATION_STATUS {
	MAX_TOP,
	FIXED_TOP,
	FIXED_BOTTOM,
	FLOATING
}

let navigation_status: NAVIGATION_STATUS = NAVIGATION_STATUS.MAX_TOP;

function handle_scroll() {
	clearTimeout(auto_scroll_timeout);
	let scroll = window.scrollY;

	// -------------------------------- Title background --------------------------------

	title_background.classList.toggle("always_visible", scroll > 0);

	// -------------------------------- Sticky navigation -------------------------------

	let navigation_block_pos = markets.getBoundingClientRect();
	let relative_pos = navigation_block_pos.top - content_area.getBoundingClientRect().top;

	let new_position: string = "",
		new_top: string = "";
	let old_status: NAVIGATION_STATUS | null = null,
		new_status: NAVIGATION_STATUS = navigation_status;

	while (old_status != new_status) {
		old_status = new_status;

		if (scroll >= last_scroll) { // Scrolling down
			switch (old_status) {
				case NAVIGATION_STATUS.MAX_TOP:
				case NAVIGATION_STATUS.FLOATING:
					if (navigation_block_pos.top <= 86 && navigation_block_pos.bottom <= window.innerHeight) {
						// console.log("Changing navbar to FIXED_BOTTOM:", Math.min(86, window.innerHeight - navigation_block_pos.height) + "px");
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
		auto_scroll_timeout = setTimeout(() => {
			window.scroll({
				top: 0,
				left: 0,
				behavior: "smooth"
			});
		}, SCROLL_DELAY);

	} else if (scroll < window.innerHeight) {
		auto_scroll_timeout = setTimeout(() => {
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


function change_market(market: string = HOMEPAGE_REGION) {
	markets_items.forEach(selector => {
		selector.classList.toggle("active", selector.getAttribute("data-mkt") == market);
	});
}

change_market();

window.addEventListener("hashchange", () => {
	let market = window.location.hash.slice(1);
	if (REGIONS.indexOf(market) === -1) {
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
	markets_toggle.checked = window.innerWidth > 950;
	toggle_market_selector();
}

markets_toggle.addEventListener('change', toggle_market_selector);
window.addEventListener("resize", toggle_market_selector_by_screen_size);
toggle_market_selector_by_screen_size();


// ================================================= Page fully loaded =================================================

window.addEventListener('load', () => {
	document.body.classList.add("shown");
});
