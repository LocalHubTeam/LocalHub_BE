from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Location

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/api/maps",
    summary="장소 목록 조회",
    description="카테고리, 소분류, 지역, 검색어로 장소 목록을 전체 조회합니다.",
    tags=["map"],
)
def list_locations_no_pagination(
    type: str | None = Query(None, description="대분류 코드 (예: 12, 14, 39)"),
    subcategory: str | None = Query(None, description="소분류 코드 (예: NA04)"),
    region: str | None = Query(None, description="지역 코드 (예: 47-190, regn-signgu 형식)"),
    keyword: str | None = Query(None, description="검색어(제목 또는 주소 기준)"),
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
        query = query.filter(
            or_(
                Location.title.contains(keyword),
                Location.addr1.contains(keyword),
            )
        )

    items = query.all()
    return {"total": len(items), "items": items}
