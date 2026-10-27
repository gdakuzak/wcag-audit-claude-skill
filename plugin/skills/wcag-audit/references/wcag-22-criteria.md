# WCAG 2.2 Level A + AA Success Criteria — Audit Checklist

All 55 success criteria required for Level AA conformance (31 Level A + 24 Level AA),
organized by principle. For each criterion, the "What to check" text describes what to look for
in the source code. Mark a criterion N/A only when the page has no content of that kind.

Criteria marked **New in 2.2** didn't exist in WCAG 2.1 — they're the most often forgotten.

---

## Principle 1: Perceivable

### SC 1.1.1 Non-text Content (Level A)
Every `<img>` needs meaningful `alt` text (or `alt=""` if decorative). `<canvas>`, `<svg>`,
icon fonts, and CSS background images used to convey info also need text alternatives.
Check `<video>` and `<audio>` poster images. Role="img" elements need `aria-label`.
Icon-only buttons need an accessible name; decorative inline SVGs need `aria-hidden="true"`.

### SC 1.2.1 Audio-only and Video-only (Prerecorded) (Level A)
Pre-recorded audio-only needs a transcript. Pre-recorded video-only needs a transcript or
audio description. If the page has no audio/video, mark N/A.

### SC 1.2.2 Captions (Prerecorded) (Level A)
Pre-recorded video with audio needs synchronized captions (`<track kind="captions">`).
Auto-generated captions don't count unless they've been reviewed for accuracy.

### SC 1.2.3 Audio Description or Media Alternative (Prerecorded) (Level A)
Pre-recorded video needs either an audio description track or a full text transcript.

### SC 1.2.4 Captions (Live) (Level AA)
Live audio in synchronized media (streams, webinars) needs real-time captions.
N/A if there is no live media.

### SC 1.2.5 Audio Description (Prerecorded) (Level AA)
Pre-recorded video content needs an audio description track for visual-only information.

### SC 1.3.1 Info and Relationships (Level A)
Semantic HTML is the key check here:
- Headings use `<h1>`–`<h6>` (not styled `<div>`s)
- Lists use `<ul>`/`<ol>`/`<dl>`
- Tables have `<th>` and `scope` attributes
- Form inputs have associated `<label>` elements; groups use `<fieldset>`/`<legend>`
- Landmark regions: `<header>`, `<nav>`, `<main>`, `<footer>`
- Programmatic relationships match visual relationships

### SC 1.3.2 Meaningful Sequence (Level A)
DOM order matches visual order. CSS layout (flexbox `order`, grid, `position: absolute`)
shouldn't create a reading order that contradicts the source order.

### SC 1.3.3 Sensory Characteristics (Level A)
Instructions don't rely solely on shape, color, size, visual location, or sound.
"Click the green button" fails. "Click Submit" or "Click the green Submit button" passes.

### SC 1.3.4 Orientation (Level AA)
Content isn't locked to portrait or landscape. Fails: CSS/JS that rotates or blocks content
based on `orientation` media query, "please rotate your device" overlays.

### SC 1.3.5 Identify Input Purpose (Level AA)
Inputs collecting the user's own data have the right `autocomplete` token:
`name`, `email`, `tel`, `street-address`, `postal-code`, `cc-number`, `username`,
`current-password`, `new-password`, `bday`, etc. Missing or wrong `autocomplete` fails.

### SC 1.4.1 Use of Color (Level A)
Color isn't the only way to convey information. Links need underlines (or other non-color
indicator, or 3:1 contrast with surrounding text plus a non-color cue on hover/focus),
form errors need icon/text in addition to red highlighting, chart data needs patterns.

### SC 1.4.2 Audio Control (Level A)
Audio that plays automatically for >3 seconds must have pause/stop/volume control.

### SC 1.4.3 Contrast (Minimum) (Level AA)
**This is where programmatic checking happens.**
- Normal text (< 18pt / < 14pt bold): **4.5:1** minimum
- Large text (≥ 18pt / ≥ 14pt bold): **3:1** minimum
- Check ALL themes/modes
- Disabled controls, decorative text and logos are exempt

### SC 1.4.4 Resize Text (Level AA)
Text can be resized up to 200% without loss of content or functionality.
Check: no `overflow: hidden` cutting off text at 200% zoom, no fixed-height containers
that clip enlarged text, no font sizes in `px` inside `vw`-locked layouts.

### SC 1.4.5 Images of Text (Level AA)
Don't use images for text that could be rendered as actual text.
Exceptions: logos, text that's part of a photo/illustration.

### SC 1.4.10 Reflow (Level AA)
Content reflows at 320px width (400% zoom on a 1280px viewport) without horizontal
scrolling. Check for fixed-width containers, `overflow-x: auto` on body content,
two-dimensional scrolling requirements. Data tables and complex diagrams are exempt.

