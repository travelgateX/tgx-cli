# TravelgateX CLI

[![Python](https://img.shields.io/pypi/pyversions/tgx-cli.svg?maxAge=2592000)](https://pypi.python.org/pypi/tgx-cli)
[![Travis](https://api.travis-ci.org/travelgateX/tgx-cli.svg?branch=master)](https://travis-ci.org/travelgateX/tgx-cli)
[![Slack](https://slack.travelgatex.com/badge.svg)](https://slack.travelgatex.com)

Tool that you can use to manage your TravelgateX platform


## Installation

```bash
pip install tgx-cli
```

## Usage

```bash
tgx COMMAND
      Options:
          --endpoint              Gateway endpoint.
          --auth_type             ak or apikey, br or bearer
          --auth                  Auth Token

      Commands:
          organization            Create organization or an organization with apikey
          apikey                  Create apikey
          configure               Create a file with the credentials and run options

```

### Get Started

For usage and help content, pass in the `--help` parameter, for example:

```bash
$ tgx organization --help
$ tgx configure --mode TEST --endpoint https:// --auth_type br --auth useyourown
$ tgx organization create_all --user user@mail.com --organization_code XXX

```
