# SSO go-live with Auth0

Provider chosen: **Auth0** (Jun 26). The code (PR #28) is provider-agnostic and
already supports Auth0 via standard OIDC. This doc is the checklist to turn it on.
No secrets are stored in this repo - all values are env vars on prod.

## Two requirements before SSO can work in production

1. **Auth0 application credentials** (someone with the Auth0 login creates the app).
2. **HTTPS on prod.** Auth0 rejects `http://` callback URLs except for `localhost`.
   Prod is currently `http://95.216.199.47:3000` (no TLS), so the login redirect
   will not work there until prod is served over HTTPS (a domain + certificate).
   Until then, SSO can only be exercised against `http://localhost`.

## Step 1 - Create the Auth0 application

In the Auth0 dashboard: Applications -> Create Application -> **Regular Web Application**.

Settings to set:
- **Allowed Callback URLs:**
  - Dev: `http://localhost:3000/api/auth/callback`
  - Prod (once HTTPS exists): `https://<your-domain>/api/auth/callback`
- **Allowed Logout URLs:** `http://localhost:3000/`, `https://<your-domain>/`
- **Allowed Web Origins:** `http://localhost:3000`, `https://<your-domain>`

Then copy three values:
- **Domain** (e.g. `dev-xxxx.us.auth0.com`)
- **Client ID**
- **Client Secret**

## Step 2 - Set the prod env (backend/.env on /opt/ai-pathway)

```
OIDC_ENABLED=true
OIDC_ISSUER=https://<your-auth0-domain>      # e.g. https://dev-xxxx.us.auth0.com
OIDC_CLIENT_ID=<client id>
OIDC_CLIENT_SECRET=<client secret>
OIDC_REDIRECT_URI=https://<your-domain>/api/auth/callback   # or http://localhost:3000/... for dev
OIDC_POST_LOGIN_REDIRECT=/
SESSION_SECRET=<generated 48-byte url-safe secret - provided out of band, never commit>
SESSION_TTL_HOURS=12
```

The settings keys map to `config.py` (`oidc_*`, `session_secret`). `OIDC_ISSUER`
is the Auth0 domain with `https://` and NO trailing slash; discovery is read from
`{issuer}/.well-known/openid-configuration` automatically.

## Step 3 - Map email domains to orgs (optional, recommended)

So enterprise users land in their org automatically: set each Organization's
`domain` (via the org API) to the company's email domain. On login,
`org_id_for_email` assigns the user to the matching org, else the default org.

## Step 4 - Restart + verify

- Restart the backend so it picks up the env (`docker compose up -d` on prod).
- `GET /api/auth/status` should return `{"enabled": true}`.
- Visit `/api/auth/login` -> redirects to Auth0 -> after login, `/api/auth/me`
  returns the user with their `org_id`.

## Still deferred (next increment, after SSO is on)

- Enforce auth on learner-facing routes (a `require_user` 401 dependency).
- Frontend login UI (sign-in button gated on `/api/auth/status`).
- Per-entity org scoping + tenant isolation (multi-tenancy increment 2).
