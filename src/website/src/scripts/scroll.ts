import { AUTOSCROLL_DELAY } from './constants';
import { contentArea, markets, title } from './elements';

let autoScrollTimeout: any
let lastScroll: number = window.scrollY

enum NavigationStatus {
	MAX_TOP,
	FIXED_TOP,
	FIXED_BOTTOM,
	FLOATING
}

let navigationStatus: NavigationStatus = NavigationStatus.MAX_TOP

export function updateHomepageAutoscroll(scroll: number = window.scrollY) {
	clearTimeout(autoScrollTimeout)
	const window_height = window.innerHeight

	if (scroll * 2 < window_height) {
		autoScrollTimeout = setTimeout(() => {
			window.scroll({
				top: 0,
				behavior: 'smooth'
			})
		}, AUTOSCROLL_DELAY)

	} else if (scroll < window_height) {
		autoScrollTimeout = setTimeout(() => {
			window.scroll({
				top: window_height + 1,
				behavior: 'smooth'
			})
		}, AUTOSCROLL_DELAY)
	}
}

export function handleScroll() {
	const scroll = window.scrollY

	updateHomepageAutoscroll(scroll)

	// ---------- Title background ----------

	title.classList.toggle('permanent_hover', scroll > 0)

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
						newStatus = NavigationStatus.FIXED_BOTTOM
						newPosition = 'fixed'
						newTop = Math.min(106, window.innerHeight - navigationBlockPos.height) + 'px'
					}
					break

				case NavigationStatus.FIXED_TOP:
					newStatus = NavigationStatus.FLOATING
					newPosition = 'absolute'
					newTop = relativePos + 'px'
					break
			}

		} else { // Scrolling up
			switch (oldStatus) {
				case NavigationStatus.FIXED_TOP:
					if (relativePos <= 106) {
						newStatus = NavigationStatus.MAX_TOP
						newPosition = 'absolute'
						newTop = '106px'
					}
					break

				case NavigationStatus.FIXED_BOTTOM:
					newStatus = NavigationStatus.FLOATING
					newPosition = 'absolute'
					newTop = relativePos + 'px'
					break

				case NavigationStatus.FLOATING:
					if (navigationBlockPos.top >= 106) {
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
			markets.style.position = newPosition
		}
		if (markets.style.top != newTop) {
			markets.style.top = newTop
		}
	}

	navigationStatus = newStatus
	lastScroll = scroll
}

export function initScroll() {
	window.addEventListener('scroll', handleScroll, { passive: true })
	window.addEventListener('resize', handleScroll, { passive: true })

	window.addEventListener('touchstart', () => updateHomepageAutoscroll(), { passive: true });
	window.addEventListener('touchmove', () => updateHomepageAutoscroll(), { passive: true });
	window.addEventListener('mousedown', () => updateHomepageAutoscroll());
	window.addEventListener('mousemove', (e: MouseEvent) => {
		if (e.buttons > 0) {
			updateHomepageAutoscroll();
		}
	}, { passive: true });
}
