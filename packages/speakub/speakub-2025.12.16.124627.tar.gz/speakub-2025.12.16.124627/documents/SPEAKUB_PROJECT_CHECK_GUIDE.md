# SpeakUB 專案標準檢查指南

## 📋 本指南的目的

**確保每次專案分析都遵循統一的高品質標準流程**

本指南提供了完整的專案檢查流程，讓AI每次處理SpeakUB專案時都能：
- 🔍 實際分析代碼而非依賴過時文檔
- ✅ 發現真實問題而非歷史備忘錄
- 📄 同步清理文檔狀態誤導
- 🔄 立即改善文檔維護問題

---

## 🎯 專案情境說明

### 專案背景
**SpeakUB** 是一個先進的EPUB閱讀器，具備TTS (文字轉語音) 功能，專注於平滑音頻播放和系統效能優化。

### 專案特點 ⚠️ **關鍵重點**
- **有大量歷史markdown備忘錄** - 這些文檔內容常常與實際專案狀態不符，容易誤導分析
- **架構經多次重構** - 舊的TODO項目往往已完成，文檔卻未更新
- **文檔質量問題** - 過時的實施建議會給人錯誤的優先級判斷

### 常見誤區 🆘 **務必避免**
- ❌ **依賴markdown文件分析專案狀態**
- ❌ **把舊備忘錄當作當前問題清單**
- ❌ **假定文檔記載等於實際狀態**
- ❌ **忽略文檔同步問題**

---

## 🚀 標準檢查流程 (必須按順序執行)

### Phase 0: 準備階段 (每次務必)
```bash
# 1. 確認專案結構和環境
cd {SPEAKUB_PROJECT_ROOT}  # 切換到SpeakUB專案根目錄
# 說明: {SPEAKUB_PROJECT_ROOT} 應替換為實際專案路徑，例如:
# cd /home/sam/Templates/epub-reader-rich\ 專案/GGGG/speakub_H1V9_39
# 或在專案目錄中直接執行檢查命令

python --version  # 確認Python版本
python -c "import speakub; print('匯入成功')"  # 基礎功能檢查

# 2. 準備檢查工具
pip install flake8 mypy pytest  # 如尚未安裝
```

### Phase 1: 實際代碼分析 🔥 **最重要**
```bash
# ⚠️ 注意: 這是最關鍵的階段，不要跳過！

# 1. 風格檢查 (實際代碼品質)
flake8 speakub/ --max-line-length=88 --statistics > quality_report.txt

# 2. 類型安全檢查 (實際代碼問題)
mypy speakub/ --ignore-missing-imports > type_report.txt

# 3. 並發安全檢查 (SpeakUB架構重點)
python -c "
# 檢查鎖定使用規範遵守情況
import re
from pathlib import Path

def check_concurrency_safety():
    issues = []
    speakub_files = list(Path('speakub').rglob('*.py'))
    
    for file_path in speakub_files:
        try:
            content = file_path.read_text()
            
            # 檢查AsyncBridge使用是否正確分類
            bridge_calls = re.findall(r'async_bridge\.(run_async_task|run_coroutine|delegate_to_async_task)', content)
            for call in bridge_calls:
                # 檢查關鍵操作是否正確使用run_coroutine
                if call == 'run_async_task' and any(keyword in content[max(0, m.start()-100):m.start()+100] 
                                                   for m in re.finditer(call, content) 
                                                   for keyword in ['play', 'pause', 'stop', 'status']):
                    issues.append(f'{file_path.name}: 關鍵操作使用run_async_task (應使用run_coroutine)')
            
            # 檢查鎖定層次結構違規
            if '_tts_lock' in content and '_async_tts_lock' in content:
                # 檢查是否有嵌套鎖定
                lock_pattern = r'with.*_tts_lock.*:.*with.*_async_tts_lock'
                if re.search(lock_pattern, content, re.DOTALL):
                    issues.append(f'{file_path.name}: 違反鎖定層次結構 (同步->異步)')
                    
        except Exception as e:
            issues.append(f'{file_path.name}: 無法檢查 - {e}')
    
    print('並發安全檢查結果:')
    for issue in issues[:10]:  # 只顯示前10個
        print(f'⚠️  {issue}')
    if not issues:
        print('✅ 未發現明顯的並發安全問題')
    elif len(issues) > 10:
        print(f'...還有{len(issues) - 10}個問題')

check_concurrency_safety()
"

# 3. 測試狀態檢查 (實際可運行性)
python -c "
import pytest
import sys
from pathlib import Path

# 收集測試數量
tests_dir = Path('tests')
py_files = list(tests_dir.rglob('test_*.py'))
total_tests = len(py_files)
print(f'發現測試檔案數量: {total_tests}')

# 嘗試收集測試
try:
    result = pytest.main(['--collect-only', 'tests/', '--quiet'])
    print(f'測試收集: 完成')
except Exception as e:
    print(f'測試收集錯誤: {e}')
"

# 4. 依賴檢查 (實際安裝狀態)
python -c "
try:
    print('檢查關鍵依賴...')
    import pygame; print('✅ pygame:', pygame.version.ver)
    print('✅ 基本依賴正常')
except ImportError as e:
    print('❌ 依賴問題:', e)
"
```

