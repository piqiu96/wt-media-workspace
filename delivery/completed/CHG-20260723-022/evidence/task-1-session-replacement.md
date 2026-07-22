# Task 1 Evidence: 会话替换确认

## 1. Scope

Task 1 implements only the M2-A2 login replacement slice:

- an active old session requires explicit replacement confirmation;
- unconfirmed replacement does not invalidate the old session;
- confirmed replacement invalidates the old session and creates a new session;
- Web login shows a Chinese confirmation prompt before retrying with `replace_existing=true`.

It does not implement Desktop status, BitBrowser identity binding, or sensitive local entry guards.

## 2. Implementation facts

Changed files:

- `wt-media-cloud/internal/modules/identity/service.go`
- `wt-media-cloud/internal/modules/identity/routes.go`
- `wt-media-cloud/internal/modules/identity/store_mysql.go`
- `wt-media-cloud/internal/modules/identity/service_test.go`
- `wt-media-cloud/internal/modules/identity/routes_test.go`
- `wt-media-cloud/internal/modules/identity/store_mysql_test.go`
- `wt-media-cloud/web/src/shared/api/session.js`
- `wt-media-cloud/web/src/modules/auth/pages/LoginPage.vue`

Behavior:

- `POST /api/v1/auth/login` accepts `replace_existing`.
- Without `replace_existing`, a login for a user with an active session returns HTTP 409 / `errcode=20010`.
- With `replace_existing=true`, Cloud invalidates the previous active session and issues a new HttpOnly cookie.
- Web catches `errcode=20010`, asks the user whether to replace the old session, and only retries when confirmed.

## 3. Automated verification

Command:

```text
GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build go test ./internal/modules/identity
```

Result:

```text
ok  	github.com/wt-media/wt-media-cloud/internal/modules/identity	6.582s
```

Command:

```text
npm run test
```

Result:

```text
Test Files  5 passed (5)
Tests       14 passed (14)
```

Note:

`npm run test -- --runInBand` was attempted first and failed because Vitest does not support that Jest option. The project script was rerun without the unsupported option and passed.

## 4. Real MySQL + Cloud API verification

Environment:

- MySQL: `127.0.0.1:3306`
- Database: `wt_media_m2_a1_web_acceptance`
- Cloud: `127.0.0.1:18080`
- Admin user: `m2a1_admin`

Operation:

1. Login with `replace_existing=true` to create a known old session.
2. Login again without `replace_existing`.
3. Verify response is 409 / `errcode=20010`.
4. Verify old cookie still accesses `/api/v1/auth/me`.
5. Login again with `replace_existing=true`.
6. Verify old cookie is rejected and new cookie accesses `/api/v1/auth/me`.

Actual result:

```text
first {'errcode': 0, 'message': 'success', 'username': 'm2a1_admin'}
blocked {'errcode': 20010, 'message': '当前账号已在其他位置登录，请确认是否替换旧会话', 'username': None}
old_me_before_confirm {'errcode': 0, 'message': 'success', 'username': 'm2a1_admin'}
confirmed {'errcode': 0, 'message': 'success', 'username': 'm2a1_admin'}
old_me_after_confirm {'errcode': 11001, 'message': '请先登录或凭证已过期', 'username': None}
new_me {'errcode': 0, 'message': 'success', 'username': 'm2a1_admin'}
blocked_http_status 409
old_after_confirm_http_status 401
```

Result: PASS.

## 5. Browser page verification

Operation:

- Opened Cloud Web login page at `http://127.0.0.1:5173/login`.
- Submitted `m2a1_admin` credentials while an active session already existed.

Actual result:

- Browser observed a JavaScript `confirm` dialog from the login page.
- Confirmed path reached Dashboard with current user `m2a1_admin`.

Limitation:

- The in-app browser runtime did not preserve the dialog object long enough for a stable scripted dismiss path. The cancel/no-replacement semantics are therefore verified by API evidence above, not by a browser screenshot.

Result: PASS with noted limitation.

