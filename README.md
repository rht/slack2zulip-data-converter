The script `slack2zulip.py` converts the Slack data export (see details at the
`slack/` example folder, and https://github.com/slackhq/slack-api-docs for
documentation)

More documentations incoming.
## Usage

To convert a slack data, let the zip file be `slack_data.zip`, then
1. Unzip it to a folder residing in this repo's directory
2. `./slack2zulip.py slack_data`
3. `zip -r zulip_data.zip zulip_data`

To deploy the data onto an existing fresh Zulip repo,
`./manage.py import zulip_data.zip`

## References

0. Zulip's export function https://github.com/zulip/zulip/blob/master/zerver/lib/export.py
1. Zulip's sample export data https://github.com/zulip/zulip/blob/master/zerver/tests/test_export.py
2. Zulip's current users and channels import https://github.com/zulip/zulip/tree/master/api/integrations/slack
3. https://get.slack.help/hc/en-us/articles/220556107-Understand-Slack-data-exports
