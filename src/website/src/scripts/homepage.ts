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

	HOMEPAGE_DELAY: number = 5000, // Delay between homepage images. Does not include transition time

	AUTOSCROLL_DELAY: number = 2000 // Delay before automatic scroll

// =====================================================================================================================

interface ImageEntry {
	date: string
	url: string
	title: string

	[key: string]: any
}

const YESTERDAY: Date = (d => new Date(d.setDate(d.getDate() - 1)))(new Date) // Yesterday
const PREVIOUS_YEAR: number = YESTERDAY.getFullYear() - 1 // Previous year to avoid having only one image on January 1st

const homepageBackground = document.querySelector<HTMLImageElement>('#background')!
const homepageForeground = document.querySelector<HTMLImageElement>('#foreground')!
// const timer_path = document.querySelector('#timer_path')
const title = document.querySelector<HTMLAnchorElement>('#title')!
const titleBackground = document.querySelector<HTMLElement>('#title_background')!
const titleTexts = document.querySelectorAll<HTMLSpanElement>('#title span')

const contentArea = document.querySelector<HTMLElement>('#content')!

const marketsWrapper = document.querySelector<HTMLElement>('#markets_wrapper')!
const markets = document.querySelector<HTMLElement>('#markets')!
const marketsItems = document.querySelectorAll<HTMLAnchorElement>('#markets a')
const marketsToggle = document.querySelector<HTMLInputElement>('#markets_menu')!

const curImageReal = document.querySelector<HTMLImageElement>('#cur_image_real')!
const curImageInitial = document.querySelector<HTMLImageElement>('#cur_image_initial')!
// const cur_image_title = document.querySelector<HTMLElement>('#cur_image_title')!
// const cur_image_description = document.querySelector<HTMLElement>('#cur_image_description')!

// cur_image_title = document.querySelector<HTMLElement>('#cur_image_title')!
// cur_image_description = document.querySelector<HTMLElement>('#cur_image_description')!

// transition_delay_initial = 200, // Initial delay before showing the first image
// transition_delay_true = 1000,
// delay = 5000,
// hold_delay = 3000,
// timer_duration = delay - transition_delay_true,

// homepage_image_transition_duration = parseFloat(getComputedStyle(homepage_foreground)['transitionDuration'])

// timer_path.style.animationDuration = `${(timer_duration) / 1000}s`

// let hold = false

let curHomepageImage: HTMLImageElement = homepageForeground, // Either background or foreground: image shown at the moment
	nextHomepageImage: HTMLImageElement = homepageBackground

// ======================================================= Fonts =======================================================

async function loadFullFonts() {
	try {
		const fontsToLoad = [
			// {weight: '300', name: 'MiSans-Light'},
			{weight: '400', name: 'MiSans-Regular'},
			// {weight: '700', name: 'MiSans-Bold'},
		]

		const fontPromises = fontsToLoad.map(fontInfo => {
			const fontFace = new FontFace(
				'Mi Sans',
				`url(fonts/MiSans/${fontInfo.name}.woff2) format('woff2'),
				 url(fonts/MiSans/${fontInfo.name}.woff) format('woff')`,
				{
					weight: fontInfo.weight,
					style: 'normal',
					display: 'swap',
				},
			)
			return fontFace.load()
		})

		const loadedFonts = await Promise.all(fontPromises)

		loadedFonts.forEach(font => (document.fonts as any).add(font))

		console.log('Full Mi Sans font loaded and activated.')

	} catch (error) {
		console.error('Failed to load and activate full Mi Sans font:', error)
	}
}

// ==================================================== Api storage ====================================================

class Region {
	lang: string
	country: string
	images: Map<string, ImageEntry>
	dates: string[]

	constructor(region: string) {
		[this.lang, this.country] = region.split('-')
		this.images = new Map<string, ImageEntry>()
		this.dates = []
	}

	add(date: string, item: ImageEntry) {
		if (!this.images.has(date)) {
			this.dates.push(date)
		}
		this.images.set(date, item)
	}

	addAll(items: ImageEntry[]) {
		items.forEach(item => this.add(item['date'], item))
	}

	get(date: string): ImageEntry | undefined {
		return this.images.get(date)
	}

