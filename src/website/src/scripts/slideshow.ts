import { SLIDESHOW_DELAY, RegionId } from './constants';
import { slideshowBackground, slideshowForeground, slideshowTitle, slideshowTitleTexts } from './elements';
import { apiByRegion } from './Region';
import { wait, waitAnimation, waitFor } from './animation_utils';
import { getLogicalScroll, getViewportHeight } from './scroll';

export const SLIDESHOW_REGION: RegionId = 'US-en'

export class Slideshow {
	curImage: HTMLImageElement = slideshowForeground
	nextImage: HTMLImageElement = slideshowBackground

	async roll() {
		let chosenImage = undefined

		let attempts = 0
		while (chosenImage === undefined || (!chosenImage.title || chosenImage.title.trim() === '') && attempts < 20) {
			chosenImage = apiByRegion[SLIDESHOW_REGION].getRandom()
			attempts++
		}

		if (!chosenImage) {
			console.warn('Warning: no images available for slideshow. Retrying...')
			setTimeout(() => void this.roll(), 200)
			return
		}

		this.queueImage(chosenImage['url'])
		this.nextImage.alt = chosenImage['title']

		await waitFor(
			() => document.visibilityState === 'visible' && getLogicalScroll() < getViewportHeight(),
			300
		)

		// console.log(getLogicalScroll(), getViewportHeight(), getLogicalScroll() < getViewportHeight())
		console.log(`Image will change in ${SLIDESHOW_DELAY / 1000} seconds`)
		await wait(SLIDESHOW_DELAY)

		await waitFor(() => this.nextImage.complete)

		const targetOpacity = this.nextImage === slideshowForeground ? '1' : '0'
		waitAnimation(slideshowForeground, 'opacity', targetOpacity)
			.then(() => {
				this.swapImages()
				void this.roll()
			})

		waitAnimation(slideshowTitle, 'opacity', '0').then(() => {
			slideshowTitleTexts.forEach(span => span.textContent = chosenImage['title'])
			slideshowTitle.href = chosenImage['url']

			slideshowTitle.classList.toggle('fullwidth', slideshowTitle.getBoundingClientRect().left == 0)

			slideshowTitle.style.opacity = '1'
		})
	}

	queueImage(highResHomepageUrl: string) {
		this.nextImage.src = highResHomepageUrl
	}

	swapImages() {
		[this.curImage, this.nextImage] = [this.nextImage, this.curImage]
	}
}

export const slideshow = new Slideshow()

export function initTitleClick() {
	slideshowTitle.addEventListener('click', (e) => {
		const selection = window.getSelection()
		if (selection && !selection.isCollapsed && selection.anchorNode && slideshowTitle.contains(selection.anchorNode)) {
			e.preventDefault()
		}
	})
}
