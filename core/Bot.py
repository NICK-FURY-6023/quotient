from __future__ import annotations

from typing import TYPE_CHECKING, Any, AsyncGenerator, Callable, Coroutine, Dict, Iterable, List, Optional, Union

if TYPE_CHECKING:
    from ..cogs.reminder import Reminders

import asyncio
import itertools
import os
import time
from datetime import datetime, timedelta

import aiohttp
import discord
from aiocache import cached
from discord import AllowedMentions, Intents
from discord.ext import commands
from lru import LRU

import config as cfg
import constants as csts
from models import Guild, Timer

from .cache import CacheManager
from .Context import Context
from .Help import HelpCommand

intents = Intents.default()
intents.members = True
intents.message_content = True


os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["OMP_THREAD_LIMIT"] = "1"

__all__ = ("Quotient", "bot")


on_startup: List[Callable[["Quotient"], Coroutine]] = []


class Quotient(commands.AutoShardedBot):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            max_messages=1000,
            strip_after_prefix=True,
            case_insensitive=True,
            help_command=HelpCommand(),
            chunk_guilds_at_startup=False,
            allowed_mentions=AllowedMentions(everyone=False, roles=False, replied_user=True, users=True),
            activity=discord.Activity(type=discord.ActivityType.listening, name="qsetup | qhelp"),
            proxy=getattr(cfg, "PROXY_URI", None),
            **kwargs,
        )

        self.loop = asyncio.get_event_loop()
        self.start_time = datetime.now(tz=csts.IST)
        self.cmd_invokes = 0
        self.seen_messages = 0

        self.persistent_views_added = False
        self.sio = None

        self.lockdown: bool = False
        self.lockdown_msg: Optional[str] = None
        self._BotBase__cogs = commands.core._CaseInsensitiveDict()

        self.message_cache: Dict[int, Any] = LRU(1024)  # type: ignore

    @property
    def config(self) -> cfg:
        return __import__("config")

    

    async def init_quo(self):
        self.session = aiohttp.ClientSession(loop=self.loop)
        

        self.cache = CacheManager(self)
        await self.cache.fill_temp_cache()

        for mname, model in Tortoise.apps.get("models").items():
            model.bot = self

    async def setup_hook(self) -> None:
        await self.init_quo()
        for coro_func in on_startup:
            self.loop.create_task(coro_func(self))

    async def get_prefix(self, message: discord.Message) -> Union[str, Callable, List[str]]:
        if not message.guild:
            return commands.when_mentioned_or("q")(self, message)

        prefix = None
        guild = self.cache.guild_data.get(message.guild.id)
        if guild:
            prefix = guild.get("prefix")
        else:
            self.cache.guild_data[message.guild.id] = {
                "prefix": "q",
                "color": self.color,
                "footer": cfg.FOOTER,
            }

        prefix = prefix or "q"

        return commands.when_mentioned_or(
            *tuple("".join(chars) for chars in itertools.product(*zip(prefix.lower(), prefix.upper())))
        )(self, message)

    async def close(self) -> None:
        await super().close()
        if hasattr(self, "session"):
            await self.session.close()
        

    async def on_ready(self):
        print(f"[Quotient] Logged in as {self.user.name}({self.user.id})")


bot = Quotient()


@bot.before_invoke
async def bot_before_invoke(ctx: Context):
    if ctx.guild is not None and not ctx.guild.chunked:
        bot.loop.create_task(ctx.guild.chunk())