### SC 1.4.11 Non-text Contrast (Level AA)
**3:1 ratio** against adjacent colors required for:
- UI component boundaries (form field borders, button outlines)
- Focus indicators (outlines, rings)
- Graphical objects needed to understand content (icons, chart segments)
- Custom form controls (checkboxes, toggles, sliders) in every state

### SC 1.4.12 Text Spacing (Level AA)
Content must remain functional with: line height ≥ 1.5× font size, paragraph spacing ≥ 2×
font size, letter spacing ≥ 0.12× font size, word spacing ≥ 0.16× font size.
Check: no `overflow: hidden` / fixed heights on text containers that would clip adjusted text.

### SC 1.4.13 Content on Hover or Focus (Level AA)
Hover/focus-triggered content (tooltips, dropdowns) must be: dismissible (Escape),
hoverable (user can move the pointer onto it), persistent (stays until dismissed).

---

## Principle 2: Operable

### SC 2.1.1 Keyboard (Level A)
All functionality available via keyboard. Check: can Tab reach every interactive element?
Do custom controls work with Enter/Space? Do dropdowns work with arrow keys?
`<div onclick>` without `tabindex="0"` + key handler fails.

### SC 2.1.2 No Keyboard Trap (Level A)
Focus can always move away from any component using standard keys (Tab, Shift+Tab, Escape).
Modals must trap focus within themselves but release it when closed.

### SC 2.1.4 Character Key Shortcuts (Level A)
Single-character shortcuts (a letter, number, or symbol without a modifier) must be
turn-off-able, remappable, or only active when the component has focus.
Look for `keydown` listeners on `document`/`window` that act on `e.key` alone.

### SC 2.2.1 Timing Adjustable (Level A)
Time limits (session timeouts, auto-advancing steps, OTP expiry) can be turned off,
adjusted, or extended with a warning of at least 20 seconds. Look for `setTimeout`
redirects/logouts and `<meta http-equiv="refresh">`.

### SC 2.2.2 Pause, Stop, Hide (Level A)
Moving, blinking, scrolling or auto-updating content that starts automatically and lasts
> 5 seconds (carousels, marquees, tickers, animated backgrounds) needs a pause/stop/hide control.

### SC 2.3.1 Three Flashes or Below Threshold (Level A)
Nothing flashes more than 3 times per second. Check fast CSS `animation`s toggling
opacity/color, flashing GIFs/videos.

### SC 2.4.1 Bypass Blocks (Level A)
A way to skip repeated blocks: a "skip to main content" link as the first focusable element,
or proper landmarks (`<main>`, `<nav>`) / heading structure.

### SC 2.4.2 Page Titled (Level A)
`<title>` exists, isn't empty, and describes the page (SPAs update it on route change).

### SC 2.4.3 Focus Order (Level A)
Tab order follows a logical reading sequence. Check `tabindex` values — positive `tabindex`
disrupts natural order. `-1` is fine (programmatic focus only). `0` is fine (natural order).
Opening a dialog moves focus into it; closing returns focus to the trigger.

### SC 2.4.4 Link Purpose (In Context) (Level A)
Each link's purpose is clear from its text plus its context (sentence, list item, table cell,
heading). Several identical "Read more"/"Saiba mais" links pointing to different places
without `aria-label`/`aria-describedby` fail.

### SC 2.4.5 Multiple Ways (Level AA)
At least two ways to locate a page within a site: navigation menu, site map, search,
table of contents, links between pages. Single-page apps: provide navigation or TOC.
N/A for a single page that is a step in a process.

### SC 2.4.6 Headings and Labels (Level AA)
Headings and labels describe the topic or purpose. Generic labels like "Click here" or
"Field 1" fail unless context makes the purpose clear.

### SC 2.4.7 Focus Visible (Level AA)
Interactive elements show a visible focus indicator. Check `:focus-visible` and `:focus`
styles. If `outline: none` appears, verify a replacement is provided. Browser defaults
are acceptable but custom styles are preferred for clarity. Visually hidden native inputs
(custom checkbox/radio/switch) must show focus on their visible proxy.

### SC 2.4.11 Focus Not Obscured (Minimum) (Level AA) — **New in 2.2**
When an element receives keyboard focus, it's not entirely hidden by other content
(sticky headers, footers, cookie banners, non-modal dialogs). Partially obscured is OK at AA.
Check `z-index` layering, `position: sticky/fixed` elements, `scroll-padding`.

### SC 2.5.1 Pointer Gestures (Level A)
Anything operated by multipoint (pinch, two-finger) or path-based gestures (swipe) also
works with a single pointer without a path (tap/click buttons). Carousels driven only by
swipe fail.

### SC 2.5.2 Pointer Cancellation (Level A)
Actions fire on the up-event (`click`, `pointerup`), not `mousedown`/`pointerdown`/`touchstart`,
or can be aborted/undone. Look for destructive actions bound to down-events.

### SC 2.5.3 Label in Name (Level A)
For elements with visible text labels, the accessible name includes that visible text.
Button text "Search" should have an accessible name that contains "Search" (not just
`aria-label="Find"` when the visible text says "Search").

