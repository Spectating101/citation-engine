# Native CI

Citation Engine now carries a repository-native GitHub Actions workflow.

The workflow tests the kernel on Python 3.11 and 3.13 and executes the minimal seed smoke after the test suite. This document was added through a pull request specifically so the `pull_request` trigger itself is exercised rather than assuming an app-authored push will recursively trigger Actions.

A green run means future consumer changes can point to native kernel CI in addition to the earlier reconstructed validation history.
