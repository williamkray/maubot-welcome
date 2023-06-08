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
                    await self.client.send_markdown(self.config["notification_room"], f"User {evt.sender} joined \
                            {evt.room_id} and I want everyone in this @room to know")



    @classmethod
    def get_config_class(cls) -> Type[BaseProxyConfig]:
        return Config
