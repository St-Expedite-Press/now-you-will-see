# Book Covers — File Naming Schema

## Pattern

```
{author}_{book}_{role}_{variant}.{ext}
```

| Segment | Description |
|---|---|
| `author` | Author's last name, lowercase |
| `book` | Short title slug, lowercase, words separated by hyphens |
| `role` | Image function: `cover` or `art` |
| `variant` | Distinguishing characteristics, lowercase, words separated by hyphens |
| `ext` | File extension (`png`, `jpg`, etc.) |

---

## Roles

| Value | Meaning |
|---|---|
| `cover` | Complete book cover — includes all text and artwork |
| `art` | Standalone artwork or background element — no text |

---

## Variant Conventions

**For `cover` files:**

| Value | Meaning |
|---|---|
| `bw-left` | Black-and-white; title text positioned on the left |
| `bw-right` | Black-and-white; title text positioned on the right |
| `sepia` | Warm sepia / cream color palette |

**For `art` files:**

| Value | Meaning |
|---|---|
| `tree` | Ink tree silhouette, no other figures |
| `tree-birds` | Ink tree silhouette with bird figures |

---

## Current Files

| File | Description |
|---|---|
| `early_works_fletcher/fletcher_early-works_cover_bw-left.png` | Landscape cover, B&W, title text on left |
| `early_works_fletcher/fletcher_early-works_cover_bw-right.png` | Landscape cover, B&W, title text on right |
| `early_works_fletcher/fletcher_early-works_cover_sepia.png` | Cover with warm sepia/cream palette |
| `early_works_fletcher/fletcher_early-works_art_tree-birds.png` | Ink tree artwork with two birds, no text |
| `early_works_fletcher/fletcher_early-works_art_tree.png` | Ink tree artwork, no birds, no text |
