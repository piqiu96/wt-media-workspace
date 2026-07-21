# Proxy page empty-list fix

## Root cause

With an empty `proxy_configs` table, the MySQL list implementation returned a
nil slice. JSON encoded it as `data: null`; `ProxyPage.vue` then accessed
`proxies.length`, causing a render exception and leaving the page unusable.

## Fix

- Cloud initializes list results as an empty slice, producing `data: []`.
- Web normalizes legacy/null responses to an empty array before rendering.

## Verification

- Reproduced the authenticated page against the local MySQL-backed Cloud.
- After reload, `/proxies` renders the table and `暂无代理`/`共 0 条数据` instead
  of the previous `TypeError: Cannot read properties of null (reading 'length')`.
- Web tests: 8/8 passed; Cloud and Desktop builds passed.
