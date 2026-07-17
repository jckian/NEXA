# SP26 Research — Session Log

SCI-Arc Spring 2026 | Program Agent System  
Three.js Visualizers · Blender Export · Python Simulation

---

## 概覽 Overview

本 session 擴充了原有的 TPAC program agent 系統，新增兩個案例研究的完整程式分配資料與 3D 視覺化工具，並建立統一的多案例入口介面。

---

## 新增檔案

### `index.html`
三個 HTML 視覺化的統一入口介面。

- 頂部導覽列切換三個案例（TPAC / 53W53 / Tama）
- 使用 `visibility` 而非 `display:none` 隱藏非作用中的 iframe — 確保三個 Three.js context 同時載入，切換時不重新渲染
- 每個 iframe 首次載入時顯示掃描線動畫 loader
- 視覺風格與三個子頁面一致（深色 / minimal）

```
display:none  → iframe 不載入（錯誤作法）
visibility:hidden → iframe 正常載入、只是視覺隱藏（正確作法）
```

---

### `references/53W53-PROGRAM-DISTRIBUTION.txt`
Jean Nouvel 53W53 完整樓層程式分配。

| 項目 | 數值 |
|---|---|
| 樓層範圍 | B1（-1）至 L73 |
| 程式類型 | 33 種 |
| 程式條目 | ~430 筆 |
| 格式 | `{type}/{area}/{level}/{category}/{w,d}` |

分區邏輯：
- **L0–L3** 公共底層：MoMA 畫廊、大廳、餐廳
- **L4–L11** 下層住宅：2 戶/層，40×40m 裙樓
- **L12–L16** 設施層：健身、水療、住戶交誼廳
- **L17–L25** 中層住宅 A：28×28m
- **L26–L35** 中層住宅 B：25×25m
- **L36–L45** 上中層住宅：全層單戶，22×22m
- **L46–L47** 冠層交誼廳：20×20m
- **L48–L55** 上層住宅 A：18×18m
- **L56–L60** 上層住宅 B：15×15m
- **L61–L73** 塔尖區：逐層縮減至 6×6m

---

### `references/TAMA-PROGRAM-DISTRIBUTION.txt`
Toyo Ito 多摩美術大學圖書館完整樓層程式分配。

| 項目 | 數值 |
|---|---|
| 樓層範圍 | B1（-1）/ L0（0）/ L1（1） |
| 程式類型 | 25 種 |
| 程式條目 | 39 筆 |
| 總 GFA | ~5,750 m² |

設計特點：
- 無中央核心筒 — 三個防火梯分布於建築周邊角落
- `open stair` 與 `service corridor` 作為一般 layout block 處理（非固定錨點）
- 防火梯位置依分配說明對應：SW（主入口）/ NE（閱讀端）/ SE（服務側）

---

### `pythonFiles/Blender53W53.py`
53W53（B1–L30）Blender Python 匯出腳本。

**座標對應（Three.js → Blender）：**

| Three.js | Blender |
|---|---|
| X（東西） | X |
| Y（高度） | Z |
| Z（深度） | Y |

**功能：**
- 完整移植 `floorFootprint()` 與 `layoutFloor()` 邏輯（Python）
- 依程式類型建立 Blender 材質（sRGB hex → 線性 RGBA）
- 以 `53W53 > F00 ~ F30` 集合階層組織物件
- 程式資料硬編碼（B1 至 L30，對應 `TAPER_TOP = 30`）

**執行方式：** Blender → Scripting workspace → Run Script

---

## 修改檔案

### `53w53-program-diagram.html`

#### 程式資料更新
- `DEFAULT_PROGRAM_TEXT` 替換為 `53W53-PROGRAM-DISTRIBUTION.txt` 完整內容
- `TYPE_COLORS` 新增全部 33 種類型的色彩對應
- 類型 key 使用底線正規化：`fire_stair_and_elevator_1`
- `CORE_TYPES` Set 對應三種核心類型

#### 樓層數調整
- `TAPER_TOP` 從 `73` 改為 `30`
- `param-floor-count` 輸入預設值同步更新為 `30`
- `buildScene()` 加入 `level > TAPER_TOP` 過濾，限制渲染樓層

#### Core 消減規則（新增）
```javascript
function getActiveCores(level) {
  const t = level / Math.max(1, TAPER_TOP);
  if (t <= 0.55)  → 3 核（貨梯 + 客梯1 + 客梯2）
  if (t <= 0.85)  → 2 核（移除貨梯）
  else            → 1 核（僅保留主客梯）
}
```
- `layoutFloor()` 呼叫 `getActiveCores(level)` 過濾非活躍核心
- 非活躍核心的 entries 直接跳過，不佔用樓層平面空間

