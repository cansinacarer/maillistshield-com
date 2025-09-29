# [1.10.0](https://github.com/cansinacarer/maillistshield-com/compare/v1.9.0...v1.10.0) (2025-09-29)


### Bug Fixes

* correct the error code on wrong method ([84ba1ea](https://github.com/cansinacarer/maillistshield-com/commit/84ba1eacbd3c36eb7049e0899cd4ce25d067c5a0))
* remove redundant colons ([1560150](https://github.com/cansinacarer/maillistshield-com/commit/15601506ba255cebe12d339208e68b3539098776))


### Features

* add link for the api reference in the footer ([1517b0c](https://github.com/cansinacarer/maillistshield-com/commit/1517b0c35982bacbfb8eb921b4b8b924d5f85014))

# [1.9.0](https://github.com/cansinacarer/maillistshield-com/compare/v1.8.0...v1.9.0) (2025-09-29)


### Features

* implement API endpoints for single email validation, balance check, and key test ([6949a61](https://github.com/cansinacarer/maillistshield-com/commit/6949a61b84d039b23b8ebac400860044634b73ac))

# [1.8.0](https://github.com/cansinacarer/maillistshield-com/compare/v1.7.0...v1.8.0) (2025-09-28)


### Features

* ability to create/revoke API keys ([a1a4428](https://github.com/cansinacarer/maillistshield-com/commit/a1a4428ba6a228beedcd0132500709f0f88941ee))

# [1.7.0](https://github.com/cansinacarer/maillistshield-com/compare/v1.6.1...v1.7.0) (2025-09-28)


### Bug Fixes

* **ci:** add the same set of env variables as those in test ([9704fc0](https://github.com/cansinacarer/maillistshield-com/commit/9704fc0fa5c4e9799d2d9bee25b67b0aa23ed95c))
* **ci:** we are not doing db migrations on ci ([6bdc9e7](https://github.com/cansinacarer/maillistshield-com/commit/6bdc9e7176ae9727985cac222684373dbd1bb1c9))
* resolve the flickering before dark mode is applied ([e4c505a](https://github.com/cansinacarer/maillistshield-com/commit/e4c505a74cecd8d38bfe10d74214759f782618f8))


### Features

* add readme buttons for one-click dev environment providers ([7722849](https://github.com/cansinacarer/maillistshield-com/commit/7722849afda450f031f973b9425ae5383ec52f75))
* add schema versioning with Flask-Migrate ([00f72f4](https://github.com/cansinacarer/maillistshield-com/commit/00f72f47ac9eee48fa1ea8fadb9977e022b615e2))
* better navigation on homepage when logged in ([e9c42b4](https://github.com/cansinacarer/maillistshield-com/commit/e9c42b49aadf57dfd3eec47628835e2372c3d059))

## [1.6.1](https://github.com/cansinacarer/maillistshield-com/compare/v1.6.0...v1.6.1) (2025-09-28)

### Bug Fixes

* **ci:** correct the workspace path in the devcontainer ([8cf6fb7](https://github.com/cansinacarer/maillistshield-com/commit/8cf6fb790e741923fc947c39b34bb7a77c23e1aa))

# [1.6.0](https://github.com/cansinacarer/maillistshield-com/compare/v1.5.3...v1.6.0) (2025-09-21)

### Bug Fixes

* upload file now sends the user directly to the upload page instead of `/app` ([b359fb7](https://github.com/cansinacarer/maillistshield-com/commit/b359fb7ef02ac65cd2555c24c9dbd0839952187a))

### Features

* implement single email validation form on the private side ([5582363](https://github.com/cansinacarer/maillistshield-com/commit/5582363aa5807990db0d114d9e91e7a12d3a56b1))

## [1.5.3](https://github.com/cansinacarer/maillistshield-com/compare/v1.5.2...v1.5.3) (2025-09-21)

### Bug Fixes

* handle the error case when anonymous user tries downloading a results file ([8cc9765](https://github.com/cansinacarer/maillistshield-com/commit/8cc97655965cb1d65a39583852def8a9f9736cd9))

## [1.5.2](https://github.com/cansinacarer/maillistshield-com/compare/v1.5.1...v1.5.2) (2025-09-21)

### Bug Fixes

* make the homepage validator catch the case of less common email providers ([1cdb34a](https://github.com/cansinacarer/maillistshield-com/commit/1cdb34a9126d554a18c21163159f75883e1632c4))
* resolve flickering in dark mode on page load ([887f5b9](https://github.com/cansinacarer/maillistshield-com/commit/887f5b9fed130653fca70e4fc2df008d022a9ab0))

## [1.5.1](https://github.com/cansinacarer/maillistshield-com/compare/v1.5.0...v1.5.1) (2025-09-21)

### Bug Fixes

* complete the missing parts of file download ([c1155c8](https://github.com/cansinacarer/maillistshield-com/commit/c1155c86ab971d0cad8f9c05c811cd9d403b4c83))

# [1.5.0](https://github.com/cansinacarer/maillistshield-com/compare/v1.4.5...v1.5.0) (2025-09-21)

### Features

* download results endpoint ([73ba860](https://github.com/cansinacarer/maillistshield-com/commit/73ba8605927b0e5a61b30b8ce3eff32dfcf85050))

## [1.4.5](https://github.com/cansinacarer/maillistshield-com/compare/v1.4.4...v1.4.5) (2025-09-20)

### Bug Fixes

* sort batch jobs in the ui by order of creation ([58521cc](https://github.com/cansinacarer/maillistshield-com/commit/58521cc4ec0dad5b3b2ad4aae7131ecd569c71af))

## [1.4.4](https://github.com/cansinacarer/maillistshield-com/compare/v1.4.3...v1.4.4) (2025-09-20)

### Bug Fixes

* **ci:** correct sphinx version ([ef5ded7](https://github.com/cansinacarer/maillistshield-com/commit/ef5ded7022e417694728832da11ff9f9b53bb3a6))

## [1.4.3](https://github.com/cansinacarer/maillistshield-com/compare/v1.4.2...v1.4.3) (2025-09-20)

### Bug Fixes

* correctly round file progress to 2 digits ([47f13d4](https://github.com/cansinacarer/maillistshield-com/commit/47f13d45f077f2b5206b33d710aff6b0f98b1001))

## [1.4.2](https://github.com/cansinacarer/maillistshield-com/compare/v1.4.1...v1.4.2) (2025-09-20)

### Bug Fixes

* improvements on status tracking ([6188765](https://github.com/cansinacarer/maillistshield-com/commit/6188765621e8c5ed1850b03046a5411e64bd6a2f))

## [1.4.1](https://github.com/cansinacarer/maillistshield-com/compare/v1.4.0...v1.4.1) (2025-09-20)

### Bug Fixes

* complete the batch job state -> label mapping ([3ff549b](https://github.com/cansinacarer/maillistshield-com/commit/3ff549b3c9b6ad342574551cf7e39571417ff726))

# [1.4.0](https://github.com/cansinacarer/maillistshield-com/compare/v1.3.0...v1.4.0) (2025-09-16)

### Features

* add system status link to private page footers ([e84a4a8](https://github.com/cansinacarer/maillistshield-com/commit/e84a4a828c5a158247e20199535edf1d99ef4cf5))

# [1.3.0](https://github.com/cansinacarer/maillistshield-com/compare/v1.2.1...v1.3.0) (2025-05-09)

### Features

* **analytics:** add a dataLayer event for implementation services notice ([7821cdc](https://github.com/cansinacarer/maillistshield-com/commit/7821cdca4b0c0071b69241e53f0488db0ba6370c))

## [1.2.1](https://github.com/cansinacarer/maillistshield-com/compare/v1.2.0...v1.2.1) (2025-05-09)

### Bug Fixes

* push to dataLayer directly instead of using gtag() ([89bfdc2](https://github.com/cansinacarer/maillistshield-com/commit/89bfdc2cd2ceb18d9c93e4738ab824e6c9ffd236))

# [1.2.0](https://github.com/cansinacarer/maillistshield-com/compare/v1.1.2...v1.2.0) (2025-05-09)

### Features

* install Google Tag Manager to templates ([d87b4f0](https://github.com/cansinacarer/maillistshield-com/commit/d87b4f0271646887c835dacffeb35581eb36715c))

## [1.1.2](https://github.com/cansinacarer/maillistshield-com/compare/v1.1.1...v1.1.2) (2025-05-07)

### Bug Fixes

* update app reference to be compatible with the application factory pattern ([82ede00](https://github.com/cansinacarer/maillistshield-com/commit/82ede00fe239c44319a04b039db13685fef71ca6))

## [1.1.1](https://github.com/cansinacarer/maillistshield-com/compare/v1.1.0...v1.1.1) (2025-05-05)

### Bug Fixes

* adjust recaptcha height and border radius ([387c6ed](https://github.com/cansinacarer/maillistshield-com/commit/387c6ede12c0dc1add1457f428681ad936ab36e0))

# [1.1.0](https://github.com/cansinacarer/maillistshield-com/compare/v1.0.0...v1.1.0) (2025-05-04)

### Features

* add reCAPTCHA v2 support ([5a33a5d](https://github.com/cansinacarer/maillistshield-com/commit/5a33a5d88253dc9143225e665797c21c9dd34821))

# 1.0.0 (2025-04-22)

# [1.1.0](https://github.com/cansinacarer/My-Base-SaaS-Flask/compare/v1.0.1...v1.1.0) (2025-05-04)

### Features

* add reCAPTCHA v2 support ([5a33a5d](https://github.com/cansinacarer/My-Base-SaaS-Flask/commit/5a33a5d88253dc9143225e665797c21c9dd34821))

## [1.0.1](https://github.com/cansinacarer/My-Base-SaaS-Flask/compare/v1.0.0...v1.0.1) (2025-04-19)

### Bug Fixes

* add access to the github token in gh action ([1c79add](https://github.com/cansinacarer/maillistshield-com/commit/1c79add433f55437020818a6c237de3131fa35a6))
* add env variables in test environment ([15294b9](https://github.com/cansinacarer/maillistshield-com/commit/15294b9f0d9097ae8fc788d9582103400103fd18))
* add missing comma ([afeab32](https://github.com/cansinacarer/maillistshield-com/commit/afeab32be16dc88381bd4f16d255fb8d84f7fb68))
* add vscode docker extension ([ad2c930](https://github.com/cansinacarer/maillistshield-com/commit/ad2c930c36ab8656c40379c5d8d911466af5a6fe))
* correct the python version ([46d51c0](https://github.com/cansinacarer/maillistshield-com/commit/46d51c07c742984d6ab7024bf24866d8fcb37f95))
* correct the reference to generate_coverage_badge.py in gh action ([fd5b889](https://github.com/cansinacarer/maillistshield-com/commit/fd5b889734a20da94e2693354c3a32aa7c4c602b))
* correct the reference to the coverage svg ([eacf821](https://github.com/cansinacarer/maillistshield-com/commit/eacf821db3b860bb2456c797b945c422cd6ba80b))
* fix the html problems prettier found ([7219722](https://github.com/cansinacarer/maillistshield-com/commit/72197221b647af48c8618e98c20529f0224957c4))
* **github-actions:** resolve conflict between actions that simultaneously try to pull/push this repo ([b5c75e1](https://github.com/cansinacarer/maillistshield-com/commit/b5c75e1db641cb0be386b6c534504cb098b3e3be))
* ignore node modules and package files used ([f857153](https://github.com/cansinacarer/maillistshield-com/commit/f8571531ea294b7d9ea7f0a328084b5578b219c6))
* make the automatic coverage badge use conventional commit msg ([51b147f](https://github.com/cansinacarer/maillistshield-com/commit/51b147f06069a1923a152770a07e03f5a46e8f89))
* placeholders too short ([aa5bce0](https://github.com/cansinacarer/maillistshield-com/commit/aa5bce0210e2d0886b44f3b61c6d533e173b21fd))
* use /bin/bash to match shebang ([b0ca7c4](https://github.com/cansinacarer/maillistshield-com/commit/b0ca7c49eef7d477e89bd75a4b27e6669984e151))

* **github-actions:** resolve conflict between actions that simultaneously try to pull/push this repo ([b5c75e1](https://github.com/cansinacarer/My-Base-SaaS-Flask/commit/b5c75e1db641cb0be386b6c534504cb098b3e3be))

# 1.0.0 (2025-04-19)

### Bug Fixes

* add access to the github token in gh action ([1c79add](https://github.com/cansinacarer/My-Base-SaaS-Flask/commit/1c79add433f55437020818a6c237de3131fa35a6))
* add env variables in test environment ([15294b9](https://github.com/cansinacarer/My-Base-SaaS-Flask/commit/15294b9f0d9097ae8fc788d9582103400103fd18))
* add missing comma ([afeab32](https://github.com/cansinacarer/My-Base-SaaS-Flask/commit/afeab32be16dc88381bd4f16d255fb8d84f7fb68))
* add vscode docker extension ([ad2c930](https://github.com/cansinacarer/My-Base-SaaS-Flask/commit/ad2c930c36ab8656c40379c5d8d911466af5a6fe))
* correct the python version ([46d51c0](https://github.com/cansinacarer/My-Base-SaaS-Flask/commit/46d51c07c742984d6ab7024bf24866d8fcb37f95))
* correct the reference to generate_coverage_badge.py in gh action ([fd5b889](https://github.com/cansinacarer/My-Base-SaaS-Flask/commit/fd5b889734a20da94e2693354c3a32aa7c4c602b))
* correct the reference to the coverage svg ([eacf821](https://github.com/cansinacarer/My-Base-SaaS-Flask/commit/eacf821db3b860bb2456c797b945c422cd6ba80b))
* fix the html problems prettier found ([7219722](https://github.com/cansinacarer/My-Base-SaaS-Flask/commit/72197221b647af48c8618e98c20529f0224957c4))
* ignore node modules and package files used ([f857153](https://github.com/cansinacarer/My-Base-SaaS-Flask/commit/f8571531ea294b7d9ea7f0a328084b5578b219c6))
* make the automatic coverage badge use conventional commit msg ([51b147f](https://github.com/cansinacarer/My-Base-SaaS-Flask/commit/51b147f06069a1923a152770a07e03f5a46e8f89))
* use /bin/bash to match shebang ([b0ca7c4](https://github.com/cansinacarer/My-Base-SaaS-Flask/commit/b0ca7c49eef7d477e89bd75a4b27e6669984e151))

### Features

* Add .gitattributes file to enforce LF line endings ([15bc24d](https://github.com/cansinacarer/maillistshield-com/commit/15bc24dccb2f0ca9be5582e36129c614cc11aee7))
* add a github action for tests ([27092e6](https://github.com/cansinacarer/maillistshield-com/commit/27092e63efe28023ba78c66087f0779a69549f39))
* add a self-signed ssl key for the devcontainer ([15a4fe9](https://github.com/cansinacarer/maillistshield-com/commit/15a4fe95608b67f1b2a28a7f0dd06e2fbfbba808))
* add a simple prettier config file ([5593450](https://github.com/cansinacarer/maillistshield-com/commit/55934505a92a769967bbfb4ff7d23195200dd1fd))
* add devcontainers ([47d594e](https://github.com/cansinacarer/maillistshield-com/commit/47d594e1ef81bd5e4587b54dda26ea6fb0e7549e))
* add markdownlint ([185a162](https://github.com/cansinacarer/maillistshield-com/commit/185a1627dd8a1fed51ee11bfcad8a3a10d2f3969))
* add npm and install prettier in the devcontainer ([6dbe68b](https://github.com/cansinacarer/maillistshield-com/commit/6dbe68b84b64ca1d0fb9e5fc361fb11bd390f53a))
* add prettier hook for pre-commit ([ef94ea5](https://github.com/cansinacarer/maillistshield-com/commit/ef94ea548476361065a76b5a376f29a60faeca27))
* add vscode debugger config ([d39a8a7](https://github.com/cansinacarer/maillistshield-com/commit/d39a8a7fa998bc5f4d82b9e38c513a119a46f4c6))
* add vscode settings for black-formatter ([8d650e9](https://github.com/cansinacarer/maillistshield-com/commit/8d650e9763e0228daa3f9b878f4e1a795b8ba216))
* add vscode settings for js, json, html, css ([b0929be](https://github.com/cansinacarer/maillistshield-com/commit/b0929be58d86e939fb50430d044f8b1b85c5191b))
* commitlint ([399d97e](https://github.com/cansinacarer/maillistshield-com/commit/399d97e1dded3357fce7ab660c53037543ee4407))
* coverage reports ([033768d](https://github.com/cansinacarer/maillistshield-com/commit/033768d6e0daf06945ec8e08f9334c0d16bb33e7))
* enforce no trailing comma after the last element ([ed09653](https://github.com/cansinacarer/maillistshield-com/commit/ed09653f3138464158cb283fbb7981443b9e8c9e))
* enforce python black formatting with pre-commit ([90b05aa](https://github.com/cansinacarer/maillistshield-com/commit/90b05aa031a5bcb4469d1f71fefa64a2ce163bbd))
* install prettier with jinja plugin in the dev container ([9477fd9](https://github.com/cansinacarer/maillistshield-com/commit/9477fd9c31fb471da6c76c7f26910d7d8031474c))
* offcanvas menu on mobile ([92bfffd](https://github.com/cansinacarer/maillistshield-com/commit/92bfffd62520346e51c2eb76f14a5573bf6c3a9e))
* pull updates from my base saas v1.0.1 ([dda1c20](https://github.com/cansinacarer/maillistshield-com/commit/dda1c2069872ec7a85f0477f9c7719dacf9cb01c))
* round robin load balancing between multiple workers ([eaac64b](https://github.com/cansinacarer/maillistshield-com/commit/eaac64b32c6fed1a7de831740a4de83e32427483))
* sematic release ([1bc1c80](https://github.com/cansinacarer/maillistshield-com/commit/1bc1c801c8d8ee7c187f0ffa2910eadaed394fad))
