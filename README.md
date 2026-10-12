# Muhammad Subhi — Automation Developer

Single static page. No build step, no dependencies, no framework.

Live at **https://5ubh1.github.io/subhi-portfolio/**

## What this is

A one-page portfolio: what I run in production, the code you can read, and two
real failures with what they cost. Written for someone deciding whether to get
in touch.

## Editing it

Everything lives in `index.html` — CSS is embedded in a `<style>` block, there is
no JavaScript. Open it in a browser to preview; commit and push to publish.

Design tokens are CSS custom properties at the top of the `<style>` block:

```css
--paper:  #f7f5f0;   /* page background   */
--ink:    #16202b;   /* primary text      */
--muted:  #5d6b7a;   /* secondary text    */
--accent: #b4531a;   /* links, emphasis   */
```

All text colours clear WCAG AA contrast against the background (measured, not
assumed: 15.1:1 / 5.0:1 / 4.6:1).

## Publishing

GitHub Pages serves `main` from the repository root. Pushing to `main` publishes
within a minute or two.

## Licence

The text and design are mine. Please don't republish them as your own portfolio.
