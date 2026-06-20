# MCP Server Plan

## Purpose

MCP servers should support source discovery, bibliographic verification,
document storage, issue/PR workflow, and browser-based source inspection for
_The Early Works of John Gould Fletcher_. They should not replace local
page-image transcription.

## Recommended Servers

| Server | Use | Priority | Notes |
| --- | --- | --- | --- |
| Filesystem | Controlled access to this repo and adjacent source folders | High | Limit roots to `Fletcher/`, Downloads/source staging, and any explicit archive folder. |
| GitHub | Repository hosting, issues, PR review, release work | High | Useful once the edition is versioned remotely. |
| Google Drive | Shared editorial docs, scans supplied by collaborators, export/import | Medium | Already useful if source PDFs or editorial drafts live in Drive. |
| Browser / Playwright | Visual source inspection, Internet Archive/HathiTrust page checks | High | Use for source discovery and screenshots, not final transcription text. |
| Zotero | Bibliography, citation metadata, archive records | High | Best home for Fletcher bibliography and edition notes. |
| Crossref | DOI and bibliographic lookup for modern criticism | Medium | Relevant for afterword and scholarly apparatus. |
| Internet Archive | Source lookup and metadata for public-domain scans | High | Prefer an MCP server if available; otherwise use browser plus local PDFs. |
| Library of Congress | Authority records and publication metadata | Medium | Useful for author/title authority and catalog corroboration. |
| HathiTrust | Catalog verification and source location | Medium | Full-text/download constraints vary; use mainly for bibliographic confirmation. |
| SQLite | Local research index over poem metadata, source pages, notes | Medium | Useful after more volumes are transcribed. |
| Search / Fetch | Current web lookup with cited source snippets | Medium | Use for bibliography discovery and source acquisition leads; prefer primary/archive sources for facts. |

## Configuration Plan

1. Add only servers with a clear job; avoid broad connectors that duplicate local
   tools.
2. Configure filesystem roots narrowly and read-only by default where possible.
3. Store API tokens in the standard MCP/client secret mechanism, not in this repo.
4. Add a local SQLite database only after the metadata schema stabilizes.
5. Document installed MCP servers and scopes in this file.
6. Keep deterministic repo work in `machinery/tools/`; use MCP for external context,
   source discovery, and collaboration.

## Proposed Order

1. Filesystem
2. Browser / Playwright
3. Zotero
4. Internet Archive
5. GitHub
6. Google Drive
7. Crossref / Library of Congress / HathiTrust
8. Search / Fetch
9. SQLite local research index

