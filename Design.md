# Designer Color Studio - 1순위 4페이지 개발 계획서

## 1. 프로젝트 개요
- **프로젝트명**: Designer Color Studio (Streamlit 기반 디자이너 색상 도구)
- **목표**: 디자이너가 매일 쓰는 색상 의사결정을 4클릭 안에 끝내는 올인원 도구
- **1순위 조합 선정 기준**: Figma / Coolors / Adobe Color 사용 빈도 분석
  1. 단일 색상 탐색/변환 - 모든 작업의 시작점
  2. 하모니 팔레트 생성 - 브랜드, UI 시스템 핵심
  3. 그라데이션 생성 - 배경, 버튼, 히어로 섹션
  4. 접근성+추출+Export - 실무 배포 직전 필수 검증

## 2. 4페이지 IA (Information Architecture)

### PAGE 1: 컬러 랩 (Color Lab) - 🎯
**역할**: 기준색 정의

**기능**:
- color_picker + HEX 직접 입력 (3자리/6자리 모두 허용)
- 실시간 변환: HEX / RGB / HSL / HSV / CMYK 근사
- Luminance(상대 휘도) 계산으로 텍스트 색상 추천 (black/white)
- 1-click 복사 버튼
- 최근 사용 색상 8개 히스토리 (session_state)

**핵심 로직**:
- `utils.hex_to_rgb(hex)`
- `utils.rgb_to_hsl(rgb)`
- `utils.luminance(rgb)`

**UI**: 왼쪽 40% 스와치 대형 프리뷰(200px), 오른쪽 60% 값 테이블 + metric

---

### PAGE 2: 팔레트 스튜디오 (Palette Studio) - 🌈 [CORE]
**역할**: 시스템 컬러 생성 - 가장 중요한 페이지

**기능**:
- Base color 1개 → 6가지 하모니 생성
  - Complementary (180°)
  - Analogous (±30°)
  - Split Complementary (150°, 210°)
  - Triadic (120° 간격)
  - Tetradic (90° 간격)
  - Monochromatic (Lightness 20~80% 5단계)
- 잠금(Lock) 기능: 특정 색 고정 후 나머지 Shuffle (향후 확장)
- 개수 슬라이더 (3~8), 채도/명도 미세조정
- 팔레트 저장 → Page 4 Export 센터로 전달

**기술**: Python `colorsys` HLS 기반 변환, 향후 `colormath`로 LAB 보정 가능

**성과지표**: 3초 안에 5색 팔레트 생성 및 저장

---

### PAGE 3: 그라데이션 스튜디오 (Gradient Studio) - 🌅
**역할**: 배경/CTA 제작

**기능**:
- Type: linear / radial / conic (1순위는 linear 집중)
- Color stop 2~5개 지원 (중간색 추가 체크박스)
- Angle 0~360° 슬라이더, Position 편집
- 실시간 프리뷰 (div background: linear-gradient)
- CSS, Tailwind, Figma용 코드 Export
- Random Gradient 추천 버튼 (셔플)

**기술**: CSS 문자열 조합 `linear-gradient({angle}deg, {c1}, {c_mid}, {c2})`

**Export 예시**:
```css
background: linear-gradient(90deg, #7C3AED, #EC4899);
```
```html
<div className="bg-[linear-gradient(90deg,#7C3AED,#EC4899)]"></div>
```

---

### PAGE 4: 추출 & 접근성 센터 (Extract & A11y Hub) - ♿
**역할**: 배포 전 검증 + 에셋화

**기능 1 - 이미지 추출**:
- 업로드 (jpg/png/webp) → resize 150x150 → KMeans(k=추출수) → 주요 색상 반환
- 브랜드 무드보드에서 바로 팔레트화
- 함수: `utils.extract_colors_from_image(image, n_colors=5)`

**기능 2 - 대비 검사**:
- Foreground / Background color_picker
- WCAG 2.1 contrast_ratio 계산 `(L1+0.05)/(L2+0.05)`
- AA(4.5:1 일반 텍스트, 3:1 대형 텍스트), AAA(7:1, 4.5:1) 뱃지 표시
- 실제 텍스트 프리뷰 박스

**기능 3 - Export 센터**:
- CSS Variables `:root { --color-1: #... }`
- Tailwind config object
- JSON / TXT / SVG palette strip 다운로드
- 전체 저장 팔레트 관리 (삭제)

---

## 3. 기술 스택 & 파일 구조

**Tech Stack**:
- streamlit>=1.35.0 (st.navigation 4페이지 라우팅)
- Pillow>=10.0.0 (이미지 처리)
- numpy>=1.26.0 + scikit-learn>=1.4.0 (KMeans 색상 추출)

**File Structure**:
```
designer_tools/
├── app.py            # st.navigation 4페이지 라우팅 (메인)
├── app_4pages.py     # 4페이지 버전 백업
├── utils.py          # 색상 변환/하모니/대비/추출 핵심 로직
├── requirements.txt  # 의존성
├── PLAN.md           # 상세 계획서
└── design.md         # 본 문서 (다운로드용)
```

## 4. 개발 단계 (WBS) - 총 6시간 예상

| Phase | 시간 | 내용 | 산출물 |
|-------|------|------|--------|
| Phase 0 | 30분 | 폴더 생성, venv, utils.py 10개 함수 단위 테스트 | utils.py |
| Phase 1 | 1시간 | PAGE 1 Color Lab - picker + 변환 테이블 + 복사 UX | Page 1 완성 |
| Phase 2 | 1.5시간 | PAGE 2 Palette Studio - 하모니 알고리즘 + 잠금/셔플 + 저장 | Core 완성 |
| Phase 3 | 1시간 | PAGE 3 Gradient - 프리뷰 div + angle slider + 코드 Export | Page 3 완성 |
| Phase 4 | 1.5시간 | PAGE 4 Extract & A11y - 업로드+KMeans, contrast_ratio, Export 통합 | Page 4 완성 |
| Phase 5 | 30분 | 스타일링 (Space Grotesk, 카드 hover), README, 배포 테스트 | 최종 배포 |

## 5. UX 원칙
1. 모든 HEX는 대문자 표시, 클릭 시 복사 (추후 pyperclip)
2. 스와치는 110px 카드, hover 시 translateY(-3px)로 살짝 떠오름
3. 텍스트 색상은 luminance >0.5면 검정, 아니면 흰색으로 자동 대비
4. 저장된 팔레트는 session_state에 유지, 새로고침 전까지 보존 (추후 localStorage 고려)
5. 모든 Export 코드는 `st.code`로 즉시 복사 가능

## 6. 실행 방법
```bash
cd designer_tools
pip install -r requirements.txt
streamlit run app.py
```

## 7. 확장 로드맵 (1순위 이후)
- [ ] Color Blind Simulator (Deuteranopia, Protanopia, Tritanopia)
- [ ] Coolors.co 스타일 스페이스바로 랜덤 팔레트
- [ ] Figma Plugin 연동용 API / JSON Export
- [ ] ASE (Adobe Swatch Exchange) Export
- [ ] 컬러 네이밍 (e.g., #7C3AED → Amethyst)

---
© 2026 Designer Color Studio • 1순위 4페이지 계획서
