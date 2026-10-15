// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import starlightLinksValidator from 'starlight-links-validator';

// https://astro.build/config
export default defineConfig({
	site: 'https://docs.goodgrief.dev',
	integrations: [
		starlight({
			title: 'Good Grief',
			plugins: [starlightLinksValidator()],
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/glyph-guild/gg' }],
			editLink: { baseUrl: 'https://github.com/glyph-guild/goodgrief-docs/edit/main/' },
			sidebar: [
				{ label: 'Start here', items: [{ autogenerate: { directory: 'start-here' } }] },
				{ label: 'Concepts', items: [{ autogenerate: { directory: 'concepts' } }] },
				{ label: 'Reference', items: [{ autogenerate: { directory: 'reference' } }] },
				{ label: 'Contributing', items: [{ autogenerate: { directory: 'contributing' } }] },
			],
		}),
	],
});
