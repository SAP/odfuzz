# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased - Alpha version 0.14a2]

### Added
- New feature - Add support for HTTP DELETE method in fuzzing.

## [0.13.3]

### Added
- New possibility to ignore metadata restrictions by ENV variable ODFUZZ_IGNORE_METADATA_RESTRICTIONS

### Fixed
 - Fix env ODFUZZ_URLS_PER_PROPERY typing to int
 - Lower loglevel from error to info for unsupported generators and mutators

## [0.13.2]

### Fixed

- Fix Edm.Guid mutator 
- Fix extra single quote in URL for datetime
- Pin install dependencies for deterministic installations
- Use the new signal handler interface after update to latest Gevent library 20.5.0
- Print error messages, which cause the fuzzer to stop, to stdout

## [0.13.1]

### Added
- log module version on fuzzer CLI start

## [0.13.0] - first tracked Release.
