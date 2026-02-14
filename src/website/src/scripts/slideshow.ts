import { HOMEPAGE_DELAY, HOMEPAGE_REGION } from './constants';
import { homepageBackground, homepageForeground, title, titleTexts } from './elements';
import { apiByRegion } from './Region';
import { wait, waitAnimation, waitFor } from './animation_utils';

export class Slideshow {
	curHomepageImage: HTMLImageElement = homepageForeground;
	nextHomepageImage: HTMLImageElement = homepageBackground;

	async roll() {
		const chosenImage = apiByRegion[HOMEPAGE_REGION].getRandom()
		if (!chosenImage) {
			console.warn('Warning: no images available for slideshow. Retrying...')
			setTimeout(() => void this.roll(), 200)
			return
		}

		this.queueImage(chosenImage['url'])
		this.nextHomepageImage.alt = chosenImage['title']

		await waitFor(
			() => document.visibilityState === 'visible' && window.scrollY < window.innerHeight,
			300
		)

		console.log(`Image will change in ${HOMEPAGE_DELAY / 1000} seconds`)
		await wait(HOMEPAGE_DELAY)

		await waitFor(() => this.nextHomepageImage.complete)

		const targetOpacity = this.nextHomepageImage === homepageForeground ? '1' : '0'
		waitAnimation(homepageForeground, 'opacity', targetOpacity)
			.then(() => {
				this.swapImages()
				void this.roll()
			})

		waitAnimation(title, 'opacity', '0').then(() => {
			titleTexts.forEach(span => span.textContent = chosenImage['title'])
			title.href = chosenImage['url']

			title.classList.toggle('fullwidth', title.getBoundingClientRect().left == 0)

			title.style.opacity = '1'
		})
	}

	queueImage(highResHomepageUrl: string) {
		this.nextHomepageImage.src = highResHomepageUrl;
	}

	swapImages() {
		[this.curHomepageImage, this.nextHomepageImage] = [this.nextHomepageImage, this.curHomepageImage];
	}
}

export const slideshow = new Slideshow();
