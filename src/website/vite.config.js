import {defineConfig} from 'vite';
import legacy from '@vitejs/plugin-legacy';
import htmlMinifier from 'vite-plugin-html-minifier';
import fs from 'fs';
import path from 'path';

function inlineSvgPlugin() {
    return {
        name: 'inline-svg',
        transformIndexHtml(html) {
            return html.replace(/<inline-svg([^>]*)><\/inline-svg>/g, (match, attrs) => {
                const srcMatch = attrs.match(/src="([^"]+)"/);
                if (!srcMatch) return match;
                const src = srcMatch[1];
                const otherAttrs = attrs.replace(srcMatch[0], '').trim();

                const svgPath = path.resolve(import.meta.dirname, 'src', src);
                if (fs.existsSync(svgPath)) {
                    let svgContent = fs.readFileSync(svgPath, 'utf-8').trim();
                    svgContent = svgContent.replace(/<!--[\s\S]*?-->/g, '').trim();
                    return svgContent.replace(/^<svg(\s|>)/, `<svg ${otherAttrs}$1`);
                }
                console.warn(`SVG not found: ${svgPath}`);
                return match;
            });
        },
    };
}

export default defineConfig({
    base: './',
    root: 'src',

    plugins: [
        inlineSvgPlugin(),
        htmlMinifier({
            minify: {
                collapseWhitespace: true,
                keepClosingSlash: true,
                removeComments: true,
                removeRedundantAttributes: true,
                removeScriptTypeAttributes: true,
                removeStyleLinkTypeAttributes: true,
                removeEmptyAttributes: true,
                useShortDoctype: true,
                minifyCSS: false,
                minifyJS: true,
                minifyURLs: false,
            },
        }),
        legacy(),
    ],

    build: {
        outDir: '../root/_website',
        emptyOutDir: false,
    },
});
