import streamlit as st
import pandas as pd
import os

# --- CONFIGURATION ---
DATA_FILE = "anything_ai_leads.csv"
TARGET_GOAL = 50
ELITE_THRESHOLD = 80

# --- DATA PERSISTENCE ---
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=[
        "Name", "Handle", "Followers", "Bio", "Link", 
        "CAP Score", "Status", "Niche", "Personalized_Hook"
    ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# --- CORE LOGIC: CAP SCORING SYSTEM ---
def calculate_cap(bio, followers, has_link, eng_grade):
    score = 0
    # 1. Relevance (40%)
    keywords = ['ai', 'nocode', 'saas', 'builder', 'productivity', 'tech', 'automation', 'app', 'fitness']
    match_count = sum(1 for word in keywords if word in bio.lower())
    score += (min(match_count / 3, 1.0) * 40)
    
    # 2. Monetization Intent (20%)
    score += 20 if has_link else 0
    
    # 3. Follower Sweet Spot (20%) - 10k to 50k is Gold
    if 10000 <= followers <= 50000: score += 20
    elif 50001 <= followers <= 100000: score += 15
    else: score += 5

    # 4. Engagement Grade (20%)
    grade_map = {"A (High)": 20, "B (Medium)": 10, "C (Low)": 0}
    score += grade_map.get(eng_grade, 0)
    
    return round(score, 2)

# --- UI INITIALIZATION ---
st.set_page_config(page_title="Anything AI - Creator CRM PRO", layout="wide")
st.title("🛡️ Anything AI: Elite Outreach Engine v4.0")

df = load_data()

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Discovery (Dorks)", 
    "📥 Add & Vette", 
    "📈 Elite Pipeline", 
    "📝 Playbook & DMs"
])

# --- TAB 1: SMART DISCOVERY ---
with tab1:
    st.header("Lead Sourcing (Google Dorks)")
    KEYWORD_LIB = {
        "AI & Tech": ["AI tools reviewer", "ChatGPT tutorials", "AI workflow", "Generative AI"],
        "Fitness Tech": ["Fitness AI", "Biohacking gadgets", "Wearable tech reviewer", "Smart gym"],
        "Productivity": ["Notion creator", "Systems thinking", "Workflow automation", "No-code builder"],
        "Lifestyle": ["Recipe app", "Meal planner", "Parenting organization", "Budgeting tools"]
    }
    
    cat = st.selectbox("Target Niche", list(KEYWORD_LIB.keys()))
    plat = st.radio("Platform", ["Instagram", "LinkedIn"])
    
    st.write("Copy-paste these into Google Search to find 10k-100k creators:")
    for kw in KEYWORD_LIB[cat]:
        dork = f'site:{plat.lower()}.com "{kw}" "10k..100k followers" "USA" -inurl:posts'
        st.code(dork, language="bash")

# --- TAB 2: ADD & SCORE ---
with tab2:
    st.header("Creator Vetting & Scoring")
    with st.form("vetting_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Creator Name")
            handle = st.text_input("Handle / Profile URL")
            fols = st.number_input("Followers", min_value=0, step=1000)
            niche = st.selectbox("Niche", ["AI", "Fitness", "Tech", "Productivity", "Lifestyle"])
        with c2:
            bio_text = st.text_area("Profile Bio")
            has_link = st.checkbox("Monetization Link (Stan.store/Gumroad/Newsletter)?")
            egrade = st.select_slider("Engagement Quality", options=["C (Low)", "B (Medium)", "A (High)"])
        
        hook_ref = st.text_input("Personalized Ref (e.g., 'your budget meal preps')", help="Used in Message 1")
        
        if st.form_submit_button("Analyze & Save Elite Lead"):
            if name and handle:
                score = calculate_cap(bio_text, fols, has_link, egrade)
                new_lead = pd.DataFrame([{
                    "Name": name, "Handle": handle, "Followers": fols, "Bio": bio_text,
                    "Link": "Yes" if has_link else "No", "CAP Score": score,
                    "Status": "Draft", "Niche": niche, "Personalized_Hook": hook_ref
                }])
                df = pd.concat([df, new_lead], ignore_index=True)
                save_data(df)
                
                if score >= ELITE_THRESHOLD:
                    st.success(f"🔥 ELITE LEAD DETECTED! Score: {score}")
                    st.balloons()
                else:
                    st.warning(f"⚠️ Score: {score}. This lead is hidden from the main pipeline (Threshold: {ELITE_THRESHOLD}).")
            else:
                st.error("Please enter Name and Handle.")

