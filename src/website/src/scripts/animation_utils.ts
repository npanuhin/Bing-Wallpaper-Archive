export function waitAnimation(element: HTMLElement, property: keyof CSSStyleDeclaration, value: string): Promise<void> {
	return new Promise(resolve => {
		element.style.setProperty(property as string, String(value))

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

export function waitFrames(frames: number = 1): Promise<void> {
	return new Promise(resolve => {
		let count = 0

		function step() {
			if (++count >= frames) {
				resolve()
			} else {
				requestAnimationFrame(step)
			}
		}

		requestAnimationFrame(step)
	})
}

export function waitFrame(): Promise<void> {
	return new Promise(resolve => requestAnimationFrame(() => resolve()))
}
