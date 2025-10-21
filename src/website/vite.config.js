import {defineConfig} from 'vite';
import legacy from '@vitejs/plugin-legacy';
import htmlMinifier from 'vite-plugin-html-minifier';

export default defineConfig({
	base: './',
	root: 'src',

	plugins: [
		htmlMinifier({
			minifyURLs: false,
		}),
		legacy(),
	],

	build: {
		outDir: '../root/_website',
		emptyOutDir: true,
	},
});
