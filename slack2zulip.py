#!/usr/bin/env python
import os
import json
import hashlib
import sys
import argparse
import shutil


def rm_tree(path):
    # type: (str) -> None
    if os.path.exists(path):
        shutil.rmtree(path)


def users2zerver_userprofile(slack_dir, realm_id):
    # type: () -> None
    print('######### IMPORTING USERS STARTED #########\n')
    users = json.load(open(slack_dir + '/users.json'))
    zerver_userprofile = []
    added_users = {}
    user_id_count = 1
    for user in users:
        slack_user_id = user['id']
        profile = user['profile']
        if 'email' not in profile:
            email = hashlib.blake2b(user['real_name'].encode()).hexdigest() + "@zulipchat.com"
        userprofile = dict(
            enable_desktop_notifications=True,
            is_staff=False,
            # avatar_source:
            is_bot=user['is_bot'],
            avatar_version=1,
            autoscroll_forever=False,
            default_desktop_notifications=True,
            timezone=user.get("tz", ""),
            default_sending_stream=None,
            enable_offline_email_notifications=True,
            user_permissions=[],  # TODO ???
            is_mirror_dummy=False,
            pointer=-1,
            default_events_register_stream=None,
            is_realm_admin=user['is_admin'],  # TODO
            invites_granted=0,
            enter_sends=True,
            bot_type=1 if user['is_bot'] else None,
            enable_stream_sounds=False,
            is_api_super_user=False,
            rate_limits="",
            # last_login=1498439473,  TODO
            tos_version=None,
            default_all_public_streams=False,
            full_name=user['real_name'],
            twenty_four_hour_time=False,
            groups=[],  # TODO
            muted_topics=[],
            enable_online_push_notifications=False,
            alert_words="[]",
            # bot_owner= null,  TODO
            short_name=user['name'],
            enable_offline_push_notifications=True,
            left_side_userlist=False,
            enable_stream_desktop_notifications=False,
            enable_digest_emails=True,
            last_pointer_updater="",
            email=email,
            # date_joined= 1498439473,  TODO
            # last_reminder= 1498439473,  TODO
            is_superuser=False,
            tutorial_status="F",  # TODO should this be T?
            default_language="en",
            enable_sounds=True,
            pm_content_in_desktop_notifications=True,
            is_active=True,
            onboarding_steps="[]",
            emojiset="google",
            emoji_alt_code=False,
            realm=realm_id,  # TODO
            quota=1073741824,  # TODO
            invites_used=0,
            id=user_id_count)

        # TODO map if user is `deleted` or not (true/false)

        # TODO map the permission hierarchy:
        # - in Slack: is_primary_owner, is_owner, is_admin, member (default),
        # is_restricted (for guests), is_ultra_restricted
        # - in Zulip: is_realm_admin, is_staff, is_superuser, is_api_super_user
        # Slack's permission hierarchy is more granular

        # TODO map the avatar
        # zerver auto-infer the url from Gravatar instead of from a specified
        # url; zerver.lib.avatar needs to be patched
        # profile['image_32'], Slack has 24, 32, 48, 72, 192, 512 size range

        zerver_userprofile.append(userprofile)
        added_users[slack_user_id] = user_id_count
        user_id_count += 1
        print(u"{} -> {}\nCreated\n".format(user['name'], userprofile['email']))
    print('######### IMPORTING USERS FINISHED #########\n')
    return zerver_userprofile, added_users

#def create_streams_and_add_subscribers(added_users):
def channels2zerver_stream(slack_dir, realm_id):
    # type: (Dict[str, Dict[str, str]]) -> None
    print('######### IMPORTING CHANNELS STARTED #########\n')
    channels = json.load(open(slack_dir + '/channels.json'))
    added_channels = {}
    zerver_stream = []
    stream_id_count = 1
    for channel in channels:
        # slack_channel_id = channel['id']

        # TODO Zulip doesn't store subscribed users in zerver_stream, should
        # this be the case?
        #subscribed_users = [added_users[member]['email'] for member in
        #                    channel['members'] if member in added_users.keys()]
        stream = dict(
                   realm=realm_id,
                   name=channel["name"],
                   deactivated=channel["is_archived"],
                   description=channel["topic"]["value"],
                   invite_only=not channel["is_general"],
                   date_created=channel["created"],
                   id=stream_id_count)
        zerver_stream.append(stream)
        added_channels[stream['name']] = stream_id_count
        stream_id_count += 1
        print(u"{} -> created\n".format(channel['name']))

        # TODO map creator
        # TODO map Slack's topic and purpose content, 
        # e.g.
        # "topic": {
        #      "value": "Company-wide announcements and work-based matters",
        #      "creator": "U6006P1CN",
        #      "last_set": "1498401043"
        # },
        # "purpose": {
        #     "value": "This channel is for team-wide communication and announcements. All team members are in this channel.",
        #     "creator": "U6006P1CN",
        #     "last_set": "1498401043"
        # }
        # TODO map Slack's pins to Zulip's stars
        # "pins": [
        #         {
        #             "id": "1444755381.000003",
        #             "type": "C",
        #             "user": "U061A5N1G",
        #             "owner": "U061A5N1G",
        #             "created": "1444755463"
        #         }
        #         ],
    print('######### IMPORTING STREAMS FINISHED #########\n')
    return zerver_stream, added_channels