# --- TAB 3: PIPELINE TRACKER ---
with tab3:
    st.header("Campaign Pipeline (Elite Only)")
    
    # Summary Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Scanned", len(df))
    elite_df = df[df['CAP Score'] >= ELITE_THRESHOLD].copy()
    m2.metric("Elite Leads (>80)", len(elite_df))
    posted_count = len(df[df['Status'] == '✅ Posted'])
    m3.metric("Goal: ₹5000", f"{posted_count} / {TARGET_GOAL} Posts")
    
    st.divider()
    
    view_mode = st.radio("Filter View", ["Elite Active", "Claimed by others", "All History"], horizontal=True)
    
    if view_mode == "Elite Active":
        display_df = elite_df[elite_df['Status'] != "🔴 Claimed"]
    elif view_mode == "Claimed by others":
        display_df = df[df['Status'] == "🔴 Claimed"]
    else:
        display_df = df

    if not display_df.empty:
        updated_df = st.data_editor(
            display_df,
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Draft", "⏳ Pending Approval", "✅ Approved", "📩 Msg 1 Sent", "💬 Replied", "📝 Applied", "✅ Posted", "🔴 Claimed"],
                    required=True
                ),
                "Handle": st.column_config.LinkColumn("Profile")
            },
            disabled=["CAP Score", "Name", "Bio", "Followers"],
            hide_index=True,
            key="editor_v4"
        )
        
        if st.button("Sync Changes to Database"):
            # Update main dataframe with edits
            for index, row in updated_df.iterrows():
                df.loc[df['Handle'] == row['Handle'], 'Status'] = row['Status']
                df.loc[df['Handle'] == row['Handle'], 'Personalized_Hook'] = row['Personalized_Hook']
            save_data(df)
            st.success("Database Synced!")
            st.rerun()
    else:
        st.info("No leads matching this view. Go to 'Add & Score' to hunt!")

# --- TAB 4: PLAYBOOK & DM STRATEGY ---
with tab4:
    st.header("The Anything AI Outreach Playbook")
    n_choice = st.selectbox("Select Niche for Script", ["AI/Tech", "Fitness", "Productivity", "Food/Lifestyle"])
    
    hooks = {
        "AI/Tech": "AI tool tutorials",
        "Fitness": "home workout challenges",
        "Productivity": "study tip series",
        "Food/Lifestyle": "budget meal prep videos"
    }

    st.subheader("Phase 1: Open the Door (Msg 1)")
    st.code(f"Hey [Name]! Been following your {hooks[n_choice]} for a while. Quick question: have you ever thought about turning your knowledge into an app for your audience? There's a creator program I think you'd be a great fit for. Happy to share more if you're interested.", language="text")
    
    st.subheader("Phase 2: The Pitch (Msg 2 - Only after they reply)")
    st.info("Anything.com is an AI app builder. 1.5M users. Invite-only program: 100% rev share in month 1, 50% for a year. Want the application link?")

    with st.expander("Common Objections (Use for Message 2/3)"):
        st.write("**What is Anything?** -> 1.5M people use it, real mobile/web apps with databases.")
        st.write("**How much can I make?** -> 100% first month, 50% for a year. Check the calculator on the app page.")
        st.write("**Is it a scam?** -> $100M+ valuation, backed by real investors. Check Anything.com.")
