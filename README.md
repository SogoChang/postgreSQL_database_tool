# PostgreSQL JSON 工具介面

這是一個基於 Gradio 和 PostgreSQL 的數據分析工具，專門用於處理和分析 JSON 格式的交易策略數據。該工具提供了直觀的 Web 介面，用於數據導入、視覺化分析和條件篩選。

## 功能特色

- 📂 **批量 JSON 數據導入**：支援從資料夾批量導入 JSON 文件到 PostgreSQL 數據庫
- 📈 **PnL 視覺化**：根據 ID 繪製損益（PnL）趨勢圖表
- 🔍 **條件篩選**：基於 Sharpe 比率、Fitness、Turnover 等指標篩選策略
- 🌐 **Web 介面**：基於 Gradio 的友好 Web 用戶介面
- 🛡️ **數據驗證**：內建數據完整性檢查和觸發器

## 系統要求

- Python 3.7+
- PostgreSQL 12+
- 必要的 Python 套件（見安裝說明）

## 安裝說明

1. **克隆專案**
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **安裝 Python 依賴**
   ```bash
   pip install gradio psycopg2-binary pandas matplotlib
   ```

3. **設置 PostgreSQL 數據庫**
   - 確保 PostgreSQL 服務正在運行
   - 創建數據庫（或使用現有數據庫）
   - 按順序執行 SQL 文件來設置數據庫結構

## 數據庫設置

請按照以下順序執行 SQL 文件來初始化數據庫：

1. 創建存儲過程：
   ```bash
   psql -d your_database -f create_procedure.sql
   ```

2. 創建驗證函數：
   ```bash
   psql -d your_database -f check_field.sql
   ```

3. 創建觸發器：
   ```bash
   psql -d your_database -f create_trigger.sql
   ```

4. 創建查詢函數：
   ```bash
   psql -d your_database -f function_get_id.sql
   psql -d your_database -f function_condition.sql
   ```

## 使用方法

1. **啟動應用程式**
   ```bash
   python gradio_ui.py
   ```

2. **訪問 Web 介面**
   - 應用程式將自動在瀏覽器中打開 `http://127.0.0.1:7860`
   - 或手動訪問該地址

3. **配置資料庫連接**
   - 在「🔑 資料庫設定」頁籤中輸入您的 PostgreSQL 連接資訊

## 文件說明

### 核心文件

#### [`gradio_ui.py`](gradio_ui.py)
主要的應用程式文件，包含：
- **Gradio Web 介面**：提供多個功能頁籤的用戶介面
- **數據導入功能**：`upload_json_from_folder()` - 批量導入 JSON 文件
- **PnL 視覺化**：`plot_pnl_by_id()` - 根據 ID 繪製損益圖表
- **條件篩選**：`filter_ids()` - 基於多個條件篩選策略 ID
- **系統控制**：`stop_gradio()` - 安全關閉應用程式

### SQL 文件

#### [`create_procedure.sql`](create_procedure.sql)
定義存儲過程 `insert_multiple_json()`：
- 接受 JSON 陣列作為輸入
- 批量插入多筆 JSON 數據到 `json_data` 表
- 包含錯誤處理和事務回滾機制

#### [`check_field.sql`](check_field.sql)
定義數據驗證函數 `validate_json_fields_before_insert()`：
- 檢查必要的 SQL 欄位（`id`, `file_name`）
- 驗證 JSON 結構中的必要欄位（`response_data`, `fitness`）
- 在數據插入前進行完整性檢查

#### [`create_trigger.sql`](create_trigger.sql)
創建觸發器 `trg_check_fields_before_insert`：
- 在每次插入 `json_data` 表之前自動執行驗證
- 確保數據完整性和一致性

#### [`function_get_id.sql`](function_get_id.sql)
定義查詢函數 `get_pnl_by_id()`：
- 根據指定 ID 獲取對應的 PnL 數據
- 返回 JSONB 格式的損益數據
- 用於 PnL 視覺化功能

#### [`function_condition.sql`](function_condition.sql)
定義條件篩選函数 `get_ids_by_conditions()`：
- 支援多個篩選條件：
  - 最低 Sharpe 比率
  - 最低 Fitness 值
  - 最高 Turnover 值
  - CONCENTRATED_WEIGHT 檢查結果為 PASS
  - LOW_SUB_UNIVERSE_SHARPE 檢查結果為 PASS
- 返回符合所有條件的策略 ID

## 數據結構

### JSON 數據格式
系統期望的 JSON 數據結構包含：
```json
{
  "id": "策略唯一識別碼",
  "response_data": {
    "sharpe": "Sharpe比率",
    "fitness": "適應度分數", 
    "turnover": "周轉率",
    "checks": [
      {
        "name": "檢查項目名稱",
        "result": "檢查結果(PASS/FAIL)"
      }
    ]
  },
  "pnl": "損益數據陣列"
}
```

### 數據庫表結構
```sql
CREATE TABLE json_data (
    id TEXT PRIMARY KEY,
    file_name TEXT NOT NULL,
    json_data JSONB NOT NULL
);
```

## 功能頁籤說明

1. **🔑 資料庫設定**：配置 PostgreSQL 連接參數
2. **📈 PnL 視覺化**：輸入 ID 查看損益圖表
3. **📂 資料匯入**：指定資料夾路徑批量導入 JSON 文件
4. **🔍 條件篩選**：根據策略指標篩選符合條件的 ID
5. **🛑 關閉系統**：安全關閉 Gradio 服務器

## 錯誤處理

- 所有數據庫操作都包含異常處理
- 插入失敗時會提供詳細的錯誤訊息
- 觸發器確保數據完整性
- 連接失敗時會顯示相應的錯誤提示

## 注意事項

- 確保 PostgreSQL 服務正在運行且可以連接
- JSON 文件必須包含必要的欄位結構
- 大量數據導入時請耐心等待處理完成
- 建議在生產環境中使用適當的數據庫權限設置

## 貢獻

歡迎提交 Issue 和 Pull Request 來改進這個專案。

## 授權

請根據專案需求添加適當的授權條款。
