import { SLIDESHOW_DELAY } from './home';
import { apiByRegion, ImageEntry, RegionName } from './api';
import {
	curImageDescription,
	curImageReal,
	curImageTitle,
	slideshowBackground,
	slideshowForeground,
	slideshowTitle,
	slideshowTitleTexts
} from './elements';
import { wait, waitAnimation, waitFor } from './animation_utils';
import { text2html } from './utils';
import { getLogicalScroll, getViewportHeight } from './scroll';

export const SLIDESHOW_REGION: RegionName = 'US-en'

export class Slideshow {
	curImage: HTMLImageElement = slideshowForeground
	nextImage: HTMLImageElement = slideshowBackground
	curImageData: ImageEntry | null = null

	async roll() {
		const chosenImage = apiByRegion[SLIDESHOW_REGION].getRandom()

		if (!chosenImage) {
			console.warn('Warning: no images available for slideshow. Retrying...')
			setTimeout(() => void this.roll(), 200)
			return
		}

		this.queueImage(chosenImage.url)
		this.nextImage.alt = chosenImage.title

		await waitFor(
			() => document.visibilityState === 'visible' && getLogicalScroll() < getViewportHeight(),
			300
		)

		// console.log(getLogicalScroll(), getViewportHeight(), getLogicalScroll() < getViewportHeight())
		console.log(`Image will change in ${SLIDESHOW_DELAY / 1000} seconds`)
		await wait(SLIDESHOW_DELAY)

		await waitFor(() => this.nextImage.complete)

		const targetOpacity = this.nextImage === slideshowForeground ? '1' : '0'
		slideshowForeground.style.pointerEvents = targetOpacity === '1' ? 'auto' : 'none'
		waitAnimation(slideshowForeground, 'opacity', targetOpacity)
			.then(() => {
				this.swapImages()
				void this.roll()
			})

		waitAnimation(slideshowTitle, 'opacity', '0').then(() => {
			slideshowTitleTexts.forEach(span => span.textContent = chosenImage.title)
			slideshowTitle.href = chosenImage.url

			this.curImageData = chosenImage

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
		e.preventDefault()

		const selection = window.getSelection()
		if (selection && !selection.isCollapsed && selection.anchorNode && slideshowTitle.contains(selection.anchorNode)) {
			return
		}

		window.scroll({
			top: getViewportHeight(),
			behavior: 'smooth'
		})

		if (slideshow.curImageData) {
			curImageReal.src = slideshow.curImageData.url
			curImageTitle.textContent = slideshow.curImageData.title
			curImageDescription.innerHTML = text2html(slideshow.curImageData.description ?? '')
		}
	})
}
