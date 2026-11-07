# Enrico Scala — static personal website

This is a static rebuild of https://sites.google.com/view/enricoscalashomepage/,
captured on 5 November 2026. It preserves all seven public pages, your portrait,
56 original publication entries, 26 news items, original links, and the two publication correction notes.
The updated bibliography adds 47 papers/preprints and six other research outputs,
with all 110 records from the public Scholar profile reviewed on 5 November 2026.
The KR 2026 paper and IJCAI 2024 extended abstract were also verified in their
official proceedings. The bibliography now displays 109 entries in total.
The original site's Milan page is empty; its new page retains the title.
The new design uses local fonts, a sidebar, readable typography, and responsive CSS.
No web framework, server application, analytics, or external font service is needed.

## Files

- `public/`: complete standalone website. Open `public/index.html` to view it.
- `google-sites/embed.html`: self-contained version for pasting into Google Sites;
  CSS, JavaScript and the portrait are included in the file.
- `content/`: editable content, one HTML fragment per page; `news.json` holds the news.
  `publications-added.json` holds the added bibliography records and links;
  `bibliography-review.json` documents coverage and duplicate decisions.
- `source-snapshot/`: content snapshots for comparison, with Google's runtime
  scripts and API keys removed; not for hosting.
- `scripts/build.py`: generates both versions using Python 3, standard library only.
- `scripts/verify.py`: checks source text and link preservation and local assets.
- `scripts/check_secrets.py`: checks tracked files for credential patterns without
  printing matched values. This check runs before deployment.

## Publish using Google Sites

Google Sites does not offer an import of a static website folder to replace its
native pages. Its supported custom HTML route is an **embed**. The result remains
inside a Google Sites page, with Google's outer layout and URL.

1. Open your Google Sites editor using the account that owns your site. The
   `sites.google.com/u/0/new/` link is the Sites creation/dashboard entry point,
   rather than a public link to your existing website.
2. Try this on a new draft page first, so the existing published pages stay available.
3. Open `google-sites/embed.html` in a **text editor**, select all, and copy the
   HTML source. Do not copy the rendered page from a browser.
4. In Google Sites, choose **Insert → Embed → Embed code**. Paste the complete
   source, then choose **Next → Insert**. Enlarge the embed to use the page width
   and provide enough height. You can also try **Pages → + → Full page embed →
   Embed code** for a page dedicated to the embedded site.
5. Use Google Sites' Preview to check desktop and mobile views, the seven
   navigation links, publication search, and external links. The embed has been
   checked locally, but has not been tested inside your authenticated Sites editor.
6. Click **Publish** when you are satisfied. Keep your existing site URL if desired.

The embed contains all pages. Its navigation switches sections inside the frame.
External links open in a new tab. The photo is embedded, so no image hosting is
required. Pasting code does **not** establish a connection to these local files:
after editing content, rebuild and replace the embedded code, then publish again.
Google Sites search and search engines may treat framed content differently from
native pages; standalone hosting gives each page its own normal URL.

Official instructions: https://support.google.com/sites/answer/90569?hl=en

## Standalone hosting on Google's Firebase Hosting

For a conventional static website with separate page URLs, Firebase Hosting is
Google's dedicated product. It serves HTML, CSS, JavaScript and images over HTTPS.
You can later embed its published URL in Google Sites, if you want to retain a
Google Sites entry page. Check current quotas and pricing before deployment.

1. Create/select a project in https://console.firebase.google.com/.
2. On a computer with Node.js/npm, install the official Firebase CLI and sign in:

   ```sh
   npm install -g firebase-tools
   firebase login
   ```

3. From this folder, run `firebase init hosting`. Choose your project and `public`
   as the public directory. Answer **No** to the single-page application rewrite
   and **No** if asked to overwrite the existing `index.html`.
4. Run `firebase deploy --only hosting`. Use the HTTPS URL Firebase returns.

To display that URL in Google Sites, use **Insert → Embed → By URL**, or a full
page embed, and publish. Hosting updates then happen through Firebase deployment;
the embedded URL stays the same.

Official guide: https://firebase.google.com/docs/hosting/quickstart

## Editing and previewing

Edit the appropriate `content/*.html` fragment; edit `public/styles.css` for styling
and `public/site.js` for publication search. Then, from this folder:

```sh
python3 scripts/build.py
python3 scripts/verify.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory public
```

Open http://127.0.0.1:8000/. The verification script checks revised pages against current content and
untouched pages against the original snapshot, including local links and embed routes.
Do not rerun `capture_source.py` after editing local content: it refreshes the
snapshot and overwrites the content fragments from the old live Google Site.

## Keeping publications current

The list retains the original 2010–2023 entries and adds verified missing records
through 2026. Original PDF links and correction notes are preserved. Journal and
conference versions remain separate; recognised alternate-title duplicates are
mapped to the existing records. Preprints are labelled, and theses, reports,
editorial contributions and less certain Scholar records appear under Other
research outputs. The review file records the one possible title duplicate kept
in that latter section. DBLP's flagged ORCID identity conflict was checked, and
unrelated extortion/ransomware records were excluded.

No Scholar scraper runs in visitors' browsers. Search filters all 109 local entries
by author, title, venue, or year; the full list is readable without JavaScript.

For future updates, export your profile's records as BibTeX and merge new
publications into `content/publications-added.json`. Update the review date in
`content/bibliography-review.json`. Preserve the existing PDF links,
software links, and correction notes; do not replace the whole list blindly.
Rebuild and republish afterward. A future scheduled build can use a supported
bibliographic API or reviewed exports while the published website remains static.
Google Scholar does not provide bulk access for a direct native synchronization:
https://scholar.google.com/intl/en/scholar/help.html

## Migration notes

The original publication descriptions, including older dates, “to appear”
statuses and original spelling, are retained as supplied. New records use the
reviewed bibliography metadata described above. The existing site's
Google search, cookie banner, tracking code, and site logo
were not carried over as website content. The embedded News block is restored as
native static HTML, with the six latest updates and an expandable archive. Existing external destinations have
been retained verbatim; they were not all checked for continued availability.
Nothing has been published or modified on your live Google Site.

## Homepage content review — 6 November 2026

The homepage now presents four research directions, including action-model
learning and neurosymbolic planning with GNNs, with links to the existing
bibliography. LeapNP remains in the full bibliography and is not featured on the
homepage. Project descriptions and roles were reconciled with the CV in the
Amazon proposal project; RCRA and OVERLAY are listed as scientific activities.
Project-to-paper links describe documented outputs or motivations, rather than
inferring funding from a paper's topic.

Supervision names were checked against that CV and university notifications and
working correspondence in email. Davide Leone and Simona Rusmini have ongoing
supervision documented in October–November 2026. Other lists describe supervision
without inferring graduation from a scheduled defence or a thesis approval.
Degree categories are used only where documented; the combined list avoids
guessing missing degree information. Private email content, student contact
details, student numbers and administrative documents are not included here.

Internal links in the embed use `#page/anchor` routes (for example,
`#publications/scholar-60`), while standalone pages use normal HTML links.
Opening a citation clears a publication filter if it would hide the target.
The verification script checks current source content, local anchors, embed
parity and routes, and continues checking untouched pages and bibliography
against the migration snapshot. No publication or deployment is performed by
the local build.
