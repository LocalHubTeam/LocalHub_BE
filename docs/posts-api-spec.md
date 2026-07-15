# 게시판 API 명세서

이 문서는 `LocalHub_BE`의 게시판 API를 기준으로 프론트엔드에서 바로 연동할 수 있도록 정리한 명세입니다.

## 1. 기본 정보

- Base URL: `/api/posts`
- Content-Type: `application/json`
- 인증 방식: 없음
- 비밀번호 검증: 게시글 생성 시 저장한 비밀번호와 요청 비밀번호를 서버에서 비교

## 2. 공통 응답 규칙

### 성공
- 조회 성공: `200 OK`
- 생성 성공: `201 Created`
- 삭제 성공: `200 OK`

### 실패
- `404 Not Found`: 게시글이 존재하지 않음
- `401 Unauthorized`: 비밀번호가 일치하지 않음
- `422 Unprocessable Entity`: 필수 값 누락, 길이 제한 위반 등 입력 검증 실패

## 3. 데이터 모델

### PostRead
게시글 조회 응답에 사용됩니다.

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| id | number | 게시글 ID |
| category | string | 게시판 카테고리 |
| title | string | 제목 |
| content | string | 내용 |
| view_count | number | 조회수 |
| created_at | string(datetime) | 생성 시각 |
| updated_at | string(datetime) | 수정 시각 |

### PostCreate
게시글 생성 요청에 사용됩니다.

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| category | string | Y | 카테고리 |
| title | string | Y | 제목 |
| content | string | Y | 내용 |
| password | string | Y | 게시글 비밀번호 |

### PostUpdate
게시글 수정 요청에 사용됩니다.

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| category | string | Y | 카테고리 |
| title | string | Y | 제목 |
| content | string | Y | 내용 |
| password | string | Y | 기존 비밀번호 확인용 |

### PasswordVerifyRequest
비밀번호 확인 및 삭제 요청에 사용됩니다.

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| password | string | Y | 확인할 비밀번호 |

### PasswordVerifyResponse

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| verified | boolean | 비밀번호 일치 여부 |

## 4. API 목록

### 4.1 게시글 목록 조회

- `GET /api/posts`

#### Query Parameters

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| keyword | string | N | 제목 또는 내용에서 검색할 키워드 |
| category | string | N | 카테고리 필터 (`관광지`, `맛집`, `축제·행사` 등) |
| page | number | N | 페이지 번호, 기본값 1 |
| pageSize | number | N | 페이지당 게시글 수, 기본값 10 |

#### 동작
- `keyword`가 없으면 전체 게시글을 조회합니다.
- `category`가 있으면 해당 카테고리 게시글만 조회합니다.
- `keyword`가 있으면 제목 또는 내용에 해당 문자열이 포함된 게시글만 반환합니다.
- 정렬은 `created_at desc`, `id desc` 순서입니다.
- 응답은 페이지네이션 정보를 포함한 객체로 반환됩니다.

#### Response `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "category": "관광지",
      "title": "게시판 오픈 안내",
      "content": "게시판이 오픈되었습니다.",
      "view_count": 12,
      "created_at": "2026-07-14T09:00:00",
      "updated_at": "2026-07-14T09:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

---

### 4.2 게시글 상세 조회

- `GET /api/posts/{postId}`

#### Path Parameters

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| postId | number | Y | 게시글 ID |

#### Response `200 OK`
```json
{
  "id": 1,
  "category": "공지사항",
  "title": "게시판 오픈 안내",
  "content": "게시판이 오픈되었습니다.",
  "view_count": 12,
  "created_at": "2026-07-14T09:00:00",
  "updated_at": "2026-07-14T09:00:00"
}
```

#### Response `404 Not Found`
```json
{
  "detail": "게시글을 찾을 수 없습니다."
}
```

---

### 4.3 게시글 생성

- `POST /api/posts`

#### Request Body
```json
{
  "category": "자유게시판",
  "title": "첫 글입니다",
  "content": "안녕하세요",
  "password": "1234"
}
```

