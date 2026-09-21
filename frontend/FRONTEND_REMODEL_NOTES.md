# AI Donations Frontend Remodel

## Visual direction
- Violet + Gold professional SaaS-style visual system.
- Primary: `#6D28D9`
- Primary hover: `#5B21B6`
- Gold accent: `#D4A72C`
- Light background: `#FAFAF9`
- Soft violet: `#F5F3FF`
- Dark background: `#111113`
- Dark card: `#1C1C20`

## Dashboard improvements
- Rebuilt donor dashboard presentation to match the approved Violet + Gold reference.
- Preserved the existing `my-donations/` API and derives all counters from returned donation data.
- No fake donation amounts or fabricated backend metrics were introduced.
- Added responsive hero, progress summary, latest donation list, quick actions, impact banner and dark mode support.
- Fixed the ThemeToggle inline red background so it now follows the selected theme.

## Safety
- Existing routes and API calls remain intact.
- Visual changes are isolated to the frontend presentation layer.
