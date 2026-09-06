# AK_predicts dashboard

A Monza motorsport editorial design with a cinematic cover, charcoal surfaces, restrained scarlet accents, team-colour podium cards, readable forecast data, and Instagram sharing.

## Features

- AK_predicts identity, metadata, favicon, and Instagram profile links.
- Responsive section navigation with active state, visible keyboard focus, and reduced-motion support.
- Forecast overview with search, sorting, and access to every existing model metric.
- Driver comparison using actual model ranks and probabilities.
- Simulator with reset, loading and error states, and prevention of stale results.
- Downloadable 1080 × 1350 PNG podium card with branding, probabilities, and the actual dataset name.
- Visible dataset provenance. Monza race information does not relabel the loaded Dutch GP forecast.
- Branded recovery screen when the prediction API is unavailable.

## Cover artwork

Generated with the built-in image generation tool. Asset: `public/monza-cover.png`. The cover is labelled as AI-generated in the dashboard. It is illustrative, not a photograph of an actual race.

Final generation prompt:

> Use case: ads-marketing. Create a cinematic editorial motorsport website cover artwork, wide 1536x1024. A scarlet red unbranded modern Formula-style open wheel racing car shot from low front three-quarter angle, car positioned entirely on the RIGHT HALF of frame, nose pointing toward lower left, on Italian racing circuit at dusk. Rich dark charcoal asphalt foreground, subtle red and white kerb bottom right, distant Italian pine trees, softly blurred grandstands with red flags, atmospheric silver-grey overcast sky and warm sunlit haze. Strong photographic panning motion blur around environment, car sharply rendered, beautiful glossy red bodywork and black carbon fiber, dramatic high-end sports magazine photography. Keep left 45 percent very dark, uncluttered and mostly empty to overlay large white website heading. Palette almost monochromatic black and charcoal with bold scarlet car. No text, no letters, no logos, no watermark. This is atmospheric illustrative artwork, not an actual race photograph.

Circuit and weekend reference: https://www.formula1.com/en/racing/2026/italy

## Validation

Passed ESLint, TypeScript, and the production Next.js build. Confirmed HTTP 200 for the page and local cover image, valid rendered section anchors, correct Instagram links, visible dataset provenance, and an HTTP 200 model simulation response. Browser connections were unavailable, so visual checks and actual click-through interaction/download testing remain unverified.
