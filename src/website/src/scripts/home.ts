import { HOMEPAGE_REGION, PREVIOUS_YEAR, START_DATE, TODAY } from './constants';
import { curImageInitial, curImageReal, homepageForeground } from './elements';
import { apiByRegion } from './region';
import { changeHomepage, nextHomepageImage, setInitialImages, swapInitialImages } from './background';
import { wait, waitAnimations, waitFor } from './animations';
import { initScroll } from './scroll';
import { initMarkets } from './markets';
import { loadFullFonts } from './fonts';

// =================================================== On page load ====================================================

const domReady = new Promise<void>(resolve => {
	if (document.readyState === 'interactive' || document.readyState === 'complete') {
		return resolve()
	}
	document.addEventListener('DOMContentLoaded', () => resolve(), { once: true })
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
		homepageForeground.addEventListener('load', onImageReady, { once: true })
		homepageForeground.addEventListener('error', onImageReady, { once: true })
	}
})

Promise.all([domReady, document.fonts.ready, initialImageLoad]).then(() => {
	document.body.classList.add('shown')

	console.log('DOM, initial image, and fonts are ready. Website rendered.')

	const highResHomepageUrl = homepageForeground.dataset.realImage!
	setInitialImages(highResHomepageUrl)
	curImageReal.src = highResHomepageUrl;

	(async () => {
		await waitFor(() => nextHomepageImage.complete)
		console.log('Initial image loaded in full resolution')
		void loadFullFonts()
		await waitAnimations(homepageForeground, 'opacity', '0');
		swapInitialImages()

		await apiByRegion[HOMEPAGE_REGION]
			.fetchYear(PREVIOUS_YEAR)
			.catch((e) => {
				console.log(e);
				alert(String(e))
			})

		void changeHomepage()

        // TODO: Fetch all regions
		for (let year = START_DATE.getFullYear(); year <= TODAY.getFullYear(); ++year) {
			if (year === PREVIOUS_YEAR) continue
			apiByRegion[HOMEPAGE_REGION]
				.fetchYear(year)
				.catch(console.log)
		}
	})();

	(async () => {
		await waitFor(() => curImageReal.complete)
		console.log('Current image loaded')
		await waitAnimations(curImageInitial, 'opacity', '0')
		requestAnimationFrame(async () => {
			await wait(1000)
			if (curImageInitial.parentNode) {
				curImageInitial.parentNode.removeChild(curImageInitial)
			}
		})
	})()

	initScroll()
	initMarkets()
})