### Phase 2: 文檔狀態同步檢查 📄 **專案特色要求**
```bash
# ⚠️ SpeakUB專案的文檔問題很嚴重，務必檢查

# 檢查關鍵文檔是否存在過時內容
grep -r "TODO" *.md | head -10
grep -r "建議.*實施" *.md | head -10

# 自動化文檔健康檢查
python -c "
import re
from pathlib import Path

def check_doc_status():
    docs_to_check = [
        'IMPLEMENTATION_CHECKLIST.md',
        'RESERVOIR_POST_IMPLEMENTATION_FIXES_ANALYSIS.md',
        'RESERVOIR_COMPLETE_OPTIMIZATION_SUMMARY.md',
        'stage4_migration_plan.md',
        'README_v4_reservoir.md'
    ]
    
    issues = []
    for doc in docs_to_check:
        if Path(doc).exists():
            content = Path(doc).read_text()
            # 檢查是否包含狀態標記
            if not re.search(r'文檔狀態.*📖|🚧|✅', content):
                issues.append(f'{doc}: 缺少狀態標記')
            # 檢查鏈接
            if 'IMPLEMENTATION_CHECKLIST.md' in content and doc != 'IMPLEMENTATION_CHECKLIST.md':
                if not re.search(r'\[.*\]\(.*IMPLEMENTATION_CHECKLIST\.md.*\)', content):
                    issues.append(f'{doc}: 未鏈接到實施清單')
    
    print('文檔狀態檢查結果:')
    for issue in issues:
        print(f'⚠️  {issue}')
    if not issues:
        print('✅ 所有文檔狀態良好')

check_doc_status()
"
```

### Phase 3: 問題識別和清單製作
```bash
# 基於檢查結果製作實施清單
python -c "
# 讀取檢查結果並生成報告
import subprocess
import re

def analyze_findings():
    findings = []
    
    # 分析flake8結果
    try:
        flake8_output = subprocess.run(
            ['flake8', 'speakub/', '--max-line-length=88', '--statistics'], 
            capture_output=True, text=True, timeout=30
        )
        flake8_lines = flake8_output.stderr.count('\n')
        if flake8_lines > 0:
            findings.append(f'🔴 代碼品質問題: 發現 {flake8_lines} 個風格錯誤')
    except:
        findings.append('❌ 無法執行flake8檢查')
    
    # 分析mypy結果  
    try:
        mypy_output = subprocess.run(
            ['mypy', 'speakub/', '--ignore-missing-imports'], 
            capture_output=True, text=True, timeout=60
        )
        mypy_errors = mypy_output.stdout.count('error:')
        if mypy_errors > 0:
            findings.append(f'🟡 類型安全問題: 發現 {mypy_errors} 個類型註釋缺失')
    except:
        findings.append('❌ 無法執行mypy檢查')
    
    print('檢查發現的主要問題:')
    for finding in findings:
        print(finding)
    
    return findings

analyze_findings()
"
```

### Phase 4: 實際問題修復 (如果有能力)
```bash
# 修復常見問題 (如果AI有權限)

# 1. 文檔狀態標記補齊
# 2. 鏈接更新
# 3. 狀態同步
# 4. 實施清單更新
```

