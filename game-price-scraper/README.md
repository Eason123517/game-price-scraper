# 🎮 二手遊戲片價格比較工具

一個功能強大的網路爬蟲應用程式，能夠自動搜尋多個台灣電商平台的二手遊戲價格，幫助玩家找到最優惠的遊戲價格。

## ✨ 主要功能

- **多平台搜尋**: 支援露天拍賣、蝦皮購物、Yahoo拍賣、PChome 24h等主要平台
- **智慧平台偵測**: 自動識別遊戲平台（Nintendo Switch、PS5、PS4、Xbox等）
- **即時價格比較**: 按價格排序，快速找到最優惠選項
- **進階篩選功能**: 可依平台、商品狀況、價格區間等條件篩選
- **響應式設計**: 支援桌面和行動裝置
- **反爬蟲處理**: 採用多種技術避免被網站封鎖

## 🛠️ 技術架構

### 後端
- **Python 3.11**: 主要程式語言
- **Flask**: 網頁框架
- **Selenium**: 動態網頁爬取
- **BeautifulSoup**: HTML解析
- **Requests**: HTTP請求處理

### 前端
- **HTML5**: 網頁結構
- **CSS3**: 現代化樣式設計
- **JavaScript ES6+**: 互動功能
- **響應式設計**: 支援各種裝置

### 部署
- **Docker**: 容器化部署
- **Gunicorn**: WSGI伺服器
- **GitHub Codespaces**: 開發環境支援

## 🚀 快速開始

### 方法一：使用 GitHub Codespaces（推薦）

1. 點擊 "Code" -> "Codespaces" -> "Create codespace on main"
2. 等待環境自動設定完成
3. 在終端執行：
```bash
pip install -r requirements.txt
python app.py
```
4. 開啟瀏覽器前往 `http://localhost:5000`

### 方法二：本地安裝

#### 系統需求
- Python 3.8+
- Google Chrome 瀏覽器
- Git

#### 安裝步驟

1. **複製專案**
```bash
git clone <repository-url>
cd game-price-scraper
```

2. **建立虛擬環境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. **安裝依賴**
```bash
pip install -r requirements.txt
```

4. **啟動應用程式**
```bash
python app.py
```

5. **開啟瀏覽器**
前往 `http://localhost:5000`

### 方法三：Docker 部署

1. **建構映像檔**
```bash
docker build -t game-price-scraper .
```

2. **執行容器**
```bash
docker run -p 5000:5000 game-price-scraper
```

3. **訪問應用程式**
前往 `http://localhost:5000`

## 📖 使用說明

### 基本搜尋
1. 在搜尋框輸入遊戲名稱（中文或英文）
2. 點擊「搜尋」按鈕
3. 等待30-60秒完成搜尋
4. 查看按價格排序的搜尋結果

### 搜尋技巧
- **使用完整遊戲名稱**: 例如「薩爾達傳說 王國之淚」
- **嘗試簡稱**: 例如「薩爾達」、「寶可夢」
- **避免版本號**: 不需要加入「中文版」、「亞版」等字詞
- **英文名稱**: 也可搜尋英文遊戲名稱

### 進階功能
- **平台篩選**: 只顯示特定遊戲平台的結果
- **狀況篩選**: 選擇「全新」或「二手」商品
- **排序方式**: 按價格、平台或狀況排序
- **價格統計**: 查看最低、最高和平均價格

## 🔧 設定檔說明

### 環境變數
```bash
FLASK_APP=app.py
FLASK_ENV=development  # 開發模式
FLASK_DEBUG=True      # 除錯模式
PORT=5000             # 端口號
```

### Chrome 設定
程式會自動處理 Chrome 瀏覽器的設定，包括：
- 無頭模式運行
- 停用安全沙箱
- 使用者代理輪換
- 反自動化偵測

## 🛡️ 注意事項

### 法律聲明
- 本工具僅用於個人學習和價格比較
- 請遵守各網站的使用條款
- 不得用於商業用途或大量爬取
- 使用者需自行承擔使用風險

### 技術限制
- 搜尋速度受網路狀況影響
- 某些網站可能有反爬蟲保護
- 搜尋結果可能不完整
- 價格資訊僅供參考

### 最佳實踐
- 避免過於頻繁的搜尋
- 搜尋間隔建議3-5秒以上
- 網路不穩定時可能影響結果
- 建議在網路負載較低時使用

## 🔍 故障排除

### 常見問題

**Q: 搜尋一直顯示「載入中」？**
A: 檢查網路連線，某些平台可能暫時無法存取。等待60秒後重試。

**Q: Chrome 驅動程式錯誤？**
A: 確保已安裝 Google Chrome，或嘗試重新安裝 webdriver-manager。

**Q: 搜尋結果很少或沒有結果？**
A: 嘗試不同的關鍵字，或檢查遊戲名稱拼寫。

**Q: 應用程式無法啟動？**
A: 檢查 Python 版本和依賴安裝，確保所有套件都正確安裝。

### 除錯模式
啟用除錯模式查看詳細日誌：
```bash
export FLASK_DEBUG=True
python app.py
```

## 🚀 部署到生產環境

### 使用 Gunicorn
```bash
gunicorn --bind 0.0.0.0:5000 --workers 2 --threads 2 --timeout 120 app:app
```

### 使用 Nginx 反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 API 文檔

### 搜尋 API
```http
POST /search
Content-Type: application/json

{
  "game_name": "薩爾達傳說"
}
```

**回應格式**：
```json
{
  "success": true,
  "count": 15,
  "search_term": "薩爾達傳說",
  "results": [
    {
      "title": "薩爾達傳說 王國之淚 Nintendo Switch",
      "price": 1680,
      "platform": "Nintendo Switch",
      "condition": "二手",
      "seller": "seller123",
      "location": "台北市",
      "source": "露天拍賣",
      "url": "https://www.ruten.com.tw/item/..."
    }
  ]
}
```

### 健康檢查 API
```http
GET /health
```

### 平台清單 API
```http
GET /api/platforms
```

## 🤝 貢獻指南

歡迎貢獻代碼！請遵循以下步驟：

1. Fork 此專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

### 開發規範
- 遵循 PEP 8 代碼風格
- 添加適當的註解和文檔
- 確保所有測試通過
- 更新相關文檔

## 📝 版本歷史

- **v1.0.0** (2024-08): 初始版本發布
  - 支援多平台搜尋
  - 基本價格比較功能
  - 響應式網頁介面

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 文件

## 🙏 致謝

- Flask 社群提供的優秀框架
- Selenium 團隊的網頁自動化工具
- BeautifulSoup 的 HTML 解析功能
- 所有貢獻者和使用者的支持

## 📞 聯絡資訊

如有問題或建議，請透過以下方式聯絡：

- 開啟 [GitHub Issue](../../issues)
- 電子郵件：[your-email@example.com]
- 專案主頁：[https://github.com/your-username/game-price-scraper]

---

**⚠️ 免責聲明**: 本工具僅供學習和個人使用，請勿用於違反網站服務條款的行為。使用者需自行承擔使用本工具的一切風險和責任。