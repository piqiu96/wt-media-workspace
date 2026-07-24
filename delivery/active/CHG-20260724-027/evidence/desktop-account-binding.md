# Task 4 Desktop 账号与窗口绑定入口

## Command / manual action

- Reworked the shared account ledger page so Desktop can expose binding controls while Cloud Web stays view-oriented.
- Ran Desktop build.

## Expected result

- Desktop account page can create ledger records and optionally bind an authorized active browser window.
- Desktop account detail can bind, unbind, or rebind a window.
- The page explains that binding / rebind returns the account to a pending-check state.
- The page does not perform account check in B3.

## Actual result

- Desktop detects `window.__WT_MEDIA_APP__ === "desktop"`.
- Desktop create dialog includes an authorized active Profile selector.
- Desktop detail drawer includes a Profile selector for bind / unbind / rebind.
- Binding changes call Cloud business APIs only; no Agent / BitBrowser call is introduced in B3.
- Account check remains excluded from this CHG and will be handled in B4.

## Verification

- `npm run build:desktop --prefix web`: PASS
- Frontend API test covers bind and unbind client calls: PASS

## Status

PASS
