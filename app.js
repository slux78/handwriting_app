document.addEventListener('DOMContentLoaded', () => {
  const isFileProtocol = window.location.protocol === 'file:';

  // Elements
  const btnGenerate = document.getElementById('btn-generate');
  const categorySelect = document.getElementById('category-select');
  const modelSelect = document.getElementById('model-select');
  const loadingOverlay = document.getElementById('loading-overlay');
  const loadingTimer = document.getElementById('loading-timer');
  const statusBanner = document.getElementById('status-banner');
  const statusMessage = document.getElementById('status-message');
  const btnCloseBanner = document.getElementById('btn-close-banner');
  
  // Sheet Elements
  const displayCategory = document.getElementById('display-category');
  const displayDate = document.getElementById('display-date');
  const displayChars = document.getElementById('display-chars');
  const displayTitle = document.getElementById('display-title');
  const displayAuthor = document.getElementById('display-author');
  const displayContent = document.getElementById('display-content');

  // Sidebar Elements
  const datesList = document.getElementById('dates-list');
  const btnShowRecent = document.getElementById('btn-show-recent');

  // Tools & Practice
  const btnFontSmaller = document.getElementById('btn-font-smaller');
  const btnFontReset = document.getElementById('btn-font-reset');
  const btnFontLarger = document.getElementById('btn-font-larger');
  const btnTogglePractice = document.getElementById('btn-toggle-practice');
  const practicePanel = document.getElementById('practice-panel');
  const practiceInput = document.getElementById('practice-input');
  const practiceProgress = document.getElementById('practice-progress');
  const practiceCount = document.getElementById('practice-count');
  const btnCopy = document.getElementById('btn-copy');
  const btnPrint = document.getElementById('btn-print');

  // Modal Elements
  const btnOpenSettings = document.getElementById('btn-open-settings');
  const settingsModal = document.getElementById('settings-modal');
  const btnCloseModal = document.getElementById('btn-close-modal');
  const btnCancelSettings = document.getElementById('btn-cancel-settings');
  const btnSaveSettings = document.getElementById('btn-save-settings');
  const inputApiKey = document.getElementById('input-api-key');
  const modalDefaultModel = document.getElementById('modal-default-model');
  const keyStatusText = document.getElementById('key-status-text');
  const apiStatusDot = document.getElementById('api-status-dot');

  let currentRecord = null;
  let currentFontSize = 1.15; // rem
  let activeDateFilter = null;
  let timerInterval = null;

  // ==================== 오프라인 엄선 보관함 ====================
  const CURATED_FALLBACKS = [
    {
      title: "서시(序詩)",
      author: "윤동주",
      category: "시",
      content: "죽는 날까지 하늘을 우러러\n한 점 부끄럼이 없기를,\n잎새에 이는 바람에도\n나는 괴로워했다.\n별을 노래하는 마음으로\n모든 죽어가는 것을 사랑해야지\n그리고 나한테 주어진 길을\n걸어가야겠다.\n\n오늘 밤에도 별이 바람에 스치운다.\n\n계절이 지나가는 하늘에는\n가을로 가득 차 있습니다.\n나는 아무 걱정도 없이\n가을 속의 별들을 다 헤일 듯합니다.\n가슴 속에 하나 둘 새겨지는 별을\n이제 다 못 헤는 것은\n쉬이 아침이 오는 까닭이요,\n내일 밤이 남은 까닭이요,\n아직 나의 청춘이 다하지 않은 까닭입니다."
    },
    {
      title: "월든(Walden) - 숲속의 생활",
      author: "헨리 데이비드 소로",
      category: "에세이",
      content: "내가 숲속으로 들어간 것은 인생을 의도적으로 살아보기 위해서였다.\n다시 말해 인생의 본질적인 사실들만을 직면해보고,\n인생이 가르쳐주는 바를 내가 배울 수 있는지 알아보고 싶었으며,\n그리하여 마침내 죽음에 이르렀을 때 내가 헛된 삶을 살지 않았음을 깨닫고 싶었다.\n나는 삶이 아닌 삶을 살고 싶지 않았으니, 삶이란 참으로 소중한 것이다.\n또한 정말 불가피하지 않는 한 체념하는 삶을 살고 싶지도 않았다.\n나는 깊이 있게 살기를 바랐고, 인생의 모든 골수를 빼먹고 싶었으며,\n스파르타인처럼 강인하게 살아 삶이 아닌 것은 모두 박멸하고 싶었다.\n\n우리의 삶은 사소한 일들에 의해 흐트러지고 있다.\n정직한 사람은 대개 열 손가락만 있으면 충분하고, 극단적인 경우라도 발가락 열 개만 더하면\n자신의 모든 일을 셀 수 있을 것이다. 단순하게, 단순하게, 단순하게 살라!\n그대의 일을 백 가지나 천 가지로 늘리지 말고 두세 가지로 줄여라."
    },
    {
      title: "어린 왕자 - 길들임의 의미",
      author: "앙투안 드 생텍쥐페리",
      category: "소설",
      content: "\"안녕.\" 여우가 말했다.\n\"안녕.\" 어린 왕자가 정중하게 대답하고 돌아섰지만 아무것도 보이지 않았다.\n\"나 여기 있어. 사과나무 밑에.\" 그 목소리가 말했다.\n\"너는 누구니? 참 예쁘구나.\" 어린 왕자가 말했다.\n\"난 여우야.\" 여우가 말했다.\n\"이리 와서 나와 함께 놀자. 난 지금 너무 쓸쓸해.\" 어린 왕자가 제안했다.\n\"난 너와 놀 수 없어. 길들여지지 않았으니까.\" 여우가 말했다.\n\n\"'길들인다'는 게 무슨 뜻이야?\" 어린 왕자가 물었다.\n\"그건 너무 잊혀진 일이지. 관계를 맺는다는 뜻이야.\" 여우가 말했다.\n\"관계를 맺는다고?\"\n\"그래. 넌 나에게 아직은 수많은 다른 소년들과 다를 바 없는 한 아이에 지나지 않아.\n그래서 난 네가 필요하지 않아. 너 역시 내가 필요하지 않고.\n하지만 네가 나를 길들인다면, 우리는 서로에게 이 세상에서 유일한 존재가 될 거야.\n밀밭이 황금빛으로 물들 때마다 난 너를 기억하게 될 거야.\""
    },
    {
      title: "침묵의 봄 - 사색의 길",
      author: "레이첼 카슨",
      category: "에세이",
      content: "자연의 아름다움에 대해 깊이 사색하는 사람은 삶이 다하는 날까지\n생명력을 잃지 않는 힘의 원천을 발견하게 된다.\n계절의 순환 속에는 끝없는 위로와 치유가 깃들어 있으며,\n겨울의 혹독한 추위 뒤에는 어김없이 봄이 찾아오리라는 변치 않는 약속이 있다.\n\n지구의 역사를 통틀어 볼 때, 생명체와 그 주변 환경의 관계는 서로 끊임없이 영향을 주고받는 상호작용의 과정이었다.\n인간이 자연을 정복하겠다는 오만한 생각을 버리고, 자연의 섭리와 조화를 이루며\n겸허한 태도로 살아갈 때 비로소 진정한 평화와 지속 가능한 미래를 만날 수 있다.\n숲길을 홀로 걷거나 고요한 바다를 바라보는 순간,\n우리는 우리 자신이 거대한 생명의 그물망 속 한 올의 실에 불과함을 깨닫는다."
    },
    {
      title: "그리스인 조르바 - 자유와 영혼",
      author: "니코스 카잔차키스",
      category: "소설",
      content: "나는 아무것도 바라지 않는다. 나는 아무것도 두려워하지 않는다. 나는 자유다.\n인간이 자기 자신을 구원할 수 있는 길은 오직 하나뿐이다.\n그것은 끊임없이 투쟁하고, 의심하고, 스스로를 넘어서며 전진하는 것이다.\n\n조르바는 나에게 삶을 사랑하고 죽음을 두려워하지 않는 법을 가르쳐 주었다.\n그는 먹을 때는 먹는 일에 온 영혼을 쏟았고, 사랑할 때는 온몸으로 사랑했으며,\n일할 때는 대지 깊숙이 뿌리를 박은 거목처럼 일했다.\n책 속의 활자로는 결코 설명할 수 없는 날것의 생명력, 그것이 바로 조르바의 위대함이었다.\n\"선생님, 산다는 게 도대체 무엇입니까? 두 손으로 흙을 쥐고 그 냄새를 깊이 들이마셔 보세요.\n바다의 푸른 물결에 몸을 던져 헤엄쳐 보세요. 그 속에 모든 대답이 들어 있습니다.\""
    },
    {
      title: "데미안 - 나를 찾아가는 길",
      author: "헤르만 헤세",
      category: "소설",
      content: "내 속에서 솟아 나오려는 것, 바로 그것을 나는 살아보려 했다.\n왜 그것이 그토록 어려웠을까?\n한 사람 한 사람의 삶은 자기 자신에게로 이르는 길이다.\n일찍이 그 어떤 사람도 완전히 자기 자신이 되어본 적은 없었다.\n그럼에도 누구나 자기 자신이 되려고 애쓴다.\n새는 알에서 나오려고 투쟁한다.\n알은 세계이다. 태어나려는 자는 하나의 세계를 깨뜨려야 한다.\n새는 신에게로 날아간다. 그 신의 이름은 아프락사스다."
    },
    {
      title: "명상록 - 내면의 고요",
      author: "마르쿠스 아우렐리우스",
      category: "위대한 사상가의 명언 및 철학 수필",
      content: "인간의 영혼은 외부의 사건에 의해 상처받지 않는다.\n오직 그 사건을 바라보는 자신의 생각과 판단에 의해서만 흔들릴 뿐이다.\n언제든 그대의 내면으로 물러서라. 인간이 찾아갈 수 있는 그 어떤 휴양지보다\n더 조용하고 번잡하지 않은 곳은 바로 자신의 영혼 속이다.\n그곳으로 들어가 잠시 머물며 마음을 가라앉히고 다시 삶의 의무로 돌아오라."
    },
    {
      title: "무소유의 역설",
      author: "법정",
      category: "에세이",
      content: "우리는 필요에 의해서 물건을 갖게 되지만,\n때로는 그 물건 때문에 적잖게 마음이 쓰이게 된다.\n무엇인가를 갖는다는 것은 다른 한편 무엇인가에 얽매이는 일이다.\n크게 버리는 사람만이 크게 얻을 수 있다.\n아무것도 갖지 않을 때 비로소 온 세상을 갖게 된다는 것은 무소유의 역설적인 진리이다."
    },
    {
      title: "창백한 푸른 점",
      author: "칼 세이건",
      category: "에세이",
      content: "저 점을 다시 보라. 저것이 여기다. 저것이 우리의 고향이며, 저것이 우리다.\n우리가 사랑하는 모든 이들, 우리가 알고 있는 모든 이들, 역사 속에 존재했던 모든 인류가\n햇빛 속에 떠도는 먼지 한 톨 위에서 살다 갔다.\n우주라는 거대한 암흑의 무대 속에서 우리의 지구는 너무나 외로운 얼룩 하나에 불과하다.\n우리가 아는 유일한 보금자리인 이 창백한 푸른 점을 소중히 보존해야 할 책임이 우리 모두에게 있다."
    },
    {
      title: "향수(鄕愁)",
      author: "정지용",
      category: "시",
      content: "넓은 벌 동쪽 끝으로\n옛이야기 지줄대는 실개천이 휘돌아 나가고,\n얼룩백이 황소가\n해설피 금빛 게으른 울음을 우는 곳,\n— 그곳이 차마 꿈엔들 잊힐 리야.\n\n질화로에 재가 식어지면\n비인 밭에 밤바람 소리 말을 달리고,\n엷은 졸음에 겨운 늙으신 아버지가\n짚베개를 돋아 고이시는 곳,\n— 그곳이 차마 꿈엔들 잊힐 리야."
    }
  ];

  // ==================== 데이터 어댑터 (브라우저 직접 초고속 호출 + 서버 DB 하이브리드) ====================
  const dataAdapter = {
    _rawApiKey: '',

    async getSettings() {
      if (isFileProtocol) {
        const key = localStorage.getItem('gemini_api_key') || '';
        const model = localStorage.getItem('gemini_model') || 'gemini-3.8-flash';
        this._rawApiKey = key;
        const isSet = key.length > 5;
        return {
          has_api_key: isSet,
          masked_key: isSet ? key.substring(0, 6) + '...' + key.substring(key.length - 4) : '',
          preferred_model: model
        };
      } else {
        const res = await fetch('/api/settings');
        const data = await res.json();
        if (data.api_key) this._rawApiKey = data.api_key;
        return data;
      }
    },

    async saveSettings(apiKey, model) {
      if (apiKey) {
        this._rawApiKey = apiKey.trim();
        localStorage.setItem('gemini_api_key', this._rawApiKey);
      }
      if (model) {
        localStorage.setItem('gemini_model', model);
      }

      if (isFileProtocol) {
        return { success: true };
      } else {
        const res = await fetch('/api/settings', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ api_key: apiKey ? apiKey.trim() : '', model: model || '' })
        });
        return await res.json();
      }
    },

    async getDates() {
      if (isFileProtocol) {
        const records = this._getLocalRecords();
        const dateMap = {};
        records.forEach(r => {
          dateMap[r.date] = (dateMap[r.date] || 0) + 1;
        });
        const dates = Object.keys(dateMap).sort().reverse().map(d => ({
          date: d,
          count: dateMap[d]
        }));
        return { dates };
      } else {
        const res = await fetch('/api/dates');
        return await res.json();
      }
    },

    async getRecords(dateStr) {
      if (isFileProtocol) {
        const records = this._getLocalRecords();
        const filtered = dateStr ? records.filter(r => r.date === dateStr) : records.slice(-30).reverse();
        return { records: filtered };
      } else {
        const url = dateStr ? `/api/records?date=${encodeURIComponent(dateStr)}` : '/api/records';
        const res = await fetch(url);
        return await res.json();
      }
    },

    async getRecordById(id) {
      if (isFileProtocol) {
        const records = this._getLocalRecords();
        const found = records.find(r => r.id === parseInt(id));
        return { record: found };
      } else {
        const res = await fetch(`/api/records/${id}`);
        return await res.json();
      }
    },

    // 생성: 서버 모드에서는 서버 API만, file:// 모드에서만 브라우저 직접 호출
    async generate(preferredCategory, preferredModel) {
      const apiKey = this._rawApiKey || localStorage.getItem('gemini_api_key');
      const targetModel = preferredModel || localStorage.getItem('gemini_model') || 'gemini-3.8-flash';
      const today = new Date().toISOString().slice(0, 10);
      const nowStr = new Date().toLocaleString();

      // 서버 모드: 서버 /api/generate 단일 호출 (서버 측 curl --ipv4로 최적화)
      if (!isFileProtocol) {
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 15000);
          const res = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ category: preferredCategory, model: targetModel }),
            signal: controller.signal
          });
          clearTimeout(timeoutId);
          return await res.json();
        } catch (e) {
          console.warn('[서버 API 호출 실패]:', e);
          // 서버 timeout/에러 시 엄선 보관함으로 폴백
          return await this._generateFallback(preferredCategory);
        }
      }

      // file:// 모드: 브라우저에서 직접 Gemini API 호출
      if (apiKey) {
        try {
          const directData = await this._fetchGeminiDirect(apiKey, preferredCategory, targetModel);
          if (directData && directData.content) {
            directData.date = today;
            directData.created_at = nowStr;
            const records = this._getLocalRecords();
            records.push(directData);
            localStorage.setItem('handwriting_records', JSON.stringify(records));
            return { record: directData };
          }
        } catch (e) {
          console.warn('[브라우저 직접 호출 실패]:', e);
        }
      }

      // 폴백: 엄선 보관함
      return await this._generateFallback(preferredCategory);
    },

    async _fetchGeminiDirect(apiKey, preferredCategory, targetModel) {
      const categories = ["시", "소설", "에세이", "여행기", "위대한 사상가의 명언 및 철학 수필"];
      const cat = preferredCategory || categories[Math.floor(Math.random() * categories.length)];

      const prompt = `당신은 마음을 정돈하는 필사(손글씨 연습) 전문가입니다.
1. 분야: ${cat}
2. 분량: A4 1장 손글씨용 분량 (공백 포함 약 750자~950자 내외). 문단을 명확히 나눌 것.
3. 톤: 장난기 없는 진중하고 격조 높은 한국어 문체.

반드시 순수 JSON만 응답:
{
  "title": "작품 제목",
  "author": "작가/인물명",
  "category": "${cat}",
  "content": "본문 텍스트"
}`;

      const url = `https://generativelanguage.googleapis.com/v1beta/models/${targetModel}:generateContent?key=${apiKey}`;
      
      // 10초 timeout으로 무한 대기 방지
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);

      try {
        // 먼저 thinkingConfig 포함하여 시도
        const resp = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          signal: controller.signal,
          body: JSON.stringify({
            contents: [{ parts: [{ text: prompt }] }],
            generationConfig: {
              responseMimeType: "application/json",
              temperature: 0.7,
              topP: 0.9,
              maxOutputTokens: 2048,
              thinkingConfig: { thinkingBudget: 0 }
            }
          })
        });
        clearTimeout(timeoutId);

        let jsonResp;
        if (!resp.ok) {
          // thinkingConfig 미지원 시 thinking 없이 재시도 (새 timeout)
          const controller2 = new AbortController();
          const timeoutId2 = setTimeout(() => controller2.abort(), 10000);
          const resp2 = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            signal: controller2.signal,
            body: JSON.stringify({
              contents: [{ parts: [{ text: prompt }] }],
              generationConfig: {
                responseMimeType: "application/json",
                temperature: 0.7,
                maxOutputTokens: 2048
              }
            })
          });
          clearTimeout(timeoutId2);
          if (!resp2.ok) return null;
          jsonResp = await resp2.json();
        } else {
          jsonResp = await resp.json();
        }

        const rawText = jsonResp.candidates[0].content.parts[0].text;
        const clean = rawText.replace(/```json/g, '').replace(/```/g, '').trim();
        const parsed = JSON.parse(clean);

        return {
          id: Date.now(),
          title: parsed.title || '무제',
          author: parsed.author || '작자 미상',
          category: parsed.category || cat,
          content: parsed.content || '',
          char_count: (parsed.content || '').length,
          meta_message: `Gemini AI (${targetModel})로 생성되었습니다.`,
          source: 'gemini_api'
        };
      } catch (err) {
        clearTimeout(timeoutId);
        throw err;
      }
    },

    _generateFallback(preferredCategory) {
      const records = this._getLocalRecords();
      const existingTitles = records.map(r => r.title);
      const today = new Date().toISOString().slice(0, 10);
      const nowStr = new Date().toLocaleString();

      let candidates = CURATED_FALLBACKS.filter(c => !existingTitles.includes(c.title));
      let chosen = candidates.length > 0 ? candidates[Math.floor(Math.random() * candidates.length)] : CURATED_FALLBACKS[Math.floor(Math.random() * CURATED_FALLBACKS.length)];
      const newRecord = {
        id: Date.now(),
        title: chosen.title + (candidates.length === 0 ? ' (새로 필사)' : ''),
        author: chosen.author,
        category: chosen.category,
        content: chosen.content,
        char_count: chosen.content.length,
        date: today,
        created_at: nowStr,
        meta_message: '보관함에서 즉시 로드되었습니다.',
        source: 'curated_fallback'
      };
      records.push(newRecord);
      localStorage.setItem('handwriting_records', JSON.stringify(records));
      return { record: newRecord };
    },

    _getLocalRecords() {
      try {
        const raw = localStorage.getItem('handwriting_records');
        if (!raw) {
          const first = {
            id: 1,
            title: CURATED_FALLBACKS[0].title,
            author: CURATED_FALLBACKS[0].author,
            category: CURATED_FALLBACKS[0].category,
            content: CURATED_FALLBACKS[0].content,
            char_count: CURATED_FALLBACKS[0].content.length,
            date: new Date().toISOString().slice(0, 10),
            created_at: new Date().toLocaleString()
          };
          localStorage.setItem('handwriting_records', JSON.stringify([first]));
          return [first];
        }
        return JSON.parse(raw);
      } catch (e) {
        return [];
      }
    }
  };

  // ==================== 초기 로딩 ====================
  init();

  async function init() {
    await checkApiSettings();
    await loadDates();
    await loadRecentRecords(true);
  }

  // ==================== API Key & 모델 설정 확인 ====================
  async function checkApiSettings() {
    try {
      const data = await dataAdapter.getSettings();
      if (data.has_api_key) {
        apiStatusDot.classList.add('connected');
        apiStatusDot.title = 'Gemini API 연동됨';
        keyStatusText.textContent = `현재 등록된 키: ${data.masked_key}`;
        keyStatusText.style.color = '#27ae60';
      } else {
        apiStatusDot.classList.remove('connected');
        apiStatusDot.title = 'Gemini API 미연동 (보관함 모드)';
        keyStatusText.textContent = '등록된 API 키가 없습니다.';
        keyStatusText.style.color = '#888';
      }
      if (data.preferred_model) {
        modelSelect.value = data.preferred_model;
        modalDefaultModel.value = data.preferred_model;
      }
    } catch (e) {
      console.error('설정 로드 실패', e);
    }
  }

  // ==================== 날짜 목록 로드 ====================
  async function loadDates() {
    try {
      const data = await dataAdapter.getDates();
      renderDates(data.dates || []);
    } catch (e) {
      datesList.innerHTML = '<div class="empty-state">날짜 목록을 불러오지 못했습니다.</div>';
    }
  }

  function renderDates(dates) {
    if (!dates || dates.length === 0) {
      datesList.innerHTML = '<div class="empty-state">생성된 필사 기록이 없습니다. 상단에서 새로 생성해보세요.</div>';
      return;
    }

    datesList.innerHTML = '';
    dates.forEach(d => {
      const groupEl = document.createElement('div');
      groupEl.className = `date-group ${activeDateFilter === d.date ? 'active' : ''}`;
      groupEl.innerHTML = `
        <div class="date-header" data-date="${d.date}">
          <span>📅 ${d.date}</span>
          <span class="date-badge">${d.count}편</span>
        </div>
        <div class="date-records-list hidden" id="records-for-${d.date}">
          <div class="loading-sub">목록 불러오는 중...</div>
        </div>
      `;

      const header = groupEl.querySelector('.date-header');
      header.addEventListener('click', () => toggleDateGroup(d.date, groupEl));
      datesList.appendChild(groupEl);
    });
  }

  async function toggleDateGroup(dateStr, groupEl) {
    const listEl = groupEl.querySelector(`#records-for-${dateStr}`);
    const isHidden = listEl.classList.contains('hidden');

    document.querySelectorAll('.date-group').forEach(el => {
      if (el !== groupEl) {
        el.classList.remove('active');
        const otherList = el.querySelector('.date-records-list');
        if (otherList) otherList.classList.add('hidden');
      }
    });

    if (isHidden) {
      groupEl.classList.add('active');
      listEl.classList.remove('hidden');
      activeDateFilter = dateStr;
      btnShowRecent.classList.remove('active');

      try {
        const data = await dataAdapter.getRecords(dateStr);
        renderRecordsList(listEl, data.records || []);
      } catch (e) {
        listEl.innerHTML = '<div class="empty-state">기록 조회 오류</div>';
      }
    } else {
      groupEl.classList.remove('active');
      listEl.classList.add('hidden');
      activeDateFilter = null;
    }
  }

  function renderRecordsList(container, records) {
    if (!records || records.length === 0) {
      container.innerHTML = '<div class="empty-state">기록이 없습니다.</div>';
      return;
    }
    container.innerHTML = '';
    records.forEach(r => {
      const itemEl = document.createElement('div');
      itemEl.className = `record-item ${currentRecord && currentRecord.id === r.id ? 'selected' : ''}`;
      itemEl.innerHTML = `
        <div class="record-item-title">${escapeHtml(r.title)}</div>
        <div class="record-item-meta">
          <span>${escapeHtml(r.author || '미상')}</span>
          <span>•</span>
          <span>${r.category || '기타'}</span>
        </div>
      `;
      itemEl.addEventListener('click', () => {
        document.querySelectorAll('.record-item').forEach(i => i.classList.remove('selected'));
        itemEl.classList.add('selected');
        loadRecordDetail(r.id);
      });
      container.appendChild(itemEl);
    });
  }

  // ==================== 최근 목록 로드 ====================
  async function loadRecentRecords(autoSelectFirst = false) {
    try {
      const data = await dataAdapter.getRecords(null);
      const records = data.records || [];
      if (records.length > 0 && autoSelectFirst) {
        loadRecordDetail(records[0].id);
      }
    } catch (e) {
      console.error('최근 기록 로드 오류', e);
    }
  }

  btnShowRecent.addEventListener('click', async () => {
    btnShowRecent.classList.add('active');
    activeDateFilter = null;
    document.querySelectorAll('.date-group').forEach(el => {
      el.classList.remove('active');
      const list = el.querySelector('.date-records-list');
      if (list) list.classList.add('hidden');
    });
    await loadRecentRecords(false);
  });

  // ==================== 단일 기록 상세 조회 ====================
  async function loadRecordDetail(id) {
    try {
      const data = await dataAdapter.getRecordById(id);
      if (data.record) {
        renderSheet(data.record);
      }
    } catch (e) {
      showBanner('기록을 불러오지 못했습니다.', 'error');
    }
  }

  function renderSheet(record) {
    currentRecord = record;
    displayTitle.textContent = record.title;
    displayAuthor.textContent = record.author || '작자 미상';
    displayCategory.textContent = record.category || '필사';
    displayDate.textContent = record.date;
    displayChars.textContent = `${record.char_count || record.content.length}자 (A4 1장)`;
    displayContent.textContent = record.content;

    practiceInput.value = '';
    updatePracticeStats();
  }

  // ==================== 새 글 생성 (경과 시간 타이머 포함) ====================
  btnGenerate.addEventListener('click', async () => {
    const category = categorySelect.value;
    const model = modelSelect.value;
    
    // 타이머 시작
    let startTime = Date.now();
    loadingTimer.textContent = '0.0';
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => {
      let elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
      loadingTimer.textContent = elapsed;
    }, 100);

    loadingOverlay.classList.remove('hidden');

    try {
      const data = await dataAdapter.generate(category, model);
      clearInterval(timerInterval);
      loadingOverlay.classList.add('hidden');

      if (data.record) {
        renderSheet(data.record);
        await loadDates();
        let totalTime = ((Date.now() - startTime) / 1000).toFixed(1);
        showBanner(`새로운 필사 글 「${data.record.title}」이(가) ${totalTime}초 만에 보관되었습니다. (${data.record.meta_message || ''})`, 'success');
      } else {
        showBanner(data.error || '필사 글 생성 중 일시적인 문제가 발생했습니다.', 'error');
      }
    } catch (e) {
      clearInterval(timerInterval);
      loadingOverlay.classList.add('hidden');
      showBanner('통신 중 문제가 발생했습니다.', 'error');
    }
  });

  // ==================== 글자 크기 조절 ====================
  btnFontSmaller.addEventListener('click', () => {
    if (currentFontSize > 0.9) {
      currentFontSize -= 0.1;
      applyFontSize();
    }
  });

  btnFontReset.addEventListener('click', () => {
    currentFontSize = 1.15;
    applyFontSize();
  });

  btnFontLarger.addEventListener('click', () => {
    if (currentFontSize < 1.6) {
      currentFontSize += 0.1;
      applyFontSize();
    }
  });

  function applyFontSize() {
    displayContent.style.fontSize = `${currentFontSize}rem`;
  }

  // ==================== 필사 연습 모드 ====================
  btnTogglePractice.addEventListener('click', () => {
    practicePanel.classList.toggle('hidden');
    if (!practicePanel.classList.contains('hidden')) {
      practiceInput.focus();
    }
  });

  practiceInput.addEventListener('input', updatePracticeStats);

  function updatePracticeStats() {
    if (!currentRecord) return;
    const typed = practiceInput.value;
    const target = currentRecord.content;
    practiceCount.textContent = typed.length;

    let progress = Math.min(100, Math.round((typed.length / target.length) * 100));
    practiceProgress.textContent = `${progress}%`;
  }

  // ==================== 복사 & 인쇄 ====================
  btnCopy.addEventListener('click', () => {
    if (!currentRecord) return;
    const fullText = `[${currentRecord.title}] - ${currentRecord.author}\n\n${currentRecord.content}`;
    navigator.clipboard.writeText(fullText).then(() => {
      showBanner('필사 내용이 클립보드에 복사되었습니다.', 'success');
    }).catch(() => {
      showBanner('복사 권한을 확인해주세요.', 'error');
    });
  });

  btnPrint.addEventListener('click', () => {
    window.print();
  });

  // ==================== 설정 모달 ====================
  btnOpenSettings.addEventListener('click', () => {
    settingsModal.classList.remove('hidden');
  });

  btnCloseModal.addEventListener('click', () => settingsModal.classList.add('hidden'));
  btnCancelSettings.addEventListener('click', () => settingsModal.classList.add('hidden'));

  btnSaveSettings.addEventListener('click', async () => {
    const key = inputApiKey.value.trim();
    const model = modalDefaultModel.value;

    try {
      const data = await dataAdapter.saveSettings(key, model);
      if (data.success) {
        settingsModal.classList.add('hidden');
        inputApiKey.value = '';
        modelSelect.value = model;
        await checkApiSettings();
        showBanner('Gemini API 설정이 성공적으로 저장되었습니다!', 'success');
      } else {
        alert(data.error || '저장 실패');
      }
    } catch (e) {
      alert('설정 저장 중 오류가 발생했습니다.');
    }
  });

  // ==================== 배너 알림 ====================
  function showBanner(msg, type = 'info') {
    statusMessage.textContent = msg;
    statusBanner.className = `status-banner ${type}`;
    statusBanner.classList.remove('hidden');

    setTimeout(() => {
      statusBanner.classList.add('hidden');
    }, 6000);
  }

  btnCloseBanner.addEventListener('click', () => {
    statusBanner.classList.add('hidden');
  });

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>'\"]/g, tag => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    }[tag] || tag));
  }
});
