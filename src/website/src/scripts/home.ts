import { PREVIOUS_YEAR, START_DATE, TODAY } from './constants';
import { curImageInitial, curImageReal, slideshowForeground } from './elements';
import { apiByRegion } from './Region';
import { initTitleClick, slideshow, SLIDESHOW_REGION } from './slideshow';
import { wait, waitAnimation, waitFor, waitFrame } from './animation_utils';
import { initScroll } from './scroll';
import { initMarkets } from './markets_sidebar';
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

	if (slideshowForeground.complete) {
		onImageReady()
	} else {
		slideshowForeground.addEventListener('load', onImageReady, { once: true })
		slideshowForeground.addEventListener('error', onImageReady, { once: true })
	}
})

Promise.all([domReady, document.fonts.ready, initialImageLoad]).then(() => {
	console.log('DOM, fonts, and initial image are ready. Showing website...')
	document.body.classList.add('shown')

	const highResHomepageUrl = slideshowForeground.dataset.realImage!
	slideshow.queueImage(highResHomepageUrl)
	curImageReal.src = highResHomepageUrl;

	(async () => {
		await waitFor(() => slideshow.nextImage.complete)
		console.log('Slideshow image loaded in full resolution')

		void loadFullFonts()

		const apiPromise =
			apiByRegion[SLIDESHOW_REGION]
				.fetchYear(PREVIOUS_YEAR)
				.catch((e) => {
					console.log(e);
					alert(String(e))
				})

		void apiPromise.finally(() => {
			// TODO: Fetch all regions
			for (let year = START_DATE.getFullYear(); year <= TODAY.getFullYear(); ++year) {
				if (year === PREVIOUS_YEAR) continue
				apiByRegion[SLIDESHOW_REGION]
					.fetchYear(year)
					.catch(console.log)
			}
		})

		const animPromise =
			waitAnimation(slideshowForeground, 'opacity', '0')
				.then(() => {
					slideshow.swapImages()
				})

		await Promise.all([apiPromise, animPromise])

		void slideshow.roll()
	})();

	(async () => {
		await waitFor(() => curImageReal.complete)
		console.log('Current image loaded in full resolution')
		await waitAnimation(curImageInitial, 'opacity', '0')
		await waitFrame()
		await wait(1000)
		if (curImageInitial.parentNode) {
			curImageInitial.parentNode.removeChild(curImageInitial)
		}
	})()

	initScroll()
	initMarkets()
	initTitleClick()
})
