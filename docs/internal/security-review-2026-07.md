# 安全審查紀錄（WBS 2.1）

> **日期:** 2026-07-12（v0.57.0）
> **範圍:** 依賴掃描（三個 Python 服務 + dashboard）、auth 流程審計、資料層注入面檢查
> **方法:** pip-audit（--no-deps 對 requirements 針腳）、npm audit、原始碼審視

## 發現與處置

| # | 發現 | 嚴重度 | 處置 |
| --- | --- | --- | --- |
| 1 | starlette 0.41.3 帶 8 個已知漏洞（PYSEC-2026-161/248/249/1941/1942、CVE-2026-48817/48818），由 fastapi 0.115.6 引入，影響三個服務 | HIGH | ✅ 升級 fastapi 0.139.0 / starlette 1.3.1 / uvicorn 0.51.0 並明確鎖定；112 測試全過後 pip-audit 乾淨 |
| 2 | pytest 8.3.4 一個已知漏洞（PYSEC-2026-1845） | LOW（僅測試環境） | ✅ 升級 9.1.1 |
| 3 | PBKDF2-HMAC-SHA256 迭代 120k，低於 OWASP 現行建議 | MEDIUM | ✅ 升至 600k；雜湊格式自帶迭代數，舊雜湊持續可驗證（含回歸測試） |
| 4 | 缺 token 請求回 403（框架舊行為） | INFO | ✅ 升級後框架依 RFC 7235 回 401，測試同步修正 |

## 審計通過項（無需變更）

- **Token**：HMAC 簽章 + 過期時間戳；密鑰自環境變數；生產環境拒絕開發預設密鑰。
- **登入防護**：密碼政策（長度/組成/不得含帳號）、失敗次數視窗鎖定（可配置）。
- **注入面**：MySQL 層全程參數化查詢（`%s` 佔位）；無字串拼接 SQL。
- **CORS**：白名單限定 `localhost:5173` 來源。
- **日誌**：請求日誌排除 body、Authorization、cookie 與 query string。
- **Demo reset**：生產環境回 404（含回歸測試）。
- **秘密管理**：`.env` 忽略、gate 內建 secret 掃描、範例檔僅空值。
- **npm audit**：0 vulnerabilities。

## 延後項（託管部署閘門，已見 ARCHITECTURE Security Boundaries）

全域速率限制（目前僅登入鎖定）、TLS/安全標頭（CSP/HSTS，屬反向代理層）、token 撤銷與 refresh、帳號救援流程、滲透測試。

## 重跑方式

```powershell
python -m pip install pip-audit
python -m pip_audit -r backend-api\requirements.txt --no-deps
python -m pip_audit -r scheduler-service\requirements.txt --no-deps
python -m pip_audit -r ml-service\requirements.txt --no-deps
cd web-dashboard; npm audit
```
