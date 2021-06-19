FALALALA
# conda-forge-webservices
[![tests](https://github.com/conda-forge/conda-forge-webservices/workflows/tests/badge.svg)](https://github.com/conda-forge/conda-forge-webservices/actions?query=workflow%3Atests) [![clean-and-update](https://github.com/conda-forge/conda-forge-webservices/workflows/clean-and-update/badge.svg)](https://github.com/conda-forge/conda-forge-webservices/actions?query=workflow%3Aclean-and-update)

This repository is the source for the Heroku hosted webapp which powers the conda-forge-admin
commands and lints conda-forge's recipes. The linting itself comes from conda-smithy
(https://github.com/conda-forge/conda-smithy).

## Configuration
Rather than using OAuth, this app is using a pre-determined "personal access token" which has
appropriate conda-forge permissions. It has been configured with:

    heroku config:set GH_TOKEN=<token>

The service deploys to the "conda-forge" heroku project: https://dashboard.heroku.com/apps/conda-forge/resources

## Testing

The tests for this repo require a GitHub API key which is not available on forks. Thus the tests only pass
for PRs made from a branch in this repo. If your PR is in a fork, please ask a member of `@conda-forge/core`
to push your PR branch to the main repo to enable the tests.
