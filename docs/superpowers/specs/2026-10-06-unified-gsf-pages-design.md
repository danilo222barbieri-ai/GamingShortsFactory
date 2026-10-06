# Gaming Shorts Factory — Unified Page System Design

Date: 2026-10-06
Status: design approved in conversation; pending written-spec review
Base: `fix/v294-home-desktop-realign` (`7fa9952d099b1c073ee3e24a763ace66efcce05a`)
Scope version: V296 design, with V295 Creator Hub/Profile included as the first page conversion

## 1. Goal

Make Home, Crea con IA / Motori, Game Editor, Crea Short / Pubblica o scarica, and Creator Hub feel like one coherent Gaming Shorts Factory product rather than separate overlays with unrelated proportions.

The visual system must preserve the approved GSF language: light pastel/metallic blue surfaces, white canvas, soft glass borders, rounded geometry, the current global font family, restrained handwritten murals, and the existing product logic. The work is presentation/navigation architecture only unless a route needs a small bridge to an already-existing section.

Success means:

- every desktop page is visually centered and balanced on common laptop/desktop resolutions;
- the central task is always the dominant visual element;
- ads support the page instead of squeezing or displacing the product content;
- page-to-page transitions preserve the same visual vocabulary;
- the global Game Bar uses the same destinations everywhere and replaces `Social` with `Le mie Live` on both desktop and mobile;
- Profile opens as a clean white Creator Hub overlay with no ads and no Game Bar;
- mobile does not shrink complex operational pages into unreadable one-screen layouts: Home remains compact, while content-heavy pages may scroll vertically;
- existing AI, Editor, render, upload, social-account, project, and Creator Hub logic is preserved.

Live-page redesign is explicitly out of scope. Only the Game Bar destination to the existing Live section is included.

## 2. Architectural choice

Use a **shared GSF page shell plus page-specific content layouts**.

Do not continue stacking unrelated full-page CSS overrides, and do not rewrite the application from scratch. The current runtime logic remains mounted; the new page system becomes the authoritative presentation/navigation layer.

The shell owns:

- canvas/background;
- global typography tokens;
- central content axis and desktop max-width rules;
- desktop ad rails;
- bottom banner slot;
- footer spacing;
- global Game Bar appearance and routing;
- responsive breakpoints and safe areas;
- shared card, icon, button, border, shadow, and spacing tokens.

Each page owns only its central task layout and page-specific murals/help text.

This keeps page geometry consistent while allowing Motori, Editor and Crea Short to have different center structures.

## 3. Shared desktop geometry

Desktop breakpoint begins at 761 px, with primary calibration for 1366×768 through 1920×1080.

The shell uses three visual columns:

`left ad/support rail | centered product content | right ad/support rail`

Rules:

- center content is horizontally centered to the viewport, not centered in the leftover space after arbitrary side offsets;
- left/right ad rails are symmetric and never determine the width of the product area;
- side ads use restrained widths and heights similar to the corrected V294 Home proportions;
- product content receives a page-specific max-width but shares the same center axis;
- footer/banner/Game Bar align to the same center axis;
- no desktop page may inherit phone-scale widths or transforms;
- no page-specific transform should be used merely to compensate for another page's shell.

The V294 Home geometry remains the reference for balance, not a source to duplicate blindly.

## 4. Shared visual language

### Palette

- primary canvas: white to very pale blue;
- primary accent: pastel metallic/light blue already used by Home;
- secondary editor accent may retain the approved soft mint identity;
- final-create emphasis may retain the approved pale warm/yellow accent where already used;
- text: dark desaturated navy;
- secondary text: muted blue-gray;
- borders: low-contrast blue-gray glass lines;
- shadows: soft, shallow and consistent.

### Typography

Use one global product font family everywhere except handwritten mural text. Preserve the larger V281 typography policy rather than reverting to small historical type.

### Shapes

- main cards: rounded rectangles with consistent corner radius;
- icon containers: square/rounded-square, not unrelated pill shapes;
- controls: large enough to read and click at normal desktop distance;
- handwritten murals remain decorative guidance, not primary instructions.

## 5. Global Game Bar

The authoritative Game Bar destinations are:

1. Home
2. Hub / Creator Hub
3. I miei Shorts
4. Bozze
5. Le mie Live

`Social` is removed from the Game Bar on both desktop and mobile.

`Le mie Live` must route to the already-existing Creator Hub Live section, not to a dead placeholder.

The Game Bar is global on ordinary app pages, but **is intentionally hidden inside the Profile overlay**. Profile uses a single top-left/back control: `← Torna al tuo Creator Hub`.

The Game Bar must not be recreated differently per page. Page shells may render it in different physical positions for responsive reasons, but labels, icons, routes and active-state semantics come from one source of truth.

