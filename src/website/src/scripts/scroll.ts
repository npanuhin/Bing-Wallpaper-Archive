import { AUTOSCROLL_DELAY } from './constants';
import { contentArea, header, slideshowElement, slideshowTitleContainer } from './elements';

let autoScrollTimeout: any
let slideshowCollapsed: boolean = false
let lastScroll: number = getLogicalScroll()
let slideshowExpandTimeout: any = null
const SLIDESHOW_EXPAND_DELAY = 200

export function getViewportHeight(): number {
	return window.visualViewport?.height ?? window.innerHeight
}

export function getLogicalScroll() {
	return slideshowCollapsed ? window.scrollY + getViewportHeight() : window.scrollY
}

export function updateSlideshowAutoscroll(scroll: number = getLogicalScroll()) {
	clearTimeout(autoScrollTimeout)
	if (slideshowCollapsed) return
	const window_height = getViewportHeight()
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
	const windowHeight = getViewportHeight()
	const logicalScroll = getLogicalScroll()

	const slideshowExpandThreshold = windowHeight * 1.05  // %5 of window height after content start
	if (logicalScroll <= lastScroll) {  // Scrolling up
		// console.log('Scrolling up')
		if (slideshowCollapsed && logicalScroll <= slideshowExpandThreshold) {
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
		if (!slideshowCollapsed && logicalScroll > slideshowExpandThreshold) {
			slideshowCollapse()
			return
		}
	}

	slideshowTitleContainer.style.top = slideshowCollapsed ? '0' : 'var(--window-height)'

	updateSlideshowAutoscroll(logicalScroll)

	// ---------- Title background ----------

	slideshowTitleContainer.classList.toggle('permanent_hover', logicalScroll > windowHeight * 0.01)
	contentArea.classList.toggle('has-shadow', logicalScroll > windowHeight * 0.01)

	// ---------- Header shadow ----------

	// const headerBottom = header.getBoundingClientRect().bottom
	// const curImageTop = curImageReal.getBoundingClientRect().top
	header.classList.toggle('has-shadow', logicalScroll > windowHeight + 30)  // margin-top for markets is at least 30px

	lastScroll = logicalScroll
}

function slideshowExpand() {  // When scrolling up
	// console.log('Expanding slideshow')
	requestAnimationFrame(() => {
		const newScroll = window.scrollY + getViewportHeight()
		slideshowElement.style.marginTop = '0'
		slideshowTitleContainer.style.top = 'var(--window-height)'
		window.scrollTo({ left: 0, top: newScroll, behavior: 'instant' })
		// handleScroll()
		slideshowCollapsed = false
	})
}

function slideshowCollapse() {  // When scrolling down
	// console.log('Collapsing slideshow')
	requestAnimationFrame(() => {
		const newScroll = window.scrollY - getViewportHeight()
		slideshowElement.style.marginTop = 'calc(var(--window-height) * -1)'
		slideshowTitleContainer.style.top = '0'
		window.scrollTo({ left: 0, top: newScroll, behavior: 'instant' })
		// handleScroll()
		slideshowCollapsed = true
	})
}

export function initScroll() {
	window.addEventListener('scroll', handleScroll, { passive: true })
	window.addEventListener('resize', handleScroll, { passive: true })
	window.visualViewport?.addEventListener('resize', handleScroll, { passive: true })

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
