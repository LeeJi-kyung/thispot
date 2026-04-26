# THISPOT

산책을 캐릭터 친구와 함께하는 iOS 앱. SwiftUI 기반, 영어 UI.

---

## 컨셉

- **한 줄**: "오늘도 같이 걸을까?" — 내가 고른 캐릭터(POT 친구)와 함께 산책을 기록하는 가벼운 앱
- **톤**: cream + sage green + warm brown. 부드럽고 둥근 형태, soft shadow, spring 애니메이션
- **언어**: UI는 모두 영어. 대화/주석은 자유

---

## Navigation Flow

`THISPOTApp` 안에 `NavigationStack` 한 개. 각 화면은 `@State` flag + `.navigationDestination(isPresented:)` 패턴으로 push.

```
SplashView (2초, 자동 진행)
    ↓
SignUpView (nickname 입력 → Next)
    ↓
CharacterSelectView(nickname:) (4개 중 선택 → Done)
    ↓
MainView(nickname:, characterAsset:) ← 현재 endpoint
    ├─ Previous   (TODO: 기록물 화면)
    └─ Let's Walk (TODO: 산책 세션 화면)
```

값은 화면 간 **파라미터로 직접 전달**. 별도 글로벌 state 없음 (MVP). 화면이 더 늘어나거나 산책 데이터가 공유되어야 하면 그때 `AppState: ObservableObject` 도입.

---

## Design System

> 현재는 각 View 안에 색상을 inline으로 두고 있음. 화면이 안정되면 `Theme/` 로 이동 예정.

### 컬러 (RGB 0~1)

| 이름 | 값 | 용도 |
|---|---|---|
| `backgroundCream` | `(0.973, 0.965, 0.953)` | 모든 화면 배경 |
| `brandGreen` | `(0.502, 0.651, 0.388)` | Primary CTA, 선택 강조, 포커스 테두리 |
| `brandBrown` | `(0.600, 0.420, 0.220)` | Secondary 텍스트, 아이콘, back 버튼 |
| `textDark` | `(0.20, 0.20, 0.20)` | 본문/타이틀 텍스트 |
| `placeholderGray` | `(0.70, 0.70, 0.70)` | Disabled, placeholder, 비선택 테두리 |

> Asset Catalog에 이미 `SteamCream`, `CalmSage`, `PotTerracotta`, `MutedWarmGray`, `EmberGlow`, `TextPrimary/Secondary` 등 컬러셋이 있음. Theme 정리 시 매핑 가능.

### 타이포그래피

System font 사용 (Pretendard 폰트는 Info.plist에 등록되어 있으나 아직 미사용).

| Role | Size / Weight |
|---|---|
| Page title | 28 / bold |
| Subtitle | 14~15 / regular |
| Body | 16 / regular |
| Label / chip | 13 / semibold |
| Button | 16~19 / semibold~bold |
| Tiny caption | 10~11 / semibold |

### 컴포넌트 패턴

- **Primary 버튼**: `120×48`, `cornerRadius 24`, brandGreen fill, white text. 활성화 시 `brandGreen.opacity(0.35)` glow shadow. Disabled 시 placeholderGray fill, 그림자 0.
- **Round CTA** (Let's Walk): `124×124` 원형, brandGreen fill, 강한 shadow `radius 14`.
- **Custom back 버튼**: `40pt` 원, white 70% fill, brandBrown chevron, 옅은 brandBrown stroke. 모든 push된 화면에서 `.navigationBarBackButtonHidden(true)` + 좌상단에 직접 배치.
- **Slot card**: `cornerRadius 16`, white 70% fill. 선택 시 brandGreen 2.5pt stroke + green glow shadow.
- **Capsule chip** (location 등): white 75% fill, 옅은 brandBrown stroke.
- **카드 일반**: `cornerRadius 12~20`, white 70% fill.

### 모션

- 선택/포커스 변경: `.animation(.easeInOut(duration: 0.2))`
- 스케일 등장: `.spring(response: 0.4~0.6, dampingFraction: 0.6~0.75)`
- 화면 등장 (splash 로고 등): scale 0.6 → 1.0 + opacity 0 → 1, spring

---

## Assets

- `logo` — 스플래시 로고
- `POT` — POT 마스코트 (현재 미사용)
- `background` — 메인 화면 배경 (blur 8 + cream 55% overlay 적용해서 흐리게 사용)
- `location` — 위치 chip 아이콘
- `charactor1` ~ `charactor4` — 선택 가능한 캐릭터. **이름이 `character`가 아니라 `charactor` 오타 상태**. 정리할 때 같이 고치기

> 새 PNG 추가 규칙: lowercase, snake/단일단어 선호. 추가 후 Xcode Assets에서 image set 생성하고 그대로 `Image("...")`로 호출.

---

## 폴더 구조

```
THISPOT/
├── THISPOTApp.swift        # @main, NavigationStack root
├── SplashView.swift
├── ContentView.swift       # Xcode 기본, 사용 안 함 — 나중에 제거 가능
├── Info.plist              # NSLocationWhenInUseUsageDescription 포함
├── Models/
│   └── LocationManager.swift
├── ViewModels/             # (비어있음)
├── Views/
│   ├── SignUpView.swift
│   ├── CharacterSelectView.swift
│   └── MainView.swift
├── Theme/                  # (비어있음 — color/font 추출 예정)
└── Assets.xcassets/
```

> Finder에서 새 파일/폴더를 만들면 Xcode가 자동으로 인식하지 않음. 새 `.swift`는 항상 Xcode navigator에서 우클릭 → **Add Files to "THISPOT"** 으로 target에 추가해야 빌드됨.

---

## 코딩 패턴

- **상태 전달**: 다음 화면에 필요한 값은 생성자 파라미터로 그대로 넘긴다 (`CharacterSelectView(nickname:)`, `MainView(nickname:, characterAsset:)`).
- **네비게이션 push**: `@State var goToX: Bool` + 버튼 action에서 `goToX = true` + `.navigationDestination(isPresented: $goToX) { NextView(...) }`.
- **권한이 필요한 기능**: `Models/`에 ObservableObject wrapper 만들고 (`LocationManager`처럼), 화면에서 `@StateObject`로 보유, `.onAppear`에서 `start()`.
- **시스템 nav bar는 사용하지 않음**: 각 화면이 `.navigationBarBackButtonHidden(true)`. back이 필요하면 좌상단 custom 원형 버튼 + `@Environment(\.dismiss)`.

---

## 현재 TODO

- `MainView` Previous → 산책 기록 화면
- `MainView` Let's Walk → 산책 세션 화면 (지도, 타이머, 캐릭터 동행)
- `charactor` → `character` 이름 정리 (asset rename + 코드의 배열)
- `Theme/`에 Color / Font 추출
- `ContentView.swift` 제거
- 산책 데이터 모델 / 영속화 (AppState 또는 SwiftData) 도입 시점 판단

---

## 빌드 / 실행

- Xcode에서 `THISPOT.xcodeproj` 열고 시뮬레이터 선택 → `Cmd+R`
- 새 파일 추가 후 빌드 안 되면 → Xcode navigator에서 해당 파일이 target membership 체크되어 있는지 확인
- Location chip이 "Locating..."에서 멈추면 → 시뮬 메뉴 **Features → Location → Apple / Custom Location** 설정