## 6. Home

Home stays conceptually as currently approved and receives the V294 desktop realignment already implemented on its branch.

Desktop requirements:

- compact centered upload circle;
- three CTA cards aligned beneath it: Crea con IA, Game Editor, Crea Short;
- readable desktop Game Bar width;
- murals close enough to the upload circle to read as guidance, not detached decoration;
- ad rails supportive and smaller than the main product content;
- no page scroll on normal desktop resolutions;
- current larger global typography is retained.

Mobile Home remains compact and keeps its current no-scroll policy. Mobile murals are not changed by this work.

## 7. Crea con IA / Motori page

This page follows the user's paper layout as the authoritative information hierarchy.

Desktop vertical flow:

1. centered title: `Scegli il tuo motore IA`;
2. four engine controls in one clear row near the top;
3. large central area: `I 3 migliori momenti`;
4. two primary next actions below the moments: Game Editor and Crea Short;
5. horizontal banner slot;
6. global Game Bar and footer.

Left and right desktop ad rails flank the center without compressing it.

The selected engine needs a strong but tasteful selected state. The three moments must visually dominate the page after analysis; engine controls must not stay larger than the results.

Handwritten guide text may point toward engine selection and the three moments, but must not overlap cards or video previews.

Existing four-engine behavior and candidate-selection logic remain unchanged.

## 8. Game Editor page

This page follows the rotated paper sketch as the authoritative geometry.

Desktop hierarchy:

1. centered title: `Modifica il tuo gameplay`;
2. one large Editor/player workspace centered in the page;
3. left and right desktop ad rails;
4. contextual handwritten/help elements in the free space between content and rails where safe;
5. horizontal banner under the Editor;
6. global Game Bar and footer.

The Editor must be the largest single object on the page. No secondary panel may reduce it to a preview-sized player.

Existing Game Editor controls, HUD, player behavior, selection state and rendering logic remain intact. The new work only changes page composition and presentation unless an existing control is currently unreachable because of page-shell layering.

## 9. Crea Short / Pubblica o scarica page

This page follows the user's paper sketch as the authoritative hierarchy.

Desktop vertical flow:

1. centered title: `Pubblica o scarica`;
2. mini preview of the final Short near the top center;
3. `Pubblica su` row with the available social destinations represented by large, recognizable controls;
4. lower split area with `Scarica su` on the left and `Condividi su` on the right;
5. horizontal banner;
6. global Game Bar and footer.

Left/right ad rails remain present on desktop.

The final Short preview is the visual anchor. Publishing, sharing and download controls must read as three clear outcome families rather than one long form.

Existing account-connect and publish/download behavior remains authoritative. This design does not reintroduce obsolete publication-detail forms.

## 10. Creator Hub

Creator Hub remains a product dashboard, not a full advertising page.

Desktop Hub requirements:

- centered page composition using the same GSF shell;
- account identity block at the top;
- readable, adequately sized modules for Profile, Projects, Live, Social/account connections and Subscription;
- folders/cards must not be stretched into very wide, shallow strips;
- the layout must use the available center area rather than reducing content to tiny type to avoid scrolling;
- ordinary Creator Hub may use the global Game Bar;
- its Live module is the destination for the new `Le mie Live` Game Bar item.

The current Hub data/state bridge remains unchanged.

## 11. Profile overlay

Profile is intentionally different from ordinary secondary pages.

On desktop, clicking Profile opens a **compact white overlay above Creator Hub** rather than opening the advertising page shell.

Profile overlay rules:

- white/very pale canvas;
- centered compact panel sized to its content;
- no left/right ads;
- no banner ad;
- no global Game Bar;
- top control: `← Torna al tuo Creator Hub`;
- underlying Creator Hub remains the return context;
- contains photo/avatar editing, creator name, Shorts created, drafts, current plan/subscription, connected social/account state, and existing management controls;
- no duplicate Creator Hub navigation inside Profile.

The overlay should feel like a focused account sheet, not a separate website page.

Mobile Profile is not redesigned in the first desktop phase. Its existing behavior is preserved until the later mobile pass.

## 12. Responsive/mobile contract

The initial implementation is desktop-first, but new shared code must not hard-code assumptions that prevent the later mobile pass.

Immediate mobile requirements:

- Home remains as currently approved and no-scroll;
- Game Bar label/route replacement `Social → Le mie Live` applies immediately on mobile too;
- existing mobile murals are preserved;
- no desktop-only ad rail may appear on mobile;
- no desktop page CSS may shrink mobile content unintentionally.

Later mobile pass policy already agreed:

- complex operational pages such as Motori, Game Editor and Crea Short may use natural vertical scrolling;
- readability and touch target size take priority over fitting everything on one viewport;
- pages that genuinely fit well in one screen may remain no-scroll;
- do not force a one-screen layout by making players, text or controls too small.

