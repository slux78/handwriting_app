import json
import urllib.request
import urllib.error
import subprocess
import socket
import os
import random
import threading
import queue
import time

from db import get_existing_titles_and_authors, get_setting, is_content_duplicate, save_title_history, get_title_history

# macOS 환경에서 IPv6 DNS 블랙홀로 인한 15~25초 지연/타임아웃을 방지하기 위해 IPv4 강제 적용
_ipv4_patched = False
try:
    if not _ipv4_patched:
        _orig_getaddrinfo = socket.getaddrinfo
        def _ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
            return _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
        socket.getaddrinfo = _ipv4_getaddrinfo
        _ipv4_patched = True
except Exception:
    pass

# 고품질 문학 및 명문장 보관함
CURATED_FALLBACKS = [
    {
        "title": "서시(序詩)",
        "author": "윤동주",
        "category": "시",
        "content": (
            "죽는 날까지 하늘을 우러러\n"
            "한 점 부끄럼이 없기를,\n"
            "잎새에 이는 바람에도\n"
            "나는 괴로워했다.\n"
            "별을 노래하는 마음으로\n"
            "모든 죽어가는 것을 사랑해야지\n"
            "그리고 나한테 주어진 길을\n"
            "걸어가야겠다.\n\n"
            "오늘 밤에도 별이 바람에 스치운다.\n\n"
            "계절이 지나가는 하늘에는\n"
            "가을로 가득 차 있습니다.\n"
            "나는 아무 걱정도 없이\n"
            "가을 속의 별들을 다 헤일 듯합니다.\n"
            "가슴 속에 하나 둘 새겨지는 별을\n"
            "이제 다 못 헤는 것은\n"
            "쉬이 아침이 오는 까닭이요,\n"
            "내일 밤이 남은 까닭이요,\n"
            "아직 나의 청춘이 다하지 않은 까닭입니다."
        )
    },
    {
        "title": "월든(Walden) - 숲속의 생활",
        "author": "헨리 데이비드 소로",
        "category": "에세이",
        "content": (
            "내가 숲속으로 들어간 것은 인생을 의도적으로 살아보기 위해서였다.\n"
            "다시 말해 인생의 본질적인 사실들만을 직면해보고,\n"
            "인생이 가르쳐주는 바를 내가 배울 수 있는지 알아보고 싶었으며,\n"
            "그리하여 마침내 죽음에 이르렀을 때 내가 헛된 삶을 살지 않았음을 깨닫고 싶었다.\n"
            "나는 삶이 아닌 삶을 살고 싶지 않았으니, 삶이란 참으로 소중한 것이다.\n"
            "또한 정말 불가피하지 않는 한 체념하는 삶을 살고 싶지도 않았다.\n"
            "나는 깊이 있게 살기를 바랐고, 인생의 모든 골수를 빼먹고 싶었으며,\n"
            "스파르타인처럼 강인하게 살아 삶이 아닌 것은 모두 박멸하고 싶었다.\n\n"
            "우리의 삶은 사소한 일들에 의해 흐트러지고 있다.\n"
            "정직한 사람은 대개 열 손가락만 있으면 충분하고, 극단적인 경우라도 발가락 열 개만 더하면\n"
            "자신의 모든 일을 셀 수 있을 것이다. 단순하게, 단순하게, 단순하게 살라!\n"
            "그대의 일을 백 가지나 천 가지로 늘리지 말고 두세 가지로 줄여라."
        )
    },
    {
        "title": "어린 왕자 - 길들임의 의미",
        "author": "앙투안 드 생텍쥐페리",
        "category": "소설",
        "content": (
            "\"안녕.\" 여우가 말했다.\n"
            "\"안녕.\" 어린 왕자가 정중하게 대답하고 돌아섰지만 아무것도 보이지 않았다.\n"
            "\"나 여기 있어. 사과나무 밑에.\" 그 목소리가 말했다.\n"
            "\"너는 누구니? 참 예쁘구나.\" 어린 왕자가 말했다.\n"
            "\"난 여우야.\" 여우가 말했다.\n"
            "\"이리 와서 나와 함께 놀자. 난 지금 너무 쓸쓸해.\" 어린 왕자가 제안했다.\n"
            "\"난 너와 놀 수 없어. 길들여지지 않았으니까.\" 여우가 말했다.\n\n"
            "\"'길들인다'는 게 무슨 뜻이야?\" 어린 왕자가 물었다.\n"
            "\"그건 너무 잊혀진 일이지. 관계를 맺는다는 뜻이야.\" 여우가 말했다.\n"
            "\"관계를 맺는다고?\"\n"
            "\"그래. 넌 나에게 아직은 수많은 다른 소년들과 다를 바 없는 한 아이에 지나지 않아.\n"
            "그래서 난 네가 필요하지 않아. 너 역시 내가 필요하지 않고.\n"
            "하지만 네가 나를 길들인다면, 우리는 서로에게 이 세상에서 유일한 존재가 될 거야.\n"
            "밀밭이 황금빛으로 물들 때마다 난 너를 기억하게 될 거야.\""
        )
    },
    {
        "title": "침묵의 봄 - 사색의 길",
        "author": "레이첼 카슨",
        "category": "에세이",
        "content": (
            "자연의 아름다움에 대해 깊이 사색하는 사람은 삶이 다하는 날까지\n"
            "생명력을 잃지 않는 힘의 원천을 발견하게 된다.\n"
            "계절의 순환 속에는 끝없는 위로와 치유가 깃들어 있으며,\n"
            "겨울의 혹독한 추위 뒤에는 어김없이 봄이 찾아오리라는 변치 않는 약속이 있다.\n\n"
            "지구의 역사를 통틀어 볼 때, 생명체와 그 주변 환경의 관계는 서로 끊임없이 영향을 주고받는 상호작용의 과정이었다.\n"
            "인간이 자연을 정복하겠다는 오만한 생각을 버리고, 자연의 섭리와 조화를 이루며\n"
            "겸허한 태도로 살아갈 때 비로소 진정한 평화와 지속 가능한 미래를 만날 수 있다.\n"
            "숲길을 홀로 걷거나 고요한 바다를 바라보는 순간,\n"
            "우리는 우리 자신이 거대한 생명의 그물망 속 한 올의 실에 불과함을 깨닫는다."
        )
    },
    {
        "title": "그리스인 조르바 - 자유와 영혼",
        "author": "니코스 카잔차키스",
        "category": "소설",
        "content": (
            "나는 아무것도 바라지 않는다. 나는 아무것도 두려워하지 않는다. 나는 자유다.\n"
            "인간이 자기 자신을 구원할 수 있는 길은 오직 하나뿐이다.\n"
            "그것은 끊임없이 투쟁하고, 의심하고, 스스로를 넘어서며 전진하는 것이다.\n\n"
            "조르바는 나에게 삶을 사랑하고 죽음을 두려워하지 않는 법을 가르쳐 주었다.\n"
            "그는 먹을 때는 먹는 일에 온 영혼을 쏟았고, 사랑할 때는 온몸으로 사랑했으며,\n"
            "일할 때는 대지 깊숙이 뿌리를 박은 거목처럼 일했다.\n"
            "\"선생님, 산다는 게 도대체 무엇입니까? 두 손으로 흙을 쥐고 그 냄새를 깊이 들이마셔 보세요.\n"
            "바다의 푸른 물결에 몸을 던져 헤엄쳐 보세요. 그 속에 모든 대답이 들어 있습니다.\""
        )
    },
    {
        "title": "데미안 - 나를 찾아가는 길",
        "author": "헤르만 헤세",
        "category": "소설",
        "content": (
            "내 속에서 솟아 나오려는 것, 바로 그것을 나는 살아보려 했다.\n"
            "왜 그것이 그토록 어려웠을까?\n"
            "한 사람 한 사람의 삶은 자기 자신에게로 이르는 길이다.\n"
            "일찍이 그 어떤 사람도 완전히 자기 자신이 되어본 적은 없었다.\n"
            "그럼에도 누구나 자기 자신이 되려고 애쓴다.\n"
            "새는 알에서 나오려고 투쟁한다.\n"
            "알은 세계이다. 태어나려는 자는 하나의 세계를 깨뜨려야 한다.\n"
            "새는 신에게로 날아간다. 그 신의 이름은 아프락사스다."
        )
    },
    {
        "title": "명상록 - 내면의 고요",
        "author": "마르쿠스 아우렐리우스",
        "category": "위대한 사상가의 명언 및 철학 수필",
        "content": (
            "인간의 영혼은 외부의 사건에 의해 상처받지 않는다.\n"
            "오직 그 사건을 바라보는 자신의 생각과 판단에 의해서만 흔들릴 뿐이다.\n"
            "언제든 그대의 내면으로 물러서라. 인간이 찾아갈 수 있는 그 어떤 휴양지보다\n"
            "더 조용하고 번잡하지 않은 곳은 바로 자신의 영혼 속이다.\n"
            "그곳으로 들어가 잠시 머물며 마음을 가라앉히고 다시 삶의 의무로 돌아오라."
        )
    },
    {
        "title": "무소유의 역설",
        "author": "법정",
        "category": "에세이",
        "content": (
            "우리는 필요에 의해서 물건을 갖게 되지만,\n"
            "때로는 그 물건 때문에 적잖게 마음이 쓰이게 된다.\n"
            "무엇인가를 갖는다는 것은 다른 한편 무엇인가에 얽매이는 일이다.\n"
            "크게 버리는 사람만이 크게 얻을 수 있다.\n"
            "아무것도 갖지 않을 때 비로소 온 세상을 갖게 된다는 것은 무소유의 역설적인 진리이다."
        )
    },
    {
        "title": "창백한 푸른 점",
        "author": "칼 세이건",
        "category": "에세이",
        "content": (
            "저 점을 다시 보라. 저것이 여기다. 저것이 우리의 고향이며, 저것이 우리다.\n"
            "우리가 사랑하는 모든 이들, 우리가 알고 있는 모든 이들, 역사 속에 존재했던 모든 인류가\n"
            "햇빛 속에 떠도는 먼지 한 톨 위에서 살다 갔다.\n"
            "우주라는 거대한 암흑의 무대 속에서 우리의 지구는 너무나 외로운 얼룩 하나에 불과하다.\n"
            "우리가 아는 유일한 보금자리인 이 창백한 푸른 점을 소중히 보존해야 할 책임이 우리 모두에게 있다."
        )
    },
    {
        "title": "향수(鄕愁)",
        "author": "정지용",
        "category": "시",
        "content": (
            "넓은 벌 동쪽 끝으로\n"
            "옛이야기 지줄대는 실개천이 휘돌아 나가고,\n"
            "얼룩백이 황소가\n"
            "해설피 금빛 게으른 울음을 우는 곳,\n"
            "— 그곳이 차마 꿈엔들 잊힐 리야.\n\n"
            "질화로에 재가 식어지면\n"
            "비인 밭에 밤바람 소리 말을 달리고,\n"
            "엷은 졸음에 겨운 늙으신 아버지가\n"
            "짚베개를 돋아 고이시는 곳,\n"
            "— 그곳이 차마 꿈엔들 잊힐 리야."
        )
    }
]

