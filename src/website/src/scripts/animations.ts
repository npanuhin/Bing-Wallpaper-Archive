export function waitAnimations(element: HTMLElement, property: keyof CSSStyleDeclaration, value: string): Promise<void> {
	return new Promise(resolve => {
		element.style.setProperty(property as string, String(value));

		const transitionEnded = (animation: TransitionEvent) => {
			if (animation.propertyName !== property) return
			element.removeEventListener('transitionend', transitionEnded)
			resolve()
		}
		element.addEventListener('transitionend', transitionEnded)
	})
}

export function wait(delay: number): Promise<void> {
	return new Promise(resolve => setTimeout(resolve, delay))
}

export async function waitFor(conditionFunction: () => boolean, interval: number = 50): Promise<void> {
	while (!conditionFunction()) {
		await wait(interval)
	}
}
