from datetime import datetime, timezone
import httpx
from .config import settings
from .models import WindowRequest, Occupation

class ConfigurationError(RuntimeError): pass

class BaneNorClient:
    def _validate(self):
        needed={"BANENOR_BASE_URL":settings.banenor_base_url,"BANENOR_CAPACITY_PATH":settings.banenor_capacity_path}
        missing=[k for k,v in needed.items() if not v]
        if missing: raise ConfigurationError("Missing Bane NOR configuration: "+", ".join(missing))

    async def _headers(self):
        headers={"Accept":"application/json"}
        if settings.banenor_subscription_key:
            headers["Ocp-Apim-Subscription-Key"]=settings.banenor_subscription_key
        if settings.banenor_token_url:
            if not settings.banenor_client_id or not settings.banenor_client_secret:
                raise ConfigurationError("OAuth token URL is set, but client credentials are missing")
            async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as c:
                r=await c.post(settings.banenor_token_url,data={"grant_type":"client_credentials","client_id":settings.banenor_client_id,"client_secret":settings.banenor_client_secret})
                r.raise_for_status(); headers["Authorization"]="Bearer "+r.json()["access_token"]
        return headers

    async def occupations(self, req: WindowRequest):
        self._validate()
        url=settings.banenor_base_url.rstrip('/')+'/'+settings.banenor_capacity_path.lstrip('/')
        params={"lineId":req.line_id,"kmFrom":req.km_from,"kmTo":req.km_to,"from":req.start.isoformat(),"to":req.end.isoformat()}
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as c:
            r=await c.get(url,params=params,headers=await self._headers()); r.raise_for_status(); payload=r.json()
        # Mapping must be aligned with Bane NOR's approved OpenAPI schema.
        rows=payload.get("items",payload if isinstance(payload,list) else [])
        return [Occupation(start=x["start"],end=x["end"],identifier=str(x.get("trainNumber") or x.get("id")),kind=x.get("kind","train"),source_version=x.get("version")) for x in rows]

    async def locations(self, query: str):
        if not settings.banenor_locations_path: raise ConfigurationError("Missing BANENOR_LOCATIONS_PATH")
        url=settings.banenor_base_url.rstrip('/')+'/'+settings.banenor_locations_path.lstrip('/')
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as c:
            r=await c.get(url,params={"query":query},headers=await self._headers()); r.raise_for_status(); return r.json()
