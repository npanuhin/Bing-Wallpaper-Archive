import { AUTOSCROLL_DELAY } from './constants';
import { contentArea, header, markets, slideshowTitle, curImageReal, slideshowTitleContainer, slideshowElement } from './elements';

let autoScrollTimeout: any
let slideshowCollapsed: boolean = false
let lastScroll: number = getLogicalScroll()
let slideshowExpandTimeout: any = null
const SLIDESHOW_EXPAND_DELAY = 200
export function getLogicalScroll() {
	return slideshowCollapsed ? window.scrollY + window.innerHeight : window.scrollY
}

enum NavigationStatus {
	MAX_TOP,
	FIXED_TOP,
	FIXED_BOTTOM,
	FLOATING
}

let navigationStatus: NavigationStatus = NavigationStatus.MAX_TOP

export function updateSlideshowAutoscroll(scroll: number = getLogicalScroll()) {
	clearTimeout(autoScrollTimeout)
	if (slideshowCollapsed) return
	const window_height = window.innerHeight
	if (scroll <= 0 || scroll >= window_height) return

	if (scroll * 2 < window_height) {
		// console.log('Autoscrolling to top')
		autoScrollTimeout = setTimeout(() => {
			window.scroll({
				top: 0,
				behavior: 'smooth'
			})
		}, AUTOSCROLL_DELAY)

	} else {
		// console.log('Autoscrolling to bottom')
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
	const windowHeight = window.innerHeight

	const logicalScroll = getLogicalScroll()

	if (logicalScroll < lastScroll) {  // Scrolling up
		// console.log('Scrolling up')
		if (slideshowCollapsed && scroll < windowHeight * 0.05) {  // Higher than %5 of window height
			if (!slideshowExpandTimeout) {
				// console.log('Requesting slideshow expand')
				slideshowExpandTimeout = setTimeout(slideshowExpand, SLIDESHOW_EXPAND_DELAY)
			}
		}
	} else if (logicalScroll > lastScroll) {  // Scrolling down
		// console.log('Scrolling down')
		if (slideshowExpandTimeout) {
			clearTimeout(slideshowExpandTimeout)
			slideshowExpandTimeout = null
		}
		if (!slideshowCollapsed && scroll > windowHeight * 1.05) {  // Lower than %5 of window height
			slideshowCollapse()
			return
		}
	}

	slideshowTitleContainer.style.top = slideshowCollapsed ? '0' : '100vh'

	updateSlideshowAutoscroll(logicalScroll)

	// ---------- Title background ----------

	slideshowTitle.classList.toggle('permanent_hover', logicalScroll > 0)
	slideshowTitleContainer.classList.toggle('has-shadow', logicalScroll > 0)
	contentArea.classList.toggle('has-shadow', logicalScroll > 0)

	// ---------- Header shadow ----------

	const headerBottom = header.getBoundingClientRect().bottom
	const curImageTop = curImageReal.getBoundingClientRect().top
	header.classList.toggle('has-shadow', curImageTop <= headerBottom)

	// ---------- Sticky navigation ----------

	let navigationBlockPos = markets.getBoundingClientRect()
	let relativePos = navigationBlockPos.top - contentArea.getBoundingClientRect().top

	let newPosition: string = '',
		newTop: string = ''
	let oldStatus: NavigationStatus | null = null,
		newStatus: NavigationStatus = navigationStatus

	while (oldStatus != newStatus) {
		oldStatus = newStatus

		if (logicalScroll >= lastScroll) { // Scrolling down  // TODO: is == needed?
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
	lastScroll = logicalScroll
}

function slideshowExpand() {   // When scrolling up
	// console.log('Expanding slideshow')
	requestAnimationFrame(() => {
		const newScroll = window.scrollY + window.innerHeight;
		slideshowElement.style.marginTop = '0'
		slideshowTitleContainer.style.top = '100vh'
		window.scrollTo({ left: 0, top: newScroll, behavior: 'instant' })
		// handleScroll()
		slideshowCollapsed = false
	})
}

function slideshowCollapse() {  // When scrolling down
	// console.log('Collapsing slideshow')
	requestAnimationFrame(() => {
		const newScroll = window.scrollY - window.innerHeight
		slideshowElement.style.marginTop = '-100vh'
		slideshowTitleContainer.style.top = '0'
		window.scrollTo({ left: 0, top: newScroll, behavior: 'instant' })
		// handleScroll()
		slideshowCollapsed = true
	})
}

export function initScroll() {
	window.addEventListener('scroll', handleScroll, { passive: true })
	window.addEventListener('resize', handleScroll, { passive: true })

	window.addEventListener('touchstart', () => updateSlideshowAutoscroll(), { passive: true })
	window.addEventListener('touchmove', () => updateSlideshowAutoscroll(), { passive: true })
	window.addEventListener('mousedown', () => updateSlideshowAutoscroll(), { passive: true })
	window.addEventListener('mousemove', (mouseEvent: MouseEvent) => {
		if (mouseEvent.buttons > 0) {
			updateSlideshowAutoscroll()
		}
	}, { passive: true })

	handleScroll()
}