## 13. Navigation and data flow

The new page system does not own application data. It consumes existing state and emits navigation actions.

Navigation flow:

- Home CTA `Crea con IA` → Motori page;
- Home CTA `Game Editor` → Editor page;
- Home CTA `Crea Short` → final Crea Short page when a final selection exists, otherwise preserve existing guard/flow;
- Motori selection → existing AI analysis flow → three candidate moments;
- candidate moment → existing selection state;
- Motori action `Game Editor` → Editor with selected moment/video loaded;
- Motori action `Crea Short` → existing final-create path;
- global Game Bar `Hub` → Creator Hub dashboard;
- global Game Bar `I miei Shorts` → existing Shorts section;
- global Game Bar `Bozze` → existing drafts section;
- global Game Bar `Le mie Live` → existing Hub Live section;
- Creator Hub Profile → Profile overlay;
- Profile back → same Creator Hub context, without resetting upload/project state.

No navigation action may silently clear the current upload, selected moment, draft or project unless the existing application flow explicitly requires it.

## 14. Error and empty states

The visual redesign must preserve or improve clarity of existing states:

- no uploaded video: CTA requiring video shows the existing guard message instead of opening a broken page;
- AI analysis pending: results area shows a clear active/loading state while retaining page geometry;
- no spoken track: retain the existing `Nessuna traccia parlata` behavior;
- no Shorts/drafts/live items: show a centered empty state within the appropriate module, not a collapsed box;
- social account not connected: publishing control routes to the existing connection flow without resetting the project;
- Editor cannot load selected media: show a visible recoverable error and a route back, never a blank player;
- Profile data unavailable: render the overlay shell and a compact retry/recovery state rather than reopening the advertising shell.

## 15. Implementation boundaries

This project may modify:

- shared UI/page shell modules;
- page-specific HTML/CSS/JS components;
- page navigation bridge code;
- Creator Hub presentation layer;
- startup patch ordering when needed to make the authoritative page layer load last;
- regression tests for layout markers, routes and page-shell ownership.

This project must not modify unless a failing integration test proves it necessary:

- render codec/quality settings;
- V293 render-memory guard;
- AI ranking/scoring behavior;
- Whisper/caption timing logic;
- upload/materialization pipeline;
- social API credentials/authentication protocols;
- database/storage semantics.

## 16. Testing strategy

### Static/contract tests

Create tests that assert:

- one authoritative shared Game Bar definition;
- `Social` is absent from Game Bar labels and `Le mie Live` is present;
- `Le mie Live` maps to the existing Hub Live route;
- Profile overlay explicitly suppresses ads and Game Bar on desktop;
- page-specific shell markers exist for Home, Motori, Editor, Crea Short and Creator Hub;
- desktop CSS is scoped to desktop media queries and does not overwrite mobile mural/layout selectors;
- V293 startup/render hooks remain present and unchanged.

### Runtime smoke tests

On an isolated Railway service:

- Home loads without horizontal/vertical desktop overflow at representative viewport sizes;
- each CTA opens the intended page without resetting state;
- Creator Hub folders remain clickable;
- Profile opens/returns without page reload or state loss;
- global Game Bar destinations work from every ordinary page;
- Game Bar Live destination opens the existing Live section;
- Editor still loads media;
- Crea Short still exposes working publish/share/download controls;
- no page produces a blank iframe/component.

### Visual acceptance

Check at minimum:

- 1366×768 desktop;
- 1440×900 desktop;
- 1920×1080 desktop;
- one iPhone-size viewport only as a regression check during the desktop phase.

Acceptance focuses on center-axis alignment, symmetry of side rails, readable type, non-overlapping murals, consistent card geometry, and unchanged mobile Home.

## 17. Rollout order

1. Merge and verify V294 Home desktop realignment.
2. Build shared GSF page-shell/navigation source of truth.
3. Convert Creator Hub desktop and Profile overlay first, because they currently expose the largest desktop inconsistency.
4. Convert Motori page to the new shell.
5. Convert Game Editor page.
6. Convert Crea Short / Pubblica o scarica page.
7. Run full desktop visual/navigation regression suite.
8. Deploy to isolated Railway service and verify.
9. Merge to production only after the isolated build is green.
10. Start the dedicated mobile page pass later; do not redesign Live in this scope.

## 18. Non-goals

- redesigning the Live product page;
- changing AI engine behavior;
- adding new social providers;
- replacing Streamlit/backend architecture;
- forcing all mobile pages to fit in one viewport;
- changing the approved mobile Home murals;
- adding more advertising to Profile or Creator Hub account-management surfaces.
