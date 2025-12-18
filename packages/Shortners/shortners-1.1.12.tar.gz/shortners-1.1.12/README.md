<p align="center">
    📦 <a href="https://pypi.org/project/shortners" style="text-decoration:none;">SHORTNERS</a>
</p>

<p align="center">
   <a href="https://telegram.me/clinton_abraham"><img src="https://img.shields.io/badge/𝑪𝒍𝒊𝒏𝒕𝒐𝒏 𝑨𝒃𝒓𝒂𝒉𝒂𝒎-30302f?style=flat&logo=telegram" alt="telegram badge"/></a>
   <a href="https://telegram.me/Space_x_bots"><img src="https://img.shields.io/badge/Sᴘᴀᴄᴇ ✗ ʙᴏᴛꜱ-30302f?style=flat&logo=telegram" alt="telegram badge"/></a>
   <a href="https://telegram.me/sources_codes"><img src="https://img.shields.io/badge/Sᴏᴜʀᴄᴇ ᴄᴏᴅᴇꜱ-30302f?style=flat&logo=telegram" alt="telegram badge"/></a>
</p>

## INSTALLATION
```bash
pip install shortners
```

<img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif">

```python

import asyncio
from Shortners.functions import Shortners

shortner_api = "a1cgsja52iey3j53mg"
shortner_url = "https://modijiurl.com/api"
contents_url = "https://github.com/Clinton-Abraham"

core = Shortners(api=shortner_api, domain=shortner_url)

async def test():
    o = await core.convert(contents_url)
    print(o.result)
    print(o.status)
    print(o.errors)

asyncio.run(test())

```

<img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif">

```python

import asyncio
from Shortners.functions import Shortners

shortner_api = "a1cgsja52iey3j53mg"
shortner_url = "https://xxxxxx.net/api"
contents_url = "Link01 : https://github.com/Clinton-Abraham Link02 : https://telegram.me/Clinton_Abraham"

core = Shortners(api=shortner_api, domain=shortner_url)

async def test():
    o = await core.bulkshort(contents_url)
    print(o)

asyncio.run(test())

```

<img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif">