# 백그라운드 프리페치 큐 (클릭 시 즉시 반환을 위한 큐)
_prefetch_queue = queue.Queue(maxsize=3)
_prefetch_lock = threading.Lock()
_is_prefetching = False

# thinkingConfig 지원 여부 캐시 (모델명 -> bool)
_thinking_support_cache = {}


def get_gemini_api_key():
    key = os.environ.get("GEMINI_API_KEY")
    if key and key.strip():
        return key.strip()
    
    key = get_setting("gemini_api_key")
    if key and key.strip():
        return key.strip()

    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("GEMINI_API_KEY="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val
    return None

def get_preferred_model():
    m = get_setting("gemini_model")
    return m if m and m.strip() else "gemini-3.8-flash"


def _build_gen_config(model_name):
    """모델별 최적 generationConfig 생성. thinkingConfig 지원 여부에 따라 분기."""
    gen_config = {
        "temperature": 0.9,
        "topP": 0.9,
        "maxOutputTokens": 2048,
        "responseMimeType": "application/json"
    }
    # 캐시된 결과에서 thinking 미지원으로 판명된 모델은 thinkingConfig 제외
    if _thinking_support_cache.get(model_name) is False:
        return gen_config
    # 기본적으로 thinkingBudget=0 설정 (thinking 비활성화하여 지연 방지)
    gen_config["thinkingConfig"] = {"thinkingBudget": 1}
    return gen_config


def _call_gemini_api(api_key, model_name, prompt, retry_without_thinking=True):
    """Gemini API 단일 호출. curl 우선, urllib 폴백. thinkingConfig 에러 시 1회 자동 재시도."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    gen_config = _build_gen_config(model_name)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": gen_config
    }
    data_str = json.dumps(payload)

    # 1차: macOS 네이티브 curl (IPv4 강제, 빠른 타임아웃)
    if os.path.exists("/usr/bin/curl"):
        cmd = [
            "/usr/bin/curl",
            "--ipv4",
            "-sS",
            "--connect-timeout", "3",
            "--max-time", "8",
            "-X", "POST",
            url,
            "-H", "Content-Type: application/json",
            "--data-raw", data_str
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=9)
            if res.returncode == 0 and res.stdout:
                resp_json = json.loads(res.stdout)
                if "error" in resp_json:
                    err_msg = resp_json["error"].get("message", "")
                    err_code = resp_json["error"].get("code")
                    # thinkingConfig 미지원 모델이면 캐시 후 thinking 없이 재시도
                    if err_code == 400 and "thinkingConfig" in err_msg and retry_without_thinking:
                        _thinking_support_cache[model_name] = False
                        return _call_gemini_api(api_key, model_name, prompt, retry_without_thinking=False)
                    raise Exception(f"API {err_code}: {err_msg}")
                return resp_json
        except json.JSONDecodeError as e:
            print(f"[curl JSON 파싱 오류]: {e}")
        except subprocess.TimeoutExpired:
            print(f"[curl timeout: {model_name}]")
        except Exception as e:
            if "thinkingConfig" in str(e) and retry_without_thinking:
                _thinking_support_cache[model_name] = False
                return _call_gemini_api(api_key, model_name, prompt, retry_without_thinking=False)
            print(f"[curl 예외, urllib 시도]: {e}")

    # 2차: urllib 폴백 (IPv4 패치 적용)
    headers = {"Content-Type": "application/json"}
    data_bytes = data_str.encode("utf-8")
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            resp_json = json.loads(resp.read().decode("utf-8"))
            if "error" in resp_json:
                err_msg = resp_json["error"].get("message", "")
                if resp_json["error"].get("code") == 400 and "thinkingConfig" in err_msg and retry_without_thinking:
                    _thinking_support_cache[model_name] = False
                    return _call_gemini_api(api_key, model_name, prompt, retry_without_thinking=False)
            return resp_json
    except urllib.error.HTTPError as e:
        if e.code == 400 and retry_without_thinking:
            _thinking_support_cache[model_name] = False
            return _call_gemini_api(api_key, model_name, prompt, retry_without_thinking=False)
        raise e


# 프롬프트 다양성을 위한 랜덤 요소들
_STYLE_DIRECTIVES = [
    "서정적이고 감성적인 문체로",
    "담백하고 절제된 문체로",
    "철학적이고 사색적인 문체로",
    "서사적이고 웅장한 문체로",
    "따뜻하고 위로가 되는 문체로",
    "고요하고 명상적인 문체로",
    "강렬하고 열정적인 문체로",
    "유려하고 시적인 문체로",
]

_ERA_DIRECTIVES = [
    "고전 작품(19세기 이전) 중에서",
    "근대 문학(19세기~20세기 초) 중에서",
    "현대 문학(20세기 중반 이후) 중에서",
    "동양 고전 중에서",
    "서양 고전 중에서",
    "한국 근현대 문학 중에서",
    "일본 문학 중에서",
    "유럽 문학 중에서",
    "러시아 문학 중에서",
    "남미 문학 중에서",
    "시대와 국적에 관계없이 숨겨진 명문 중에서",
]

_EXTENDED_CATEGORIES = [
    "시", "소설", "에세이", "여행기",
    "위대한 사상가의 명언 및 철학 수필",
    "편지글", "일기문학", "회고록",
    "자연과학 산문", "역사 서술",
    "고전 산문", "명연설문",
]


def _normalize_title(title):
    """제목에서 부제, 괄호, 특수문자 등을 제거하여 핵심 키워드만 추출."""
    import re
    t = title.strip()
    # '제목 - 부제' 형식에서 주제목만
    t = t.split(' - ')[0].split(' — ')[0].split(' : ')[0]
    # 괄호 및 괄호 내용 제거
    t = re.sub(r'[\(\)\[\]\{\}（）「」『』\-·]', ' ', t)
    # 공백 정리
    t = ' '.join(t.split()).strip()
    return t


def _is_title_duplicate(title, existing_items):
    """제목이 기존 목록에 있는지 부분 일치(substring)로 확인."""
    norm_new = _normalize_title(title)
    if not norm_new:
        return False
    for item in existing_items:
        norm_exist = _normalize_title(item.get('title', ''))
        if not norm_exist:
            continue
        # 어느 한쪽이 다른 쪽에 포함되면 중복
        if norm_new in norm_exist or norm_exist in norm_new:
            return True
    return False


def _generate_live(api_key, preferred_category=None, preferred_model=None):
    """실시간 Gemini API 호출. 중복 시 최대 5회 재시도."""
    # DB에서 기존 작품 + 생성 이력을 모두 가져와 중복 방지
    existing_items = get_existing_titles_and_authors(limit=200)
    title_history_items = get_title_history(limit=500)
    all_excluded_items = existing_items + title_history_items

    excluded_titles = [item['title'] for item in all_excluded_items if item.get('title')]
    existing_summary = ", ".join([f"'{t}'" for t in excluded_titles])

    selected_category = (
        preferred_category if preferred_category in _EXTENDED_CATEGORIES
        else random.choice(_EXTENDED_CATEGORIES)
    )

    target_model = preferred_model or get_preferred_model()
    max_attempts = 5

    for attempt in range(1, max_attempts + 1):
        # 매 시도마다 스타일/시대를 랜덤으로 변경하여 다양성 확보
        style = random.choice(_STYLE_DIRECTIVES)
        era = random.choice(_ERA_DIRECTIVES)
        seed_hint = random.randint(1, 99999)

        prompt = f"""당신은 마음을 정돈하는 필사(손글씨 연습) 전문가입니다.
1. 분야: {selected_category}
2. 스타일: {style}
3. 시대/지역: {era}
4. 분량: 손글씨 필사용 (공백 포함 약 350자~950자). A4 반 장에서 한 장 분량. 문단을 명확히 나눌 것.
5. 톤: 장난기 없는 진중하고 격조 높은 한국어 문체.
6. 중복 제외 (아래 작품들은 절대 다시 선택하지 말 것): [{existing_summary}]
7. 독창성: 널리 알려진 작품보다는 잘 알려지지 않은 숨은 명작이나 명문장을 우선 선택하라.
8. 다양성 시드: {seed_hint} (이 숫자를 참고하여 이전과 전혀 다른 작품을 선택하라)

반드시 JSON만 응답:
{{
  "title": "작품 제목",
  "author": "작가/인물명",
  "category": "{selected_category}",
  "content": "필사 본문 텍스트"
}}"""

        t0 = time.time()
        try:
            print(f"[Gemini API] 호출 시작 (시도 {attempt}/{max_attempts}): {target_model}...")
            result_json = _call_gemini_api(api_key, target_model, prompt)

            candidates = result_json.get("candidates", [])
            if not candidates:
                print(f"[Gemini API] {target_model}: 빈 응답")
                continue
            content_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")

            clean_text = content_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()

            parsed = json.loads(clean_text)
            title = parsed.get("title", "무제").strip()
            author = parsed.get("author", "작자 미상").strip()
            category = parsed.get("category", selected_category).strip()
            content = parsed.get("content", "").strip()

            elapsed = round(time.time() - t0, 2)

            if not content:
                print(f"[Gemini API] {target_model}: 빈 콘텐츠 (시도 {attempt})")
                continue

            # 중복 체크: 제목 부분 일치 또는 콘텐츠 해시가 동일하면 재시도
            if _is_title_duplicate(title, all_excluded_items) or is_content_duplicate(content):
                save_title_history(title, author)  # DB에 이력 저장
                print(f"[Gemini API] 중복 감지 '「{title}」({author})' → DB 이력 저장, 재시도 ({attempt}/{max_attempts})")
                # 재시도 시 제외 목록 갱신 & 카테고리 변경
                excluded_titles.append(title)
                existing_summary = ", ".join([f"'{t}'" for t in excluded_titles])
                selected_category = random.choice(_EXTENDED_CATEGORIES)
                continue

            # 성공한 제목도 DB 이력에 저장
            save_title_history(title, author)

            print(f"[Gemini API] 호출 성공: {target_model} ({elapsed}초 소요)")
            return {
                "title": title,
                "author": author,
                "category": category,
                "content": content,
                "source": f"gemini_api ({target_model})",
                "message": f"Gemini AI ({target_model})로 {elapsed}초 만에 생성되었습니다.",
                "model": target_model
            }
        except urllib.error.HTTPError as e:
            elapsed = round(time.time() - t0, 2)
            if e.code == 429:
                print(f"[Gemini API] 할당량 초과 (429) → 재시도 중단, 폴백 사용")
                return None  # 즉시 중단 → 폴백으로
            print(f"[Gemini API] {target_model} 실패 ({elapsed}초, 시도 {attempt}): {e}")
        except Exception as e:
            elapsed = round(time.time() - t0, 2)
            if "429" in str(e):
                print(f"[Gemini API] 할당량 초과 (429) → 재시도 중단, 폴백 사용")
                return None  # 즉시 중단 → 폴백으로
            print(f"[Gemini API] {target_model} 실패 ({elapsed}초, 시도 {attempt}): {e}")

    return None

def trigger_background_prefetch(preferred_model=None):
    def worker():
        global _is_prefetching
        with _prefetch_lock:
            if _is_prefetching or _prefetch_queue.full():
                return
            _is_prefetching = True
        try:
            key = get_gemini_api_key()
            if key:
                item = _generate_live(key, preferred_category=None, preferred_model=preferred_model)
                if item and not is_content_duplicate(item["content"]):
                    _prefetch_queue.put_nowait(item)
                    print(f"[Prefetch] 백그라운드 프리페치 완료: 「{item['title']}」")
        except Exception as e:
            print(f"[Prefetch] 오류: {e}")
        finally:
            with _prefetch_lock:
                _is_prefetching = False

    t = threading.Thread(target=worker, daemon=True)
    t.start()

def generate_handwriting_text(api_key=None, preferred_category=None, preferred_model=None):
    if not api_key:
        api_key = get_gemini_api_key()

    existing_items = get_existing_titles_and_authors(limit=200)
    # DB 생성 이력도 합산하여 중복 체크
    title_history_items = get_title_history(limit=500)
    all_excluded_items = existing_items + title_history_items

    # 1. 특정 분야 지정이 없는 경우, 프리페치 큐(즉시 반환) 확인
    if not preferred_category or preferred_category == "":
        try:
            cached = _prefetch_queue.get_nowait()
            # 제목 + 콘텐츠 해시 모두 중복 체크
            if not _is_title_duplicate(cached.get("title", ""), all_excluded_items) \
               and not is_content_duplicate(cached["content"]):
                trigger_background_prefetch(preferred_model=preferred_model)
                cached["message"] = f"사전 준비된 Gemini AI ({cached.get('model', '')}) 문장으로 즉시 로드되었습니다."
                return cached
            else:
                save_title_history(cached.get("title", ""), cached.get("author", ""))
                print(f"[Prefetch] 프리페치 캐시 중복 감지 → 폐기 & DB 이력 저장: 「{cached.get('title', '')}」")
        except queue.Empty:
            pass

    # 2. 실시간 Gemini API 호출
    if api_key:
        live_item = _generate_live(api_key, preferred_category=preferred_category, preferred_model=preferred_model)
        if live_item:
            trigger_background_prefetch(preferred_model=preferred_model)
            return live_item

    # 3. 네트워크 장애 또는 API 실패 시 엄선 보관함 폴백
    candidates = [c for c in CURATED_FALLBACKS if not _is_title_duplicate(c['title'], all_excluded_items)]
    chosen = random.choice(candidates) if candidates else random.choice(CURATED_FALLBACKS)
    return {
        "title": chosen["title"],
        "author": chosen["author"],
        "category": chosen["category"],
        "content": chosen["content"],
        "source": "curated_fallback",
        "message": "Gemini API 연결 지연으로 엄선 보관함에서 제공되었습니다."
    }
