# goodgrief-docs

Source for [docs.goodgrief.dev](https://docs.goodgrief.dev), built with
[Astro Starlight](https://starlight.astro.build) and deployed to GitHub Pages
by `.github/workflows/deploy.yml` on every push to `main`.

## Develop

Requires Node 22+.

```sh
npm install
npm run dev      # http://localhost:4321
npm run build    # output in dist/
```

Pages live in `src/content/docs/` as Markdown/MDX; the sidebar is configured in
`astro.config.mjs`.
