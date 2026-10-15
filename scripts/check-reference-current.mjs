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
	// A release older than `gg reference --json` cannot produce a snapshot, so
	// asking for a refresh would block every page with no way to comply.
	if (!(await canDescribeItself(latest))) {
		console.log(`::warning::gg ${latest} has been released, but it has no \`gg reference\` command, so the reference stays at ${pinned}.`);
		process.exit(0);
	}
	console.error(`The reference describes gg ${pinned}, and gg ${latest} has been released.`);
	console.error(`Run scripts/refresh-reference.sh ${latest}, then npm run build.`);
	process.exit(1);
}

// Whether a release's help lists `gg reference`, read from the source at its tag.
async function canDescribeItself(version) {
	const source = await fetch(`https://raw.githubusercontent.com/glyph-guild/gg/v${version}/Gg.Cli/CliArgs.cs`);
	return source.ok && (await source.text()).includes('"gg reference --json');
}

console.log(`The reference describes gg ${pinned}, the newest release.`);
