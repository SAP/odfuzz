# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]


## [0.18.0]

- Exclude Properties from URI Using Exclusion List


## [0.17.2]

- Fixing Edm.Int64 + Edm.Double Giving 400 Bad Request
- Fixing 400 bad request for Edm.Decimal

## [0.17.1]

- Broken release, should not be used.

## [0.17.0]

-  Implement entity and entityset restrictions
-  DirectBuider.build() returns a list of entities after restrictions are applied, instead of the object of the class QueryableEntities  

## [0.16.1]

-  Fixed SAP_VENDOR_ENABLED for DateTimeOffset

## [0.16.0]

- New feature: Add support for switching between Generic vs SAP OData implementation 

## [0.15.0]

 - New feature: Function imports fuzzing

## [0.14.0]

### Added
- New feature - Add support for HTTP DELETE, PUT, POST and MERGE methods in fuzzing - intentionaly DirectBuilder usage only, CLI pending.
- fuzzing - Add support for sap:display-format="NonNegative"
- chore: Add version logging for CLI usage
- chore: Add config option to set random.seed() via env.var ODFUZZ_CLI_RUNNER_SEED
- chore: Update dependencies (setup.py)

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
