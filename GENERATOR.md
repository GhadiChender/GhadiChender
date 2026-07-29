# How the terminal cards are generated

Both images at the top of the profile are **plain SVG files committed to this repo**.
Nothing is rendered at request time — no third-party image service, no headless
browser, no font embedding. They are generated locally by two small Python
scripts and committed as build output.

| Script | Output | What it draws |
| --- | --- | --- |
| `ascii_to_svg.py` | `dark.svg`, `light.svg` | neofetch-style card: ASCII portrait + info pane |
| `stats_card.py` | `stats-dark.svg`, `stats-light.svg` | year-in-review metric strip |

## Running them

```bash
pip install pillow          # ascii_to_svg.py only; stats_card.py is stdlib
python3 ascii_to_svg.py     # -> dark.svg, light.svg
python3 stats_card.py       # -> stats-dark.svg, stats-light.svg
```

## The ASCII portrait

`ascii_to_svg.py` turns `assets/ninja.jpg` into text in four steps:

1. **Downsample.** The image is converted to greyscale, contrast-boosted, cropped
   to the pane's aspect ratio (biased toward the top so the face survives the
   crop), then resized to a `COLS × ROWS` grid — one pixel per character cell.
2. **Map luminance to a character.** Each cell's brightness `v ∈ [0,1]` indexes
   into a ramp ordered dark → bright:

   ```python
   RAMP   = " .`':;~-=+*x#%@"
   THRESH = 0.042   # below this -> background, keeps the card from looking muddy
   GAMMA  = 0.40    # lifts shadows so the figure fills densely
   ```

   `THRESH` and `GAMMA` are the two knobs that decide whether the result reads as
   a portrait or as noise. Tune those first.
3. **Bucket the colors.** The same brightness value also picks from a short
   per-theme palette, so the art is a gradient rather than monochrome.
4. **Emit runs, not characters.** Adjacent cells sharing a color bucket are
   merged into a single `<tspan>`. That is the whole trick for keeping the file
   small — a naive one-`<tspan>`-per-character card is enormous; run-length
   encoding brings it to ~48 KB.

The info pane on the right is a declarative list of `("kv", (key, value))` tuples.
Dot leaders are computed per line from the pane width so keys and values stay
aligned in the monospace grid without measuring text.

## Light and dark

Each script emits two files from one `THEMES` dict, and the README picks between
them with `<picture>`:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="light.svg">
  <img alt="..." src="dark.svg" width="100%">
</picture>
```

## Fonts

The SVG asks for a monospace stack
(`ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace`) and the
layout is computed from fixed cell metrics (`CW_A`, `CH_A`), so the grid holds up
across viewers even when the exact font differs.

## Adapting it

Drop your own image at `assets/ninja.jpg` (or change `IMG`), edit the `INFO`
list, tune `THRESH` / `GAMMA` until the portrait reads, and re-run. Everything
else — sizing, palette, dot leaders — follows from the constants at the top of
the file.

## The snake

The contribution snake below the cards is not from these scripts — it is
[`Platane/snk`](https://github.com/Platane/snk), run on a schedule by
`.github/workflows/snake.yml` and pushed to the `output` branch.