def channelmessage2zerver_message(slack_dir, channel, added_users, added_channels):
    json_names = os.listdir(slack_dir + '/' + channel)
    zerver_message = []
    msg_id_count = 1
    for json_name in json_names:
        msgs = json.load(open(slack_dir + '/%s/%s' % (channel, json_name)))
        for msg in msgs:
            text = msg['text']
            zulip_message = dict(
                    sending_client=1,  # TODO detect this
                    rendered_content_version=1,  # TODO ?? doublecheck
                    has_image=False,  # TODO
                    subject=channel,  # TODO default subject to channel name; Slack has subtype and type
                    pub_date=msg['ts'],
                    id=msg_id_count,
                    has_attachment=False,  # attachment will be posted in the subsequent message; this is how Slack does it, less like email
                    edit_history=None,
                    sender=added_users[msg['user']],  # map slack id to zulip id
                    content=text,
                    rendered_content=text,  # TODO slack doesn't cache this, check whether text is rendered
                    recipient=added_channels[channel],
                    last_edit_time=None,
                    has_link=False)  # TODO
            zerver_message.append(zulip_message)
    return zerver_message

def main(slack_dir):
    # type: () -> None
    DOMAIN_NAME = "zulipchat.com"
    REALM_ID = 1
    REALM_NAME = "FleshEatingBatswithFangs"

    # Make sure the directory output is clean
    output_dir = 'zulip_data'
    rm_tree(output_dir)
    os.makedirs(output_dir)

    realm = dict(
            zerver_defaultstream=[],  # TODO
            zerver_client=[{"name": "populate_db", "id": 1},
                           {"name": "website", "id": 2},
                           {"name": "API", "id": 3}],
            zerver_userpresence=[],  # TODO
            zerver_userprofile_mirrordummy=[],
            zerver_realmdomain=[{"realm": REALM_ID,
                                 "allow_subdomains": False,
                                 "domain": DOMAIN_NAME,
                                 "id": REALM_ID}],
            zerver_useractivity=[],
            zerver_realm=[{
                          "message_retention_days": None,
                          "inline_image_preview": True,
                          "name_changes_disabled": False,
                          "string_id": REALM_NAME,  # TODO what is the difference between this and real name below?
                          "icon_version": 1,
                          "waiting_period_threshold": 0,
                          "email_changes_disabled": False,
                          "deactivated": False,
                          "notifications_stream": None,
                          "restricted_to_domain": True,
                          "show_digest_email": True,
                          "allow_message_editing": True,
                          "description": "The Zulip development environment default organization.  It's great for testing!",
                          "default_language": "en",
                          "icon_source": "G",
                          "invite_required": False,
                          "invite_by_admins_only": False,
                          "create_stream_by_admins_only": False,
                          "mandatory_topics": False,
                          "inline_url_embed_preview": True,
                          "message_content_edit_limit_seconds": 600,
                          "authentication_methods": [
                            ["Google", True],
                            ["Email", True],
                            ["GitHub", True],
                            ["LDAP", True],
                            ["Dev", True],
                            ["RemoteUser", True]
                          ],
                          "name": REALM_NAME,
                          "org_type": 1,
                          "add_emoji_by_admins_only": False,
                          "date_created": 1498439472.229782,  # TODO
                          "id": REALM_ID,
                          }],
            zerver_huddle=[],  # TODO
            zerver_userprofile_crossrealm=[],  # TODO
            zerver_useractivityinterval=[],
            zerver_realmfilter=[],
            zerver_realmemoji=[])

    zerver_userprofile, added_users = users2zerver_userprofile(slack_dir, REALM_ID)
    realm['zerver_userprofile'] = zerver_userprofile

    # TODO generate zerver_subscription from zerver_userprofile
    # TODO generate zerver_recipient from zerver_userprofile

    zerver_stream, added_channels = channels2zerver_stream(slack_dir, REALM_ID)
    realm['zerver_stream'] = zerver_stream
    # IO
    json.dump(realm, open(output_dir + '/realm.json', 'w'))

    # now for message.json
    message_json = {}
    zerver_message = []
    # TODO map zerver_usermessage
    for channel in added_channels.keys():
        zerver_message.append(channelmessage2zerver_message(slack_dir, channel,
                              added_users, added_channels))
    message_json['zerver_message'] = zerver_message
    # IO
    json.dump(message_json, open(output_dir + '/message.json', 'w'))

    # TODO
    # attachments

    sys.exit(0)

if __name__ == '__main__':
    description = ("script to convert Slack export data into Zulip export data")
    parser = argparse.ArgumentParser(description=description)
    slack_dir = sys.argv[1]
    main(slack_dir)
