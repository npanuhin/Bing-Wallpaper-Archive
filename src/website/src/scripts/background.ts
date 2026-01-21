import { HOMEPAGE_DELAY, HOMEPAGE_REGION } from './constants';
import { homepageBackground, homepageForeground, title, titleTexts } from './elements';
import { apiByRegion } from './region';
import { wait, waitAnimations, waitFor } from './animations';

export let curHomepageImage: HTMLImageElement = homepageForeground;
export let nextHomepageImage: HTMLImageElement = homepageBackground;

export async function changeHomepage() {
	const chosenImage = apiByRegion[HOMEPAGE_REGION].getRandom()!

	nextHomepageImage.src = chosenImage['url']
	nextHomepageImage.alt = chosenImage['title']

	await waitFor(
		() => document.visibilityState === 'visible' && window.scrollY < window.innerHeight,
		100
	)

	console.log('Changing image soon')
	await wait(HOMEPAGE_DELAY)

	await waitFor(() => nextHomepageImage.complete)

	waitAnimations(homepageForeground, 'opacity', (nextHomepageImage === homepageForeground ? '1' : '0'))
		.then(() => {
			[curHomepageImage, nextHomepageImage] = [nextHomepageImage, curHomepageImage] // Swap images
			changeHomepage()
		})

	waitAnimations(title, 'opacity', '0').then(() => {
		titleTexts.forEach(span => span.textContent = chosenImage['title'])
		title.href = chosenImage['url']

		title.classList.toggle('fullwidth', title.getBoundingClientRect().left == 0)

		title.style.opacity = '1'
	})
}

export function setInitialImages(highResHomepageUrl: string) {
	nextHomepageImage.src = highResHomepageUrl;
}

export function swapInitialImages() {
	[curHomepageImage, nextHomepageImage] = [nextHomepageImage, curHomepageImage];
}
