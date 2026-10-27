from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .models import WindowRequest, WindowResponse
from .banenor import BaneNorClient, ConfigurationError
from .calculator import calculate

app=FastAPI(title="Arbeidsluke Bane",version="1.0.0")
client=BaneNorClient()
app.mount("/static",StaticFiles(directory="app/static"),name="static")

@app.get("/")
def home(): return FileResponse("app/static/index.html")
@app.get("/health")
def health(): return {"status":"ok"}
@app.get("/api/locations")
async def locations(query:str=Query(min_length=2)):
    try: return await client.locations(query)
    except ConfigurationError as e: raise HTTPException(503,str(e))
    except Exception as e: raise HTTPException(502,"Bane NOR data source error")
@app.post("/api/work-windows",response_model=WindowResponse)
async def windows(req:WindowRequest):
    try:
        occupations=await client.occupations(req)
        result=calculate(req,occupations)
        return WindowResponse(windows=result,source="Bane NOR API",retrieved_at=datetime.now(timezone.utc),warning="Planleggingsstøtte. Ikke en tildelt disponering eller tillatelse til arbeid i spor.")
    except ConfigurationError as e: raise HTTPException(503,str(e))
    except ValueError as e: raise HTTPException(400,str(e))
    except Exception: raise HTTPException(502,"Bane NOR data source error")
