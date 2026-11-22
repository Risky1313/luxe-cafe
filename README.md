# Luxe Café

Our recipe site for the Ninja Luxe Café Pro (ES701): https://risky1313.github.io/luxe-cafe/

- 77 recipes: Ninja's own Luxe Café recipes plus 5 well-reviewed outside picks per style, each rewritten as exact Luxe Café Pro steps with a link to the original.
- Style dial, search and filters (hot/iced, milk/no milk, quick/fancy, Ninja originals).
- Shared favorites, ratings and notes for everyone in your kitchen, a shared shopping list, live sync between phones.
- Brew mode (step by step, screen stays on, shot timer and countdowns), taste fixer for sour, bitter or watery coffee, dark mode.

## How it's put together

| File | What it is |
| --- | --- |
| `app-src.html` | The app itself (styles, screens and logic). |
| `web.js` | Firebase sign-in (Google or email) and Firestore live sync. Without a Firebase config the app still works and saves on the device only. |
| `firebase-config.js` | The Firebase web config (not a secret). |
| `firestore.rules` | Paste into Firebase console › Firestore Database › Rules › Publish. |
| `build.js` | `node build.js` builds `index.html` and `version.json`. Bump `APP_V` in `app-src.html` with every change so phones reload the new version. |
| `recipes/build_recipes.py` | The recipe list. `python3 recipes/build_recipes.py` writes `recipes/recipes.json` and refuses duplicate ids, names or drinks. |
| `recipes/looks.py`, `recipes/build_prompts.py` | What each drink looks like, turned into ChatGPT image prompts (`recipes/image-prompts.md`). |
| `images/credits.json` | The real drink photos: each one is a free Unsplash photo (Unsplash License, free to use). Lists the photo and photographer; the recipe page shows a small credit in the photo's corner. |
| `tools/add_photos.py` | `python3 tools/add_photos.py <folder>` turns `<recipe-id>.png` pictures into `images/<recipe-id>.webp`. Until a drink has a photo, the site draws a simple illustration. |

## Sharing a kitchen

Each person signs in with their own account. The first person gets a kitchen automatically; the invite link in the profile sheet (`…/#join-<kitchen id>`) lets someone else join it. Favorites, ratings, notes and the shopping list are shared inside the kitchen only.

## Adding a recipe

1. Add an `R(...)` entry in the right category in `recipes/build_recipes.py`, and a matching line in `recipes/looks.py`.
2. `python3 recipes/build_recipes.py && python3 recipes/build_prompts.py`
3. Bump `APP_V` in `app-src.html`, then `node build.js`.
