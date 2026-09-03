import { AUTOSCROLL_DELAY } from './home';
import { contentArea, header, slideshowElement, slideshowTitleContainer } from './elements';

let autoScrollTimeout: ReturnType<typeof setTimeout>
let slideshowCollapsed: boolean = false
let lastScroll: number = getLogicalScroll()
let slideshowExpandTimeout: ReturnType<typeof setTimeout> | null = null
const SLIDESHOW_EXPAND_DELAY = 200

export function getViewportHeight(): number {
	return window.visualViewport?.height ?? window.innerHeight
}

export function getLogicalScroll(
	viewportHeight: number = getViewportHeight()
) {
	return slideshowCollapsed ? window.scrollY + viewportHeight : window.scrollY
}

export function updateSlideshowAutoscroll(
	viewportHeight: number = getViewportHeight(),
	scroll: number = getLogicalScroll(viewportHeight)
) {
	clearTimeout(autoScrollTimeout)
	if (slideshowCollapsed) return
	if (scroll <= 0 || scroll >= viewportHeight) return

	if (scroll * 2 < viewportHeight) {
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
				top: viewportHeight + 1,
				behavior: 'smooth'
			})
		}, AUTOSCROLL_DELAY)
	}
}

export function handleScroll() {
	const viewportHeight = getViewportHeight()
	const logicalScroll = getLogicalScroll(viewportHeight)

	const slideshowExpandThreshold = viewportHeight * 1.05  // %5 of window height after content start
	if (logicalScroll <= lastScroll) {
		// console.log('Scrolling up')
		document.documentElement.classList.toggle('overscroll-disabled', slideshowCollapsed)
		if (slideshowCollapsed && logicalScroll <= slideshowExpandThreshold) {
			if (!slideshowExpandTimeout) {
				// console.log('Requesting slideshow expand')
				slideshowExpandTimeout = setTimeout(slideshowExpand, SLIDESHOW_EXPAND_DELAY)
			}
		}
	} else {
		// console.log('Scrolling down')
		document.documentElement.classList.add('overscroll-disabled')
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

	updateSlideshowAutoscroll(viewportHeight, logicalScroll)

	// ---------- Title background ----------

	const scrolledPastTop = logicalScroll > viewportHeight * 0.01
	slideshowTitleContainer.classList.toggle('permanent_hover', scrolledPastTop)
	contentArea.classList.toggle('has-shadow', scrolledPastTop)

	// ---------- Header shadow ----------

	// const headerBottom = header.getBoundingClientRect().bottom
	// const curImageTop = curImageReal.getBoundingClientRect().top
	header.classList.toggle('has-shadow', logicalScroll > viewportHeight + 30)  // margin-top for markets is at least 30px

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