#### Response `201 Created`
```json
{
  "id": 2,
  "category": "자유게시판",
  "title": "첫 글입니다",
  "content": "안녕하세요",
  "view_count": 0,
  "created_at": "2026-07-14T10:00:00",
  "updated_at": "2026-07-14T10:00:00"
}
```

#### Validation Notes
- `category`: 1자 이상 50자 이하
- `title`: 1자 이상 255자 이하
- `content`: 1자 이상
- `password`: 1자 이상 255자 이하

---

### 4.4 게시글 수정

- `PUT /api/posts/{postId}`

#### Path Parameters

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| postId | number | Y | 게시글 ID |

#### Request Body
```json
{
  "category": "자유게시판",
  "title": "수정된 제목",
  "content": "수정된 내용",
  "password": "1234"
}
```

#### 동작
- 게시글이 없으면 `404 Not Found`
- 비밀번호가 다르면 `401 Unauthorized`
- 성공 시 게시글 내용을 수정하고 `updated_at`이 갱신됩니다.

#### Response `200 OK`
```json
{
  "id": 2,
  "category": "자유게시판",
  "title": "수정된 제목",
  "content": "수정된 내용",
  "view_count": 0,
  "created_at": "2026-07-14T10:00:00",
  "updated_at": "2026-07-14T10:05:00"
}
```

#### Response `401 Unauthorized`
```json
{
  "detail": "비밀번호가 일치하지 않습니다."
}
```

---

### 4.5 게시글 삭제

- `DELETE /api/posts/{postId}`

#### Path Parameters

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| postId | number | Y | 게시글 ID |

#### Request Body
```json
{
  "password": "1234"
}
```

#### 동작
- 삭제 요청은 JSON body로 비밀번호를 전달해야 합니다.
- 게시글이 없으면 `404 Not Found`
- 비밀번호가 다르면 `401 Unauthorized`

#### Response `200 OK`
```json
{
  "message": "게시글이 삭제되었습니다."
}
```

> 주의: 일부 클라이언트는 DELETE 요청 body 전송을 기본 지원하지 않을 수 있습니다. FE에서 `fetch` 또는 `axios`로 body를 명시적으로 실어 보내야 합니다.

---

### 4.6 비밀번호 확인

- `POST /api/posts/{postId}/verify-password`

#### Path Parameters

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| postId | number | Y | 게시글 ID |

#### Request Body
```json
{
  "password": "1234"
}
```

#### Response `200 OK`
```json
{
  "verified": true
}
```

#### 동작
- 게시글이 없으면 `404 Not Found`
- 비밀번호가 일치하면 `verified: true`
- 비밀번호가 틀리면 `verified: false`

## 5. 프론트엔드 연동 메모

### 권장 화면 흐름
1. 목록 화면에서 `GET /api/posts` 호출
2. 검색 입력이 있으면 `keyword`를 붙여 재조회
3. 상세 화면에서 `GET /api/posts/{postId}` 호출
4. 작성 화면에서 `POST /api/posts`
5. 수정 화면에서 `POST /api/posts/{postId}/verify-password`로 먼저 확인 후 `PUT /api/posts/{postId}` 호출
6. 삭제 화면에서 `DELETE /api/posts/{postId}`에 비밀번호 포함

### 주의할 점
- 현재 API에는 페이지네이션이 없습니다. 목록은 전체를 반환합니다.
- 조회수 증가용 별도 API는 없습니다.
- `password`는 응답에 절대 포함되지 않습니다.
- `view_count`는 읽기 전용으로 취급하는 것이 맞습니다.

## 6. 예시 에러 응답

### 입력 검증 실패
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character",
      "input": ""
    }
  ]
}
```

### 게시글 없음
```json
{
  "detail": "게시글을 찾을 수 없습니다."
}
```

### 비밀번호 불일치
```json
{
  "detail": "비밀번호가 일치하지 않습니다."
}
```
