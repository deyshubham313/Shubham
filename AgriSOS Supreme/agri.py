import streamlit as st
import datetime
import pandas as pd
import os

# --- OmniDimension Voice Integration (Safe Import) ---
api_key = os.environ.get("OMNIDIM_API_KEY")
OMNI_ENABLED = False
try:
    if api_key:
        from omnidimension import Client
        client = Client(api_key)
        OMNI_ENABLED = True
    else:
        client = None
except Exception as e:
    print("OmniDimension error:", e)
    client = None
    OMNI_ENABLED = False

def dispatch_crop_alert(agent_id: int, to_number: str, crop, problem):
    if not OMNI_ENABLED or not client:
        return None
    context = {
        "crop": crop,
        "problem": problem,
        "severity": "high" if "blight" in problem.lower() else "moderate"
    }
    resp = client.call.dispatch_call(agent_id=agent_id,
                                     to_number=to_number,
                                     call_context=context)
    return resp

# --- Omnidimension Enhanced UI ---
st.set_page_config(page_title="AgriSOS Supreme", page_icon="🌱", layout="wide")
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@700&family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
    body, .main {
        background: linear-gradient(135deg, #e0ffe0 0%, #b2ff59 40%, #00c853 100%);
        background-size: 200% 200%;
        animation: omnidimension 10s ease-in-out infinite;
    }
    @keyframes omnidimension {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .stApp {
        background: rgba(255,255,255,0.92);
        border-radius: 18px;
        padding-bottom: 2em;
        font-family: 'Roboto', Arial, sans-serif;
        box-shadow: 0 0 40px 0 #b2ff59cc;
    }
    .stSidebar {
        background: rgba(255,255,255,0.85) !important;
        border-radius: 18px;
        box-shadow: 0 0 20px #b2ff59cc;
    }
    .stButton>button {
        background: linear-gradient(90deg, #00c853 0%, #b2ff59 100%);
        color: #222;
        border-radius: 25px;
        font-weight: bold;
        transition: 0.2s;
        box-shadow: 0 2px 8px #b2ff59;
        font-size: 1.1rem;
        padding: 0.5em 2em;
        font-family: 'Baloo 2', cursive;
        letter-spacing: 1px;
        border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #b2ff59 0%, #00c853 100%);
        color: #fff;
        transform: scale(1.05);
        box-shadow: 0 4px 16px #00c853;
    }
    .stTextInput>div>div>input, .stTextArea textarea {
        background: #fafffa;
        border-radius: 10px;
        border: 1.5px solid #b2ff59;
        font-size: 1.1rem;
        font-family: 'Roboto', Arial, sans-serif;
        box-shadow: 0 1px 4px #b2ff5944;
    }
    .stDataFrame, .stTable {
        background: #fafffa;
        border-radius: 10px;
        border: 1.5px solid #b2ff59;
        font-family: 'Roboto', Arial, sans-serif;
        box-shadow: 0 1px 4px #b2ff5944;
    }
    .supreme-header {
        font-size: 2.7rem;
        font-weight: 900;
        color: #008c3a;
        text-shadow: 2px 2px 8px #b2ff59;
        animation: popin 1s cubic-bezier(.68,-0.55,.27,1.55);
        letter-spacing: 1px;
        margin-bottom: 0.5em;
        font-family: 'Baloo 2', cursive;
        background: linear-gradient(90deg, #b2ff59 0%, #00c853 100%);
        border-radius: 12px;
        padding: 0.2em 0.7em;
        box-shadow: 0 2px 12px #b2ff5944;
        display: inline-block;
    }
    @keyframes popin {
        0% { transform: scale(0.7); opacity: 0; }
        80% { transform: scale(1.1); opacity: 1; }
        100% { transform: scale(1); }
    }
    .supreme-section {
        background: linear-gradient(120deg, #fafffa 60%, #e0ffe0 100%);
        border-radius: 18px;
        box-shadow: 0 2px 16px #b2ff5944;
        padding: 1.5rem 1.5rem 1rem 1.5rem;
        margin-bottom: 1.5rem;
        animation: fadein 1.2s;
        font-size: 1.1rem;
        font-family: 'Roboto', Arial, sans-serif;
    }
    @keyframes fadein {
        0% { opacity: 0; transform: translateY(30px);}
        100% { opacity: 1; transform: translateY(0);}
    }
    .emoji-bounce {
        display: inline-block;
        animation: bounce 1.2s infinite;
    }
    @keyframes bounce {
        0%, 100% { transform: translateY(0);}
        50% { transform: translateY(-10px);}
    }
    .footer {
        color: #008c3a;
        font-size: 1.1rem;
        text-align: center;
        margin-top: 2em;
        margin-bottom: 1em;
        font-family: 'Baloo 2', cursive;
        background: linear-gradient(90deg, #b2ff59 0%, #e0ffe0 100%);
        border-radius: 12px;
        padding: 0.5em 0;
        box-shadow: 0 2px 12px #b2ff5944;
    }
    .feature-badge {
        display: inline-block;
        background: #00c853;
        color: #fff;
        font-size: 0.95em;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.2em 0.7em;
        margin-left: 0.5em;
        margin-bottom: 0.2em;
        box-shadow: 0 1px 4px #b2ff5944;
        font-family: 'Baloo 2', cursive;
        letter-spacing: 1px;
    }
    /* Omnidimension voice mic button */
    .voice-mic {
        background: linear-gradient(135deg, #00c853 0%, #b2ff59 100%);
        border: none;
        border-radius: 50%;
        width: 56px;
        height: 56px;
        box-shadow: 0 2px 16px #00c85388;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0.5em auto 1em auto;
        cursor: pointer;
        transition: box-shadow 0.2s, transform 0.2s;
    }
    .voice-mic:hover {
        box-shadow: 0 4px 32px #00c853cc;
        transform: scale(1.08);
    }
    .voice-mic svg {
        width: 32px;
        height: 32px;
        fill: #fff;
    }
    </style>
""", unsafe_allow_html=True)

# --- Omnidimension Voice Assistant (browser-based, Chrome/Edge only) ---
st.markdown("""
<div style="text-align:center;">
    <button class="voice-mic" id="voice-mic-btn" title="Speak to AgriSOS" type="button">
        <svg viewBox="0 0 24 24"><path d="M12 15a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3zm5-3a1 1 0 1 0-2 0 5 5 0 0 1-10 0 1 1 0 1 0-2 0 7 7 0 0 0 6 6.92V21h2v-2.08A7 7 0 0 0 19 12z"/></svg>
    </button>
    <div id="voice-result" style="font-size:1.2em;color:#008c3a;font-family:'Baloo 2',cursive;"></div>
</div>
<script>
window.addEventListener("DOMContentLoaded", function() {
    let recognizing = false;
    let recognition;
    if ("webkitSpeechRecognition" in window) {
        recognition = new webkitSpeechRecognition();
        recognition.lang = "en-IN";
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.onresult = function(event) {
            let transcript = event.results[0][0].transcript;
            document.getElementById("voice-result").innerText = transcript;
            window.localStorage.setItem("omni_voice", transcript);
            recognizing = false;
        };
        recognition.onerror = function() {
            recognizing = false;
            document.getElementById("voice-result").innerText = "Mic error. Please check permissions.";
        };
    }
    const micBtn = document.getElementById("voice-mic-btn");
    if (micBtn) {
        micBtn.onclick = function() {
            if (recognition && !recognizing) {
                recognizing = true;
                recognition.start();
                document.getElementById("voice-result").innerText = "Listening...";
            }
        };
    }
});
</script>
""", unsafe_allow_html=True)

# --- Omnidimension Voice Integration with Streamlit ---
import streamlit.components.v1 as components

components.html("""
<script>
(function() {
    let lastVoice = "";
    setInterval(function() {
        let v = window.localStorage.getItem("omni_voice") || "";
        if (v && v !== lastVoice) {
            lastVoice = v;
            const url = new URL(window.location);
            url.searchParams.set("voice", v);
            window.history.replaceState({}, '', url);
            window.parent.postMessage({isStreamlitMessage: true, voiceInput: v}, "*");
        }
    }, 1000);
})();
</script>
""", height=0)

voice_input = st.query_params.get("voice", "")
if isinstance(voice_input, list):
    voice_input = voice_input[0] if voice_input else ""
if voice_input:
    st.info(f"🎤 Voice Assistant: {voice_input}")

# --- Sidebar Navigation & Branding ---
st.sidebar.image("https://img.icons8.com/fluency/96/plant-under-sun.png", width=80)
st.sidebar.markdown('<div class="supreme-header">🌱 AgriSOS Supreme</div>', unsafe_allow_html=True)
st.sidebar.markdown("""
**Crop Doctor, Blockchain Traceability, Smart Kitchen, Market Prices, Weather, Community**
<div style='margin-top:1em;'>
    <span class='feature-badge'>🌟 AI</span>
    <span class='feature-badge'>🛰️ Weather</span>
    <span class='feature-badge'>📊 Prices</span>
    <span class='feature-badge'>🔗 Blockchain</span>
    <span class='feature-badge'>👩‍🍳 Kitchen</span>
    <span class='feature-badge'>🤝 Community</span>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "🧭 Navigate",
    [
        "🏠 Crop Doctor",
        "🔗 Blockchain Traceability",
        "👩‍🍳 Smart Kitchen",
        "💹 Market Prices",
        "🌦️ Weather",
        "🤝 Community Q&A",
        "📤 Export Data",
        "❓ Help/FAQ"
    ]
)

# --- Dummy Data & State ---
if 'advice_history' not in st.session_state:
    st.session_state['advice_history'] = []
if 'supply_chain' not in st.session_state:
    st.session_state['supply_chain'] = []
if 'kitchen_history' not in st.session_state:
    st.session_state['kitchen_history'] = []
if 'qa_history' not in st.session_state:
    st.session_state['qa_history'] = []
if 'reminder_list' not in st.session_state:
    st.session_state['reminder_list'] = []
if 'soil_history' not in st.session_state:
    st.session_state['soil_history'] = []

# --- 1. Crop Doctor ---
def get_ai_prediction(crop, problem):
    # Simple rule-based logic for demonstration
    problem = problem.lower()
    if "yellow" in problem or "leaf" in problem:
        return "Blight"
    elif "wilt" in problem:
        return "Wilt"
    elif "pest" in problem or "insect" in problem:
        return "Pest Infestation"
    elif "rot" in problem:
        return "Root Rot"
    elif "fungal" in problem or "spot" in problem:
        return "Fungal Disease"
    elif "curl" in problem:
        return "Leaf Curl"
    elif "healthy" in problem or "no issue" in problem:
        return "Healthy"
    else:
        return "General Stress"

if page == "🏠 Crop Doctor":
    st.markdown('<div class="supreme-header">🌾 Crop Doctor <span class="emoji-bounce">🩺</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="supreme-section">Describe your crop issue and get instant, AI-powered advice with disease prediction and prevention tips.</div>', unsafe_allow_html=True)
    with st.form("advice_form"):
        crop_options = [
            "Wheat", "Rice", "Tomato", "Potato", "Onion", "Maize", "Sugarcane", "Cotton", "Soybean", "Groundnut", "Chickpea", "Mustard", "Barley", "Pea", "Brinjal", "Cabbage", "Cauliflower", "Carrot", "Beans", "Capsicum", "Other"
        ]
        crop_selected = st.selectbox("Crop name (choose or type your own):", crop_options)
        crop = st.text_input("Or type crop name (optional, overrides above):", value=voice_input if voice_input else "")
        crop_final = crop.strip() if crop.strip() else crop_selected

        issue_options = [
            "Yellow leaves", "Wilting", "Pest attack", "Fungal spots", "Low yield", "Stunted growth", "Root rot", "Leaf curl", "Fruit drop", "Other"
        ]
        issue_selected = st.selectbox("Issue (choose or type your own):", issue_options)
        problem = st.text_input("Or describe your issue (optional, overrides above):")
        problem_final = problem.strip() if problem.strip() else issue_selected

        image = st.file_uploader("Upload a crop image (optional, for AI diagnosis)", type=["jpg", "jpeg", "png"])
        submitted = st.form_submit_button("Get Advice")
        if submitted and crop_final and problem_final:
            predicted = get_ai_prediction(crop_final, problem_final)
            advice = f"AI Prediction: <b>{predicted}</b><br>For <b>{crop_final}</b> with issue '<i>{problem_final}</i>':<ul><li>Ensure proper irrigation.</li><li>Check for pests and use recommended pesticides.</li><li>Rotate crops to prevent soil-borne diseases.</li><li>Consult your local agronomist for detailed help.</li></ul>"
            if predicted != "Healthy":
                advice += f"<br><span style='color:#d32f2f;font-weight:bold;'>🚨 Early warning: {predicted} detected. Take preventive action now!</span>"
            st.session_state['advice_history'].append({
                "date": str(datetime.date.today()),
                "crop": crop_final,
                "problem": problem_final,
                "advice": advice
            })
            st.success("Advice generated below. Please review carefully.")
            st.markdown(f"<div class='supreme-section'>{advice}</div>", unsafe_allow_html=True)

            # Only try voice call if OMNI_ENABLED
            AGENT_ID = 12345
            PHONE_NUMBER = "+911234567890"
            if OMNI_ENABLED:
                try:
                    call_resp = dispatch_crop_alert(AGENT_ID, PHONE_NUMBER, crop_final, problem_final)
                    st.success("✅ Voice alert call triggered via OmniDimension!")
                except Exception as e:
                    st.error(f"Failed to dispatch voice alert: {e}")
            else:
                st.info("🔈 Voice alert not available. Please set the OMNIDIM_API_KEY environment variable if you want voice alerts.")
    if st.session_state['advice_history']:
        st.markdown('<div class="supreme-section"><b>Previous Advice</b></div>', unsafe_allow_html=True)
        options = [
            f"{entry['date']} - {entry['crop']}: {entry['problem']}" 
            for entry in reversed(st.session_state['advice_history'])
        ]
        selected = st.selectbox("Select a previous advice to view details:", options) if options else None
        if selected:
            idx = options.index(selected)
            entry = list(reversed(st.session_state['advice_history']))[idx]
            st.markdown(f"<div class='supreme-section'><b>{entry['date']} - {entry['crop']}</b>: {entry['problem']}  <br><i>Advice:</i> {entry['advice']}</div>", unsafe_allow_html=True)

# --- 1b. Soil Health Analyzer (NEW) ---
if page == "🏠 Crop Doctor":
    st.markdown('<div class="supreme-section"><b>🧪 Soil Health Analyzer</b> <span class="feature-badge">NEW</span><br>Enter your soil NPK values to get fertilizer suggestions.</div>', unsafe_allow_html=True)
    with st.form("soil_form"):
        n = st.number_input("Nitrogen (N)", min_value=0, max_value=500, value=50)
        p = st.number_input("Phosphorus (P)", min_value=0, max_value=500, value=30)
        k = st.number_input("Potassium (K)", min_value=0, max_value=500, value=20)
        soil_submit = st.form_submit_button("Analyze Soil")
        if soil_submit:
            if n < 40:
                n_sugg = "Increase Nitrogen (add Urea or compost)."
            elif n > 120:
                n_sugg = "Reduce Nitrogen input."
            else:
                n_sugg = "Nitrogen is optimal."
            if p < 20:
                p_sugg = "Increase Phosphorus (add DAP or bone meal)."
            elif p > 60:
                p_sugg = "Reduce Phosphorus input."
            else:
                p_sugg = "Phosphorus is optimal."
            if k < 20:
                k_sugg = "Increase Potassium (add MOP or wood ash)."
            elif k > 80:
                k_sugg = "Reduce Potassium input."
            else:
                k_sugg = "Potassium is optimal."
            soil_result = f"""
            <ul>
            <li><b>Nitrogen:</b> {n} - {n_sugg}</li>
            <li><b>Phosphorus:</b> {p} - {p_sugg}</li>
            <li><b>Potassium:</b> {k} - {k_sugg}</li>
            </ul>
            """
            st.session_state['soil_history'].append({
                "date": str(datetime.date.today()),
                "N": n, "P": p, "K": k,
                "result": soil_result
            })
            st.success("Soil analysis complete. See below.")
            st.markdown(f"<div class='supreme-section'>{soil_result}</div>", unsafe_allow_html=True)
    if st.session_state['soil_history']:
        st.markdown('<div class="supreme-section"><b>Previous Soil Analyses</b></div>', unsafe_allow_html=True)
        options = [
            f"{entry['date']} - N:{entry['N']} P:{entry['P']} K:{entry['K']}" 
            for entry in reversed(st.session_state['soil_history'])
        ]
        selected = st.selectbox("Select a previous soil analysis to view details:", options) if options else None
        if selected:
            idx = options.index(selected)
            entry = list(reversed(st.session_state['soil_history']))[idx]
            st.markdown(f"<div class='supreme-section'><b>{entry['date']}</b>: N={entry['N']} P={entry['P']} K={entry['K']}<br>{entry['result']}</div>", unsafe_allow_html=True)

# --- 1c. Crop Calendar & Reminders (NEW) ---
if page == "🏠 Crop Doctor":
    st.markdown('<div class="supreme-section"><b>📅 Crop Calendar & Reminders</b> <span class="feature-badge">NEW</span><br>Set reminders for sowing, irrigation, or harvesting.</div>', unsafe_allow_html=True)
    with st.form("reminder_form"):
        task = st.text_input("Task (e.g. Irrigation, Fertilizer, Harvest):")
        date = st.date_input("Date", min_value=datetime.date.today())
        reminder_submit = st.form_submit_button("Add Reminder")
        if reminder_submit and task:
            st.session_state['reminder_list'].append({
                "task": task,
                "date": str(date)
            })
            st.success("Reminder added!")
    if st.session_state['reminder_list']:
        st.markdown('<div class="supreme-section"><b>Upcoming Reminders</b></div>', unsafe_allow_html=True)
        for r in sorted(st.session_state['reminder_list'], key=lambda x: x['date']):
            st.markdown(f"<div class='supreme-section'><b>{r['date']}</b>: {r['task']}</div>", unsafe_allow_html=True)

# --- 3. Smart Kitchen Assistant ---
if page == "👩‍🍳 Smart Kitchen":
    st.markdown('<div class="supreme-header">👩‍🍳 Smart Kitchen Assistant <span class="emoji-bounce">🍲</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="supreme-section">Get AI-powered recipe ideas, nutrition info, and kitchen tips based on your available produce.</div>', unsafe_allow_html=True)
    
    # Predefined recipe suggestions for common ingredients
    recipe_db = [
        {
            "name": "Simple Veg Curry",
            "ingredients": ["potato", "tomato", "onion"],
            "recipe": "Chop all veggies, sauté onion, add tomato and potato, cook with spices and water.",
            "nutrition": "Approx 180 kcal/serving. Rich in vitamin C and fiber."
        },
        {
            "name": "Tomato Rice",
            "ingredients": ["rice", "tomato", "onion"],
            "recipe": "Cook rice, sauté onion and tomato, mix with rice and spices.",
            "nutrition": "Approx 220 kcal/serving. Good source of carbs and lycopene."
        },
        {
            "name": "Aloo Paratha",
            "ingredients": ["potato", "wheat flour"],
            "recipe": "Boil and mash potato, mix with spices, stuff in wheat dough, roll and roast.",
            "nutrition": "Approx 250 kcal/serving. High in carbs and potassium."
        },
        {
            "name": "Mixed Veg Stir Fry",
            "ingredients": ["carrot", "beans", "capsicum", "onion"],
            "recipe": "Chop all veggies, stir fry in oil with garlic and spices.",
            "nutrition": "Approx 120 kcal/serving. High in vitamins and fiber."
        },
        {
            "name": "Egg Bhurji",
            "ingredients": ["egg", "onion", "tomato"],
            "recipe": "Beat eggs, sauté onion and tomato, add eggs and scramble.",
            "nutrition": "Approx 150 kcal/serving. High in protein."
        },
        {
            "name": "Dal Tadka",
            "ingredients": ["dal", "onion", "tomato"],
            "recipe": "Cook dal, temper with sautéed onion, tomato, and spices.",
            "nutrition": "Approx 180 kcal/serving. High in protein and fiber."
        }
    ]

    # Dropdown for all suggestions
    st.markdown('<div class="supreme-section"><b>All Recipe Suggestions</b></div>', unsafe_allow_html=True)
    all_suggestion_names = [f"{rec['name']} ({', '.join(rec['ingredients'])})" for rec in recipe_db]
    selected_all = st.selectbox("Browse all recipes:", all_suggestion_names, key="all_suggestions")
    idx_all = all_suggestion_names.index(selected_all)
    rec_all = recipe_db[idx_all]
    st.markdown(
        f"<div class='supreme-section'><b>Recipe:</b> {rec_all['name']}<br>"
        f"<b>Ingredients:</b> {', '.join(rec_all['ingredients'])}<br>"
        f"<b>Instructions:</b> {rec_all['recipe']}<br>"
        f"<b>Nutrition:</b> {rec_all['nutrition']}</div>",
        unsafe_allow_html=True
    )

    # Ingredient suggestion dropdown
    all_ingredients = sorted({ing for rec in recipe_db for ing in rec["ingredients"]})
    st.markdown('<div class="supreme-section"><b>Ingredient Suggestions</b></div>', unsafe_allow_html=True)
    selected_ingredients = st.multiselect(
        "Pick ingredients from the list (optional):",
        all_ingredients,
        key="ingredient_suggestions"
    )
    ingredient_text = ", ".join(selected_ingredients) if selected_ingredients else ""

    with st.form("kitchen_form"):
        ingredients = st.text_input("What ingredients do you have? (comma separated)", value=ingredient_text)
        submitted = st.form_submit_button("Suggest Recipes")
        if submitted and ingredients:
            ing_list = [i.strip().lower() for i in ingredients.split(",") if i.strip()]
            suggestions = []
            for rec in recipe_db:
                if all(item in ing_list for item in rec["ingredients"]):
                    suggestions.append(rec)
            # Always add a generic suggestion
            if not suggestions:
                suggestions.append({
                    "name": "Custom Stir Fry",
                    "ingredients": ing_list,
                    "recipe": f"With {', '.join(ing_list)}, try a healthy stir-fry or curry. Add turmeric and cumin for flavor and health benefits. Serve with rice or bread.",
                    "nutrition": f"Estimated calories: {100 + 50*len(ing_list)} kcal. Rich in fiber and vitamins."
                })
            # Save all suggestions to history
            st.session_state['kitchen_history'].append({
                "date": str(datetime.date.today()),
                "ingredients": ingredients,
                "suggestions": suggestions
            })
            st.success("Recipe suggestions generated below.")
            # Dropdown to select among suggestions
            suggestion_names = [f"{rec['name']} ({', '.join(rec['ingredients'])})" for rec in suggestions]
            selected_sugg = st.selectbox("Select a recipe suggestion to view details:", suggestion_names)
            idx = suggestion_names.index(selected_sugg)
            rec = suggestions[idx]
            st.markdown(
                f"<div class='supreme-section'><b>Recipe:</b> {rec['name']}<br>"
                f"<b>Ingredients:</b> {', '.join(rec['ingredients'])}<br>"
                f"<b>Instructions:</b> {rec['recipe']}<br>"
                f"<b>Nutrition:</b> {rec['nutrition']}</div>",
                unsafe_allow_html=True
            )

    # Show previous suggestions with dropdown
    if st.session_state['kitchen_history']:
        st.markdown('<div class="supreme-section"><b>Previous Suggestions</b></div>', unsafe_allow_html=True)
        options = [
            f"{entry['date']}: {entry['ingredients']}" 
            for entry in reversed(st.session_state['kitchen_history'])
        ]
        selected = st.selectbox("Select a previous suggestion to view details:", options) if options else None
        if selected:
            idx = options.index(selected)
            entry = list(reversed(st.session_state['kitchen_history']))[idx]
            # Dropdown for suggestions in this entry
            suggestion_names = [f"{rec['name']} ({', '.join(rec['ingredients'])})" for rec in entry['suggestions']]
            selected_sugg = st.selectbox("Select a recipe from this suggestion:", suggestion_names, key=f"prev_{idx}")
            rec_idx = suggestion_names.index(selected_sugg)
            rec = entry['suggestions'][rec_idx]
            st.markdown(
                f"<div class='supreme-section'><b>Recipe:</b> {rec['name']}<br>"
                f"<b>Ingredients:</b> {', '.join(rec['ingredients'])}<br>"
                f"<b>Instructions:</b> {rec['recipe']}<br>"
                f"<b>Nutrition:</b> {rec['nutrition']}</div>",
                unsafe_allow_html=True
            )

# --- 6. Community Q&A ---
if page == "🤝 Community Q&A":
    st.markdown('<div class="supreme-header">🤝 Community Q&A <span class="emoji-bounce">💬</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="supreme-section">Ask questions or share advice with other farmers. (All posts are public and anonymous)</div>', unsafe_allow_html=True)
    question = st.text_input("Ask a question or share advice:")
    if st.button("Post"):
        if question:
            st.session_state['qa_history'].append({
                "date": str(datetime.date.today()),
                "question": question
            })
    if st.session_state['qa_history']:
        st.markdown('<div class="supreme-section"><b>Community Posts</b></div>', unsafe_allow_html=True)
        options = [
            f"{entry['date']}: {entry['question'][:40]}{'...' if len(entry['question']) > 40 else ''}"
            for entry in reversed(st.session_state['qa_history'])
        ]
        selected = st.selectbox("Select a post to view details:", options) if options else None
        if selected:
            idx = options.index(selected)
            entry = list(reversed(st.session_state['qa_history']))[idx]
            st.markdown(f"<div class='supreme-section'><b>{entry['date']}</b>: {entry['question']}</div>", unsafe_allow_html=True)

# --- 2. Blockchain Supply Chain Traceability ---
def generate_blockchain_hash(product, origin, destination, batch_id, date):
    # Simple deterministic hash for demonstration (not secure)
    base = f"{product}-{origin}-{destination}-{batch_id}-{date}"
    return hex(abs(hash(base)))[2:12]

if page == "🔗 Blockchain Traceability":
    st.markdown('<div class="supreme-header">🔗 Blockchain Supply Chain Traceability <span class="emoji-bounce">🔒</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="supreme-section">Track your produce from farm to market. Each entry is given a unique blockchain hash for authenticity.</div>', unsafe_allow_html=True)
    with st.form("supply_chain_form"):
        product = st.text_input("Product (e.g. Tomato, Rice):")
        origin = st.text_input("Origin (Farm/Village):")
        destination = st.text_input("Destination (Market/City):")
        batch_id = st.text_input("Batch ID (optional):")
        submitted = st.form_submit_button("Add Trace")
        if submitted and product and origin and destination:
            date = str(datetime.date.today())
            block_hash = generate_blockchain_hash(product, origin, destination, batch_id, date)
            entry = {
                "date": date,
                "product": product,
                "origin": origin,
                "destination": destination,
                "batch_id": batch_id,
                "blockchain_hash": block_hash
            }
            st.session_state['supply_chain'].append(entry)
            st.success(f"Supply chain entry added! Blockchain hash: `{block_hash}`")
    if st.session_state['supply_chain']:
        st.markdown('<div class="supreme-section"><b>Supply Chain Blockchain Records</b></div>', unsafe_allow_html=True)
        options = [
            f"{entry['date']} - {entry['product']} ({entry['origin']} → {entry['destination']})"
            for entry in reversed(st.session_state['supply_chain'])
        ]
        selected = st.selectbox("Select a record to view details:", options) if options else None
        if selected:
            idx = options.index(selected)
            entry = list(reversed(st.session_state['supply_chain']))[idx]
            st.markdown(
                f"<div class='supreme-section'><b>Date:</b> {entry['date']}<br>"
                f"<b>Product:</b> {entry['product']}<br>"
                f"<b>Origin:</b> {entry['origin']}<br>"
                f"<b>Destination:</b> {entry['destination']}<br>"
                f"<b>Batch ID:</b> {entry['batch_id']}<br>"
                f"<b>Blockchain Hash:</b> {entry['blockchain_hash']}</div>",
                unsafe_allow_html=True
            )

# --- 4. Market Prices ---
if page == "💹 Market Prices":
    st.markdown('<div class="supreme-header">💹 Live Market Prices <span class="emoji-bounce">📈</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="supreme-section">Check today\'s market prices for major crops.</div>', unsafe_allow_html=True)
    crops = ["Wheat", "Rice", "Tomato", "Potato", "Onion", "Maize"]
    # Example static prices for demonstration
    prices = {
        "Wheat": 2200,
        "Rice": 2100,
        "Tomato": 1500,
        "Potato": 1300,
        "Onion": 1400,
        "Maize": 1800
    }
    df_prices = pd.DataFrame({"Crop": list(prices.keys()), "Price (₹/quintal)": list(prices.values())})
    st.table(df_prices)
    # Dropdown for price history (static demo)
    st.markdown('<div class="supreme-section"><b>Check Price History</b></div>', unsafe_allow_html=True)
    crop_selected = st.selectbox("Select a crop to view price history:", crops)
    if crop_selected:
        # Example static price history
        price_history = {
            "Wheat": [2100, 2150, 2200, 2180, 2200, 2210, 2200],
            "Rice": [2000, 2050, 2100, 2080, 2100, 2110, 2100],
            "Tomato": [1400, 1450, 1500, 1480, 1500, 1510, 1500],
            "Potato": [1200, 1250, 1300, 1280, 1300, 1310, 1300],
            "Onion": [1300, 1350, 1400, 1380, 1400, 1410, 1400],
            "Maize": [1700, 1750, 1800, 1780, 1800, 1810, 1800]
        }
        st.line_chart(pd.DataFrame({"Price (₹/quintal)": price_history[crop_selected]}, index=[f"Day {i+1}" for i in range(7)]))

# --- 5. Weather Info ---
if page == "🌦️ Weather":
    st.markdown('<div class="supreme-header">🌦️ Weather Information <span class="emoji-bounce">☀️</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="supreme-section">Get current weather for your location. Select your state and city.</div>', unsafe_allow_html=True)

    state_city_map = {
        "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore"],
        "Bihar": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur"],
        "Delhi": ["New Delhi", "Dwarka", "Rohini", "Saket"],
        "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot"],
        "Karnataka": ["Bengaluru", "Mysuru", "Mangaluru", "Hubballi"],
        "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik"],
        "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala"],
        "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota"],
        "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem"],
        "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra"],
        "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Siliguri"]
    }

    state = st.selectbox("Select State", [""] + list(state_city_map.keys()))
    city = ""
    if state:
        city = st.selectbox("Select City", [""] + state_city_map[state])
    if city:
        if st.button("Get Weather"):
            import urllib.parse
            city_enc = urllib.parse.quote(city)
            url = f"https://wttr.in/{city_enc}?format=j1"
            try:
                import requests
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    current = data["current_condition"][0]
                    desc = current["weatherDesc"][0]["value"]
                    temp = current["temp_C"]
                    humidity = current["humidity"]
                    wind = current["windspeedKmph"]
                    st.success(f"Weather in {city}: {desc}, {temp}°C")
                    st.write(f"Humidity: {humidity}%")
                    st.write(f"Wind: {wind} km/h")
                else:
                    st.error(f"Could not fetch weather for {city}. Status code: {resp.status_code}")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.info("Please select a state and city to get weather information.")

