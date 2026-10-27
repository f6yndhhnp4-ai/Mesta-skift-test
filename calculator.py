from datetime import timedelta
from .models import WindowRequest, Occupation, WorkWindow

def calculate(req: WindowRequest, occupations: list[Occupation]) -> list[WorkWindow]:
    if req.km_to < req.km_from:
        raise ValueError("km_to must be greater than or equal to km_from")
    if req.end <= req.start:
        raise ValueError("end must be after start")
    occ = sorted([o for o in occupations if o.end > req.start and o.start < req.end], key=lambda x:x.start)
    merged=[]
    for o in occ:
        s=max(o.start, req.start); e=min(o.end, req.end)
        if merged and s <= merged[-1][1]:
            merged[-1]=(merged[-1][0], max(merged[-1][1],e), merged[-1][2], o.identifier)
        else:
            merged.append((s,e,o.identifier,o.identifier))
    blocks=[]; cursor=req.start; previous=None
    for s,e,first,last in merged:
        if s>cursor: blocks.append((cursor,s,previous,first))
        cursor=max(cursor,e); previous=last
    if cursor<req.end: blocks.append((cursor,req.end,previous,None))
    before=timedelta(minutes=req.safety_before_minutes)
    after=timedelta(minutes=req.safety_after_minutes)
    out=[]
    for s,e,prev,nxt in blocks:
        safe_s=s+(after if prev else timedelta())
        safe_e=e-(before if nxt else timedelta())
        gross=int((e-s).total_seconds()//60)
        net=max(0,int((safe_e-safe_s).total_seconds()//60))
        if net>=req.minimum_window_minutes:
            out.append(WorkWindow(start=safe_s,end=safe_e,gross_minutes=gross,net_minutes=net,preceding=prev,following=nxt))
    return out
