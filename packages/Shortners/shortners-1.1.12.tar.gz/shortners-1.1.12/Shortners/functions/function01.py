
#====================================================================================================

class Shortner:

    async def shortlink(self, recived, **kwargs):
        async with self.seon() as seion:
            param = {'api': self.apis, 'url': recived}
            async with seion.get(self.site, params=param, timeout=self.tims, **kwargs) as oem:
                if oem.status == 200 or oem.status == "success":
                    moones = await oem.json()
                    moonus = moones.get("shortenedUrl", None)
                    return moonus
                else:
                    return None

#====================================================================================================