	getRandom(): ImageEntry | undefined {
		return this.images.get(this.dates[Math.floor(Math.random() * this.dates.length)])
	}

	async fetchYear(year: number, alertError: boolean = false): Promise<void> {
		const apiPath = YEAR_API_PATH(this.country, this.lang, year)
		try {
			const response = await fetch(apiPath, {
				method: 'GET',
				headers: {
					'Content-Type': 'application/json'
				},
				mode: 'same-origin'
			})

			if (response.ok) {
				console.log(`Loaded year: ${year}`)
				this.addAll(await response.json())
			} else {
				const error = new Error(`Error: can not load API file (HTTP ${response.status}): ${apiPath}`)
				console.log(error)
				if (alertError) {
					alert(error.message)
				}
			}
		} catch (error) {
			console.log(error)
			if (alertError) {
				alert(`Error: can not load API file: ${apiPath}`)
			}
		}
	}
}

const apiByRegion = new Map<string, Region>()
REGIONS.forEach(region => apiByRegion.set(region, new Region(region)))

// =====================================================================================================================

// function random(min, max) {
// 	return Math.random() * (max - min) + min
// }

// function randomDate(from, to) {
// 	return new Date (random(from.getTime(), to.getTime()))
// }

// function leadingZeros(s: string | number, totalDigits: number): string {
// 	s = s.toString()
// 	let res = ''
// 	for (let i = 0; i < (totalDigits - s.length); ++i) res += '0'
// 	return res + s.toString()
// }

// function date2str(date: Date): string {
// 	return leadingZeros(date.getFullYear(), 4) +
// 		'-' + leadingZeros(date.getMonth() + 1, 2) +
// 		'-' + leadingZeros(date.getDate(), 2)
// }

// function reflow(element) {
// 	void(element.offsetHeight)
// }

// function wait_func(func, callback, interval = 20) {
//     (async _ => {
//         while (!func()) await new Promise(resolve => setTimeout(resolve, interval))
//         callback()
//     })()
// }

// =============================================== Waiting functionality ===============================================

// const Timer = function(delay, callback) {
//     let timerId, start, remaining = delay

//     this.pause = function() {
//         clearTimeout(timerId)
//         timerId = null
//         remaining -= Date.now() - start
//     }

//     this.resume = function() {
//         if (timerId) {
//             return
//         }

//         start = Date.now()
//         timerId = setTimeout(callback, remaining)
//     }

//     this.resume()
// }

async function waitFor(conditionFunction: () => boolean, interval: number = 50): Promise<void> {
	while (!conditionFunction()) {
		await wait(interval)
	}
}

function waitAnimations(element: HTMLElement, property: string, value: string | number): Promise<void> { // TODO rewrite + remove .style
	return new Promise(resolve => {
		(element.style as any)[property] = value
		const transitionEnded = (animation: TransitionEvent) => {
			if (animation.propertyName !== property) return
			element.removeEventListener('transitionend', transitionEnded)
			resolve()
		}
		element.addEventListener('transitionend', transitionEnded)
	})
}

function wait(delay: number): Promise<void> {
	return new Promise(resolve => setTimeout(resolve, delay))
}

// =====================================================================================================================

// let hold_release_timeout

// title.addEventListener('mouseenter', _ => {
// 	clearTimeout(hold_release_timeout)
// 	hold = true
// 	// console.log('Hold activated')

// 	timer_path.getAnimations().map(animation => {
// 		animation.pause()
// 		// if (animation.currentTime > timer_duration - hold_delay) {
// 		animation.currentTime = timer_duration - hold_delay
// 		// }
// 	})
// })
// title.addEventListener('mouseleave', _ => {
// 	clearTimeout(hold_release_timeout)
// 	hold_release_timeout = setTimeout(_ => {
// 		hold = false
// 	}, hold_delay)
// 	// console.log(`Hold will be deactivated in ${hold_delay / 1000}s`)

// 	timer_path.getAnimations().map(animation => animation.play())
// })

// let homepageChangeTimer: any

