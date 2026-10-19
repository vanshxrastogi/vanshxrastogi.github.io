# SEO and editorial review — 19 October 2026

## Decision and scope

IMPLEMENTED AWAITING DEPLOYMENT. This branch adds a separate blog and corrects the personal biography. It does not redesign the portfolio, change project data, replace media, or change film ratios. Production deployment requires the owner's explicit approval. All three articles remain DRAFTED AWAITING EDITORIAL REVIEW and are excluded from production, RSS and search sitemaps. A draft PR is not a live deployment.

Recovery branch: `backup/pre-blog-2026-10-19`, baseline `2c94939b379483b417c4b65b806e52c98242e861`. Feature branch: `feat/editorial-blog-seo`. Preserve subsequent changes when merging or reverting.

## Verified baseline and limits

- Public GitHub Pages repository; static HTML/CSS/JavaScript in `dist`, with Python packaging and a Pages Actions deployment. No application backend or package dependency manifest was found in the retrieved text source. Do not assume a server exists because an earlier brief mentions one.
- 22 portfolio projects; existing dedicated film pages, canonical tags, video sitemap, robots.txt, privacy and terms retained. Project metadata and media are outside this change.
- Search Console ownership was verified. Main and video sitemaps were submitted; the console returned **Couldn't fetch**, with zero discovered URLs at inspection. The live main sitemap opened as valid XML. Submission is not indexing; the reason for Google's fetch failure is not established. Recheck its detail report after processing and test the exact HTTPS sitemap endpoint before changing it again.
- URL inspection showed the homepage crawled successfully on 19 October 2026 at 10:42:53. Its decorative hero video was not indexed because it is not on a watch page. Preserve the homepage design; dedicated film pages are the appropriate candidates for video indexing. This does not establish that all film pages are indexed.
- Search Console reports were still processing. No verified keyword-volume, position, traffic or Core Web Vitals measurements were available. No ranking or speed score is claimed.
- AdSense accepted the exact `vanshxrastogi.github.io` site. Site review requested 19 October 2026 at 10:37 IST; status **Getting ready**, ads.txt **Authorised**. Account access, site verification and approval are distinct. Approval and earnings are NOT VERIFIED. A separate site's policy issue is not a finding against this portfolio.
- An AdSense payments-account action banner is visible. The owner must inspect it privately; no payment details were changed or collected.
- No GA4 measurement ID or active GA4 installation was verified. Tracking is specified below, not installed with an invented ID.
- Main was reported unprotected by the repository API. Account 2FA, recovery, collaborator privileges and environment approvals were not accessible in this audit. Owner review is required; this is not a completed account-security certification.

## Changes and reasons

- One Blog link alongside the original four navigation links; founder wording replaced with truthful employee/personal-portfolio wording.
- Dependency-free Markdown/JSON editorial build; separate landing, categories, articles, author, editorial policy, archive, RSS, search, Article and BreadcrumbList metadata. Empty categories and draft previews are noindex.
- Generated sitemap includes real indexable HTML. Custom 404 is noindex. No route migration or film URL changes.
- Existing AdSense account verification is preserved. Ad insertion now handles an already-present ownership meta tag correctly, but remains disabled unless both approval and consent flags are true. No ad script or tracking vendor is added by this proposal.
- Actions pinned to verified commit SHAs; checkout credentials not persisted; minimal build/deploy permissions retained; weekly Actions Dependabot checks proposed. PR checks do not deploy and have no scheduled publication.

## Security and performance checklist

Before merge, owner should enable 2FA, save recovery codes privately, review collaborators and protect main with PR review and required checks. Do not paste secrets into chat. These account changes were not made automatically.

The new builder escapes HTML and rejects unsafe Markdown link schemes; publication requires explicit reviewed status and a non-future publication date. New blog assets use system fonts, no third-party scripts, responsive SVG, visible keyboard focus and reduced-motion handling. Existing contact form, YouTube, Drive and externally hosted media remain existing third-party dependencies. Review FormSubmit spam controls and the privacy statement before adding any new form fields. Never collect financial or sensitive identity information through the portfolio form.

GitHub Pages does not provide arbitrary response-header configuration via a conventional backend. Do not add a `_headers` file and claim it applies to Pages. A strict CSP needs an inventory and compatibility test for existing embeds and scripts; it is not installed speculatively. HTTPS browser access is observed, but an exhaustive live mixed-content/network and historical-secret audit is not completed. No vulnerability-free claim is made.

