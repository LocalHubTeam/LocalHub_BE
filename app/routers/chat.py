from fastapi import APIRouter, Depends
from pydantic import BaseModel
from openai import OpenAI
from sqlalchemy.orm import Session
from sqlalchemy import or_
import os

from ..database import SessionLocal
from ..models import Location, Post

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


# 시군구까지 특정하는 지역명 (구체적 매칭, 우선순위 높음)
REGION_KEYWORDS = {
    "구미": ("47", "190"), "칠곡": ("47", "830"), "성주": ("47", "840"), "고령": ("47", "850"),
    "중구": ("27", "110"), "동구": ("27", "140"), "서구": ("27", "170"),
    "남구": ("27", "200"), "북구": ("27", "230"), "수성구": ("27", "260"),
    "달서구": ("27", "290"), "달성": ("27", "710"), "군위": ("27", "720"),
}

# 광역 단위 지역명 (구체적 매칭이 없을 때 사용)
BROAD_REGION_KEYWORDS = {
    "대구": "27",
    "경북": "47",
}

CATEGORY_KEYWORDS = {
    "관광지": "12", "관광": "12", "문화시설": "14", "축제": "15", "공연": "15",
    "여행코스": "25", "레포츠": "28", "숙박": "32", "호텔": "32",
    "쇼핑": "38", "맛집": "39", "음식점": "39", "식당": "39",
}


def search_locations(db: Session, message: str, limit: int = 5):
    query = db.query(Location)

    matched_region = False

    # 1) 시군구까지 구체적인 지역명 먼저 확인
    for keyword, (regn, signgu) in REGION_KEYWORDS.items():
        if keyword in message:
            query = query.filter(Location.lDongRegnCd == regn, Location.lDongSignguCd == signgu)
            matched_region = True
            break

    # 2) 구체적인 매칭이 없으면 광역 단위(대구/경북) 확인
    if not matched_region:
        for keyword, regn in BROAD_REGION_KEYWORDS.items():
            if keyword in message:
                query = query.filter(Location.lDongRegnCd == regn)
                matched_region = True
                break

    matched_category = False
    for keyword, type_id in CATEGORY_KEYWORDS.items():
        if keyword in message:
            query = query.filter(Location.contenttypeid == type_id)
            matched_category = True
            break

    if not matched_region and not matched_category:
        query = query.filter(Location.title.contains(message[:10]))

    return query.limit(limit).all()


def search_posts(db: Session, message: str, limit: int = 3):
    return (
        db.query(Post)
        .filter(or_(Post.title.contains(message[:10]), Post.content.contains(message[:10])))
        .order_by(Post.created_at.desc())
        .limit(limit)
        .all()
    )


def build_context(locations: list[Location], posts: list[Post]) -> str:
    parts = []

    if locations:
        parts.append("[관련 장소 정보]")
        for loc in locations:
            parts.append(
                f"- {loc.title} ({loc.addr1 or '주소 정보 없음'})"
                f"{' / 전화: ' + loc.tel if loc.tel else ''}"
            )
    else:
        parts.append("[관련 장소 정보] 검색 결과 없음")

    if posts:
        parts.append("\n[관련 커뮤니티 게시글]")
        for post in posts:
            parts.append(f"- {post.title}: {post.content[:80]}...")

    return "\n".join(parts)


@router.post("/api/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    locations = search_locations(db, req.message)
    posts = search_posts(db, req.message)
    context = build_context(locations, posts)

    system_prompt = (
        "당신은 LocalHub 챗봇입니다. 대구/경북 구미·칠곡·성주·고령 지역의 "
        "관광지, 음식점, 숙박, 축제 정보를 안내합니다. "
        "아래 제공된 실제 데이터를 근거로만 답변하고, 데이터에 없는 내용은 "
        "추측하거나 지어내지 말고 '해당 정보를 찾을 수 없습니다'라고 답하세요.\n\n"
        f"{context}"
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages += [{"role": m.role, "content": m.content} for m in req.history]
    messages.append({"role": "user", "content": req.message})

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=messages,
    )

    return {
        "reply": response.choices[0].message.content,
        "locations": [
            {
                "contentid": loc.contentid,
                "title": loc.title,
                "addr1": loc.addr1,
                "firstimage2": loc.firstimage2,
            }
            for loc in locations
        ],
    }