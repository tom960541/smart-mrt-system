import streamlit as st
import json
import math
import heapq
import re
import urllib.parse
from collections import deque
from html import escape
from PIL import Image
from io import BytesIO
from gtts import gTTS
from google import genai
from streamlit_image_coordinates import streamlit_image_coordinates
from ui_theme import apply_app_theme, render_header, render_status_strip

# ==========================================
# 系統設定與策略模式
# ==========================================
AVG_DISTANCE_PER_SEGMENT = 1.3


def get_gemini_client():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None, "未設定 GEMINI_API_KEY，已改用本地站名比對；手動選站與地圖選站不受影響。"

    try:
        return genai.Client(api_key=api_key), ""
    except Exception as exc:
        return None, f"Gemini 初始化失敗：{exc}"

# 備用計價公式 (當 TDX 查無資料時的 Fallback)
def krt_fare_strategy(dist, line_type):
    fare = 20 + (math.ceil((dist - 5) / 2) * 5) if dist > 5 else 20
    max_fare = 35 if "C" in line_type or "LRT" in line_type else 60
    return min(fare, max_fare)

def tpi_fare_strategy(dist, line_type):
    fare = 20 + (math.ceil((dist - 5) / 3) * 5) if dist > 5 else 20
    return min(fare, 65)

MAP_DATABASE = {
    "高雄捷運": {
        "json": "krt_data.json", 
        "img": "krt_map.jpg", 
        "fare_json": "krt_real_fare.json",
        "fare_func": krt_fare_strategy,
        "google_area": "Kaohsiung Taiwan"
    },
    "台北捷運": {
        "json": "tpi_data.json", 
        "img": "TaipeiMetroStamp.png", 
        "fare_json": "tpi_real_fare.json",
        "fare_func": tpi_fare_strategy,
        "google_area": "Taipei Taiwan"
    }
}

