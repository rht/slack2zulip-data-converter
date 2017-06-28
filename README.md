The script `slack2zulip.py` converts the Slack data export (see details at the
`slack/` example folder, and https://github.com/slackhq/slack-api-docs for
documentation)

More documentations incoming.
## Usage

To convert a slack data, let the zip file be `slack_data.zip`, then
1. Unzip it to a folder residing in this repo's directory
2. `./slack2zulip.py slack_data`

TODO: the intermediate step still pending

To deploy the data onto an existing fresh Zulip repo,
`./manage.py import zulip_data.zip`

## References

0. https://github.com/zulip/zulip/blob/master/zerver/lib/export.py
1. https://github.com/zulip/zulip/blob/master/zerver/tests/test_export.py
2. https://github.com/zulip/zulip/tree/master/api/integrations/slack
