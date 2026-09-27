# Contributing

Contributions that improve reliability, documentation, compatibility, or testing are welcome through GitHub issues and pull requests.

Scientific changes require additional care. A pull request that changes a threshold, timing definition, background treatment, or GTI construction should:

1. describe the scientific motivation;
2. identify the original and proposed definitions;
3. include a reproducible validation example that does not expose restricted data; and
4. explain whether historical results remain comparable.

Please do not commit observational data, credentials, unpublished results, or institutionally restricted material. Python changes should pass the repository's syntax check and should keep scientific assumptions visible in both code and documentation.
