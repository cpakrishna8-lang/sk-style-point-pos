import streamlit as st
import pandas as pd
from datetime import datetime

# ১. অ্যাপের প্রাথমিক সেটিংস
st.set_page_config(page_title="SK Style Point - Pro POS", layout="wide")

# ২. স্টাইলিস্ট সিএসএস (ডিজাইন সুন্দর করার জন্য)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .invoice-box { border: 2px solid #000; padding: 20px; background-color: white; color: black; border-radius: 10px; }
    </style>
    """, unsafe_content_html=True)

# ৩. লগইন সিস্টেম (Security)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 SK Style Point - Admin Login")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        password = st.text_input("পাসওয়ার্ড লিখুন", type="password")
        if st.button("প্রবেশ করুন"):
            if password == "1234":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("ভুল পাসওয়ার্ড! সঠিক পাসওয়ার্ড দিন।")
    st.stop()

# ৪. ডাটা স্টোরেজ (সার্ভিস, প্রোডাক্ট ও স্টাফ লিস্ট)
if 'services' not in st.session_state:
    st.session_state.services = {"চুল কাটা": 200, "শেভ": 100, "ফেসিয়াল": 500}
if 'products' not in st.session_state:
    st.session_state.products = {"শ্যাম্পু": [450, 10], "হেয়ার জেল": [250, 5]}
if 'staff_list' not in st.session_state:
    st.session_state.staff_list = ["কামাল", "জামাল", "রহিম"]
if 'sales_history' not in st.session_state:
    st.session_state.sales_history = pd.DataFrame(columns=["তারিখ", "কাস্টমার", "বিবরণ", "স্টাফ", "মোট বিল", "পেইড", "বাকি", "কমিশন"])

# ৫. সাইডবার (Admin Controls)
st.sidebar.header("⚙️ দোকান ম্যানেজমেন্ট")
admin_option = st.sidebar.selectbox("মেনু বেছে নিন", ["নতুন বিল তৈরি", "সার্ভিস/প্রোডাক্ট যোগ করুন", "স্টাফ লিস্ট", "রিপোর্ট ও ডাটা ডিলিট", "Logout"])

if admin_option == "Logout":
    st.session_state.authenticated = False
    st.rerun()

# --- সার্ভিস ও প্রোডাক্ট যোগ করার সেকশন ---
if admin_option == "সার্ভিস/প্রোডাক্ট যোগ করুন":
    st.header("🛠 নতুন আইটেম যোগ করুন")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("নতুন সার্ভিস")
        s_name = st.text_input("সার্ভিসের নাম")
        s_price = st.number_input("সার্ভিসের দাম (৳)", min_value=0)
        if st.button("সার্ভিস সেভ করুন"):
            st.session_state.services[s_name] = s_price
            st.success(f"{s_name} যোগ হয়েছে!")

    with col2:
        st.subheader("নতুন প্রোডাক্ট")
        p_name = st.text_input("প্রোডাক্টের নাম")
        p_price = st.number_input("বিক্রয় মূল্য (৳)", min_value=0)
        p_stock = st.number_input("স্টক সংখ্যা", min_value=0)
        if st.button("প্রোডাক্ট সেভ করুন"):
            st.session_state.products[p_name] = [p_price, p_stock]
            st.success(f"{p_name} যোগ হয়েছে!")

# --- স্টাফ ম্যানেজমেন্ট ---
elif admin_option == "স্টাফ লিস্ট":
    st.header("👥 স্টাফ ম্যানেজমেন্ট")
    new_staff = st.text_input("নতুন স্টাফের নাম")
    if st.button("স্টাফ যোগ করুন"):
        st.session_state.staff_list.append(new_staff)
        st.success(f"{new_staff} লিস্টে যোগ হয়েছে!")
    st.write("বর্তমান স্টাফগণ:", ", ".join(st.session_state.staff_list))

# --- মূল ক্যাশ মেমো সেকশন ---
elif admin_option == "নতুন বিল তৈরি":
    st.header("🛒 ক্যাশ মেমো (New Sale)")
    
    with st.form("billing_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        c_name = c1.text_input("কাস্টমারের নাম", "Guest")
        s_staff = c2.selectbox("কাজটি কে করেছে?", st.session_state.staff_list)
        
        sel_s = st.multiselect("সার্ভিস বেছে নিন", list(st.session_state.services.keys()))
        sel_p = st.multiselect("প্রোডাক্ট বেছে নিন", list(st.session_state.products.keys()))
        
        c3, c4, c5 = st.columns(3)
        disc = c3.number_input("ডিসকাউন্ট (৳)", min_value=0)
        paid = c4.number_input("জমা/পেইড (৳)", min_value=0)
        comm_p = c5.slider("স্টাফ কমিশন (%)", 0, 100, 20)
        
        submit_bill = st.form_submit_button("ইনভয়েস তৈরি ও সেভ করুন")

    if submit_bill:
        t_s = sum(st.session_state.services[s] for s in sel_s)
        t_p = sum(st.session_state.products[p][0] for p in sel_p)
        gross = (t_s + t_p) - disc
        due = gross - paid
        comm_amt = (t_s * comm_p) / 100
        
        # স্টক আপডেট
        for p in sel_p: st.session_state.products[p][1] -= 1
        
        new_sale = {
            "তারিখ": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
            "কাস্টমার": c_name, "বিবরণ": f"S:{len(sel_s)}, P:{len(sel_p)}",
            "স্টাফ": s_staff, "মোট বিল": gross, "পেইড": paid, "বাকি": due, "কমিশন": comm_amt
        }
        st.session_state.sales_history = pd.concat([st.session_state.sales_history, pd.DataFrame([new_sale])], ignore_index=True)
        
        # ইনভয়েস ডিজাইন
        st.markdown(f"""
        <div class="invoice-box">
            <h2 style="text-align:center;">SK Style Point</h2>
            <p style="text-align:center;">ডিজিটাল ইনভয়েস</p>
            <hr>
            <p><b>কাস্টমার:</b> {c_name} | <b>তারিখ:</b> {new_sale['তারিখ']}</p>
            <p><b>স্টাফ:</b> {s_staff}</p>
            <hr>
            <p>সার্ভিস ও প্রোডাক্ট মোট: {t_s + t_p} ৳</p>
            <p>ডিসকাউন্ট: - {disc} ৳</p>
            <h3 style="color:blue;">পরিশোধ্য: {gross} ৳</h3>
            <p>জমা: {paid} ৳ | <b>বাকি: {due} ৳</b></p>
            <hr>
            <p style="text-align:center;">ধন্যবাদ, আবার আসবেন!</p>
        </div>
        """, unsafe_content_html=True)
        st.info("টিপস: ব্রাউজারের Print (Ctrl+P) অপশন ব্যবহার করে এটি PDF সেভ করতে পারেন।")

# --- রিপোর্ট সেকশন ---
elif admin_option == "রিপোর্ট ও ডাটা ডিলিট":
    st.header("📊 ব্যবসার রিপোর্ট")
    df = st.session_state.sales_history
    
    c1, c2, c3 = st.columns(3)
    c1.metric("মোট আয় (ক্যাশ)", f"{df['পেইড'].sum()} ৳")
    c2.metric("মোট বাকি", f"{df['বাকি'].sum()} ৳")
    c3.metric("স্টাফ কমিশন", f"{df['কমিশন'].sum()} ৳")
    
    st.subheader("লেনদেনের তালিকা")
    st.dataframe(df, use_container_width=True)
    
    if st.button("সব ডাটা ক্লিয়ার করুন (সতর্কবার্তা)"):
        st.session_state.sales_history = pd.DataFrame(columns=["তারিখ", "কাস্টমার", "বিবরণ", "স্টাফ", "মোট বিল", "পেইড", "বাকি", "কমিশন"])
        st.rerun()
