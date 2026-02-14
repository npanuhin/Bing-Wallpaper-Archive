export const REGIONS_LIST = [
	'pt-BR',
	'en-CA',
	'fr-CA',
	'fr-FR',
	'de-DE',
	'en-IN',
	'it-IT',
	'ja-JP',
	'zh-CN',
	'es-ES',
	'en-GB',
	'en-US',
	'en-ROW'
] as const;

export type RegionId = typeof REGIONS_LIST[number];
export const HOMEPAGE_REGION: RegionId = 'en-US';

export const YEAR_API_PATH = (country: string, lang: string, year: number): string =>
	`${country.toUpperCase()}-${lang.toLowerCase()}.${year}.json`;

export const START_DATE: Date = new Date(2017, 2, 1); // 2017-03-01: 1080p images start here
export const AUTOSCROLL_DELAY: number = 5000; // Delay before automatic scroll
export const HOMEPAGE_DELAY: number = 5000; // Delay between homepage images. Does not include transition time

export const TODAY: Date = new Date();
export const PREVIOUS_YEAR: number = TODAY.getFullYear() - 1; // Previous year to avoid having only one image on January 1st
