import json
import os
from .database import SessionLocal
from .models import Location, LocationType, DataSource

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

CONTENT_TYPES = {
    "12": "관광지", "14": "문화시설", "15": "축제공연행사", "25": "여행코스",
    "28": "레포츠", "32": "숙박", "38": "쇼핑", "39": "음식점",
}

def seed_all():
    db = SessionLocal()
    try:
        if db.query(Location).count() > 0:
            return

        for cid, name in CONTENT_TYPES.items():
            db.merge(LocationType(contenttypeid=cid, name=name))
        db.commit()

        for filename in os.listdir(DATA_DIR):
            if not filename.endswith(".json"):
                continue
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)

            for item in data.get("items", []):
                mapx = item.get("mapx")
                mapy = item.get("mapy")
                db.merge(Location(
                    contentid=item["contentid"],
                    contenttypeid=item["contenttypeid"],
                    title=item.get("title", ""),
                    addr1=item.get("addr1", ""),
                    addr2=item.get("addr2", ""),
                    tel=item.get("tel") or None,
                    mapx=float(mapx) if mapx else None,
                    mapy=float(mapy) if mapy else None,
                    lDongRegnCd=item.get("lDongRegnCd", ""),
                    lDongSignguCd=item.get("lDongSignguCd", ""),
                    lclsSystm1=item.get("lclsSystm1", ""),
                    lclsSystm2=item.get("lclsSystm2", ""),
                    lclsSystm3=item.get("lclsSystm3", ""),
                    firstimage=item.get("firstimage") or None,
                    firstimage2=item.get("firstimage2") or None,
                    createdtime=item.get("createdtime", ""),
                    modifiedtime=item.get("modifiedtime", ""),
                ))

            db.add(DataSource(
                contenttypeid=data.get("contentTypeId"),
                filename=filename,
                source_org="한국관광공사",
                license_type="공공누리 제3유형",
                collected_count=len(data.get("items", [])),
            ))

        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    seed_all()