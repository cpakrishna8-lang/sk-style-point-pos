import streamlit as st
import pandas as pd
from datetime import datetime

# ১. অ্যাপ কনফিগারেশন ও সিকিউরিটি
st.set_page_config(page_title="SK Style Point - Pro POS", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 SK Style Point Login")
    user_pass = st.text_input("পাসওয়ার্ড দিন", type="password")
    if st.button("Login"):
        if user_pass == "1234":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("ভুল পাসওয়ার্ড!")
    st.stop()

# ২. ডাটাবেজ সেটআপ
if 'services' not in st.session_state:
    st.session_state.services = {"চুল কাটা": 200, "শেভ": 100, "ফেসিয়াল": 500}
if 'products' not in st.session_state:
    st.session_state.products = {"শ্যাম্পু": [450, 10], "হেয়ার জেল": [250, 5]}
if 'staff_list' not in st.session_state:
    st.session_state.staff_list = ["কামাল", "জামাল", "রহিম"]
if 'sales' not in st.session_state:
    st.session_state.sales = pd.DataFrame(columns=["তারিখ", "কাস্টমার", "সার্ভিস", "স্টাফ", "মোট", "পেইড", "বাকি", "কমিশন"])
if 'expense' not in st.session_state:
    st.session_state.expense = pd.DataFrame(columns=["তারিখ", "বিবরণ", "পরিমাণ"])

# ৩. মেইন অ্যাপ ইন্টারফেস
st.sidebar.title("SK Style Point")
if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🛒 ক্যাশ মেমো", "📦 স্টক লিস্ট", "💸 খরচ", "👥 স্টাফ", "📊 রিপোর্ট"])

# --- ট্যাব ১: বিলিং ও প্রিন্ট ---
with tab1:
    with st.form("billing_form", clear_on_submit=True):
        c_name = st.text_input("কাস্টমারের নাম", "Guest")
        s_staff = st.selectbox("স্টাফ", st.session_state.staff_list)
        sel_s = st.multiselect("সার্ভিস", list(st.session_state.services.keys()))
        sel_p = st.multiselect("প্রোডাক্ট", list(st.session_state.products.keys()))
        col1, col2, col3 = st.columns(3)
        paid = col1.number_input("জমা (৳)", min_value=0)
        disc = col2.number_input("ডিসকাউন্ট (৳)", min_value=0)
        comm_p = col3.slider("কমিশন (%)", 0, 100, 20)
        submit = st.form_submit_button("ইনভয়েস তৈরি করুন")

    if submit:
        total_s = sum(st.session_state.services[s] for s in sel_s)
        total_p = sum(st.session_state.products[p][0] for p in sel_p)
        net_total = (total_s + total_p) - disc
        due = net_total - paid
        comm_amt = (total_s * comm_p) / 100
        
        # স্টক কমানো
        for p in sel_p: st.session_state.products[p][1] -= 1
        
        # ডাটা সেভ
        new_row = {"তারিখ": datetime.now().strftime("%d-%m-%Y %I:%M %p"), "কাস্টমার": c_name, "সার্ভিস": f"{sel_s}, {sel_p}", "স্টাফ": s_staff, "মোট": net_total, "পেইড": paid, "বাকি": due, "কমিশন": comm_amt}
        st.session_state.sales = pd.concat([st.session_state.sales, pd.DataFrame([new_row])], ignore_index=True)
        
        # প্রিন্টযোগ্য ইনভয়েস
        st.markdown(f"""
        <div style="border:1px solid #000; padding:15px; background:white; color:black;">
            <h2 style="text-align:center;">SK Style Point</h2>
            <p>কাস্টমার: {c_name} | তারিখ: {new_row['তারিখ']}</p>
            <hr>
            <p>মোট বিল: {total_s + total_p} ৳ | ডিসকাউন্ট: {disc} ৳</p>
            <h3>পরিশোধ্য: {net_total} ৳</h3>
            <p>জমা: {paid} ৳ | বাকি: {due} ৳</p>
        </div>
        <br><button onclick="window.print()" style="background:#4CAF50; color:white; padding:10px; border:none; cursor:pointer;">🖨️ প্রিন্ট / PDF সেভ</button>
        """, unsafe_content_html=True)

# --- ট্যাব ২: স্টক ---
with tab2:
    st.subheader("📦 ইনভেন্টরি")
    st.write(st.session_state.products)

# --- ট্যাব ৩: খরচ ---
with tab3:
    with st.form("exp"):
        e_d = st.text_input("বিবরণ")
        e_a = st.number_input("পরিমাণ", min_value=0)
        if st.form_submit_button("সেভ"):
            st.session_state.expense = pd.concat([st.session_state.expense, pd.DataFrame([{"তারিখ": datetime.now().strftime("%d-%m-%Y"), "বিবরণ": e_d, "পরিমাণ": e_a}])], ignore_index=True)
    st.table(st.session_state.expense)

# --- ট্যাব ৫: ফাইনাল রিপোর্ট ---
with tab5:
    s_df = st.session_state.sales
    e_df = st.session_state.expense
    net_profit = s_df["পেইড"].sum() - (e_df["পরিমাণ"].sum() + s_df["কমিশন"].sum())
    
    c1, c2, c3 = st.columns(3)
    c1.metric("মোট ক্যাশ", f"{s_df['পেইড'].sum()} ৳")
    c2.metric("মোট বাকি", f"{s_df['বাকি'].sum()} ৳")
    c3.metric("নিট লাভ", f"{net_profit} ৳")
    st.dataframe(s_df)