### Phase 5: 最終報告產生
**必須包含的報告內容：**
- [x] 實際檢查項目總結
- [x] 發現的真實問題清單
- [x] 文檔同步處理結果
- [x] 後續改善建議
- [x] 品質指標評估

---

## 💡 如何引導AI執行這個流程

### 基本引導語句

**每次請AI檢查SpeakUB專案時，使用以下開場白：**

```markdown
**請按照以下SpeakUB專案標準檢查指南執行完整分析：**

1. **實際代碼優先檢查** 🔍
   - 先執行代碼品質檢查 (flake8, mypy, pytest)
   - 不要依賴markdown文件的過時TODO清單
   - 實際運行測試並檢查錯誤

2. **文檔同步問題處理** 📄  
   - 檢查所有markdown備忘錄的過時內容
   - 標記哪些建議實際上已實施完成
   - 更新文檔狀態標記避免誤導

3. **實施清單基於事實製作** ✅
   - 只納入實際發現的問題
   - 排除已完成的歷史項目
   - 按實際檢查結果設定優先等級

詳請參考: [SpeakUB專案標準檢查指南](documents/SPEAKUB_PROJECT_CHECK_GUIDE.md)
```

### 進階引導技巧

**如果AI表現不理想，提供額外指引：**
```markdown
**請注意SpeakUB專案的特別之處：**
- ❗ 有大量過時的markdown備忘錄，容易誤導
- ❗ 實際專案狀態常常優於文檔記錄  
- ❗ 架構已多次重構，舊建議可能已完成
- ❗ 文檔同步問題是持續性議題，務必處理
```

### 品質檢查問題

**發現AI未按標準時的修正語句：**
```markdown
這個分析似乎仍然依賴舊的markdown文件建議。
請重新開始，先執行實際的代碼檢查：`flake8 speakub/ --max-line-length=88` 和 `mypy speakub/ --ignore-missing-imports`，然後基於實際結果製作實施清單。
```

---

## 📊 品質驗證標準

### 通過標準 ✅
- [x] **實際檢查優先**: 代碼品質檢查命令實際執行
- [x] **文檔同步處理**: 過時內容都有狀態標記更新
- [x] **事實基礎**: 實施清單基於實際發現而非文檔記錄
- [x] **品質指標**: 提供具體的錯誤數量和問題統計

### 警示訊號 ⚠️
- [x] **依賴markdown TODO**: 如果清單來自主檔建議而非工具輸出
- [x] **歷史問題重提**: 如果建議修復早已完成的集成
- [x] **無實際驗證**: 如果沒有運行flake8/mypy的證據
- [x] **文檔不同步**: 如果沒有處理過時文檔標記

### 品質等級評估
```
🟢 優秀 (95%+): 完全按標準流程，問題準確，文檔同步完善
🟡 良好 (80%+): 大部分正確，有少數文檔問題未處理  
🟠 需改善 (60%+): 基本正確但有明顯標準偏離
🔴 不合格 (60%-): 明顯依賴過時文檔，問題不準確
```

---

## 🔧 持續改善機制

### 每月檢查
- [x] 驗證指南是否仍適用當前專案狀態
- [x] 更新檢查命令以適應新工具版本
- [x] 添加新發現的專案特色問題類型

### 每季審查
- [x] 評估是否有新的文檔同步問題模式
- [x] 檢查指南是否能有效防止常見AI錯誤
- [x] 更新品質門檻以反映專案成長需求

### 重大變更時
- [x] 專案架構重大調整時更新流程
- [x] 新增重要品質檢查工具時整合
- [x] 團隊變更時重新驗證指引有效性

---

## 🎯 最終目標：AI自主高品質專案分析

**讓每次SpeakUB專案分析都達到以下標準：**
- 🔬 **精確性**: 只發現實際存在的問題
- ⚡ **即時性**: 問題狀態與實際專案同步
- 📈 **建設性**: 提供具體可行的改善方案
- 🛡️ **可靠性**: 建立信任的分析過程

**這份指南是通往那個目標的引導地圖** 🗺️

---

*最後更新*: 2025-11-22
*適用版本*: SpeakUB 持續維護版
*預期效果*: AI分析品質提升 90%+ , 誤導問題減少 95%+
