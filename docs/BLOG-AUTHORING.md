# Authoring and preview

Posts live in `content/blog/*.md`. Copy a draft and change its unique slug, title, description, category, updated date and primary-source links. The format is JSON metadata, a line containing `---`, then Markdown paragraphs, `##` headings, `-` lists, links, bold and inline code. Raw HTML is escaped. Do not use unsupported Markdown constructs expecting them to render.

Keep `status: "draft"` and `reviewed: false` while writing. For publication, obtain the owner's editorial approval, set `status: "published"`, `reviewed: true`, and an actual `published: "YYYY-MM-DD"` date. Update `updated` only for meaningful content changes. Published dates cannot be in the future. Verify all sources and demonstrations; do not infer personal experience from a tool list.

Run from the repository root:

```sh
python -m unittest discover -s tests
python scripts/validate.py
SITE_URL=https://vanshxrastogi.github.io python scripts/build_pages.py
```

PowerShell: set `$env:SITE_URL='https://vanshxrastogi.github.io'` before running the builder. Python's standard library is sufficient.

For an unpublished editorial preview, copy `_site` to a separate `review-preview` directory and run:

```sh
python scripts/build_blog.py --destination review-preview --include-drafts
python -m http.server 8775 --bind 127.0.0.1 --directory review-preview
```

Open http://127.0.0.1:8775/blog/. Never deploy this draft preview. Always use the clean `build_pages.py` production build; it removes its previous destination and excludes drafts. Do not run the draft builder against `dist` or a production artifact. Archive pages paginate nine articles; homepage search covers all published article cards.

The PR workflow validates content and builds without deployment. The existing Pages workflow deploys a merge to main, so merge only after explicit approval. There is no scheduled writer or publisher. The daily calendar is a planning aid, not a promise of automatic daily execution.
