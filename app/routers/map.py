from fastapi import APIRouter, Depends, Query, HTTPException
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
    type: str | None = Query(
        None,
        description="대분류 코드 (예: 12, 14, 39)",
    ),
    subcategory: str | None = Query(
        None,
        description="소분류 코드 (예: NA04)",
    ),
    region: str | None = Query(
        None,
        description="지역 코드 (예: 47 또는 47-190)",
    ),
    keyword: str | None = Query(
        None,
        description="검색어(제목 또는 주소 기준)",
    ),
    db: Session = Depends(get_db),
):
    # LOCATION 테이블 전체 데이터를 기준으로 조회를 시작합니다.
    query = db.query(Location)

    # 대분류 값이 있을 때만 필터링합니다.
    if type and type.strip():
        query = query.filter(
            Location.contenttypeid == type.strip()
        )

    # 소분류 값이 있을 때만 필터링합니다.
    if subcategory and subcategory.strip():
        query = query.filter(
            Location.lclsSystm2 == subcategory.strip()
        )

    # 지역 값이 있을 때만 필터링합니다.
    if region and region.strip():
        region_value = region.strip()

        # 프론트엔드에서 전체 지역을 나타내는 값은 필터링하지 않습니다.
        if region_value.lower() not in {"all", "전체"}:
            region_parts = region_value.split("-")

            # 예: region=47
            # 광역 지역 코드만 들어온 경우입니다.
            if len(region_parts) == 1:
                regn = region_parts[0]

                query = query.filter(
                    Location.lDongRegnCd == regn
                )

            # 예: region=47-190
            # 광역 지역 코드와 시군구 코드가 모두 들어온 경우입니다.
            elif len(region_parts) == 2:
                regn, signgu = region_parts

                query = query.filter(
                    Location.lDongRegnCd == regn,
                    Location.lDongSignguCd == signgu,
                )

            # 지원하지 않는 지역 코드 형식입니다.
            else:
                raise HTTPException(
                    status_code=400,
                    detail="region은 '47' 또는 '47-190' 형식이어야 합니다.",
                )

    # 검색어가 있을 때 제목 또는 주소를 기준으로 검색합니다.
    if keyword and keyword.strip():
        keyword_value = keyword.strip()

        query = query.filter(
            or_(
                Location.title.contains(keyword_value),
                Location.addr1.contains(keyword_value),
            )
        )

    # 필터값이 하나도 없다면 LOCATION 테이블 전체 행이 반환됩니다.
    items = query.all()

    return {
        "total": len(items),
        "items": items,
    }