# --- 7. Export Data ---
if page == "📤 Export Data":
    st.markdown('<div class="supreme-header">📤 Export Data <span class="emoji-bounce">⬇️</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="supreme-section">Download your crop advice, supply chain, and kitchen records as CSV files.<br><b>Data is private and never shared without your consent.</b></div>', unsafe_allow_html=True)
    if st.button("Download Crop Advice CSV"):
        df = pd.DataFrame(st.session_state['advice_history'])
        csv = df.to_csv(index=False)
        st.download_button("Download Crop Advice", csv, "crop_advice.csv", "text/csv")
    if st.button("Download Supply Chain CSV"):
        df = pd.DataFrame(st.session_state['supply_chain'])
        csv = df.to_csv(index=False)
        st.download_button("Download Supply Chain", csv, "supply_chain.csv", "text/csv")
    if st.button("Download Kitchen CSV"):
        df = pd.DataFrame(st.session_state['kitchen_history'])
        csv = df.to_csv(index=False)
        st.download_button("Download Kitchen", csv, "kitchen_history.csv", "text/csv")

# --- 8. Help/FAQ ---
if page == "❓ Help/FAQ":
    st.markdown('<div class="supreme-header">❓ Help & FAQ <span class="emoji-bounce">🌟</span></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="supreme-section">
    <ul>
    <li><b>What is AgriSOS Supreme?</b><br>
      A platform for crop advice, blockchain traceability, smart kitchen, live prices, weather, and community.</li>
    <li><b>How do I get crop advice?</b><br>
      Go to 'Crop Doctor', enter your crop and problem, and get instant AI-powered tips.</li>
    <li><b>How do I track my produce?</b><br>
      Use 'Blockchain Traceability' to log your product's journey with a unique hash.</li>
    <li><b>How do I get recipe ideas?</b><br>
      Use 'Smart Kitchen' and enter your available ingredients.</li>
    <li><b>How do I check market prices?</b><br>
      Go to 'Market Prices' for live rates.</li>
    <li><b>How do I check the weather?</b><br>
      Go to 'Weather' and select your state and city.</li>
    <li><b>How do I ask the community?</b><br>
      Use 'Community Q&A' to post questions or advice.</li>
    <li><b>How do I export my data?</b><br>
      Go to 'Export Data' to download your records as CSV.</li>
    <li><b>Need more help?</b><br>
      Contact: <a href="mailto:support@agrisos.org">support@agrisos.org</a></li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="supreme-section"><b>Feedback & Suggestions:</b> <a href="mailto:support@agrisos.org">Submit here</a><br><b>Follow us:</b> <a href="https://twitter.com/">AgriSOS Twitter</a> | <a href="https://facebook.com/">AgriSOS Facebook</a></div>', unsafe_allow_html=True)
    st.info("🌟 Thank you for supporting your farming community!")

# --- Footer ---
st.markdown('<div class="footer">© 2025 AgriSOS Supreme | Ministry of Agriculture, India | All Rights Reserved</div>', unsafe_allow_html=True)