# ==========================================
# 核心資料結構
# ==========================================
@st.cache_data
def load_json_data(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def make_google_maps_urls(start_name, config):
    area = config.get("google_area", "Taiwan")
    destination = f"{start_name} MRT station {area}"

    route_params = urllib.parse.urlencode({
        "api": "1",
        "origin": "Current Location",
        "destination": destination,
        "travelmode": "transit",
    })
    search_params = urllib.parse.urlencode({
        "api": "1",
        "query": destination,
    })

    directions_url = f"https://www.google.com/maps/dir/?{route_params}"
    search_url = f"https://www.google.com/maps/search/?{search_params}"
    embed_url = f"https://www.google.com/maps?q={urllib.parse.quote_plus(destination)}&output=embed"
    return directions_url, search_url, embed_url

def render_google_maps_widget(start_name, config):
    if not start_name:
        return

    directions_url, search_url, embed_url = make_google_maps_urls(start_name, config)
    
    st.markdown(
        f"""
        <style>
        .google-map-float {{
            position: fixed;
            right: 24px;
            bottom: 24px;
            z-index: 9999;
            width: min(360px, calc(100vw - 32px));
            overflow: hidden;
            border: 1px solid rgba(60, 64, 67, 0.18);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.97);
            box-shadow: 0 16px 38px rgba(0, 0, 0, 0.18);
            font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif;
        }}
        .google-map-float summary {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 12px;
            cursor: pointer;
            list-style: none;
            color: #202124;
            font-size: 15px;
            font-weight: 700;
            background: #ffffff;
        }}
        .google-map-float summary::-webkit-details-marker {{
            display: none;
        }}
        .google-map-float summary::after {{
            content: "-";
            color: #5f6368;
            font-size: 18px;
            line-height: 1;
        }}
        .google-map-float details:not([open]) summary::after {{
            content: "+";
        }}
        .google-map-route {{
            padding: 0 12px 10px;
            color: #4a4d51;
            font-size: 13px;
            line-height: 1.35;
        }}
        .google-map-frame {{
            display: block;
            width: 100%;
            height: 220px;
            border: 0;
            background: #eef3f8;
        }}
        .google-map-actions {{
            display: flex;
            gap: 8px;
            padding: 10px 12px 12px;
        }}
        .google-map-actions a {{
            flex: 1;
            border-radius: 6px;
            padding: 8px 10px;
            text-align: center;
            text-decoration: none;
            font-size: 13px;
            font-weight: 700;
            color: #ffffff;
            background: #1a73e8;
        }}
        .google-map-actions a.secondary {{
            color: #1a73e8;
            border: 1px solid rgba(26, 115, 232, 0.35);
            background: #ffffff;
        }}
        @media (max-width: 700px) {{
            .google-map-float {{
                right: 12px;
                bottom: 12px;
                left: 12px;
                width: auto;
            }}
            .google-map-frame {{
                height: 180px;
            }}
        }}
        </style>
        <div class="google-map-float">
            <details>
                <summary>Google Maps</summary>
                <div class="google-map-route">
                    <strong>從</strong> 目前位置
                    <strong>到</strong> {escape(start_name)}
                </div>
                <iframe
                    class="google-map-frame"
                    loading="lazy"
                    referrerpolicy="no-referrer-when-downgrade"
                    src="{escape(embed_url, quote=True)}">
                </iframe>
                <div class="google-map-actions">
                    <a href="{escape(directions_url, quote=True)}" target="_blank" rel="noopener noreferrer">開啟路線</a>
                    <a class="secondary" href="{escape(search_url, quote=True)}" target="_blank" rel="noopener noreferrer">查看出發站</a>
                </div>
            </details>
        </div>
        """,
        unsafe_allow_html=True,
    )

class Station:
    def __init__(self, sid, name, coords, line_type, neighbors):
        self.sid = sid
        self.name = name
        self.display_name = name 
        self.coords = coords     
        self.line_type = line_type
        self.neighbors = neighbors

class TransitSystem:
    def __init__(self, data, fare_matrix, fare_func):
        self.stations = {}
        self.fare_matrix = fare_matrix 
        self.fare_func = fare_func     
        if not data: return 
        for sid, info in data.items():
            self.stations[sid] = Station(
                sid=sid, name=info["name"], coords=info["coords"],
                line_type=info["line_type"], neighbors=info.get("neighbors", [])
            )

    def get_station(self, sid):
        return self.stations.get(sid)

    def get_all_display_names(self):
        unique_names = set(s.display_name for s in self.stations.values())
        return sorted(list(unique_names))

    def get_sid_by_name(self, display_name):
        for sid, s in self.stations.items():
            if s.display_name == display_name:
                return sid
        return None

# ==========================================
# 邏輯函式 (尋路與雙引擎計價)
# ==========================================
def find_shortest_path(system, start_id, end_id):
    """【策略 A】BFS：尋找最少站數路徑"""
    if not start_id or not end_id: return []
    queue = deque([[start_id]])
    visited = {start_id}
    while queue:
        path = queue.popleft()
        if path[-1] == end_id: return path
        curr_st = system.get_station(path[-1])
        for neighbor in curr_st.neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])
    return []

def calculate_fare_fallback(system, path_ids):
    """內部函式：純數學公式估算 (供 Dijkstra 與輕軌備用)"""
    if not path_ids or len(path_ids) < 2: return 0
    total_fare = 0
    segment, curr_line = [path_ids[0]], system.get_station(path_ids[0]).line_type
    
    for i in range(1, len(path_ids)):
        sid, next_line = path_ids[i], system.get_station(path_ids[i]).line_type
        if next_line != curr_line:
            dist = (len(segment) - 1) * AVG_DISTANCE_PER_SEGMENT
            total_fare += system.fare_func(dist, curr_line)
            segment, curr_line = [sid], next_line
        else: segment.append(sid)
        
    if len(segment) > 1:
        dist = (len(segment) - 1) * AVG_DISTANCE_PER_SEGMENT
        total_fare += system.fare_func(dist, curr_line)
    return total_fare

