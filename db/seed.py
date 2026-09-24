from models import SiteProfile, Work

PROFILE = SiteProfile()

WORKS = [
    Work(
        id="w01",
        slug="hanuel-tea",
        title="HANUEL",
        subtitle="차의 결을 담은 패키지 시스템",
        category="Brand Identity",
        year="2025",
        cover_url="/static/img/work-1.svg",
        gallery=["/static/img/work-1.svg", "/static/img/work-1b.svg"],
        body=(
            "한울은 제주의 고원에서 자란 찻잎을 다루는 브랜드다. "
            "우리는 산의 능선, 안개의 농도, 찻잔의 온기를 하나의 시각 언어로 묶었다. "
            "로고는 수평선과 찻잎의 실루엣을 겹쳐 만들었고, 패키지는 손으로 만졌을 때의 결을 우선했다. "
            "색은 코드가 아니라 계절이다. 봄의 연녹, 가을의 황토, 겨울의 먹색."
        ),
        tags=["packaging", "identity", "print"],
        client="Hanuel Tea Co.",
        role="Art Direction / Identity / Packaging",
        featured=True,
        like_count=128,
        review_count=9,
        created_at="2025-03-12",
        updated_at="2025-08-01",
    ),
    Work(
        id="w02",
        slug="nocturne-film",
        title="NOCTURNE",
        subtitle="야간의 도시를 위한 타이틀 시퀀스",
        category="Motion",
        year="2024",
        cover_url="/static/img/work-2.svg",
        gallery=["/static/img/work-2.svg", "/static/img/work-2b.svg"],
        body=(
            "네온이 꺼진 뒤의 서울. 가로등이 남기는 잔상, 빗물에 번진 간판. "
            "이 타이틀 시퀀스는 영화의 첫 2분 동안 관객의 호흡을 늦추기 위해 설계되었다. "
            "타이포는 금속활자의 무게를 디지털 공간에 옮겼고, 커팅은 숨과 보폭을 기준으로 했다."
        ),
        tags=["motion", "title", "film"],
        client="Nocturne Pictures",
        role="Title Design / Motion Direction",
        featured=True,
        like_count=96,
        review_count=6,
        created_at="2024-11-02",
        updated_at="2025-01-18",
    ),
    Work(
        id="w03",
        slug="atelier-mono",
        title="ATELIER MONO",
        subtitle="한 사람만을 위한 가구 브랜드 사이트",
        category="Digital",
        year="2025",
        cover_url="/static/img/work-3.svg",
        gallery=["/static/img/work-3.svg", "/static/img/work-3b.svg"],
        body=(
            "대량 생산이 아닌, 한 사람의 손과 한 사람의 방을 잇는 가구. "
            "웹사이트는 카탈로그가 아니라 작업실의 창이다. "
            "스크롤은 나무결을 따라가고, 이미지는 숨 고르듯 등장한다. "
            "커머스가 아니라 초대의 문장을 썼다."
        ),
        tags=["web", "e-commerce", "editorial"],
        client="Atelier Mono",
        role="Creative Direction / UX / Visual System",
        featured=True,
        like_count=74,
        review_count=5,
        created_at="2025-06-20",
        updated_at="2025-09-01",
    ),
    Work(
        id="w04",
        slug="paper-tide",
        title="PAPER TIDE",
        subtitle="계간 문예지 리디자인",
        category="Editorial",
        year="2023",
        cover_url="/static/img/work-4.svg",
        gallery=["/static/img/work-4.svg"],
        body=(
            "종이의 물결. 글이 먼저 오는 잡지에서 이미지는 침묵의 역할을 한다. "
            "여백을 늘리고, 본문 서체를 바꾸고, 표지는 매호 하나의 색만 남겼다. "
            "독자가 책장을 넘길 때의 소리가 디자인의 리듬이 되도록 했다."
        ),
        tags=["editorial", "print", "type"],
        client="Paper Tide Quarterly",
        role="Editorial Design / Type Direction",
        featured=False,
        like_count=51,
        review_count=4,
        created_at="2023-09-08",
        updated_at="2024-02-11",
    ),
    Work(
        id="w05",
        slug="lumen-gallery",
        title="LUMEN",
        subtitle="빛으로만 안내하는 전시 공간 사인",
        category="Spatial",
        year="2024",
        cover_url="/static/img/work-5.svg",
        gallery=["/static/img/work-5.svg"],
        body=(
            "벽에 글자를 붙이지 않았다. 조명의 강도와 색온도로 동선을 만들었다. "
            "관람객은 안내판을 읽지 않고, 밝아지는 쪽으로 걷는다. "
            "전시장이 끝난 뒤에도 망막에 남는 잔광이 이 작업의 결과물이다."
        ),
        tags=["spatial", "exhibition", "light"],
        client="Lumen Gallery",
        role="Spatial Identity / Wayfinding",
        featured=False,
        like_count=43,
        review_count=3,
        created_at="2024-04-15",
        updated_at="2024-05-02",
    ),
    Work(
        id="w06",
        slug="soft-signal",
        title="SOFT SIGNAL",
        subtitle="사운드 아티스트를 위한 앨범 비주얼",
        category="Music Visual",
        year="2025",
        cover_url="/static/img/work-6.svg",
        gallery=["/static/img/work-6.svg"],
        body=(
            "주파수를 색으로, 침묵을 여백으로. "
            "앨범 커버와 라이브 비주얼은 같은 파형에서 출발하지만 다른 속도로 움직인다. "
            "청각이 시각을 앞지르지 않도록, 이미지는 항상 반 박자 늦게 도착한다."
        ),
        tags=["music", "cover", "live visual"],
        client="Soft Signal",
        role="Art Direction / Cover / Live Visual",
        featured=False,
        like_count=67,
        review_count=7,
        created_at="2025-01-28",
        updated_at="2025-02-14",
    ),
]
