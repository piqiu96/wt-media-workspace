# Task 3 Cloud Web 账号台账展示边界

## Command / manual action

- Reworked shared account ledger page to separate Cloud Web and Desktop behavior.
- Set app identity in Cloud and Desktop entrypoints.
- Ran frontend API tests and Cloud build.

## Expected result

- Cloud Web shows Cloud-saved account and browser-window binding facts.
- Cloud Web does not present Agent / BitBrowser local operation actions for this B3 closure.
- Account list supports search, filters, tags, pagination, game names, Profile binding summary, and readable executable conclusion.

## Actual result

- Cloud Web displays an informational boundary notice:
  - Cloud Web only shows saved account and Profile binding information.
  - Binding, rebind, and later account check should be handled from Desktop.
- Removed old account-detail local execution actions from the B3 page path:
  - no account check action;
  - no Cookie import/export action;
  - no manual identify action as a false executable shortcut.
- Account page now includes:
  - search;
  - game filter;
  - platform filter;
  - business status filter;
  - login status filter;
  - tag filter;
  - list pagination;
  - remark display and maintenance;
  - Cloud Profile binding summary;
  - user-facing executable conclusion.

## Verification

- `npm --prefix web test -- --run mediaAccounts profileBindings usersApi`: PASS
- `npm run build:cloud --prefix web`: PASS

## Status

PASS
