const fullFonts = [
	{ name: 'Mi Sans', path: 'MiSans/MiSans-Regular', weight: '400', style: 'normal', display: 'swap' },
] as const

export async function loadFullFonts() {
	try {
		const fontPromises = fullFonts.map(fontInfo => {
			const fontFace = new FontFace(
				fontInfo.name,
				`url(fonts/${fontInfo.path}.woff2) format('woff2'),
				 url(fonts/${fontInfo.path}.woff) format('woff')`,
				{
					weight: fontInfo.weight,
					style: fontInfo.style,
					display: fontInfo.display,
				},
			)
			return fontFace.load()
		})

		const loadedFonts = await Promise.all(fontPromises)

		loadedFonts.forEach(font => (document.fonts as any).add(font))

		console.log('Full fonts loaded and activated')

	} catch (error) {
		console.error('Failed to load and activate full fonts:', error)
	}
}
