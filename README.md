The script `slack2zulip.py` converts the Slack data export (see the sample
folder at the `slack/`, and see https://github.com/slackhq/slack-api-docs for
documentation)

## Rationale

`\exists` Slackland, Zulipland, Mattermostland. How does one engineer a tunnel
to ensure that each inhabitants can go bidirectionally, seamlessly? Currently,
this is done with Matrix.org^[1] bridge or Matterbridge.

This project tackles another use case: a full unidirectional migration from
Slack to Zulip.  Currently, only `users.json` and `channels.json` import are
possible via `zulip/zulip/api/integrations/slack` [3].

There are two approaches:
1. data-API-bridge-API-data. With this, assuming that Slack's API fully
   exposes all the data (users.json, messages.json, and channels.json), you
   still have to expose more of the Zulip's machinery.  And there is no
   low-level operation of putting the past timestamps via API.  This is a no-go.
2. data-data. This is the fastest route to reach prod state. Zulip already has a
   well-fleshed-out and well-tested data export/import. And Slack already has a
   data.zip export.

### footnote
1. Still pending to be fleshed out with ActivityPub / Linked Data Notifications

## Term Mapping

## Usage

To convert a slack data, let the zip file be `slack_data.zip`, then
1. Unzip it to a folder residing in this repo's directory
2. `./slack2zulip.py slack_data`
3. `zip -r zulip_data.zip zulip_data`

To deploy the data onto an existing fresh Zulip repo,
`./manage.py import zulip_data.zip`

## References

1. Zulip's export function https://github.com/zulip/zulip/blob/master/zerver/lib/export.py
2. Zulip's sample export data https://github.com/zulip/zulip/blob/master/zerver/tests/test_export.py
3. Zulip's existing users and channels import https://github.com/zulip/zulip/tree/master/api/integrations/slack
4. https://get.slack.help/hc/en-us/articles/220556107-Understand-Slack-data-exports
5. https://github.com/zulip/zulip/issues/908#issuecomment-247719383