async function changeHomepage() {
	const chosenImage = apiByRegion.get(HOMEPAGE_REGION)!.getRandom()!
	// console.log(chosen_image)

	nextHomepageImage.src = chosenImage['url']
	nextHomepageImage.alt = chosenImage['title']

	await waitFor(() => document.visibilityState === 'visible' && window.scrollY < window.innerHeight)

	console.log('Changing image soon')
	await wait(HOMEPAGE_DELAY)

	await waitFor(() => nextHomepageImage.complete)

	// Restart timer animation
	// setTimeout(_ => {
	// 	timer_path.classList.remove('play')
	// 	setTimeout(_ => {
	// 		timer_path.classList.add('play')
	// 	}, transition_delay / 2)
	// }, transition_delay / 2)

	waitAnimations(homepageForeground, 'opacity', (nextHomepageImage === homepageForeground ? 1 : 0))
		.then(() => {
			[curHomepageImage, nextHomepageImage] = [nextHomepageImage, curHomepageImage] // Swap images
			changeHomepage()
		})

	waitAnimations(title, 'opacity', 0).then(() => {
		titleTexts.forEach(span => span.textContent = chosenImage['title'])
		title.href = chosenImage['url']

		title.classList.toggle('fullwidth', title.getBoundingClientRect().left == 0)

		title.style.opacity = '1'
	})
}

// =================================================== On page load ====================================================

const domReady = new Promise<void>(resolve => {
	if (document.readyState === 'interactive' || document.readyState === 'complete') {
		return resolve()
	}
	document.addEventListener('DOMContentLoaded', () => resolve(), {once: true})
})

const initialImageLoad = new Promise<void>(resolve => {
	const onImageReady = () => {
		requestAnimationFrame(() => {
			requestAnimationFrame(() => {
				resolve()
			})
		})
	}

	if (homepageForeground.complete) {
		onImageReady()
	} else {
		homepageForeground.addEventListener('load', onImageReady, {once: true})
		homepageForeground.addEventListener('error', onImageReady, {once: true})
	}
})

Promise.all([domReady, document.fonts.ready, initialImageLoad]).then(() => {
	document.body.classList.add('shown')

	console.log('DOM, initial image, and fonts are ready. Website rendered.')

	const highResHomepageUrl = homepageForeground.dataset.realImage!
	nextHomepageImage.src = highResHomepageUrl
	curImageReal.src = highResHomepageUrl;

	(async () => {
		await waitFor(() => nextHomepageImage.complete)
		console.log('Initial image loaded')
		void loadFullFonts()
		await waitAnimations(homepageForeground, 'opacity', 0);
		[curHomepageImage, nextHomepageImage] = [nextHomepageImage, curHomepageImage]

		try {
			await apiByRegion.get(HOMEPAGE_REGION)!.fetchYear(PREVIOUS_YEAR)
		} catch (e) {
			console.log(e)
			alert(String(e))
		}

		void changeHomepage()

		for (let year = START_DATE.getFullYear(); year <= YESTERDAY.getFullYear(); ++year) {
			if (year === PREVIOUS_YEAR) continue
			apiByRegion.get(HOMEPAGE_REGION)!.fetchYear(year).catch(console.log)
		}
	})();

	(async () => {
		await waitFor(() => curImageReal.complete)
		console.log('Current image loaded')
		await waitAnimations(curImageInitial, 'opacity', 0)
		requestAnimationFrame(async () => {
			await wait(1000)
			if (curImageInitial.parentNode) {
				curImageInitial.parentNode.removeChild(curImageInitial)
			}
		})
	})()
})

// ===================================================== Scrolling =====================================================

let autoScrollTimeout: any
let lastScroll: number = window.scrollY

enum NavigationStatus {
	MAX_TOP,
	FIXED_TOP,
	FIXED_BOTTOM,
	FLOATING
}

let navigationStatus: NavigationStatus = NavigationStatus.MAX_TOP

