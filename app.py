import streamlit as st
import pandas as pd
import os

# --- FILE SETUP (Data Bachane ke liye) ---
DATA_FILE = "anything_ai_leads.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["Name", "Handle", "Followers", "Bio", "Link", "CAP Score", "Status", "Niche"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# --- KEYWORD LIBRARY ---
KEYWORD_LIB = {
    "AI Tools": ["AI workflow", "ChatGPT tutorials", "AI tools reviewer", "Generative AI"],
    "No-Code": ["No code builder", "Build in public", "SaaS builder", "Bubble tutorials"],
    "Productivity": ["Workflow optimization", "Notion creator", "Systems thinking"],
    "Monetization": ["Affiliate marketer", "Creator course", "Digital tools reviewer"]
}

# --- IMPROVED CAP LOGIC ---
def calculate_cap(bio, followers, has_link, eng_grade):
    score = 0
    # 1. Relevance (40 pts)
    keywords = ['ai', 'nocode', 'saas', 'builder', 'productivity', 'tech', 'automation']
    match_count = sum(1 for word in keywords if word in bio.lower())
    score += (min(match_count / 3, 1.0) * 40)
    
    # 2. Monetization (20 pts)
    score += 20 if has_link else 0
    
    # 3. Follower Tier (20 pts)
    if 10000 <= followers <= 50000: score += 20
    elif 50001 <= followers <= 100000: score += 15
    else: score += 5

    # 4. Engagement Grade (20 pts) - New manual factor
    grade_map = {"A (High)": 20, "B (Medium)": 10, "C (Low)": 0}
    score += grade_map.get(eng_grade, 0)
    
    return round(score, 2)

# --- UI SETUP ---
st.set_page_config(page_title="Anything AI - Pro CRM", layout="wide")
st.title("🛡️ Anything AI: Pro Outreach Engine")

df = load_data()

tab1, tab2, tab3, tab4 = st.tabs(["🔍 Smart Discovery", "📥 Add & Score", "📈 Pipeline Tracker", "📝 DM Templates"])

# TAB 1: SMART DISCOVERY
with tab1:
    st.header("Search Keyword Generator")
    category = st.selectbox("Select Target Category", list(KEYWORD_LIB.keys()))
    platform = st.radio("Target Platform", ["Instagram", "LinkedIn"])
    
    selected_keywords = KEYWORD_LIB[category]
    st.write("Use these keywords for best results:")
    for kw in selected_keywords:
        dork = f'site:{platform.lower()}.com "{kw}" "10k..100k followers" "USA"'
        st.code(dork, language="bash")

# TAB 2: ADD & SCORE
with tab2:
    st.header("Lead Vetting")
    with st.form("pro_add_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Creator Name")
            handle = st.text_input("Profile Link/Handle")
            fols = st.number_input("Followers", min_value=0)
            niche = st.selectbox("Niche", ["AI", "Tech", "Productivity", "SaaS"])
        with c2:
            bio_text = st.text_area("Bio")
            link_exists = st.checkbox("Monetization Link in Bio?")
            egrade = st.select_slider("Engagement Quality", options=["C (Low)", "B (Medium)", "A (High)"])
        
        if st.form_submit_button("Analyze & Save Lead"):
            score = calculate_cap(bio_text, fols, link_exists, egrade)
            new_row = pd.DataFrame([{
                "Name": name, "Handle": handle, "Followers": fols, "Bio": bio_text,
                "Link": "Yes" if link_exists else "No", "CAP Score": score,
                "Status": "Draft", "Niche": niche
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.success(f"Lead saved with CAP Score: {score}")

# TAB 3: PIPELINE TRACKER
with tab3:
    st.header("Campaign Progress")
    # Stats logic
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Total Leads", len(df))
    col_b.metric("Approved & Posted", len(df[df['Status'] == '✅ Posted']))
    col_c.metric("Target Remaining", max(50 - len(df[df['Status'] == '✅ Posted']), 0))
    
    # Editable Table
    edited_df = st.data_editor(
        df,
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Status",
                options=["Draft", "📩 Sent", "💬 Replied", "📝 Applied", "✅ Posted"],
                required=True,
            ),
            "Handle": st.column_config.LinkColumn("Profile Link")
        },
        disabled=["CAP Score"],
        hide_index=True,
    )
    if st.button("Save Changes"):
        save_data(edited_df)
        st.rerun()

# TAB 4: DM TEMPLATES
with tab4:
    st.header("High-Conversion Scripts")
    t_niche = st.selectbox("Choose Template Niche", ["AI Tools", "No-Code", "Productivity"])
    
    templates = {
        "AI Tools": "Hey [Name], love your recent video on [Topic]. We're onboarding US tech creators for Anything AI—it lets your audience build apps with just text. Since you review AI tools, the 100% revenue share hook would be massive for you. Interested?",
        "No-Code": "Hi [Name], your build-in-public journey is inspiring. Anything AI is looking for partners to showcase how fast mobile apps can be built now. 100% revenue for you in month 1. Worth a 2-min chat?",
        "Productivity": "Hey [Name], your productivity stacks are solid. We've got a tool that turns those workflows into actual apps. We're offering a premium partnership (100% rev share). Would love to share details!"
    }
    st.info(templates[t_niche])
