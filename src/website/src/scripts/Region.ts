import { REGION_API_PATH, RegionId, REGIONS_LIST, START_DATE, YEAR_API_PATH } from './constants';
import { ImageEntry } from './types';

export class Region {
	lang: string
	country: string
	images: Map<string, ImageEntry>
	slideshow_dates: string[]

	constructor(region: string) {
		[this.country, this.lang] = region.split('-')
		this.images = new Map<string, ImageEntry>()
		this.slideshow_dates = []
	}

	add(date: string, item: ImageEntry) {
		if (!this.images.has(date)) {
			const itemDate = new Date(date)
			if (itemDate >= START_DATE && item.title?.trim()) {
				this.slideshow_dates.push(date)
			}
		}
		this.images.set(date, item)
	}

	addAll(items: ImageEntry[]) {
		items.forEach(item => this.add(item.date, item))
	}

	get(date: string): ImageEntry | undefined {
		return this.images.get(date)
	}

	getRandom(): ImageEntry | undefined {
		if (this.slideshow_dates.length === 0) return undefined
		return this.images.get(this.slideshow_dates[Math.floor(Math.random() * this.slideshow_dates.length)])
	}

	async fetchYear(year: number, alertError: boolean = false): Promise<void> {
		const apiPath = YEAR_API_PATH(this.country, this.lang, year)
		return this.fetchUrl(apiPath, alertError)
	}

	async fetchAll(alertError: boolean = false): Promise<void> {
		const apiPath = REGION_API_PATH(this.country, this.lang)
		return this.fetchUrl(apiPath, alertError)
	}

	private async fetchUrl(apiPath: string, alertError: boolean = false): Promise<void> {
		try {
			const response = await fetch(apiPath, {
				method: 'GET',
				headers: {
					'Content-Type': 'application/json'
				},
				mode: 'same-origin'
			})

			if (response.ok) {
				console.log(`Loaded API: ${apiPath}`)
				this.addAll(await response.json())
			} else {
				const error = new Error(`Error: can not load API file (HTTP ${response.status}): ${apiPath}`)
				console.log(error)
				if (alertError) {
					alert(error.message)
				}
			}
		} catch (error) {
			console.log(error)
			if (alertError) {
				alert(`Error: can not load API file: ${apiPath}`)
			}
		}
	}
}

export const apiByRegion = {} as Record<RegionId, Region>
REGIONS_LIST.forEach(region => {
	apiByRegion[region] = new Region(region)
})

export function isRegion(market: string): market is RegionId {
	return (REGIONS_LIST as readonly string[]).indexOf(market) !== -1
}
