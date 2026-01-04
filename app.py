import streamlit as st
import graphviz
from supabase import create_client, Client

# --- CẤU HÌNH KẾT NỐI (Lấy từ Secrets của Streamlit Cloud) ---
try:
    # Thử lấy từ Secrets (khi chạy trên Web)
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except:
    # Dự phòng
    st.error("Chưa cấu hình Secrets!")

# Kết nối đến Supabase
@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

# --- GIAO DIỆN WEB ---
st.title("🌳 Gia Phả Dòng Họ Lê")

# Lấy dữ liệu từ Database về
response = supabase.table("members").select("*").execute()
members = response.data

if not members:
    st.warning("Chưa có dữ liệu thành viên nào!")
else:
    # --- VẼ CÂY GIA PHẢ ---
    # Tạo đối tượng biểu đồ
    graph = graphviz.Digraph()
    graph.attr(rankdir='TB') # TB = Top to Bottom (Trên xuống dưới)
    graph.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue')

    # Duyệt qua danh sách thành viên để tạo Nút (Node) và Đường nối (Edge)
    for member in members:
        # 1. Tạo hình cho thành viên này
        # Nội dung hiển thị: Tên + (Đời thứ mấy)
        label = f"{member['full_name']}\n(Đời {member['generation']})"
        
        # Tô màu khác cho các cụ tổ (Đời 1-10) để nổi bật
        color = 'gold' if member['generation'] and member['generation'] < 15 else 'lightblue'
        
        graph.node(str(member['id']), label=label, fillcolor=color)

        # 2. Nếu có cha, vẽ đường nối từ Cha -> Con
        if member['father_id']:
            graph.edge(str(member['father_id']), str(member['id']))

    # Hiển thị lên màn hình
    st.graphviz_chart(graph, use_container_width=True)

    # --- BẢNG TRA CỨU BÊN DƯỚI ---
    st.divider()
    st.subheader("Tra cứu thành viên")
    search_name = st.text_input("Nhập tên cần tìm:")
    if search_name:
        # Lọc danh sách (Python list filtering)
        results = [m for m in members if search_name.lower() in m['full_name'].lower()]
        st.dataframe(results)
    else:
        with st.expander("Xem danh sách đầy đủ"):
            st.dataframe(members)
