import { START_DATE } from './home';

export const REGIONS_LIST = [
    'BR-pt',
    'CA-en',
    'CA-fr',
    'FR-fr',
    'DE-de',
    'IN-en',
    'IT-it',
    'JP-ja',
    'CN-zh',
    'ES-es',
    'GB-en',
    'US-en',
    'ROW-en'
] as const

export type RegionName = typeof REGIONS_LIST[number]

export const YEAR_API_PATH = (country: string, lang: string, year: number): string =>
    `${country.toUpperCase()}-${lang.toLowerCase()}.${year}.json`

export const REGION_API_PATH = (country: string, lang: string): string =>
    `${country.toUpperCase()}-${lang.toLowerCase()}.json`

export interface ImageEntry {
    date: string
    url: string
    title: string
    description?: string

    [key: string]: any
}

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

export const apiByRegion = {} as Record<RegionName, Region>
REGIONS_LIST.forEach(region => {
    apiByRegion[region] = new Region(region)
})

export function isRegion(market: string): market is RegionName {
    return (REGIONS_LIST as readonly string[]).indexOf(market) !== -1
}
