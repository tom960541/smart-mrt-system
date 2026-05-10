# Design System

## 1. Foundation

智慧捷運路徑規劃採用工具型產品介面。畫面重點是路線查詢、票價結果、地圖定位與資料狀態。視覺應該穩定、低噪音、易掃描。

## 2. Color

- Page background: `#f5f7fb`
- Surface: `#ffffff`
- Primary text: `#16202a`
- Secondary text: `#5d6b7a`
- Border: `#d9e2ec`
- Primary action: `#0b5cab`
- Primary action hover: `#084985`
- Success: `#117a4f`
- Warning: `#a55f00`
- Error: `#b42318`
- Route accent: `#0f766e`

Avoid purple gradients, neon color combinations, low-contrast labels, and color as the only signal.

## 3. Typography

- Font stack: `"Noto Sans TC", "Microsoft JhengHei", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`
- Page title: 28-34px, 700 weight
- Section title: 18-22px, 700 weight
- Body: 15-16px, 400-500 weight
- Labels and captions: 13-14px, 500-600 weight

Use plain, compact copy. Reserve large type for page-level titles only.

## 4. Layout

- Default layout is a two-column workspace: controls on the left, map/results on the right.
- Keep related controls together: AI input, station selectors, route strategy, Google Maps origin.
- Important results should appear close to the action that produced them.
- Use 8px radius for framed surfaces.
- Avoid nested cards. Use separators and headings instead of stacking boxes inside boxes.

## 5. Components

- Buttons: direct verbs, icon optional, full width only for primary workflow actions.
- Inputs: clear labels, useful placeholders, no decorative helper text unless it prevents mistakes.
- Metrics: fare and station count should be visible before long route details.
- Alerts: concise, with a recovery path when possible.
- Map widget: compact, anchored, readable on mobile.

## 6. Interaction

- AI is an enhancement, not a dependency.
- Manual route selection must work without network/API access.
- Clicking the map alternates start and end selection with clear state feedback.
- When a route is found, the user should see fare, station count, segmented details, and route order without scrolling excessively.