### SC 2.5.4 Motion Actuation (Level A)
Functions triggered by device motion (shake, tilt via `devicemotion`/`deviceorientation`)
have a UI alternative and can be disabled.

### SC 2.5.7 Dragging Movements (Level AA) — **New in 2.2**
Anything done by dragging (sortable lists, sliders, kanban cards, map panning, drop zones,
range handles) also works with single clicks/taps — e.g. move up/down buttons, click-to-place,
arrow keys on a slider *plus* a pointer alternative. File drop zones pass if a click opens
the file picker.

### SC 2.5.8 Target Size (Minimum) (Level AA) — **New in 2.2**
Interactive targets must be at least **24×24 CSS pixels**, OR have sufficient spacing
(so a 24px circle centered on the target doesn't intersect other targets or their circles).
Common failures: small navigation dots, tiny close buttons, densely packed icon buttons.
Inline links in body text are exempt.
Fix: use `::before`/`::after` pseudo-elements to create invisible 24px hit areas.

---

## Principle 3: Understandable

### SC 3.1.1 Language of Page (Level A)
`<html>` element has a valid `lang` attribute (e.g., `lang="en"`, `lang="pt-BR"`).

### SC 3.1.2 Language of Parts (Level AA)
Content in a different language than the page default has `lang` attribute on its container.

### SC 3.2.1 On Focus (Level A)
Focusing an element doesn't trigger a change of context (navigation, form submit, opening
a new window, moving focus elsewhere). Look for `focus`/`focusin` handlers that do that.

### SC 3.2.2 On Input (Level A)
Changing a setting (select, radio, checkbox, typing) doesn't automatically change context
unless the user was warned beforehand. `<select onchange="location=...">` fails.

### SC 3.2.3 Consistent Navigation (Level AA)
Navigation repeated across pages appears in the same relative order. For a single page,
compare against the site template if available; otherwise note it couldn't be verified.

### SC 3.2.4 Consistent Identification (Level AA)
Components with the same function are identified consistently (same icon + same label for
"search", "close", "download" everywhere).

### SC 3.2.6 Consistent Help (Level A) — **New in 2.2**
If help mechanisms (contact info, chat, FAQ link, help form) are repeated across pages, they
appear in the same relative order. N/A when no help mechanism exists.

### SC 3.3.1 Error Identification (Level A)
Input errors are detected and described in text, with the field identified.
Red border alone fails. Error text should be linked via `aria-describedby` and the field
marked `aria-invalid="true"`.

### SC 3.3.2 Labels or Instructions (Level A)
Inputs requiring data have visible labels or instructions, including required-field markers
and format hints (date format, password rules). Placeholder-only labels fail.

### SC 3.3.3 Error Suggestion (Level AA)
When an error is detected and a fix is known, suggest it ("Enter a date as DD/MM/AAAA",
"Did you mean gmail.com?"), unless that would compromise security.

### SC 3.3.4 Error Prevention (Legal, Financial, Data) (Level AA)
Submissions with legal/financial consequences, or that modify/delete user data, are
reversible, checked for errors with a chance to correct, or confirmed before final submit.

### SC 3.3.7 Redundant Entry (Level A) — **New in 2.2**
Information the user already entered in the same process is auto-populated or selectable,
not re-asked ("billing address same as shipping" checkbox). Exceptions: security
re-confirmation, expired info.

### SC 3.3.8 Accessible Authentication (Minimum) (Level AA) — **New in 2.2**
Login doesn't require a cognitive function test (remembering, transcribing, solving a puzzle)
unless an alternative exists. Fails: blocking paste into password/OTP fields
(`onpaste="return false"`), `autocomplete="off"` on password fields preventing password
managers, text CAPTCHAs without alternative. Object-recognition CAPTCHAs are allowed at AA.

---

## Principle 4: Robust

### SC 4.1.2 Name, Role, Value (Level A)
Custom interactive components expose correct name, role, and state to assistive tech.
Check: `role` attributes, `aria-label`/`aria-labelledby`, `aria-expanded`,
`aria-selected`, `aria-current`, `aria-checked`, `aria-pressed` on custom controls,
and that state attributes update when the state changes.

### SC 4.1.3 Status Messages (Level AA)
Status messages that appear without moving focus (toasts, "3 results found", "Saved",
form error summaries, loading/progress text, cart counters) are announced via
`role="status"`, `role="alert"`, `aria-live`, or `<output>`. The live region must exist in
the DOM before the message is injected.

---

## Summary Count

| Level | Count |
|-------|-------|
| A     | 31    |
| AA    | 24    |
| **Total** | **55** |

SC 4.1.1 (Parsing) is obsolete in WCAG 2.2 and is not counted.
New in WCAG 2.2 at A/AA: 2.4.11, 2.5.7, 2.5.8, 3.2.6, 3.3.7, 3.3.8.