def find_cheapest_path(system, start_id, end_id):
    """【策略 B】Dijkstra：尋找最省票價路徑"""
    start_st = system.get_station(start_id)
    if not start_st: return []
    pq = [(0, 1, [start_id], start_st.line_type)]
    min_costs = {(start_id, start_st.line_type): (0, 1)}

    while pq:
        curr_fare, num_stat, path, curr_line = heapq.heappop(pq)
        curr_id = path[-1]
        best = min_costs.get((curr_id, curr_line), (float('inf'), float('inf')))
        if curr_fare > best[0] or (curr_fare == best[0] and num_stat > best[1]): continue
        if curr_id == end_id: return path

        for n_id in system.get_station(curr_id).neighbors:
            new_path = path + [n_id]
            new_fare = calculate_fare_fallback(system, new_path)
            n_line = system.get_station(n_id).line_type
            
            best_neigh = min_costs.get((n_id, n_line), (float('inf'), float('inf')))
            if new_fare < best_neigh[0] or (new_fare == best_neigh[0] and len(new_path) < best_neigh[1]):
                min_costs[(n_id, n_line)] = (new_fare, len(new_path))
                heapq.heappush(pq, (new_fare, len(new_path), new_path, n_line))
    return []

def get_fare_and_details(system, path_ids):
    """雙引擎計價器：優先查矩陣，查無資料就優雅降級為數學公式"""
    if not path_ids or len(path_ids) < 2: return 0, "無需搭乘"
    start_id, end_id = path_ids[0], path_ids[-1]

    tdx_fare = system.fare_matrix.get(start_id, {}).get(end_id)

    if tdx_fare is not None and tdx_fare > 0:
        total_fare = tdx_fare
        source_tag = "官方 TDX 真實票價"
    else:
        total_fare = calculate_fare_fallback(system, path_ids)
        source_tag = "系統公式估算，涵蓋輕軌與特殊路線"

    details = []
    curr_line = system.get_station(path_ids[0]).line_type
    seg_start_name = system.get_station(path_ids[0]).name
    for i in range(1, len(path_ids)):
        st_info = system.get_station(path_ids[i])
        if st_info.line_type != curr_line:
            details.append(f"- {curr_line} 線: {seg_start_name} -> {system.get_station(path_ids[i-1]).name}")
            seg_start_name = system.get_station(path_ids[i-1]).name
            curr_line = st_info.line_type
    details.append(f"- {curr_line} 線: {seg_start_name} -> {system.get_station(path_ids[-1]).name}")
    details.append(f"\n總金額：{total_fare} 元 ({source_tag})")
    
    return total_fare, "\n".join(details)


def match_stations_locally(user_text, system):
    found_stations = []
    sorted_stations = sorted(system.stations.values(), key=lambda s: len(s.name), reverse=True)

    for st_info in sorted_stations:
        aliases = {
            st_info.name,
            re.sub(r"[\(（].*?[\)）]", "", st_info.name).strip(),
        }
        for piece in re.split(r"[/／]", st_info.name):
            aliases.add(piece.strip())

        for alias in sorted((a for a in aliases if a), key=len, reverse=True):
            if alias in user_text:
                found_stations.append((st_info.sid, user_text.find(alias), len(alias)))
                break

    if not found_stations:
        return None, None

    found_stations.sort(key=lambda x: (x[1], -x[2]))

    unique_mentions = []
    seen_positions = set()
    for sid, position, _alias_length in found_stations:
        if position in seen_positions:
            continue
        seen_positions.add(position)
        unique_mentions.append((sid, position))

    if len(unique_mentions) < 2:
        return None, None

    return unique_mentions[0][0], unique_mentions[-1][0]