## Analytics specification (not enabled)

Use one owner-selected GA4 web stream, one tag installation, and applicable consent handling. Verify DebugView and network requests before production activation. Avoid duplicate page_view from both automatic and manual tracking. Do not send names, emails, messages or private media URLs as event parameters.

| Event | Trigger | Safe parameters |
|---|---|---|
| page_view | One eligible page load | page_path, page_title |
| blog_to_portfolio | Click from an article to Work | article_slug, destination_section |
| article_read | Once after 60 seconds and 75% scroll | article_slug, category |
| contact_click | Click contact CTA | placement, method |
| generate_lead | Confirmed successful enquiry submission only | form_id; no message content |

A click or direct visit to thanks.html is not proof of a successful enquiry. Validate submission confirmation before marking a key event. Use Search Console for queries and Google clicks; GA4 for consented on-site engagement. Different measurement definitions can produce different totals.

Monthly reporting fields: month, Search Console clicks/impressions/CTR/average position, indexed pages, top organic landing pages, blog pageviews, engaged sessions, confirmed enquiries, AdSense impressions/Page RPM/estimated and finalized revenue. Leave unavailable fields blank with a reason, never invent zero. Compare completed periods and annotate publication and consent changes.

## Content and distribution

The 90-day calendar and first 30 briefs are an editorial hypothesis queue based on specific production problems, not measured search-demand rankings. First priorities emphasize concrete tasks where examples can be documented. Broad 'best tool' comparisons should wait for current vendor research and real side-by-side tests. Search Console data and Trends validation remain pending; revise priority once evidence exists. Three original explanatory drafts contain labelled exercises, not invented client results.

Daily process: select one useful problem, read primary sources, document a reproducible example, draft, check every capability and pricing claim, review rights and disclosures, run checks, request editorial approval, then publish via a reviewed PR. Skip a day when evidence is insufficient. No daily scheduler or automatic article publisher is enabled.

Distribute approved guides through the owner's LinkedIn and relevant filmmaking communities only when allowed by their rules. Offer a useful extract and one relevant link; avoid bulk outreach. A practical shot-planning checklist or delivery checklist is a stronger citation resource than paid links. No messages, directory submissions or guest pitches have been sent.

## Revenue scenarios — illustrative assumptions only

Monthly estimated ad revenue = monetized pageviews / 1,000 × assumed Page RPM. These inputs are examples, not forecasts, researched market rates or promises.

| Scenario | Pageviews | Assumed Page RPM | Arithmetic result |
|---|---:|---:|---:|
| Conservative illustration | 1,000 | ₹50 | ₹50 |
| Base illustration | 10,000 | ₹150 | ₹1,500 |
| Optimistic illustration | 50,000 | ₹300 | ₹15,000 |

Actual approval, traffic, geography, consent, fill and ad viewability may produce much less, including zero. Replace assumptions with account data once available. Keep ads out of the portfolio presentation; consider article placements only after approval, applicable consent configuration and owner review. Do not click ads or encourage visitors to do so. No domain purchase or hosting migration is needed for this draft; the existing address was accepted for review.

## Verification and release checklist

Local build and eight Python tests passed. Content validation passed. Tests cover draft exclusion, escaped HTML, publication/ad gates, metadata compatibility and portable builds. Remaining checks: remote PR CI, rendered desktop/mobile review, exhaustive live HTTP crawling and post-deployment validation. Record actual results separately instead of treating this checklist as evidence they passed.

After approval: merge the reviewed feature commit, verify the Pages run succeeds, open /blog/, a published article, RSS, sitemap and an unknown URL (must return 404), inspect Google verification tags/ads.txt, test original navigation and film playback, then resubmit changed sitemap if required. If article approval is not given, do not change its draft flag. Roll back with a revert PR for this change, preserving newer unrelated commits; do not force-reset main to the backup branch.

## Primary references

- [Google: helpful content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
- [Google: generative AI content guidance](https://developers.google.com/search/docs/fundamentals/using-gen-ai-content)
- [Google: video indexing requirements](https://developers.google.com/search/docs/appearance/video)
- [AdSense site approval](https://support.google.com/adsense/answer/7584263)
- [AdSense eligibility](https://support.google.com/adsense/answer/9724)
- [GA4 recommended events](https://support.google.com/analytics/answer/9267735)
- [GitHub Actions secure use](https://docs.github.com/en/actions/reference/security/secure-use)
