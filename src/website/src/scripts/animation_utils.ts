export function waitAnimation(element: HTMLElement, property: keyof CSSStyleDeclaration, value: string): Promise<void> {
	return new Promise(resolve => {
		const propertyName = property as string
		const computedStyle = getComputedStyle(element)

		// If value is already what we want, resolve immediately
		if (computedStyle.getPropertyValue(propertyName) === value) {
			element.style.setProperty(propertyName, String(value))
			resolve()
			return
		}

		element.style.setProperty(propertyName, String(value))

		const cleanup = () => {
			element.removeEventListener('transitionend', transitionEnded)
			clearTimeout(timeoutId)
		}

		const transitionEnded = (animation: TransitionEvent) => {
			if (animation.propertyName !== property) return
			cleanup()
			resolve()
		}

		const timeoutId = setTimeout(() => {
			console.warn(`waitAnimation: transition for property "${propertyName}" timed out after 2s for element:`, element)
			cleanup()
			resolve()
		}, 2000)

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
