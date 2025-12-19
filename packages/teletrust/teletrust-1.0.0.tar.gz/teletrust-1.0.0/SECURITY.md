# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.x.x   | :x:                |

## Reporting a Vulnerability

**DO NOT** create a public GitHub issue for security vulnerabilities.

Instead, please email security concerns directly to: **<grzywajk@gmail.com>**

Include:

1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Any suggested fixes

You will receive a response within 48 hours acknowledging receipt.

## Security Controls

### Stripe Webhook Security

- All webhooks verify `Stripe-Signature` header
- Failed verification = request rejected (fail-closed)
- Event IDs stored to prevent replay attacks (idempotency)
- Audit log for all webhook events

### API Key Security

- API keys are generated with `secrets.token_urlsafe(32)`
- Keys are never logged in full (only prefix)
- Keys can be revoked by setting account status to 'restricted'

### Secrets Management

- No secrets in source code
- All secrets via environment variables
- GitHub Secrets for CI/CD
- `.env` files in `.gitignore`

### IP Protection

- `ip_guard.yml` workflow scans for leaked secrets
- Blocks patterns: `sk_live_`, `whsec_`, `rk_live_`, `pk_live_`
- Private repos for trade secret code

## Dependency Updates

Run `npm audit` and `pip-audit` regularly:

```bash
# Frontend
cd client && npm audit

# Backend
pip install pip-audit && pip-audit
```

## Contact

Michael Ordon - <grzywajk@gmail.com>
