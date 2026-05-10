import json

import streamlit as st

from ui_theme import apply_app_theme, render_header, render_status_strip


DATA_FILES = [
    "krt_data.json",
    "tpi_data.json",
    "krt_real_fare.json",
    "tpi_real_fare.json",
]


def run():
    apply_app_theme()
    render_header(
        "DATA MONITOR",
        "系統後台管理與資料庫監控",
        "檢查捷運路網、票價矩陣與原始 JSON 內容，協助確認資料部署狀態。",
    )

    st.subheader("資料檔狀態")

    target_file = st.selectbox("選擇要檢查的資料檔", DATA_FILES)

    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        render_status_strip(
            [
                ("目前檔案", target_file),
                ("主鍵筆數", f"{len(data)}"),
                ("讀取狀態", "正常"),
            ]
        )

        st.success(f"{target_file} 已成功讀取。")
        with st.expander("檢視原始 JSON 節點資料"):
            st.json(data)

    except FileNotFoundError:
        render_status_strip(
            [
                ("目前檔案", target_file),
                ("主鍵筆數", "0"),
                ("讀取狀態", "找不到檔案"),
            ]
        )
        st.error(f"找不到 {target_file}，請確認檔案已部署到專案根目錄。")
    except json.JSONDecodeError as exc:
        render_status_strip(
            [
                ("目前檔案", target_file),
                ("主鍵筆數", "0"),
                ("讀取狀態", "JSON 格式錯誤"),
            ]
        )
        st.error(f"{target_file} 不是有效 JSON：{exc}")

    st.divider()
    st.info("如需更新官方票價，請先在本地端重新產生票價資料，再部署更新後的 JSON 檔。")
