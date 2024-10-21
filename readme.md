# MailListShield.com SaaS

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
