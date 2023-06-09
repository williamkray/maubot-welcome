from typing import Awaitable, Type, Optional, Tuple
import json
import time

from mautrix.client import Client, InternalEventType, MembershipEventDispatcher, SyncStream
from mautrix.types import (Event, StateEvent, EventID, UserID, EventType,
                            RoomID, RoomAlias, ReactionEvent, RedactionEvent)
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from maubot import Plugin, MessageEvent
from maubot.handlers import command, event


class Config(BaseProxyConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("rooms")
        helper.copy("message")
        helper.copy("notification_room")
        helper.copy("notification_message")


class Greeter(Plugin):

    async def start(self) -> None:
        await super().start()
        self.config.load_and_update()
        self.client.add_dispatcher(MembershipEventDispatcher)
        
    @event.on(InternalEventType.JOIN)
    async def greet(self, evt: StateEvent) -> None:
        if evt.room_id in self.config["rooms"]:
            if evt.source & SyncStream.STATE:
                return
            else:
                nick = self.client.parse_user_id(evt.sender)[0]
                pill = '<a href="https://matrix.to/#/{mxid}">{nick}</a>'.format(mxid=evt.sender, nick=nick)
                msg = self.config["message"].format(user=pill) 
                await self.client.send_notice(evt.room_id, html=msg) 
                if self.config["notification_room"]:
                    roomnamestate = await self.client.get_state_event(evt.room_id, 'm.room.name')
                    roomname = roomnamestate['name']
                    notification_message = self.config['notification_message'].format(user=evt.sender, 
                                                                                      room=roomname)
                    await self.client.send_notice(self.config["notification_room"], html=notification_message)



    @classmethod
    def get_config_class(cls) -> Type[BaseProxyConfig]:
        return Config
