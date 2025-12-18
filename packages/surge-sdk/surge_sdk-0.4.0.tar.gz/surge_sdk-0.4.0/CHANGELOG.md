# Changelog

## 0.4.0 (2025-12-17)

Full Changelog: [v0.3.1...v0.4.0](https://github.com/surgeapi/python-sdk/compare/v0.3.1...v0.4.0)

### Features

* **api:** add retrieve message endpoint ([954d2d3](https://github.com/surgeapi/python-sdk/commit/954d2d3de777c40a5808d0f7876ec6e11b601b10))


### Bug Fixes

* compat with Python 3.14 ([340f1da](https://github.com/surgeapi/python-sdk/commit/340f1daa0b1024c2f45b71e66841302bd2cc9190))
* **compat:** update signatures of `model_dump` and `model_dump_json` for Pydantic v1 ([f657dfd](https://github.com/surgeapi/python-sdk/commit/f657dfda7eb8097cafea011a7f612122d0bd28b7))
* ensure streams are always closed ([a3d05db](https://github.com/surgeapi/python-sdk/commit/a3d05dbf55c77424e8b88803c4390c72d70a2894))
* **types:** allow pyright to infer TypedDict types within SequenceNotStr ([7724409](https://github.com/surgeapi/python-sdk/commit/7724409c6eb510edf6da6ad5867a18ec32316bc4))


### Chores

* add missing docstrings ([15bbcc4](https://github.com/surgeapi/python-sdk/commit/15bbcc4e1152d504c1a900cf49295d2091eb4a24))
* add Python 3.14 classifier and testing ([1cfb2c6](https://github.com/surgeapi/python-sdk/commit/1cfb2c6ff172ebe9a1b8bc5f25da787d42174e15))
* **deps:** mypy 1.18.1 has a regression, pin to 1.17 ([7e24ec8](https://github.com/surgeapi/python-sdk/commit/7e24ec81a02c78d3c07ea2f39fc8b2f83cbb32bc))
* **docs:** use environment variables for authentication in code snippets ([ce7f16c](https://github.com/surgeapi/python-sdk/commit/ce7f16ce441087610dd314ee17c709fb9e86a19d))
* **internal:** add missing files argument to base client ([b42fa76](https://github.com/surgeapi/python-sdk/commit/b42fa7670217848526df4a3d69033f93fc295c04))
* **internal:** codegen related update ([7ae81f1](https://github.com/surgeapi/python-sdk/commit/7ae81f18f92f5088717d109461d1fa12207670cb))
* **internal:** codegen related update ([fd67466](https://github.com/surgeapi/python-sdk/commit/fd67466a3d1e41835071287fcd6448fa09549eb1))
* **internal:** codegen related update ([1049106](https://github.com/surgeapi/python-sdk/commit/10491067966bd0e3a02f3b678bea16d0871d1914))
* **internal:** codegen related update ([7d90209](https://github.com/surgeapi/python-sdk/commit/7d90209510715401244d34253ffd6892f944376f))
* **internal:** fix test definition ([66e3f20](https://github.com/surgeapi/python-sdk/commit/66e3f200599963abe5fe5cd8a89edfa52c8fd4ac))
* **internal:** grammar fix (it's -&gt; its) ([1693443](https://github.com/surgeapi/python-sdk/commit/16934439864c8eb0cb167d9daf5c7b01c26e9702))
* **package:** drop Python 3.8 support ([1548699](https://github.com/surgeapi/python-sdk/commit/1548699689894152c1b0fdb4435c608f96872dff))
* speedup initial import ([86798d7](https://github.com/surgeapi/python-sdk/commit/86798d76d735e1dde3c7977af63838013b6c3617))
* update lockfile ([39ab4f5](https://github.com/surgeapi/python-sdk/commit/39ab4f55d1a419924e252cdff2008c8b3f973a5d))

## 0.3.1 (2025-10-31)

Full Changelog: [v0.3.0...v0.3.1](https://github.com/surgeapi/python-sdk/compare/v0.3.0...v0.3.1)

### Features

* **api:** create externally registered campaigns ([2aaae37](https://github.com/surgeapi/python-sdk/commit/2aaae3778862c64d85485e2eb9b9c6508a87606c))


### Bug Fixes

* **client:** close streams without requiring full consumption ([46da11c](https://github.com/surgeapi/python-sdk/commit/46da11c9f87b0bf9b20f93fa97ea1abca8389a5c))


### Chores

* bump `httpx-aiohttp` version to 0.1.9 ([50983ab](https://github.com/surgeapi/python-sdk/commit/50983ab68d34871cea4ac5db3fc94a7da9373c6e))
* **internal/tests:** avoid race condition with implicit client cleanup ([1785037](https://github.com/surgeapi/python-sdk/commit/17850379f87317638de53bd04492db2e7f3d2532))
* **internal:** codegen related update ([e7eb248](https://github.com/surgeapi/python-sdk/commit/e7eb2485f250c6fe2108385a50c62cb56f547f73))
* **internal:** detect missing future annotations with ruff ([3e0ad24](https://github.com/surgeapi/python-sdk/commit/3e0ad247d55004c3dc572f7b1bc611d24d362431))


### Documentation

* **api:** add context around organization contacts ([fb0897c](https://github.com/surgeapi/python-sdk/commit/fb0897ce5361bc708db7d1bb9e96eba573bb3d97))

## 0.3.0 (2025-10-09)

Full Changelog: [v0.2.0...v0.3.0](https://github.com/surgeapi/python-sdk/compare/v0.2.0...v0.3.0)

### Features

* **api:** api update ([6963cf8](https://github.com/surgeapi/python-sdk/commit/6963cf83818a22e4421272433ade940bb32959d8))
* **api:** api update ([2f3657d](https://github.com/surgeapi/python-sdk/commit/2f3657d8448c0f926b55aa646d060730500ad0e4))
* **api:** manual updates ([4f90c78](https://github.com/surgeapi/python-sdk/commit/4f90c78360f4622622a9f977a501f97db399453f))
* **api:** manual updates ([90f8f61](https://github.com/surgeapi/python-sdk/commit/90f8f61fe28690cdb2544d0885a21e9bf4df9e85))
* **types:** remove explicit params types ([49b0c02](https://github.com/surgeapi/python-sdk/commit/49b0c0262095a8df8ea9f0cf903edf52de816299))
* **types:** try removing account_update_params type ([837fd43](https://github.com/surgeapi/python-sdk/commit/837fd43cf29f97ab61d6a4e5becd30e1832c20a9))


### Chores

* do not install brew dependencies in ./scripts/bootstrap by default ([c7560f0](https://github.com/surgeapi/python-sdk/commit/c7560f05fe673690f1e6edd51c06427bd466a8cb))
* improve example values ([24fc93e](https://github.com/surgeapi/python-sdk/commit/24fc93ecf04cd848227327d876690c1ba1055828))
* **internal:** codegen related update ([803cc55](https://github.com/surgeapi/python-sdk/commit/803cc55c7e58649c00eef4abf416750cdb4d48af))
* **internal:** update pydantic dependency ([fc71fe4](https://github.com/surgeapi/python-sdk/commit/fc71fe4f7e7e807b6fd765bf8ec6f5bd133c73e8))
* **types:** change optional parameter type from NotGiven to Omit ([2d99575](https://github.com/surgeapi/python-sdk/commit/2d995752dc2f803d65cd82576caff490910e025b))

## 0.2.0 (2025-09-16)

Full Changelog: [v0.1.0...v0.2.0](https://github.com/surgeapi/python-sdk/compare/v0.1.0...v0.2.0)

### Features

* **api:** add ruby and change python package name ([7c927af](https://github.com/surgeapi/python-sdk/commit/7c927af371870b176fe51805df1be9ac64544f8b))

## 0.1.0 (2025-09-12)

Full Changelog: [v0.0.1-alpha.0...v0.1.0](https://github.com/surgeapi/python-sdk/compare/v0.0.1-alpha.0...v0.1.0)

### Chores

* sync repo ([c5ee59c](https://github.com/surgeapi/python-sdk/commit/c5ee59c5bccf5590db15b9594fa4f2fd1f096cc8))
* update SDK settings ([096a068](https://github.com/surgeapi/python-sdk/commit/096a0685eed28af9d1ccb7251746cc0e0ae04630))
* update SDK settings ([2dbeb2c](https://github.com/surgeapi/python-sdk/commit/2dbeb2c2dcfdfaa5b909faf0701d0e664cf6b182))
