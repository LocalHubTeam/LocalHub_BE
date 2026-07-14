# app/routers/locations.py
from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..database import SessionLocal
from ..models import Location, LocationType

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get(
    "/api/locations",
    summary="장소 목록 조회",
    description="카테고리, 소분류, 지역, 검색어로 장소 목록을 페이지 단위로 조회합니다.",
    tags=["locations"],
)
def list_locations(
    type: str | None = Query(None, description="대분류 코드 (예: 12, 14, 39)"),
    subcategory: str | None = Query(None, description="소분류 코드 (예: NA04)"),
    region: str | None = Query(None, description="지역 코드 (예: 47-190, regn-signgu 형식)"),
    keyword: str | None = Query(None, description="검색어(제목 또는 주소 기준)"),
    page: int = Query(1, description="페이지 번호"),
    size: int = Query(9, description="한 페이지당 데이터 개수"),
    db: Session = Depends(get_db),
):
    query = db.query(Location)

    if type:
        query = query.filter(Location.contenttypeid == type)
    if subcategory:
        query = query.filter(Location.lclsSystm2 == subcategory)
    if region:
        regn, signgu = region.split("-")
        query = query.filter(Location.lDongRegnCd == regn, Location.lDongSignguCd == signgu)
    if keyword:
        query = query.filter(or_(
            Location.title.contains(keyword),
            Location.addr1.contains(keyword),
        ))

    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return {"total": total, "page": page, "items": items}


@router.get(
    "/api/locations/{location_id}",
    summary="장소 상세 조회",
    description="contentid를 기준으로 특정 장소의 상세 정보를 조회합니다.",
    tags=["locations"],
)
def get_location_detail(location_id: str, db: Session = Depends(get_db)):
    loc = db.query(Location).filter(Location.contentid == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="장소를 찾을 수 없습니다")
    return loc


@router.get(
    "/api/location-types",
    summary="장소 타입 목록 조회",
    description="관광지, 문화시설, 음식점 등 장소 타입 목록을 조회합니다.",
    tags=["locations"],
)
def list_location_types(db: Session = Depends(get_db)):
    return db.query(LocationType).all()


@router.get(
    "/api/locations/subcategories",
    summary="소분류 목록 조회",
    description="대분류 선택 시 해당하는 소분류 목록을 조회합니다.",
    tags=["locations"],
)
def list_subcategories(type: str = Query(..., description="대분류 코드 (예: 12)"), db: Session = Depends(get_db)):
    rows = (
        db.query(Location.lclsSystm2)
        .filter(Location.contenttypeid == type, Location.lclsSystm2 != "")
        .distinct()
        .all()
    )
    return [r[0] for r in rows]