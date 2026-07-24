# Account Projection Evidence

## Command / Action

Implemented Desktop account detail projection:

- Desktop account detail shows platform UID, account name, login status, execution conclusion, and last checked time.
- Desktop detail footer shows `检查账号` only when the account is enabled and bound to a browser window.
- Cloud Web does not expose the local account-check operation.
- After Local Agent returns result, Vue submits the result to Cloud and refreshes the account list/detail.

## Expected

- Users see the business result on the media account page.
- A successful check can make the account show “可进入后续预检”.
- Failed/mismatch checks preserve ledger facts and show an understandable reason.

## Actual

- `AccountsPage.vue` now uses `loginStatusText` for operator-readable login statuses.
- `executableText` remains based on Cloud saved facts.
- `checkDetailAccount()` performs:
  1. Desktop local node status read.
  2. Cloud check start.
  3. Tauri/Rust local account check.
  4. Cloud result writeback.
  5. Account list refresh.

## Verification

```text
npm --prefix web test -- --run mediaAccounts localAgentService
```

Result:

```text
Test Files 2 passed
Tests 9 passed
```

```text
npm --prefix web run build:cloud
npm --prefix web run build:desktop
```

Result:

```text
Both builds completed successfully.
```

## Result

PASS.
