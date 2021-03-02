\<Remember to add meaningful title\>

\<Short description of the PR\>

Fixes #\<issue number\>

Before merge following needs to be applied:
- [ ] At least one example testcase added in testcases/
- [ ] PR entry added in CHANGELOG.md in **In progress** section
- [ ] All new testcases tagged as **prerelease** along other tags to exclude it from execution until released on PyPI
- [ ] Coverage threshold increased in [.coveragerc](https://github.com/devopsspiral/KubeLibrary/blob/master/.coveragerc) if new coverage is higher than actual, see the lint-and-coverage step in CI
```
fail_under = 67
```
