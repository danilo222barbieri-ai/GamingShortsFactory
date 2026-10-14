# GSF Desktop Mobile Shell V407

## Decision

Desktop is not a separate GSF interface. The existing mobile-first application is the single UI source of truth on every device.

At browser widths of 1100 px and above, the top-level Streamlit shell constrains the real app to a 480 px centered canvas. Native Streamlit rows are stacked vertically so they behave like the mobile composition, while embedded components inherit the narrow parent width and activate their existing mobile responsive rules.

Below 1100 px, V407 does not reformat the application.

## Desktop advertising rails

Wide screens use the remaining horizontal space for two fixed advertising rails. Each rail grows responsively from 220 px up to 460 px and occupies almost the full viewport height, leaving a 24 px gap from the centered mobile canvas.

V407 does not introduce a second advertising provider. `web/install_adsense_bridge.py` already installs the project's AdSense browser bridge during the Docker build. V407 extends that bridge to mirror the first two valid live AdSense slot configurations into the left and right desktop rails without removing the inline ad slots from the centered mobile UI.

When live AdSense slots are available, the rails host real AdSense placements. When live slots are not available but the existing preview slots are visible, V407 creates two geometry-only preview rails so the desktop composition can still be evaluated. When ads are off, no desktop rails are created and no fake advertisement is shown.

## Production path

The implementation is installed into Streamlit's top-level browser HTML by the existing Docker step:

`python /app/web/install_adsense_bridge.py`

This avoids modifying the generated Streamlit application, avoids an `app.py` ownership collision, and keeps the shell global across Home, Creator Hub, Crea con IA, Game Editor and publication flows.

## Contract

`web/test_v407_desktop_mobile_shell.py` verifies:

- 480 px centered mobile canvas on desktop;
- mobile-style stacking for native Streamlit columns;
- two desktop ad rails with a 460 px maximum width;
- no mobile/tablet reformatting below the desktop breakpoint;
- preservation of the mobile inline ad slots inside the centered canvas;
- live AdSense rail reuse plus preview/off rail behavior;
- Docker installation of the browser bridge.
