# MailListShield.com SaaS

[![Build & Deploy](https://github.com/cansinacarer/maillistshield-com/actions/workflows/deploy.yml/badge.svg)](https://github.com/cansinacarer/maillistshield-com/actions/workflows/deploy.yml)

This repo contains the SaaS at [maillistshield.com](https://maillistshield.com/). It is built on top of [my Flask base saas](https://github.com/cansinacarer/my-base-saas-flask).

To pull updates from the base saas, connect it as an upstream:

```sh
git remote add upstream https://github.com/cansinacarer/my-base-saas-flask
```

Then you can fetch and merge:

```sh
git fetch upstream
git merge upstream/main
```

## MailListShield repositories

- [MailListShield Flask SaaS](https://github.com/cansinacarer/maillistshield-com)
- [MailListShield File Processor](https://github.com/cansinacarer/maillistshield-file-processor)
- [MailListShield File Processor OLD](https://github.com/cansinacarer/maillistshield-scheduler)
- [MailListShield Email Validation Worker](https://github.com/cansinacarer/maillistshield-validation-worker)
- [Initial Tests & Notes](https://github.com/cansinacarer/email-verification-test)
-
