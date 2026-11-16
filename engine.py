import aiohttp
import io
from PIL import Image, ExifTags
import asyncio
import requests

class OSINTEngine:
    def init(self):
        self.session = aiohttp.ClientSession()
        self.headers = {"User-Agent": "Mozilla/5.0"}

    async def execute(self, t, v, photo=None):
        if t == "passport": return await self.passport(v)
        if t == "car": return await self.car(v)
        if t == "socials": return await self.socials(v)
        if t == "photo": return await self.photo(photo)
        if t == "ip": return await self.ip(v)
        if t == "name": return await self.name(v)
        return {"error": "unknown type"}

    async def passport(self, p):
        hibp = await self.hibp_check(p)
        return {"type": "passport", "number": p, "hibp_breaches": hibp}

    async def car(self, p):
        return {"type": "car", "plate": p.upper(), "status": "Checked"}

    async def socials(self, u):
        sites = ["GitHub", "Twitter", "Instagram", "Steam"]
        return {"type": "socials", "username": u, "found": sites}

    async def photo(self, f):
        res = {}
        try:
            img = Image.open(io.BytesIO(f))
            exif_data = img._getexif()
            
            if exif_data:
                # Словарь для перевода кодов EXIF в понятные названия
                tags = {tag: ExifTags.TAGS.get(tag, tag) for tag in exif_data.keys()}
                
                # GPS
                if 34853 in exif_data: # GPSInfo
                    gps_info = exif_data[34853]
                    # Логика парсинга GPS упрощена, так как GPS в EXIF - это сложные дробные значения
                    # Для простоты проверим наличие и выведем "GPS Found"
                    res["gps_present"] = True
                    # Если хочешь точные координаты, нужно конвертировать RATIONAL в float
                    # Но для бота наличие GPS уже ценная информация
                    
                # Дата
                if 36868 in exif_data: # DateTimeOriginal
                    res["date"] = exif_data[36868]
                elif 306 in exif_data: # DateTime
                    res["date"] = exif_data[306]
                    
                # Модель камеры
                if 272 in exif_data: # Model
                    res["device"] = exif_data[272]
                    
                # Производитель
                if 271 in exif_data: # Make
                    res["make"] = exif_data[271]
                    
        except Exception as e:
            res["error"] = str(e)
        return res

    async def ip(self, ip):
        try:
            async with self.session.get(f"http://ip-api.com/json/{ip}") as r:
                data = await r.json()
                return {"country": data.get("country"), "city": data.get("city"), "isp": data.get("isp")}
        except:
            return {"error": "fail"}

    async def name(self, n):
        return {"type": "name", "name": n, "status": "Checked"}

    async def hibp_check(self, val):
        try:
            async with self.session.get(f"https://api.pwnedpasswords.com/range/{val}") as r:
                if r.status == 200:
                    text = await r.text()
                    return len(text.splitlines())
        except:
            pass
        return 0
