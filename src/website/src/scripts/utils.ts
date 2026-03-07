export function formatDescription(text: string): string {
	return text
		.trim()
		.split('\n')
		.map(p => p.trim())
		.filter(p => p.length > 0)
		.map(paragraph => `<p>${paragraph}</p>`)
		.join('')
}
