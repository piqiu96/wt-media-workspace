# M2 Web regression and production builds

- `npm test -- --run`: 3 files, 8 tests passed.
- `npm run build:cloud`: passed.
- `npm run build:desktop`: passed.

Vite reports the existing large-chunk advisory; it is non-blocking for the M2
acceptance gate and does not affect build success.
