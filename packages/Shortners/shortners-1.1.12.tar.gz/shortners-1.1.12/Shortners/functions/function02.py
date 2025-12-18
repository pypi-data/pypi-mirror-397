import re
import aiohttp
import asyncio
from ..scripts import Regexs
from ..scripts import Scripted
from .function01 import Shortner
from .collections import SMessage
from aiohttp import ClientTimeout
#======================================================================================

class Shortners(Shortner):

    def __init__(self, **kwargs):
        self.seon = aiohttp.ClientSession
        self.tims = kwargs.get("timeout", 30)
        self.apis = kwargs.get("api", Scripted.DATA01)
        self.site = kwargs.get("domain", Scripted.DATA02)

#======================================================================================

    async def clinton(self, recived, **kwargs):
        try:
            moonus = await self.shortlink(recived, **kwargs)
            return SMessage(result=moonus, status=200)
        except asyncio.TimeoutError as errors:
            return SMessage(result=recived, status=404, errors=errors)
        except Exception as errors:
            return SMessage(result=recived, status=404, errors=errors)

#======================================================================================

    async def convert(self, recived, **kwargs):
        try:
            moonus = await self.shortlink(recived, **kwargs)
            return SMessage(result=moonus, status=200)
        except asyncio.TimeoutError as errors:
            return SMessage(result=recived, status=404, errors=errors)
        except Exception as errors:
            return SMessage(result=recived, status=404, errors=errors)

#======================================================================================

    async def bulkshort(self, text, wait=1, storage={}):
        alllinks = re.findall(Regexs.DATA01, text)
        for link in alllinks:
            newlink = await self.convert(link)
            storage[link] = newlink.result
            await asyncio.sleep(wait)

        for original, shortened in storage.items():
            text = text.replace(original, shortened)

        return text

#======================================================================================
