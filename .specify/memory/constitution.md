<!--
  SYNC IMPACT REPORT
  ==================
  Version change: N/A → 1.0.0 (initial creation)
  
  Modified principles: N/A (all new)
  Added sections: 
    - Core Principles (5 new principles)
    - Quality Standards section
    - Development Workflow section
    - Governance section
  
  Templates requiring updates: N/A (no prior constitution existed)
  
  Follow-up TODOs: None
-->

# Drupal Modules Constitution

## Core Principles

### I. Code Quality

All code MUST adhere to established coding standards and best practices. Code MUST be readable, maintainable, and self-documenting where possible. The following rules apply:

- All PHP code MUST follow Drupal coding standards (Drupal.org PSR-2/PSR-4 compliance)
- All JavaScript MUST follow project JavaScript style guides and ES standards
- All code MUST include appropriate inline documentation for complex logic
- Functions MUST NOT exceed reasonable length limits; complex functions MUST be refactored
- Code MUST avoid duplication; common functionality MUST be extracted into shared utilities
- Security best practices MUST be followed: input validation, output escaping, permission checks

Rationale: High-quality code reduces bugs, improves maintainability, and makes the codebase accessible to new contributors. Drupal modules serve critical site functionality—poor code quality can lead to security vulnerabilities and site failures.

### II. Testing Standards

All modules MUST have comprehensive test coverage. Testing is non-negotiable for any code changes. The following requirements apply:

- All new functionality MUST include unit tests with minimum 80% coverage
- All module hooks and callbacks MUST have corresponding test cases
- Integration tests MUST verify module interaction with Drupal core and dependencies
- Kernel tests MUST validate entity operations, configuration management, and field APIs
- Nightly automated test runs MUST pass before any release
- Tests MUST run against supported Drupal versions (currently Drupal 11+)

Rationale: Drupal modules often power production websites with thousands of users. Automated tests prevent regressions, ensure compatibility across Drupal versions, and give contributors confidence when making changes.

### III. User Experience Consistency

All modules MUST provide consistent and predictable user experiences. UI/UX decisions MUST follow Drupal administrative interface conventions:

- All configuration forms MUST use Drupal Form API with proper validation
- All module pages MUST follow standard Drupal menu routing patterns
- Permission labels MUST be clear, consistent, and follow Drupal permission naming conventions
- Status messages (success, error, warning) MUST use Drupal messenger service
- All user-facing text MUST be translatable via Drupal t() function
- Administrative interfaces MUST be accessible (WCAG 2.1 AA compliance)

Rationale: Site administrators expect consistent experiences across modules. Inconsistent UX increases support burden, reduces user confidence, and violates Drupal's ecosystem design principles.

### IV. Performance Requirements

All modules MUST be optimized for performance. Performance regressions are blocking issues. The following standards apply:

- Database queries MUST use Drupal's database abstraction layer with proper indexing
- Entity load operations MUST be cached appropriately (using Drupal cache API)
- Heavy operations MUST implement queue-based processing for long-running tasks
- All external API calls MUST have timeout limits and error handling
- Module MUST declare performance implications in README documentation
- Configuration forms MUST not perform expensive operations on every page load
- Cache invalidation patterns MUST follow Drupal best practices

Rationale: Drupal powers high-traffic websites. Poorly performing modules degrade site speed, increase hosting costs, and negatively impact SEO and user satisfaction.

### V. Documentation Standards

All modules MUST have complete and accurate documentation. Documentation is as important as code:

- README.md MUST contain: module purpose, installation steps, configuration options, usage examples
- Module docblocks MUST follow Drupal API documentation standards
- CHANGELOG.txt MUST document all changes per Semantic Versioning conventions
- Inline code comments MUST explain "why", not "what"
- Upgrade paths between major versions MUST be documented
- All public APIs MUST have accompanying documentation

Rationale: Documentation enables site builders to use modules effectively, reduces support requests, and helps other developers contribute improvements.

## Quality Standards

All code contributions MUST pass the following quality gates before merge:

1. **Automated Testing**: All PHPUnit tests MUST pass (unit, kernel, functional levels)
2. **Code Style**: phpcs MUST report zero violations for Drupal standards
3. **Static Analysis**: PHPStan/Mess Detector MUST report no errors
4. **Security Scan**: SA-CONTRIB or equivalent security checks MUST pass
5. **Documentation**: README and API docs MUST be updated for any new features

Contributions that fail any quality gate MUST be rejected with specific remediation guidance.

## Development Workflow

### Code Review Requirements

- All commits MUST go through pull request review before merge
- At least one approved review from module maintainers or designated reviewers REQUIRED
- Security fixes MAY bypass normal review with documented emergency process
- All reviews MUST verify compliance with constitution principles

### Branching Strategy

- Feature branches MUST be created from the default branch (main or master)
- Branch names MUST follow pattern: `type/short-description` (e.g., `feature/user-login`, `bugfix/cache-issue`)
- Commit messages MUST reference issue numbers when applicable
- Feature branches MUST be deleted after merge

### Release Process

- All releases MUST follow Semantic Versioning (MAJOR.MINOR.PATCH)
- Release notes MUST document all changes, breaking changes, and upgrade steps
- Tags MUST be created for every release with annotated tag messages
- Releases MUST be tested against all supported Drupal versions before announcement

## Governance

This constitution establishes binding rules for all Drupal module development. It supersedes informal practices and individual preferences.

### Amendment Process

Constitution amendments MUST follow this process:

1. Proposal MUST be submitted as a documented change request
2. Discussion period of minimum 7 days MUST allow community input
3. Amendment MUST be approved by module maintainers (2/3 majority for major changes)
4. Migration plan MUST accompany any breaking changes
5. Amended constitution takes effect upon merge to default branch

### Versioning Policy

Constitution versions follow Semantic Versioning:

- **MAJOR**: Backward-incompatible principle removals or redefinitions
- **MINOR**: New principles added or materially expanded guidance
- **PATCH**: Clarifications, wording improvements, typo fixes

### Compliance Review

All pull requests MUST verify constitution compliance:

- Automated checks (CI) verify testing standards and code style
- Human reviewers verify UX consistency and documentation
- Maintainers verify performance requirements and security standards

Violations MUST be corrected before merge; repeated violations may result in contribution restrictions.

**Version**: 1.0.0 | **Ratified**: 2026-01-04 | **Last Amended**: 2026-01-04
