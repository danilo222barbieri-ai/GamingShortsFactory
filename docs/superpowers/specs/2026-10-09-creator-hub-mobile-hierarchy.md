# V357 Creator Hub Mobile Hierarchy Spec

## Scope
Mobile Creator Hub only (`max-width: 767px`). Desktop, global Game Bar, global footer, routing and stored data are out of scope.

## Projects / Shorts / Drafts
- Remove the legacy component header that duplicates the internal Projects/Shorts/Drafts title.
- Keep one internal title only.
- Give the content clear breathing room below the global app header.
- Keep Shorts and Drafts content/actions unchanged.

## Live
- Remove duplicate Live headings/copy from the mobile root.
- Main Live screen contains exactly two primary folder cards: Twitch and YouTube.
- Root Live screen must fit without vertical scrolling.
- Tapping a platform opens its detail level.
- Each detail level exposes Le tue live, VOD and Highlights using the existing Live mini-folder elements and handlers.
- Provide a clear back control to return to the two-folder Live root.

## Profile / Social
- Increase vertical breathing room on the Profile main screen.
- Keep Profile edit and Subscription functionality unchanged.
- Replace the expanded Social rows on the Profile main screen with one Social collegati folder card.
- Tapping Social collegati opens a dedicated Social detail level containing the original YouTube, TikTok, Instagram, Facebook and Twitch rows.
- Preserve existing connect/disconnect behavior and connection states by reusing the original rows, not cloning them.
- Provide a clear back control to return to Profile.
- Main Profile screen should fit without page scrolling on standard iPhone heights.

## Shared constraints
- Use the existing GSF pastel/glass visual language and card geometry.
- Do not modify desktop layout.
- Do not modify the global Game Bar or footer.
- Do not introduce new social or Live backend behavior; preserve current handlers and state.
- Patch must be restart-safe and run after V352 so it can intentionally supersede V313/V352 mobile layout rules.