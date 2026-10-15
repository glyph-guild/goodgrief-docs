// Fails when src/data/gg-reference.json describes an older gg than the newest
// release, so the published reference never falls behind what people install.

import { readFileSync } from 'node:fs';

const root = new URL('..', import.meta.url).pathname;
const pinned = JSON.parse(readFileSync(`${root}src/data/gg-reference.json`, 'utf8')).version.split('+')[0];

const response = await fetch('https://api.github.com/repos/glyph-guild/gg/releases?per_page=100', {
	headers: process.env.GITHUB_TOKEN ? { authorization: `Bearer ${process.env.GITHUB_TOKEN}` } : {},
});
if (!response.ok) {
	console.error(`Could not list gg releases (${response.status}), so the reference could not be checked.`);
	process.exit(1);
}

// gg releases are tagged v<major>.<minor>.<patch>; contract releases use another prefix.
const parse = (version) => version.split('.').map(Number);
const newer = (a, b) => {
	for (let i = 0; i < 3; i++) if (a[i] !== b[i]) return a[i] > b[i];
	return false;
};
const latest = (await response.json())
	.filter((release) => !release.draft && !release.prerelease && /^v\d+\.\d+\.\d+$/.test(release.tag_name))
	.map((release) => release.tag_name.slice(1))
	.reduce((best, version) => (best === null || newer(parse(version), parse(best)) ? version : best), null);

if (latest !== null && newer(parse(latest), parse(pinned))) {
	console.error(`The reference describes gg ${pinned}, and gg ${latest} has been released.`);
	console.error(`Run scripts/refresh-reference.sh ${latest}, then npm run build.`);
	process.exit(1);
}

console.log(`The reference describes gg ${pinned}, the newest release.`);
