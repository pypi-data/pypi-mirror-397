## Instructions for Claude

When implmenting new functionality.
* Never mention the reference applications listed in bioamla.md, but use that file as a reference.
* this repo is in alpha, do not implement backwards compatability
* make changes to core modules first
* add unit tests for core modules
* run tests on core modules
* then make changes in cli modules
* add unit tests for cli modules
* run all tests
* update readme.md

### Key architectural principles

**Principle 1: bioamla knows nothing about magpy.** The core package never imports GUI code. All communication flows one direction: magpy → bioamla.
