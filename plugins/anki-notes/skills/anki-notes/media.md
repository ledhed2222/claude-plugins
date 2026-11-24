# Media on cards

Read this when a draft would teach better with a picture or a sound. "Vary the shape" in `SKILL.md` says when; this file says how to source the file, store it and place it.

## Pick the kind

- **Structure or process** (tiers, a flow, a cycle, a layout): draw a diagram yourself as SVG.
- **Recognized by sight** (a colour, a shape, a place, a label, a car): a photo from Wikimedia Commons with a free licence, or one the user supplies. If a diagram shows it as well (a colour swatch strip, a silhouette), draw that instead: it's faster and needs no licence.
- **Sound** in a language deck: Anki's built-in speech, `{{tts <lang>:<Field>}}` in the note type (see `note-types.md`), not a stored audio file.
- **The user's own** photo or screenshot: use it as they gave it.

## Draw a diagram

- Write SVG by hand: a `viewBox`, an opaque light background `<rect>` covering it (an `<img>` keeps its own colours, so without one the strokes vanish in night mode), generic fonts (`font-family="sans-serif"`; an SVG in an `<img>` can't load the deck's fonts), and text at least 12 units high in a 320-unit-wide view, so it stays legible on a phone.
- Label what the card asks about only on the back. A front image must not show the answer (no title naming it, no label on the part asked for).
- Name the file after what it shows, in lowercase with hyphens: `solera-tiers.svg`.

## Find a photo on Wikimedia Commons

Search with whatever web tool you have, through Commons' API, which returns each file's licence:

`https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrlimit=5&gsrsearch=<terms>&prop=imageinfo&iiprop=url|mime|extmetadata&iiurlwidth=800`

- **Use a file only if `extmetadata.LicenseShortName` is CC0, Public domain, CC BY or CC BY-SA** (any version). Anything else, a missing licence, NC or ND, or "fair use", is out. So are images from anywhere but Commons or the user, and generated images presented as photos.
- Take the 800-pixel `thumburl` (JPEG or PNG), not the original: it stays well under the server's media size limit.
- **Credit** it on the back, after the answer, in the deck's context line (`Why/Example`, or the field Conventions names): `<small>Photo: <Artist>, <licence>, Wikimedia Commons</small>`, with the artist's name as plain text.
- **If no file qualifies**, say so, and offer to draw a diagram or ask the user for a photo of their own. Never use one that doesn't.
- With no web tool, propose the photo instead: say what it would show and the Commons search, and add it when the user supplies the file.

## Store it

Files are SVG for diagrams, and JPEG or PNG for photos: both servers accept them and every Anki app shows them.

- **local:** write the file, then `store_media_file(filename, path)` with its absolute path; for a Commons photo, `store_media_file(filename, url)` with the `thumburl`.
- **remote:** `anki_media_store(filename, content_base64, idempotency_key)`, with the file's bytes as base64 (`base64 < file | tr -d '\n'`). A drawn SVG is a few kilobytes, so that's quick; a photo is tens of kilobytes, which takes minutes to send this way, so on remote propose a photo the way you would with no web tool and add it only when the user asks.

Then refer to it in a field as `<img src="solera-tiers.svg">`. Put it on the back, unless the card is a spotting card that shows the picture and asks what it is.

## How much

- One diagram can back two or three cards; more than that and the deck leans on one picture.
- No media on abstract facts, numbers or definitions with nothing to see, and nothing decorative: no stock photo of a barrel next to a card about glycerol.
- The charter's `Media:` line wins: `Media: none` means no media at all.
