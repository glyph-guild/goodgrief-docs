// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://docs.goodgrief.dev',
	integrations: [
		starlight({
			title: 'Good Grief',
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/glyph-guild/gg' }],
			editLink: { baseUrl: 'https://github.com/glyph-guild/goodgrief-docs/edit/main/' },
			sidebar: [
				{
					label: 'Getting started',
					items: [{ autogenerate: { directory: 'getting-started' } }],
				},
			],
		}),
	],
});
