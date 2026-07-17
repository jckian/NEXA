// ============================================================
// 參數化平台生成腳本 (供 rhinoceros_operator 執行)
// 依據既有 block 元件庫 + 259 模組規則自動組裝新平台
// ============================================================

// ---------- 參數(蓋新平台時只改這裡) ----------
double Ox = -13000, Oy = 7300, Oz = 0;  // 平台原點
int baysX = 2;                           // X 方向跨數
int baysY = 2;                           // Y 方向跨數
int stories = 2;                         // 樓層數
bool addFacade = true;                   // 是否掛帷幕
bool addWindows = true;                  // 是否放窗
// ------------------------------------------------

double M = 259.0;      // 模組
double t = 10.0;       // 構材斷面
double C = M - 2 * t;  // 淨開口 239

Func<string, int> FindDef = (name) => {
    var d = doc.InstanceDefinitions.Find(name);
    return d == null ? -1 : d.Index;
};

int idPlate  = FindDef("PLATE");
int idFrame  = FindDef("1_@ 01");
int idDeck   = FindDef("module-deck");
int idWinL   = FindDef("window");
int idWinS   = FindDef("window-1");
int idFacade = FindDef("FACADE_PANE07");

Action<int, Transform> Place = (defIdx, xf) => {
    if (defIdx >= 0) doc.Objects.AddInstanceObject(defIdx, xf);
};

// --- 1. PLATE:每個柱格一片,z = Oz + 3 ---
for (int i = 0; i < baysX; i++)
for (int j = 0; j < baysY; j++)
{
    var xf = Transform.Translation(Ox + i * M, Oy + j * M, Oz + 3);
    Place(idPlate, xf);
}

// --- 2. 框架:1_@ 01 為 1M x 2M 雙跨單元,逐層堆疊 z = Oz+8+k*M ---
for (int k = 0; k < stories; k++)
for (int i = 0; i < baysX; i++)
for (int j = 0; j < baysY; j += 2)   // 雙跨單元,Y 方向每 2 跨放一個
{
    var xf = Transform.Translation(Ox + i * M, Oy + j * M, Oz + 8 + k * M);
    Place(idFrame, xf);
}

// --- 3. 樓板:每跨 2 片 module-deck (121x239),deck 底 = 層基準 + 5 ---
// module-deck 定義為 1.2x2.4x0.1 (需 x100 縮放),插入原點在板中線
for (int k = 0; k <= stories; k++)   // 含屋頂板
for (int i = 0; i < baysX; i++)
for (int j = 0; j < baysY; j++)
{
    double zDeck = Oz + 8 + k * M + 5;
    for (int half = 0; half < 2; half++)
    {
        double dx = t + half * (C / 2.0) + (C / 4.0);  // 半跨中心
        var scale = Transform.Scale(Point3d.Origin, 100.0);
        var move  = Transform.Translation(Ox + i * M + dx, Oy + j * M + t + C / 2.0, zDeck);
        Place(idDeck, move * scale);
    }
}

// --- 4. 窗:外圍立面每跨 = window(173)+window-1(66),窗頂 = 層基準 + 243 ---
if (addWindows)
{
    for (int k = 0; k < stories; k++)
    {
        double zTop = Oz + 8 + k * M + 243;
        // 南向立面 (y = Oy) 示範;其他向依同規則旋轉
        for (int i = 0; i < baysX; i++)
        {
            double x0 = Ox + i * M + t;
            // 大窗 window: 定義 min(-0,-6,-233),插入點為窗頂
            var xfL = Transform.Translation(x0, Oy, zTop);
            Place(idWinL, xfL);
            // 小窗 window-1: 定義 min(-60,-5,-233)
            var xfS = Transform.Translation(x0 + 173 + 60, Oy, zTop);
            Place(idWinS, xfS);
        }
    }
}

// --- 5. 帷幕:面外偏移 19,垂直間距 250,由頂往下 ---
if (addFacade)
{
    double topZ = Oz + 8 + stories * M;
    int panelRows = stories + 1;   // 可向下多掛(架高平台)
    for (int r = 0; r < panelRows; r++)
    {
        double zP = topZ - 250 * (r + 1);
        for (int i = 0; i < baysX; i++)
        {
            // FACADE_PANE07 定義需 x0.5 縮放 (498 -> 249)
            var scale = Transform.Scale(Point3d.Origin, 0.5);
            var move  = Transform.Translation(Ox + i * M + 5, Oy - 19, zP);
            Place(idFacade, move * scale);
        }
    }
}

doc.Views.Redraw();
RhinoApp.WriteLine("Platform built: " + baysX + "x" + baysY + " bays, " + stories + " stories at (" + Ox + "," + Oy + "," + Oz + ")");