function handleScroll() {
	clearTimeout(autoScrollTimeout)
	let scroll = window.scrollY

	// ---------- Title background ----------

	titleBackground.classList.toggle('always_visible', scroll > 0)

	// ---------- Sticky navigation ----------

	let navigationBlockPos = markets.getBoundingClientRect()
	let relativePos = navigationBlockPos.top - contentArea.getBoundingClientRect().top

	let newPosition: string = '',
		newTop: string = ''
	let oldStatus: NavigationStatus | null = null,
		newStatus: NavigationStatus = navigationStatus

	while (oldStatus != newStatus) {
		oldStatus = newStatus

		if (scroll >= lastScroll) { // Scrolling down
			switch (oldStatus) {
				case NavigationStatus.MAX_TOP:
				case NavigationStatus.FLOATING:
					if (navigationBlockPos.top <= 106 && navigationBlockPos.bottom <= window.innerHeight) {
						// console.log('Changing navbar to FIXED_BOTTOM:', Math.min(106, window.innerHeight - navigation_block_pos.height) + 'px')
						newStatus = NavigationStatus.FIXED_BOTTOM
						newPosition = 'fixed'
						newTop = Math.min(106, window.innerHeight - navigationBlockPos.height) + 'px'
					}
					break

				case NavigationStatus.FIXED_TOP:
					// console.log('Changing navbar to FLOATING:', relative_pos + 'px')
					newStatus = NavigationStatus.FLOATING
					newPosition = 'absolute'
					newTop = relativePos + 'px'
					break
			}

		} else { // Scrolling up
			switch (oldStatus) {
				case NavigationStatus.FIXED_TOP:
					if (relativePos <= 106) {
						// console.log('Changing navbar to MAX_TOP:', '106px')
						newStatus = NavigationStatus.MAX_TOP
						newPosition = 'absolute'
						newTop = '106px'
					}
					break

				case NavigationStatus.FIXED_BOTTOM:
					// console.log('Changing navbar to FLOATING:', relative_pos + 'px')
					newStatus = NavigationStatus.FLOATING
					newPosition = 'absolute'
					newTop = relativePos + 'px'
					break

				case NavigationStatus.FLOATING:
					if (navigationBlockPos.top >= 106) {
						// console.log('Changing navbar to FIXED_TOP:', '106px')
						newStatus = NavigationStatus.FIXED_TOP
						newPosition = 'fixed'
						newTop = '106px'
					}
					break
			}
		}
	}

	if (newStatus != navigationStatus) {
		if (markets.style.position != newPosition) {
			// console.log('Changing position to', new_position)
			markets.style.position = newPosition
		}
		if (markets.style.top != newTop) {
			// console.log('Changing top to', new_top)
			markets.style.top = newTop
		}
	}

	navigationStatus = newStatus
	lastScroll = scroll

	// ---------- Autoscroll ----------

	if (scroll * 2 < window.innerHeight) {
		autoScrollTimeout = setTimeout(() => {
			window.scroll({
				top: 0,
				left: 0,
				behavior: 'smooth'
			})
		}, AUTOSCROLL_DELAY)

	} else if (scroll < window.innerHeight) {
		autoScrollTimeout = setTimeout(() => {
			window.scroll({
				top: window.innerHeight,
				left: 0,
				behavior: 'smooth'
			})
		}, AUTOSCROLL_DELAY)
	}
}

window.addEventListener('scroll', handleScroll)
window.addEventListener('resize', handleScroll)

// ====================================================== Markets ======================================================

function changeMarket(market: string = HOMEPAGE_REGION) {
	marketsItems.forEach(selector => {
		selector.classList.toggle('active', selector.getAttribute('data-mkt') == market)
	})
}

changeMarket()

window.addEventListener('hashchange', () => {
	let market = window.location.hash.slice(1)
	if (REGIONS.indexOf(market) === -1) {
		console.log(`Invalid market specified in URL hash: ${market}`)
	} else {
		changeMarket(market)
	}
})

// ================================================== Market selector ==================================================

function toggleMarketSelector() {
	markets.classList.toggle('hidden', !marketsToggle.checked)
	marketsWrapper.classList.toggle('hidden', !marketsToggle.checked)
}

function toggleMarketSelectorByScreenSize() {
	marketsToggle.checked = window.innerWidth > 950
	toggleMarketSelector()
}

marketsToggle.addEventListener('change', toggleMarketSelector)
window.addEventListener('resize', toggleMarketSelectorByScreenSize)
toggleMarketSelectorByScreenSize()
