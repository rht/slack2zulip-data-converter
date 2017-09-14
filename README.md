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

1. Still pending to be fleshed out with ActivityPub / Linked Data Notifications

### Funding Q3 2017

See https://rht.github.io/#donate.


## Term Mapping

Most parts of the structures can be mapped 1-to-1, with few exceptions:
1. Permission hierarchy
   in Slack[6]:
   * `is_primary_primary` = `is_owner` + can delete team.
   * `is_owner` = `is_admin` + can set (payments/billing, team authentication,
                  message and file retention, ...)
   * `is_admin` = `member` + can manage members + can manage channels + can handle
                maintenance functions for the team
   * `member` = can join public channel + can send message + can upload files + ..
   * `is_restricted` = can't set topic/purpose of a channel
   * `is_ultra_restricted` = TODO this possibly a custom setting construct, see https://github.com/slackhq/slack-api-docs/search?p=2&q=restricted&type=&utf8=%E2%9C%93
   There is also guest with access to one or several channels
   in Zulip:
   * `is_realm_admin`
   * `is_staff`: barely documented[7], but is functionally equivalent to a
     server admin, as seen in `require_server_admin` function in
     zerver/decorator.py
   * `is_api_super_user`: "Can send messages as other users for mirroring"[8]
   * `is_superuser`: is not used, the code uses `is_api_super_user`. See
     `zerver/views/messages.py`
   Slack's permission hierarchy is more granular.
   Currently the mapping is `is_owner` -> `is_realm_admin`, `is_admin` -> `is_staff`
2. Pins/stars security model
   Slack pins are stored in each channels.
   Zulip stars are known only to each users, stored in `zerver_usermessage`.
3. Streams/channels descriptions
   - Zulip has stream description
   - Slack has channel topic and purpose
4. user presence timestamps
   Zulip has `date_joined`, `last_reminder`, `last_login`.
   Slack has `status`.
5. user subscription in channel
   Slack: the timestamp when a user is subscribed to a channel is logged as a
   message in a channel, much like in IRC. This is not the case in Zulip so as
   not to pollute the thread with join/left announcement.
https://github.com/zulip/zulip/blob/2012913cc13332aa8c14825a042ea11b4b2cfa79/zerver/lib/actions.py#L533
6. "user agent" of a message
   Zulip has `populate_db`, `website`, and `API`
   Slack has none
7. Subscriptions
   Slack stores channel subscription in each channels, Zulip stores subscription
   flatly in zerver_subscription in a realm
8. Stream/channel creator
   Slack stores channel creator in channels.json. Zulip doesn't store stream
   creator.

## Usage

See https://my.slack.com/services/export for the step to export a Slack data.
To convert a slack data, let the zip file be `slack_data.zip`, then
`./slack2zulip.py slack_data.zip`

which outputs `zulip_data.zip`.

To deploy the data onto an existing fresh Zulip repo,
`./manage.py import zulip_data.zip`

## References

1. Zulip's export function https://github.com/zulip/zulip/blob/master/zerver/lib/export.py
2. Zulip's sample export data https://github.com/zulip/zulip/blob/master/zerver/tests/test_export.py
3. Zulip's existing users and channels import https://github.com/zulip/zulip/tree/master/api/integrations/slack
4. https://get.slack.help/hc/en-us/articles/220556107-Understand-Slack-data-exports
5. https://github.com/zulip/zulip/issues/908#issuecomment-247719383
6. https://get.slack.help/hc/en-us/articles/201314026-Roles-and-permissions-in-Slack
7. http://zulip.readthedocs.io/en/latest/analytics.html?highlight=staff
8. https://github.com/zulip/zulip/blob/2012913cc13332aa8c14825a042ea11b4b2cfa79/zerver/models.py#L266
