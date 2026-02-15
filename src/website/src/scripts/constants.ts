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
] as const;

export type RegionId = typeof REGIONS_LIST[number];

export const YEAR_API_PATH = (country: string, lang: string, year: number): string =>
	`${country.toUpperCase()}-${lang.toLowerCase()}.${year}.json`;

export const START_DATE: Date = new Date(2017, 2, 1); // 2017-03-01: 1080p images start here
export const AUTOSCROLL_DELAY: number = 5000; // Delay before automatic scroll
export const SLIDESHOW_DELAY: number = 5000; // Delay between homepage images. Does not include transition time

export const TODAY: Date = new Date();
export const PREVIOUS_YEAR: number = TODAY.getFullYear() - 1; // Previous year to avoid having only one image on January 1st
