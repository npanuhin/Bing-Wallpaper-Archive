import { HOMEPAGE_REGION } from './constants';
import { markets, marketsItems, marketsToggle, marketsWrapper } from './elements';
import { isRegion } from './Region';

export function changeMarket(market: string = HOMEPAGE_REGION) {
	marketsItems.forEach(selector => {
		selector.classList.toggle('active', selector.getAttribute('data-mkt') == market)
	})
}

export function toggleMarketSelector() {
	markets.classList.toggle('hidden', !marketsToggle.checked)
	marketsWrapper.classList.toggle('hidden', !marketsToggle.checked)
}

export function toggleMarketSelectorByScreenSize() {
	marketsToggle.checked = window.innerWidth > 950
	toggleMarketSelector()
}

export function initMarkets() {
	changeMarket()

	window.addEventListener('hashchange', () => {
		const market = window.location.hash.slice(1)
		if (!isRegion(market)) {
			console.log(`Invalid market specified in URL hash: ${market}`)
		} else {
			changeMarket(market)
		}
	})

	marketsToggle.addEventListener('change', toggleMarketSelector)
	window.addEventListener('resize', toggleMarketSelectorByScreenSize, { passive: true })
	toggleMarketSelectorByScreenSize()
}
