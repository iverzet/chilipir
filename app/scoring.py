"""Comparable-price estimation, with conservative evidence thresholds."""
import re
from statistics import median

STOP = {"de","cu","si","și","pentru","in","în","la","nou","noua","original","originala","vand","vând","foto","aparat","body","obiectiv"}
def tokens(title):
    return set(w for w in re.findall(r"[a-z0-9]+",title.lower()) if len(w)>2 and w not in STOP)
def estimate(item, others):
    own=tokens(item["title"])
    if len(own)<2: return {"status":"insufficient_comparables","comparable_count":0}
    matches=[]
    for candidate in others:
        if candidate["url"]==item["url"] or candidate["category"]!=item["category"]:continue
        other=tokens(candidate["title"])
        overlap=len(own & other)
        similarity=overlap/max(len(own),len(other),1)
        if overlap>=2 and similarity>=0.65 and candidate["price_ron"]>0:
            matches.append(candidate["price_ron"])
    if len(matches)<3: return {"status":"insufficient_comparables","comparable_count":len(matches)}
    reference=median(matches)
    discount=(reference-item["price_ron"])/reference
    return {"status":"candidate" if discount>=0.25 else "not_a_deal",
            "reference_price_ron":round(reference,2),"discount_pct":round(discount*100,1),
            "comparable_count":len(matches),
            "warning":"Median of asking prices, not verified sales. Condition and authenticity not assessed."}
