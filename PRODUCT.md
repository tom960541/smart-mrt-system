# Product Context

## Product

智慧捷運路徑規劃是一個給台灣捷運乘客使用的路線查詢工具。使用者可以用自然語言、下拉選單或互動地圖選擇起訖站，系統會回傳建議路線、票價、站數與 Google Maps 輔助資訊。

## Primary Users

- 日常通勤者：想快速確認路線、票價與站數。
- 臨時旅客：不熟捷運站名，需要 AI 或地圖輔助。
- 展示或課程評審：需要看出系統同時具備演算法、資料庫、AI 與 UI 整合能力。
- 開發維護者：需要檢查 JSON 路網與票價資料是否正確載入。

## Core Jobs

- 快速選擇捷運路網。
- 用文字或手動方式指定出發站與終點站。
- 在最少站數與最省票價兩種策略間切換。
- 清楚看見票價、站數、路線分段與地圖輔助。
- 在 AI API 失效時仍能使用基本查詢功能。

## Product Mode

This is product UI, not a marketing page. The interface should be quiet, legible, operational, and fast to scan. Visual design serves the trip-planning task.

## Voice

- 清楚、可靠、務實。
- 中文介面優先，避免中英混雜，除非是專有名詞。
- 錯誤訊息要說明下一步，不只說失敗。
- 成功訊息應簡短，不搶走路線結果的注意力。

## Anti-References

- 不使用大面積紫色漸層、玻璃擬態或過度裝飾。
- 不把所有內容都做成浮誇卡片。
- 不使用「AI 腦力激盪中」這類不夠正式的提示。
- 不讓 Gemini API 缺失阻止手動查詢。
- 不讓開發者後台看起來像一般使用者頁面。
