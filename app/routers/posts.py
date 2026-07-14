from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Query
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Post
from ..schemas import (
    PasswordVerifyRequest,
    PasswordVerifyResponse,
    PostListResponse,
    PostCreate,
    PostRead,
    PostUpdate,
)

router = APIRouter(prefix="/api/posts", tags=["posts"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_post_or_404(db: Session, post_id: int) -> Post:
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다.")
    return post


def _verify_password(post: Post, password: str) -> None:
    if post.password != password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="비밀번호가 일치하지 않습니다.")


@router.get("", response_model=PostListResponse)
def list_posts(
    keyword: str | None = None,
    category: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, alias="pageSize", ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Post)

    if category:
        query = query.filter(Post.category == category)

    if keyword:
        like_pattern = f"%{keyword}%"
        query = query.filter(
            Post.title.ilike(like_pattern) | Post.content.ilike(like_pattern)
        )

    total = query.count()
    total_pages = 0 if total == 0 else (total + page_size - 1) // page_size
    items = (
        query.order_by(Post.created_at.desc(), Post.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PostListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{postId}", response_model=PostRead)
def get_post(postId: int, db: Session = Depends(get_db)):
    return _get_post_or_404(db, postId)


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(payload: PostCreate, db: Session = Depends(get_db)):
    post = Post(
        category=payload.category,
        title=payload.title,
        content=payload.content,
        password=payload.password,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.put("/{postId}", response_model=PostRead)
def update_post(postId: int, payload: PostUpdate, db: Session = Depends(get_db)):
    post = _get_post_or_404(db, postId)
    _verify_password(post, payload.password)

    post.category = payload.category
    post.title = payload.title
    post.content = payload.content
    db.commit()
    db.refresh(post)
    return post


@router.delete("/{postId}")
def delete_post(postId: int, payload: PasswordVerifyRequest, db: Session = Depends(get_db)):
    post = _get_post_or_404(db, postId)
    _verify_password(post, payload.password)

    db.delete(post)
    db.commit()
    return {"message": "게시글이 삭제되었습니다."}


@router.post("/{postId}/verify-password", response_model=PasswordVerifyResponse)
def verify_password(postId: int, payload: PasswordVerifyRequest, db: Session = Depends(get_db)):
    post = _get_post_or_404(db, postId)
    return PasswordVerifyResponse(verified=post.password == payload.password)