def get_stations_from_ai(user_text, system):
    if not user_text.strip():
        return None, None, "請輸入出發站與終點站，例如：從左營到美麗島。"

    station_info = ", ".join([f"{s.name}({s.sid})" for s in system.stations.values()])
    prompt = (
        "你是一個捷運站名解析器。"
        "請只輸出 JSON，不要加說明文字，格式為 "
        '{"start_id":"...","end_id":"..."}。'
        f"站點列表：[{station_info}]。"
        f"使用者輸入：{user_text}"
    )

    response = None
    cloud_error = ""
    client, client_error = get_gemini_client()

    if client:
        model_candidates = [
            "gemini-3-flash-preview",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
        ]

        for model_name in model_candidates:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                break
            except Exception as e:
                cloud_error = str(e)
                continue

    if response and response.text:
        try:
            match = re.search(r"\{.*\}", response.text.strip(), re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                s_id, e_id = data.get("start_id"), data.get("end_id")
                if s_id in system.stations and e_id in system.stations:
                    return s_id, e_id, "成功，來自 Gemini 文字解析。"
        except Exception as exc:
            cloud_error = str(exc)

    s_id, e_id = match_stations_locally(user_text, system)
    if s_id and e_id:
        if client_error:
            return s_id, e_id, f"成功，使用本地站名比對。{client_error}"
        return s_id, e_id, "成功，使用本地站名比對。"

    reason = cloud_error or client_error or "無法辨識兩個有效站名"
    return None, None, f"無法解析起訖站。請改用站名下拉選單，或輸入完整站名。原因：{reason}"

def generate_speech_audio(start_name, end_name, fare):
    text = f"已為您規劃從{start_name}到{end_name}的路徑。總票價{fare}元。"
    tts = gTTS(text=text, lang='zh-tw')
    audio_fp = BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    return audio_fp

# ==========================================
# UI 介面
# ==========================================
def run():
    try:
        st.set_page_config(page_title="智慧捷運路徑規劃系統", layout="wide")
    except Exception:
        pass

    apply_app_theme()
    render_header(
        "ROUTE PLANNER",
        "智慧捷運路徑規劃",
        "輸入自然語言、手動選站或直接點擊路網圖，快速比較最少站數與最省票價路線。",
    )

    selected_map = st.selectbox("選擇路網", list(MAP_DATABASE.keys()))
    config = MAP_DATABASE[selected_map]

    sys_data = load_json_data(config["json"])
    fare_data = load_json_data(config["fare_json"])
    mrt = TransitSystem(sys_data, fare_data, config["fare_func"])

    if not sys_data:
        st.error("地圖資料載入失敗，請確認 JSON 檔案存在且格式正確。")
        return

    render_status_strip(
        [
            ("目前路網", selected_map),
            ("站點數", f"{len(mrt.stations)}"),
            ("票價來源", "TDX + 備援公式"),
        ]
    )

    names = mrt.get_all_display_names()
    if 'start_st' not in st.session_state: st.session_state.start_st = names[0]
    if 'end_st' not in st.session_state: st.session_state.end_st = names[0]
    if 'next_click_is_start' not in st.session_state: st.session_state.next_click_is_start = True
    if 'last_click' not in st.session_state: st.session_state.last_click = None
    if 'route_result' not in st.session_state: st.session_state.route_result = None

    col_ui, col_map = st.columns([1, 2.35])

    with col_ui:
        st.subheader("AI 文字助理")
        
        with st.form(key="ai_form"):
            user_input = st.text_input("輸入行程", placeholder="例如：從左營到美麗島")
            submit_btn = st.form_submit_button("解析起訖站", use_container_width=True)
            
        if submit_btn:
            with st.spinner("正在解析站名..."):
                sid_s, sid_e, msg = get_stations_from_ai(user_input, mrt)
                
                if sid_s and sid_e:
                    st.session_state.start_st = mrt.get_station(sid_s).display_name
                    st.session_state.end_st = mrt.get_station(sid_e).display_name
                    st.success(msg)
                else:
                    st.error(msg)

        st.divider()
        st.subheader("路線條件")
        idx_s = names.index(st.session_state.start_st) if st.session_state.start_st in names else 0
        idx_e = names.index(st.session_state.end_st) if st.session_state.end_st in names else 0

        sel_start = st.selectbox("出發站", names, index=idx_s)
        sel_end = st.selectbox("終點站", names, index=idx_e)

        st.session_state.start_st = sel_start
        st.session_state.end_st = sel_end

        search_mode = st.radio("路徑規劃策略", ["最少站數 (BFS)", "最省票價 (Dijkstra)"], horizontal=True)

        if st.button("查詢路徑", type="primary", use_container_width=True):
            if sel_start == sel_end:
                st.warning("起點與終點相同，請選擇不同站點。")
            else:
                id_s, id_e = mrt.get_sid_by_name(sel_start), mrt.get_sid_by_name(sel_end)
                
                if "最少站數" in search_mode:
                    path = find_shortest_path(mrt, id_s, id_e)
                else:
                    path = find_cheapest_path(mrt, id_s, id_e)
                    
                if path:
                    fare, details = get_fare_and_details(mrt, path)
                    st.session_state.route_result = {
                        "map": selected_map,
                        "start": sel_start,
                        "end": sel_end,
                        "strategy": search_mode,
                        "path": path,
                        "fare": fare,
                        "details": details,
                    }

                    try:
                        audio = generate_speech_audio(sel_start, sel_end, fare)
                        st.audio(audio, format="audio/mp3", autoplay=True)
                    except Exception:
                        st.caption("語音播報暫時無法產生，路線查詢結果不受影響。")
                else:
                    st.error("找不到相連路徑，請改用另一組站點或切換路網。")

        route_result = st.session_state.route_result
        if (
            route_result
            and route_result["map"] == selected_map
            and route_result["start"] == sel_start
            and route_result["end"] == sel_end
        ):
            path_display = " -> ".join(
                [f"[{mrt.get_station(i).line_type}] {mrt.get_station(i).name}" for i in route_result["path"]]
            )
            st.markdown(
                f"""
                <div class="route-summary">
                    <div class="route-summary-title">查詢結果：{route_result["fare"]} 元，{len(route_result["path"])} 站</div>
                    <div class="route-summary-body">{escape(route_result["strategy"])} · {escape(route_result["start"])} 到 {escape(route_result["end"])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.text_area("路線分段與票價", route_result["details"], height=130)
            st.info(f"建議路徑：\n{path_display}")

    with col_map:
        st.subheader("互動地圖")
        if st.session_state.next_click_is_start:
            st.info("請在地圖點擊出發站。")
        else:
            st.warning("請在地圖點擊終點站。")

        try:
            img = Image.open(config["img"])
            w_orig, h_orig = img.size

            TARGET_WIDTH = 520
            scale_ratio = TARGET_WIDTH / w_orig  

            click = streamlit_image_coordinates(
                img, 
                width=TARGET_WIDTH, 
                key="map_click"
            )

            if click:
                cx, cy = click["x"], click["y"]
                if st.session_state.last_click != (cx, cy):
                    st.session_state.last_click = (cx, cy)
                    closest, min_dist = None, float('inf')

                    for s in mrt.stations.values():
                        scaled_x = s.coords[0] * scale_ratio
                        scaled_y = s.coords[1] * scale_ratio

                        dist = math.sqrt((cx - scaled_x)**2 + (cy - scaled_y)**2)
                        if dist < min_dist: 
                            min_dist, closest = dist, s

                    threshold = 130 * scale_ratio

                    if closest and min_dist < threshold:
                        if st.session_state.next_click_is_start:
                            st.session_state.start_st = closest.display_name
                            st.session_state.next_click_is_start = False
                        else:
                            st.session_state.end_st = closest.display_name
                            st.session_state.next_click_is_start = True
                        st.rerun()
        except Exception as e:
            st.error(f"地圖元件錯誤: {e}")

    render_google_maps_widget(st.session_state.start_st, config)

if __name__ == "__main__":
    run()