---

### `tama-program-diagram.html`

#### 程式資料更新
- `DEFAULT_PROGRAM_TEXT`：22 筆舊條目 → 39 筆新條目
- `TYPE_COLORS`：17 種舊類型 → 29 種新類型
- 類型 key 為原始小寫字串（含空格），對應 `m[1].toLowerCase()` 解析器
- 特別注意：`{IT support}` 解析後為 `'it support'`（非 `'IT support'`）
- `LEGEND_GROUPS`：PUBLIC / PRIVATE / CIRCULATION 分組全部更新
- 預設狀態文字：`"22 entries"` → `"39 entries"`

#### 核心錨點更新
防火梯從 2 個角點擴充為 3 個周邊位置：

| 類型 | 位置 | 說明 |
|---|---|---|
| fire stair and freight elevator | SE (x=102, z=17) | 服務 / 裝卸側 |
| fire stair and elevator 1 | SW (x=18, z=17) | 主入口側 |
| fire stair and elevator 2 | NE (x=84, z=62) | 遠端閱讀區 |

---

### `pythonFiles/EllipseAgent.py`

核心類型偵測從嚴格相等改為 substring 比對：

```python
# 舊（不支援 elevator 1/2）
if programType == 'fire stair and freight elevator' or programType == 'fire stair and elevator':

# 新（支援所有命名變體）
if ('fire stair and freight elevator' in programType or
        'fire stair and elevator' in programType):
```

---

### `pythonFiles/ProgramDeveloperEllipseBoundary.py`

新增 Core 消減規則（與 HTML 同步）：

```python
def get_active_cores(level, max_level):
    t = level / max(1, max_level)
    if t <= 0.55  → 3 cores
    if t <= 0.85  → 2 cores（移除貨梯）
    else          → 1 core（僅主梯）
```

主迴圈更新：
- 讀取 `maxFloorLevel` 作為比例計算基準
- 每個 core entry 進入迴圈前先判斷是否為活躍核心，不活躍者 `continue` 跳過
- corePts 擴展為 3 個錨點（index 0/1/2），並以 `len(corePts)` 防護避免 index 越界
- 貨梯 → corePts[0]，客梯1 → corePts[1]，客梯2 → corePts[2]

---

## Core 消減規則說明

適用於 53W53（同邏輯，跨四個檔案同步）：

| 樓層比例 | 活躍核心 | 建築邏輯 |
|---|---|---|
| B1（地下） | 全 3 個 | 裝卸、BOH 基礎設施 |
| ≤ 55% of top | 全 3 個 | 公共層、設施層、下層住宅 |
| 55–85% of top | 2 個（移除貨梯） | 貨梯在中層轉換層終止 |
| > 85% of top | 1 個（僅主梯） | 單一主電梯通頂層 |

閾值依 `TAPER_TOP`（HTML/Blender）或 `maxFloorLevel`（Python agent）自動縮放。

---

## 系統架構總覽

```
index.html
├── tpac-program-diagram.html      (iframe)
├── 53w53-program-diagram.html     (iframe)
└── tama-program-diagram.html      (iframe)

references/
├── TPAC-PROGRAM-DISTRIBUTION.txt
├── 53W53-PROGRAM-DISTRIBUTION.txt
└── TAMA-PROGRAM-DISTRIBUTION.txt

pythonFiles/
├── ProgramDeveloperEllipseBoundary.py   (主模擬入口)
├── EllipseAgent.py                       (Agent 物理模擬)
├── BlenderTPAC.py                        (TPAC Blender 匯出)
└── Blender53W53.py                       (53W53 Blender 匯出)
```

---

## 案例比較

| | TPAC | 53W53 | Tama Library |
|---|---|---|---|
| 建築師 | OMA | Jean Nouvel | Toyo Ito |
| 年份 | 2023 | 2019 | 2007 |
| 樓層 | 14 層（B2–L11） | 30 層（B1–L30） | 3 層（B1–L1） |
| GFA | ~58,250 m² | ~可變 | ~5,750 m² |
| 核心系統 | 垂直核心筒（4 shaft） | 塔式 diagrid + 中央核 | 無中央核（周邊分散） |
| 特殊幾何 | 三球體突出體 | 線性漸縮 | 梯形基地 + 拱結構 |
| Blender 腳本 | BlenderTPAC.py | Blender53W53.py | — |
