# 🛡️ AutoMind AI — Security Policy & Operational Hardening Guide

## 1. Scope & Security Posture
AutoMind AI is designed with a zero-trust, production-hardened security model. This document defines mandatory secret management rules, credential rotation workflows, and operational policies for developers and deployment operators.

---

## 2. Mandatory Secret Generation & Rotation Guidelines

Before any staging or production deployment, **all default and development credentials must be rotated**:

1. **Required Secrets to Rotate:**
   - `APP_SECRET`: Primary application cryptographic signing key.
   - `JWT_SECRET`: Signing key for JSON Web Tokens (must be distinct from `APP_SECRET`).
   - `DATABASE_URL` / `MYSQL_PASSWORD`: Production database credentials.
   - `MYSQL_ROOT_PASSWORD`: Container or managed database root password.
   - External Search / LLM API Keys (DuckDuckGo, OpenAI, vLLM, etc., where configured).

2. **How to Generate Strong Cryptographic Secrets:**
   Never use dictionary words, predictable strings, or development placeholders. Generate 256-bit entropy keys using OpenSSL:
   ```bash
   # Generate APP_SECRET
   openssl rand -hex 32

   # Generate JWT_SECRET
   openssl rand -hex 32

   # Generate Database Password
   openssl rand -base64 24
   ```

3. **Protection of Secrets:**
   - **Never** commit `.env` or production environment files into Git.
   - **Never** paste credentials or API keys into issue trackers, pull request discussions, chat logs, or screenshots.
   - **Never** expose backend secrets in client-side bundles (e.g. Vite frontend code).

4. **Incident Response & Revocation:**
   - If any secret or password was committed to version control or exposed publicly, treat it as **immediately compromised**.
   - Revoke and rotate the compromised credential in the database/cloud provider immediately.
   - Update production environment variables (`--env-file` or container orchestrator secrets) and redeploy the service.
   - *Historical exposure note:* Any credentials used in earlier Git commits must be rotated immediately. Git history remediation (e.g. using BFG Repo-Cleaner or git-filter-repo) should be scheduled according to repository owner governance.

---

## 3. Authentication & Access Token Policies

- **Strict JWT Verification:** Protected API endpoints (`/api/v1/auth/me`, `/api/v1/conversations`, `/api/v1/chat`, `/api/v1/saved`, `/api/v1/feedback`) strictly require an active, validly signed Bearer token.
- **Immediate 401 Unauthorized:** Missing, empty, malformed, expired, or deactivated user tokens return `401 Unauthorized`.
- **Zero Fallback:** There is no fallback to demo accounts or admin privileges for missing or failed tokens.
- **Fixed Tokens Prohibited:** Hardcoded tokens (such as legacy demo tokens) are strictly rejected.
- **Development Demo Restrictions:** Demo accounts are disabled by default. They can only be seeded locally when `APP_ENV=development` and `SEED_DEMO_DATA=true` are explicitly passed, and the demo user is never granted admin permissions by default.

---

## 4. Production Configuration Safeguards

In `production` mode, the application will **fail fast and exit non-zero at startup** if:
- `APP_SECRET` is missing, blank, or matches a known development default.
- `JWT_SECRET` is missing, blank, or matches a known development default.
- `DATABASE_URL` is missing or blank.
- `DEBUG` is set to `True`.
- `CORS_ALLOWED_ORIGINS` is missing, blank, or contains a wildcard (`*`) while credentials are enabled.

To validate your configuration prior to deployment, execute:
```bash
python scripts/validate_config.py --env production
```

---

## 5. Reporting Security Vulnerabilities

If you discover a security vulnerability or credential leak in AutoMind AI, please report it privately to the maintainers at `security@automind.ai`. Do not open public issues for security vulnerabilities.
