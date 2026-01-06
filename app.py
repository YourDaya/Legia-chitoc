import streamlit as st
import graphviz
import pandas as pd
from supabase import create_client
import plotly.express as px

# --- 1. KẾT NỐI SUPABASE ---
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except:
    st.error("Chưa cấu hình Secrets!")
    st.stop()

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

# --- 2. CẤU HÌNH GIAO DIỆN (DASHBOARD STYLE) ---
st.set_page_config(page_title="Dashboard Lê Gia", layout="wide", page_icon="⛩️")

# CSS: Biến giao diện thành Dashboard phẳng, hiện đại
st.markdown("""
<style>
    /* Nền tổng thể màu xám nhạt công nghiệp */
    .stApp { background-color: #f1f5f9; }
    
    /* Style cho các Card số liệu (KPI) */
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 15px 20px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetricLabel"] { font-weight: bold; color: #64748b; }
    div[data-testid="stMetricValue"] { color: #8B0000; font-family: 'Arial', sans-serif; }

    /* Tiêu đề chính */
    h1 { color: #1e293b; font-family: 'Segoe UI', sans-serif; font-weight: 800; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: white;
        border-radius: 5px 5px 0 0;
        padding: 0 20px;
        border: 1px solid #e2e8f0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #fff;
        border-bottom: 2px solid #8B0000;
        color: #8B0000 !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. HÀM XỬ LÝ DỮ LIỆU ---
def format_lifespan(dob, dod):
    if not dob and not dod: return "Chưa cập nhật"
    start = dob if dob else "?"
    if dod: return f"{start} - {dod}"
    else: return f"{start} - Nay"

# --- 4. POPUP CHI TIẾT (Giữ lại tính năng bạn thích) ---
@st.dialog("HỒ SƠ NHÂN SỰ", width="large")
def show_popup(member_id, all_members):
    member = next((m for m in all_members if str(m['id']) == str(member_id)), None)
    if member:
        father_name = "Thủy tổ"
        if member['father_id']:
            father = next((m for m in all_members if m['id'] == member['father_id']), None)
            if father: father_name = father['full_name']
        
        col_img, col_info = st.columns([1, 2], gap="medium")
        with col_img:
            if member.get('avatar_url'):
                st.image(member.get('avatar_url'), use_column_width=True)
            else:
                st.info("Chưa có ảnh thẻ")
        
        with col_info:
            st.subheader(member['full_name'])
            # Badge trạng thái (Giống quản lý dự án)
            status = "Đã mất" if member.get('dod_lunar') else "Còn sống"
            color = "red" if status == "Đã mất" else "green"
            st.markdown(f":{color}[● {status}]")
            
            st.write(f"**Mã ID:** {member['id']} | **Đời thứ:** {member['generation']}")
            st.write(f"**Người quản lý (Cha):** {father_name}")
            st.write(f"**Thời gian:** {format_lifespan(member.get('dob_lunar'), member.get('dod_lunar'))}")
            
            st.divider()
            st.caption("TIỂU SỬ & GHI CHÚ")
            st.write(member.get('biography') or member.get('note') or "Chưa có dữ liệu")

# --- 5. LOGIC CHÍNH ---
response = supabase.table("members").select("*").execute()
members = response.data
df = pd.DataFrame(members) # Chuyển sang Pandas để xử lý dạng bảng dễ hơn

# --- XỬ LÝ CLICK TỪ CÂY ---
if "id" in st.query_params:
    show_popup(st.query_params["id"], members)

# --- 6. GIAO DIỆN DASHBOARD ---

# Sidebar: Bộ lọc (Giống menu trái của phần mềm)
with st.sidebar:
    st.image("https://img.icons8.com/color/96/family-tree.png", width=80)
    st.title("QUẢN LÝ GIA PHẢ")
    st.caption("Phiên bản v2.0 - Dashboard Style")
    st.divider()
    
    st.header("🔍 Bộ lọc dữ liệu")
    filter_gen = st.multiselect("Chọn Đời (Thế hệ):", options=sorted(list(set(m['generation'] for m in members))), default=[])
    search_text = st.text_input("Tìm kiếm thành viên:", placeholder="Nhập tên...")

# HEADER: KPI CARDS (Thông số tổng quan)
st.title("LÊ GIA - DASHBOARD TỔNG QUAN")
st.write("")

# Tính toán số liệu
total_members = len(members)
total_gens = max(m['generation'] for m in members) if members else 0
living_count = len([m for m in members if not m.get('dod_lunar')])
deceased_count = total_members - living_count

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Tổng Thành Viên", f"{total_members} người", border=True)
kpi2.metric("Số Thế Hệ", f"{total_gens} đời", border=True)
kpi3.metric("Còn Sống", f"{living_count} người", "🟢 Active", border=True)
kpi4.metric("Đã Tạ Thế", f"{deceased_count} người", "Inverse", border=True)

st.write("")
st.write("")

# BODY: TABS CHỨC NĂNG
tab_tree, tab_list, tab_chart = st.tabs(["🌳 SƠ ĐỒ CÂY", "🗂 DANH SÁCH (GRID)", "📊 THỐNG KÊ"])

# --- TAB 1: SƠ ĐỒ CÂY (Giữ nguyên cái cũ nhưng làm gọn) ---
with tab_tree:
    if members:
        graph = graphviz.Digraph(format='svg')
        graph.attr(rankdir='TB', splines='ortho', nodesep='0.2', ranksep='0.6')
        graph.attr('node', shape='rect', style='filled,rounded', fontname='Arial', fontsize='11', penwidth='0')
        graph.attr('edge', color='#cbd5e1', arrowsize='0.6', penwidth='1.2') # Màu xám nhạt hiện đại

        for member in members:
            # Màu sắc theo phong cách Flat Design
            gen = member['generation']
            fill_color = '#eff6ff' # Xanh nhạt mặc định
            font_color = '#1e293b'
            
            # Đổi màu các đời đầu để nổi bật
            if gen <= 17: fill_color = '#3b82f6'; font_color = 'white' # Xanh dương đậm
            elif gen == 18: fill_color = '#f59e0b'; font_color = 'white' # Vàng cam
            elif gen == 19: fill_color = '#10b981'; font_color = 'white' # Xanh lá
            
            node_url = f"?id={member['id']}"
            label = f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0">
                <TR><TD><B>{member['full_name']}</B></TD></TR>
                <TR><TD><FONT POINT-SIZE="9" COLOR="{font_color}">Đời {gen}</FONT></TD></TR>
            </TABLE>>'''

            graph.node(str(member['id']), label=label, fillcolor=fill_color, fontcolor=font_color, URL=node_url, target="_self")
            if member['father_id']:
                graph.edge(str(member['father_id']), str(member['id']))

        st.graphviz_chart(graph, use_container_width=True)

# --- TAB 2: DANH SÁCH DẠNG BẢNG (Giống AppSheet/Excel) ---
with tab_list:
    # Lọc dữ liệu theo Sidebar
    filtered_members = members
    if filter_gen:
        filtered_members = [m for m in filtered_members if m['generation'] in filter_gen]
    if search_text:
        filtered_members = [m for m in filtered_members if search_text.lower() in m['full_name'].lower()]

    # Chuẩn bị Dataframe hiển thị
    df_show = pd.DataFrame(filtered_members)
    
    # Tạo cột "Trạng thái" để hiển thị màu mè
    if not df_show.empty:
        df_show['Trạng thái'] = df_show['dod_lunar'].apply(lambda x: "Đã mất" if x else "Còn sống")
        
        # Cấu hình bảng hiển thị chuyên nghiệp
        st.dataframe(
            df_show,
            column_order=("id", "avatar_url", "full_name", "generation", "Trạng thái", "dob_lunar", "dod_lunar"),
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small"),
                "avatar_url": st.column_config.ImageColumn("Ảnh", width="small"),
                "full_name": st.column_config.TextColumn("Họ và Tên", width="medium"),
                "generation": st.column_config.NumberColumn("Đời", format="%d"),
                "Trạng thái": st.column_config.TextColumn(
                    "Trạng thái",
                    width="small",
                    validate="^(Còn sống|Đã mất)$" # Dùng để tô màu badge (Streamlit tự detect)
                ),
                "dob_lunar": "Năm sinh",
                "dod_lunar": "Năm mất"
            },
            use_container_width=True,
            hide_index=True,
            height=500
        )
    else:
        st.warning("Không tìm thấy dữ liệu phù hợp.")

# --- TAB 3: BIỂU ĐỒ THỐNG KÊ (Visualized) ---
with tab_chart:
    col_chart1, col_chart2 = st.columns(2)
    
    if not df.empty:
        with col_chart1:
            st.subheader("👥 Phân bố thành viên theo Đời")
            # Đếm số người mỗi đời
            gen_counts = df['generation'].value_counts().sort_index().reset_index()
            gen_counts.columns = ['Đời', 'Số lượng']
            
            fig_bar = px.bar(gen_counts, x='Đời', y='Số lượng', 
                             text='Số lượng', color='Số lượng',
                             color_continuous_scale='Blues')
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col_chart2:
            st.subheader("🧬 Tỷ lệ Sinh/Tử")
            df['Status'] = df['dod_lunar'].apply(lambda x: "Đã mất" if x else "Còn sống")
            status_counts = df['Status'].value_counts().reset_index()
            status_counts.columns = ['Trạng thái', 'Số lượng']
            
            fig_pie = px.pie(status_counts, names='Trạng thái', values='Số lượng', 
                             color='Trạng thái',
                             color_discrete_map={'Còn sống':'#10b981', 'Đã mất':'#ef4444'})
            st.plotly_chart(fig_pie, use_container_width=True)
