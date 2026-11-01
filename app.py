"""
CineScope 2.0 — Movie Ratings & Discovery Platform
Discover Movies. Explore Ratings. Find Your Next Favourite.

A Premium, Fully Functional Movie Discovery and Analytics Web Application.
Features:
- Complete Dark Mode and Light Mode with 100% Text Visibility & High Contrast
- Accessible UI: Scalable Font Sizes, High-Contrast Mode, Visible Focus Indicators
- Bilingual Interface: English & हिंदी (Hindi) with Seamless Real-Time Switching
- Redesigned Collapsible Sidebar with Icons AND Readable Text Labels
- Working Movie Search (Local MovieLens Dataset + Worldwide OMDb Fallback)
- Movie Comparison Tool (Side-by-Side Comparison with Winner Highlights)
- Personal Movie Ratings System (Persistent Local Storage, Original CSVs Untouched)
- Surprise Me! Feature (Random Real Movie Discovery by Genre)
- Download Reports: Clean CSV & Comprehensive Executive PDF Report (fpdf2)
- Persistent Personal Watchlist (Watched / Want to Watch)
- 9 Interactive Plotly Charts with Plain-English & Hindi Takeaways
- About Project Page with Complete 13-Member Team List
"""

import os
import re
import json
import random
import urllib.request
import urllib.parse
from datetime import datetime
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CineScope 2.0 — Movie Ratings & Analytics",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

base_dir = os.path.dirname(os.path.abspath(__file__))

# -----------------------------------------------------------------------------
# 2. Accessibility & Settings Persistence
# -----------------------------------------------------------------------------
acc_file = os.path.join(base_dir, "data", "accessibility_settings.json")
ratings_file = os.path.join(base_dir, "data", "user_ratings.json")
watchlist_file = os.path.join(base_dir, "data", "watchlist.json")

def load_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# Load saved preferences
acc_prefs = load_json(acc_file, {"font_size": "Normal", "high_contrast": False, "focus_indicators": True})

if "theme" not in st.session_state:
    st.session_state["theme"] = "dark" # "dark" or "light"

if "language" not in st.session_state:
    st.session_state["language"] = "en" # "en" or "hi"

if "font_size" not in st.session_state:
    st.session_state["font_size"] = acc_prefs.get("font_size", "Normal")

if "high_contrast" not in st.session_state:
    st.session_state["high_contrast"] = acc_prefs.get("high_contrast", False)

if "focus_indicators" not in st.session_state:
    st.session_state["focus_indicators"] = acc_prefs.get("focus_indicators", True)

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "home"

if "search_query" not in st.session_state:
    st.session_state["search_query"] = ""

if "selected_movie_id" not in st.session_state:
    st.session_state["selected_movie_id"] = None

if "sidebar_open" not in st.session_state:
    st.session_state["sidebar_open"] = True

if "user_ratings" not in st.session_state:
    st.session_state["user_ratings"] = load_json(ratings_file, {})

if "watchlist" not in st.session_state:
    st.session_state["watchlist"] = load_json(watchlist_file, {
        "318": {"movieId": 318, "title": "The Shawshank Redemption", "year": 1994, "genres": "Crime|Drama", "rating": 4.43, "status": "Watched"},
        "79132": {"movieId": 79132, "title": "Inception", "year": 2010, "genres": "Action|Crime|Drama|Mystery|Sci-Fi|Thriller", "rating": 4.07, "status": "Want to Watch"}
    })

if "surprise_movie" not in st.session_state:
    st.session_state["surprise_movie"] = None

if "compare_movie_1" not in st.session_state:
    st.session_state["compare_movie_1"] = 79132 # Inception
if "compare_movie_2" not in st.session_state:
    st.session_state["compare_movie_2"] = 109487 # Interstellar

# -----------------------------------------------------------------------------
# 3. Bilingual Dictionary (English & Hindi)
# -----------------------------------------------------------------------------
TRANSLATIONS = {
    "en": {
        "app_title": "CineScope",
        "app_tagline": "Discover Movies. Explore Ratings. Find Your Next Favourite.",
        "nav_home": "🏠 Home",
        "nav_search": "🔍 Search Movies",
        "nav_compare": "⚖️ Movie Comparison",
        "nav_surprise": "🎲 Surprise Me!",
        "nav_analytics": "📊 Analytics Dashboard",
        "nav_genres": "🎭 Explore Genres",
        "nav_top": "⭐ Top Rated Movies",
        "nav_insights": "📈 Rating Insights",
        "nav_watchlist": "❤️ My Watchlist",
        "nav_reports": "📥 Download Reports",
        "nav_accessibility": "♿ Accessibility Settings",
        "nav_about": "ℹ️ About Project",
        # Top Navbar
        "toggle_theme_dark": "🌙 Dark Mode",
        "toggle_theme_light": "☀️ Light Mode",
        "lang_switch": "🇮🇳 हिंदी",
        # Hero
        "hero_tag": "CineScope 2.0 • Data Analytics Project",
        "hero_heading": "Discover Movies. Explore Ratings. Find Your Next Favourite.",
        "hero_subtitle": "Search thousands of movies, discover true audience ratings, view director and cast details, and explore cinema history powered by real data.",
        "search_placeholder": "Search by title... e.g. Inception, The Dark Knight, Titanic, 3 Idiots, Interstellar, Dangal",
        "search_btn": "🔍 Search Movie",
        "quick_try": "Quick Suggestions:",
        # Key Metrics
        "total_movies": "Total Movies",
        "total_movies_desc": "Unique catalog movies (1902–2018)",
        "total_ratings": "Total Ratings",
        "total_ratings_desc": "Verified reviews submitted by audience",
        "active_users": "Active Reviewers",
        "active_users_desc": "Users who rated 20+ movies",
        "avg_rating": "Average Rating",
        "avg_rating_desc": "Overall score across entire catalog",
        "most_rated_movie": "Most Rated Movie",
        "top_ranked_movie": "Top Ranked Movie",
        "most_rated_genre": "Most Popular Genre",
        # Section Titles
        "featured_title": "⭐ Featured All-Time Fan Favourites",
        "featured_desc": "Hand-picked cinema masterpieces with high audience scores and hundreds of reviews.",
        "view_details": "View Details ➔",
        "back_to_results": "⬅ Back to Search Results",
        # Details & Ratings
        "movie_details_title": "Movie Details",
        "plot_title": "Story / Plot Overview",
        "director": "Director",
        "cast": "Main Cast",
        "runtime": "Runtime",
        "language": "Language",
        "released": "Released Date",
        "movielens_score": "MovieLens Rating",
        "fair_score": "Fair Ranking Score",
        "external_score": "External IMDb Rating",
        "personal_rating_title": "⭐ Your Personal Rating",
        "rate_this_movie": "Rate this movie (1 to 5 stars):",
        "save_rating_btn": "Save My Rating",
        "rating_saved_msg": "Your personal rating was saved! (Saved locally, dataset CSVs remain untouched).",
        "add_watchlist": "❤️ Add to Watchlist",
        "in_watchlist": "✓ In Watchlist",
        "remove_watchlist": "🗑️ Remove",
        "similar_movies_title": "🎯 Similar Movies You Might Enjoy",
        "recommend_reason": "Recommended because this movie shares high-rated {} genres with similar audience appeal.",
        # Comparison
        "compare_heading": "⚖️ Side-by-Side Movie Comparison",
        "compare_subtitle": "Select two movies to compare their ratings, votes, genres, release years, and audience appeal.",
        "compare_select_1": "Select First Movie (Movie A):",
        "compare_select_2": "Select Second Movie (Movie B):",
        "higher_rating_badge": "🏆 HIGHER RATED",
        "more_votes_badge": "🔥 MORE VOTES",
        # Surprise Me
        "surprise_heading": "🎲 Surprise Me! Movie Discovery",
        "surprise_subtitle": "Can't decide what to watch? Pick a genre and let CineScope surprise you with a real highly-rated film!",
        "surprise_genre": "Choose a Genre:",
        "surprise_btn": "🎲 Surprise Me!",
        "surprise_another_btn": "🎲 Discover Another Movie",
        # Reports
        "reports_heading": "📥 Download Project Reports",
        "reports_subtitle": "Export real project data, leaderboards, and a complete executive PDF analytics report.",
        "download_csv_btn": "📄 Download Filtered Movies (CSV)",
        "download_pdf_btn": "📕 Download Executive Analytics Report (PDF)",
        # Accessibility
        "acc_heading": "♿ Accessibility Settings",
        "acc_subtitle": "Customize fonts, contrast, and visual navigation to make CineScope comfortable for everyone.",
        "acc_font_size": "Text Size:",
        "acc_high_contrast": "High-Contrast Mode (Sharper borders and maximum text contrast)",
        "acc_focus": "Visible Keyboard Focus Indicators (Outlines active inputs and buttons)",
        "acc_save_btn": "Save Accessibility Preferences",
        # Watchlist
        "watchlist_heading": "❤️ My Movie Watchlist",
        "watchlist_subtitle": "Save movies you want to watch or track the ones you have already enjoyed.",
        "empty_watchlist": "Your watchlist is empty! Search for movies and click 'Add to Watchlist' to save them here.",
        # Analytics & Explanations
        "analytics_heading": "📊 Movie Analytics Dashboard",
        "analytics_subtitle": "Comprehensive, interactive charts built directly on 100,000+ real ratings from the MovieLens dataset.",
        "filter_years": "Release Year Range:",
        "filter_min_ratings": "Show only movies with at least this many ratings:",
        "chart_explainer_prefix": "What this chart shows:",
        "chart_takeaway_prefix": "🎯 Key takeaway:",
        # Genres
        "genres_heading": "🎭 Explore Movie Genres",
        "genres_subtitle": "Compare movie genres, discover which categories have the most movies, and explore titles within your favourite genres.",
        # Top Movies
        "top_heading": "⭐ Top Rated Movies Leaderboard",
        "top_subtitle": "Discover top films ranked using our Fair Score formula that balances review scores with a minimum number of ratings.",
        # Rating Insights
        "insights_heading": "📈 Rating Insights & What We Learned",
        "insights_subtitle": "Key takeaways and patterns discovered through empirical analysis of over 100,000 real audience reviews.",
        # About
        "about_heading": "ℹ️ About CineScope 2.0",
        "about_subtitle": "Academic Data Analytics Project • Movie Ratings and Genre Trends (Project ID: DA-006)",
        "team_title": "👥 Project Team / Presented By",
        "dataset_title": "📂 Dataset Documentation",
        "tech_title": "🛠️ Tools & Technologies",
        "footer_text": "CineScope 2.0 — Movie Ratings and Genre Trends Project • Built with Python, Streamlit, Pandas, Plotly & OMDb API"
    },
    "hi": {
        "app_title": "CineScope",
        "app_tagline": "फिल्में खोजें। रेटिंग देखें। अपनी अगली पसंदीदा फिल्म पाएं।",
        "nav_home": "🏠 होम",
        "nav_search": "🔍 फिल्म खोजें",
        "nav_compare": "⚖️ फिल्मों की तुलना",
        "nav_surprise": "🎲 सरप्राइज मी! (अचानक खोजें)",
        "nav_analytics": "📊 विश्लेषण डैशबोर्ड",
        "nav_genres": "🎭 फिल्म की श्रेणियाँ",
        "nav_top": "⭐ शीर्ष रेटिंग वाली फिल्में",
        "nav_insights": "📈 रेटिंग की जानकारी",
        "nav_watchlist": "❤️ मेरी पसंदीदा फिल्में",
        "nav_reports": "📥 रिपोर्ट डाउनलोड करें",
        "nav_accessibility": "♿ सुगमता सेटिंग्स",
        "nav_about": "ℹ️ प्रोजेक्ट के बारे में",
        # Top Navbar
        "toggle_theme_dark": "🌙 डार्क मोड",
        "toggle_theme_light": "☀️ लाइट मोड",
        "lang_switch": "🇬🇧 English",
        # Hero
        "hero_tag": "सिनेस्कोप 2.0 • डेटा एनालिटिक्स प्रोजेक्ट",
        "hero_heading": "फिल्में खोजें। रेटिंग देखें। अपनी अगली पसंदीदा फिल्म पाएं।",
        "hero_subtitle": "हजारों फिल्में खोजें, दर्शकों की वास्तविक रेटिंग देखें, निर्देशक और कलाकारों का विवरण पाएं और सिनेमा के इतिहास का विश्लेषण करें।",
        "search_placeholder": "फिल्म का नाम खोजें... जैसे Inception, The Dark Knight, Titanic, 3 Idiots, Interstellar, Dangal",
        "search_btn": "🔍 फिल्म खोजें",
        "quick_try": "सुझाव:",
        # Key Metrics
        "total_movies": "कुल फिल्में",
        "total_movies_desc": "कैटलॉग में 1902 से 2018 तक की फिल्में",
        "total_ratings": "कुल रेटिंग",
        "total_ratings_desc": "दर्शकों द्वारा दी गई वास्तविक समीक्षाएं",
        "active_users": "सक्रिय समीक्षक",
        "active_users_desc": "उपयोगकर्ता जिन्होंने 20+ फिल्में रेट कीं",
        "avg_rating": "औसत रेटिंग",
        "avg_rating_desc": "पूरी लाइब्रेरी का समग्र औसत स्कोर",
        "most_rated_movie": "सर्वाधिक समीक्षा वाली फिल्म",
        "top_ranked_movie": "सर्वश्रेष्ठ क्रमबद्ध फिल्म",
        "most_rated_genre": "सबसे लोकप्रिय श्रेणी",
        # Section Titles
        "featured_title": "⭐ सर्वकालिक लोकप्रिय फिल्में",
        "featured_desc": "उच्च रेटिंग और सैकड़ों समीक्षाओं वाली चुनिंदा सिनेमाई कृतियां।",
        "view_details": "विवरण देखें ➔",
        "back_to_results": "⬅ खोज परिणामों पर वापस जाएं",
        # Details & Ratings
        "movie_details_title": "फिल्म का विवरण",
        "plot_title": "कहानी का सारांश",
        "director": "निर्देशक",
        "cast": "मुख्य कलाकार",
        "runtime": "अवधि",
        "language": "भाषा",
        "released": "रिलीज़ की तारीख",
        "movielens_score": "मूवीलेंस रेटिंग",
        "fair_score": "उचित रैंकिंग स्कोर",
        "external_score": "बाहरी IMDb रेटिंग",
        "personal_rating_title": "⭐ आपकी व्यक्तिगत रेटिंग",
        "rate_this_movie": "इस फिल्म को अपनी रेटिंग दें (1 से 5 स्टार):",
        "save_rating_btn": "मेरी रेटिंग सहेजें",
        "rating_saved_msg": "आपकी व्यक्तिगत रेटिंग सहेज ली गई है! (मूल डेटासेट सुरक्षित है)।",
        "add_watchlist": "❤️ पसंदीदा में जोड़ें",
        "in_watchlist": "✓ पसंदीदा सूची में मौजूद",
        "remove_watchlist": "🗑️ हटाएं",
        "similar_movies_title": "🎯 मिलती-जुलती फिल्में जो आपको पसंद आ सकती हैं",
        "recommend_reason": "सिफारिश की गई क्योंकि यह फिल्म उच्च रेटिंग वाली {} शैली साझा करती है।",
        # Comparison
        "compare_heading": "⚖️ फिल्मों की आमने-सामने तुलना",
        "compare_subtitle": "दो फिल्मों का चयन करें और उनकी रेटिंग, वोट संख्या, शैली और लोकप्रियता की तुलना करें।",
        "compare_select_1": "पहली फिल्म चुनें (फिल्म A):",
        "compare_select_2": "दूसरी फिल्म चुनें (फिल्म B):",
        "higher_rating_badge": "🏆 उच्च रेटिंग",
        "more_votes_badge": "🔥 अधिक वोट",
        # Surprise Me
        "surprise_heading": "🎲 सरप्राइज मी! यादृच्छिक फिल्म खोज",
        "surprise_subtitle": "तय नहीं कर पा रहे कि क्या देखें? एक शैली चुनें और सिनेस्कोप को एक बेहतरीन फिल्म सुझाने दें!",
        "surprise_genre": "फिल्म की श्रेणी चुनें:",
        "surprise_btn": "🎲 फिल्म सुझाएं!",
        "surprise_another_btn": "🎲 कोई अन्य फिल्म दिखाएं",
        # Reports
        "reports_heading": "📥 प्रोजेक्ट रिपोर्ट डाउनलोड करें",
        "reports_subtitle": "वास्तविक प्रोजेक्ट डेटा, रैंकिंग और कार्यकारी PDF विश्लेषण रिपोर्ट डाउनलोड करें।",
        "download_csv_btn": "📄 फ़िल्टर की गई फिल्में (CSV) डाउनलोड करें",
        "download_pdf_btn": "📕 विस्तृत विश्लेषण रिपोर्ट (PDF) डाउनलोड करें",
        # Accessibility
        "acc_heading": "♿ सुगमता (Accessibility) सेटिंग्स",
        "acc_subtitle": "फ़ॉन्ट आकार, कंट्रास्ट और विज़ुअल संकेत अनुकूलित करें ताकि सिनेस्कोप का उपयोग सभी के लिए आसान हो।",
        "acc_font_size": "टेक्स्ट का आकार:",
        "acc_high_contrast": "हाई-कंट्रास्ट मोड (स्पष्ट बॉर्डर और अधिकतम दृश्यता)",
        "acc_focus": "कीबोर्ड फोकस संकेत (इनपुट और बटन के चारों ओर स्पष्ट रेखा)",
        "acc_save_btn": "सेटिंग्स सहेजें",
        # Watchlist
        "watchlist_heading": "❤️ मेरी पसंदीदा फिल्में (Watchlist)",
        "watchlist_subtitle": "उन फिल्मों को सहेजें जिन्हें आप देखना चाहते हैं या जो आप देख चुके हैं।",
        "empty_watchlist": "आपकी पसंदीदा सूची खाली है! फिल्में खोजें और उन्हें सहेजने के लिए 'पसंदीदा में जोड़ें' पर क्लिक करें।",
        # Analytics & Explanations
        "analytics_heading": "📊 मूवी एनालिटिक्स डैशबोर्ड",
        "analytics_subtitle": "मूवीलेंस डेटासेट से 100,000+ वास्तविक रेटिंग्स पर आधारित इंटरैक्टिव चार्ट्स।",
        "filter_years": "रिलीज़ वर्ष सीमा:",
        "filter_min_ratings": "केवल इतनी न्यूनतम समीक्षाओं वाली फिल्में दिखाएं:",
        "chart_explainer_prefix": "यह चार्ट क्या दर्शाता है:",
        "chart_takeaway_prefix": "🎯 मुख्य निष्कर्ष:",
        # Genres
        "genres_heading": "🎭 फिल्म की श्रेणियाँ (Genres)",
        "genres_subtitle": "फिल्म श्रेणियों की तुलना करें और अपनी पसंदीदा श्रेणी की फिल्में खोजें।",
        # Top Movies
        "top_heading": "⭐ सर्वश्रेष्ठ रेटिंग वाली फिल्मों की सूची",
        "top_subtitle": "हमारे निष्पक्ष स्कोर फॉर्मूले के आधार पर शीर्ष फिल्मों की रैंकिंग।",
        # Rating Insights
        "insights_heading": "📈 रेटिंग की जानकारी और निष्कर्ष",
        "insights_subtitle": "100,000 से अधिक समीक्षाओं के अध्ययन से सामने आए महत्वपूर्ण परिणाम।",
        # About
        "about_heading": "ℹ️ सिनेस्कोप 2.0 प्रोजेक्ट विवरण",
        "about_subtitle": "अकादमिक डेटा एनालिटिक्स प्रोजेक्ट • Movie Ratings and Genre Trends (Project ID: DA-006)",
        "team_title": "👥 प्रोजेक्ट टीम / प्रस्तुतकर्ता",
        "dataset_title": "📂 डेटासेट स्रोत और जानकारी",
        "tech_title": "🛠️ प्रयुक्त तकनीकें",
        "footer_text": "सिनेस्कोप 2.0 — मूवी रेटिंग्स और जॉनर ट्रेंड्स प्रोजेक्ट • Python, Streamlit, Pandas, Plotly एवं OMDb द्वारा निर्मित"
    }
}

def t(key):
    lang = st.session_state.get("language", "en")
    return TRANSLATIONS.get(lang, {}).get(key, TRANSLATIONS["en"].get(key, key))

# -----------------------------------------------------------------------------
# 4. Comprehensive Theme & Accessibility CSS Engine (DARK MODE TEXT FIX)
# -----------------------------------------------------------------------------
is_dark = (st.session_state["theme"] == "dark")
high_contrast = st.session_state["high_contrast"]
font_scale = 1.0
if st.session_state["font_size"] == "Large":
    font_scale = 1.15
elif st.session_state["font_size"] == "Extra Large":
    font_scale = 1.30

if is_dark:
    if high_contrast:
        theme_tokens = """
        :root {
            --bg-main: #000000;
            --bg-card: #0A0F1D;
            --bg-card-hover: #131E35;
            --border-card: #F59E0B;
            --border-focus: #FBBF24;
            --text-title: #FFFFFF;
            --text-body: #FFFFFF;
            --text-muted: #E2E8F0;
            --hero-bg: #0A0F1D;
            --explainer-bg: #0F172A;
            --navbar-bg: #050811;
            --sidebar-bg: #050811;
            --chip-bg: #2E1065;
            --chip-text: #FDE047;
            --input-bg: #0A0F1D;
            --input-text: #FFFFFF;
        }
        """
    else:
        theme_tokens = """
        :root {
            --bg-main: #0B0F19;
            --bg-card: #131D33;
            --bg-card-hover: #1A2744;
            --border-card: #223354;
            --border-focus: #F59E0B;
            --text-title: #FFFFFF;
            --text-body: #F1F5F9;
            --text-muted: #CBD5E1;
            --hero-bg: linear-gradient(135deg, #1E1B4B 0%, #172554 50%, #0B0F19 100%);
            --explainer-bg: #111A2E;
            --navbar-bg: #0F172A;
            --sidebar-bg: #0F172A;
            --chip-bg: rgba(139, 92, 246, 0.25);
            --chip-text: #E9D5FF;
            --input-bg: #131D33;
            --input-text: #FFFFFF;
        }
        """
else:
    if high_contrast:
        theme_tokens = """
        :root {
            --bg-main: #FFFFFF;
            --bg-card: #FFFFFF;
            --bg-card-hover: #F8FAFC;
            --border-card: #000000;
            --border-focus: #2563EB;
            --text-title: #000000;
            --text-body: #000000;
            --text-muted: #1E293B;
            --hero-bg: #FFFFFF;
            --explainer-bg: #F8FAFC;
            --navbar-bg: #FFFFFF;
            --sidebar-bg: #FFFFFF;
            --chip-bg: #E0E7FF;
            --chip-text: #1E1B4B;
            --input-bg: #FFFFFF;
            --input-text: #000000;
        }
        """
    else:
        theme_tokens = """
        :root {
            --bg-main: #F8FAFC;
            --bg-card: #FFFFFF;
            --bg-card-hover: #F1F5F9;
            --border-card: #E2E8F0;
            --border-focus: #3B82F6;
            --text-title: #0F172A;
            --text-body: #1E293B;
            --text-muted: #475569;
            --hero-bg: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 50%, #F8FAFC 100%);
            --explainer-bg: #F1F5F9;
            --navbar-bg: #FFFFFF;
            --sidebar-bg: #FFFFFF;
            --chip-bg: #EDE9FE;
            --chip-text: #6D28D9;
            --input-bg: #FFFFFF;
            --input-text: #0F172A;
        }
        """

focus_css = """
    *:focus-visible {
        outline: 3px solid #F59E0B !important;
        outline-offset: 2px !important;
    }
""" if st.session_state["focus_indicators"] else ""

st.markdown(f"""
<style>
    {theme_tokens}
    
    html, body, [class*="st-"] {{
        font-size: {font_scale * 100}% !important;
    }}
    
    .stApp {{
        background-color: var(--bg-main) !important;
        color: var(--text-body) !important;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }}
    
    /* Global Typography Fix for Dark Mode */
    h1, h2, h3, h4, h5, h6 {{
        color: var(--text-title) !important;
        font-weight: 750 !important;
    }}
    p, span, label, div {{
        color: var(--text-body);
    }}
    .stMarkdown p {{
        color: var(--text-body) !important;
    }}
    
    /* Streamlit Input Fields & Selectboxes Text Fix */
    div[data-baseweb="input"] {{
        background-color: var(--input-bg) !important;
        border-color: var(--border-card) !important;
        color: var(--input-text) !important;
    }}
    input {{
        color: var(--input-text) !important;
        background-color: transparent !important;
    }}
    input::placeholder {{
        color: var(--text-muted) !important;
        opacity: 0.8 !important;
    }}
    div[data-baseweb="select"] > div {{
        background-color: var(--input-bg) !important;
        border-color: var(--border-card) !important;
        color: var(--input-text) !important;
    }}
    div[data-baseweb="popover"] div {{
        background-color: var(--bg-card) !important;
        color: var(--input-text) !important;
    }}
    
    /* Streamlit Buttons Text Fix */
    .stButton > button {{
        color: var(--text-title) !important;
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-card) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button:hover {{
        border-color: var(--border-focus) !important;
        background-color: var(--bg-card-hover) !important;
        color: #F59E0B !important;
    }}
    .stButton > button[kind="primary"] {{
        background: linear-gradient(90deg, #F59E0B, #D97706) !important;
        color: #0F172A !important;
        font-weight: 800 !important;
        border: none !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        background: linear-gradient(90deg, #FBBF24, #F59E0B) !important;
        color: #000000 !important;
    }}
    
    /* Sidebar Text & Label Visibility */
    [data-testid="stSidebar"] {{
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border-card) !important;
    }}
    [data-testid="stSidebar"] * {{
        color: var(--text-body) !important;
    }}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
        color: var(--text-title) !important;
    }}
    
    /* Top Navbar */
    .top-navbar {{
        background-color: var(--navbar-bg);
        border: 1px solid var(--border-card);
        border-radius: 14px;
        padding: 12px 20px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    
    /* Hero Banner */
    .hero-banner {{
        background: var(--hero-bg);
        border: 1px solid var(--border-card);
        border-radius: 16px;
        padding: 30px 34px;
        margin-bottom: 24px;
    }}
    .hero-title {{
        font-size: 2.4rem;
        font-weight: 800;
        color: var(--text-title) !important;
        margin: 0;
    }}
    .hero-tag {{
        display: inline-block;
        background: linear-gradient(90deg, #F59E0B, #D97706);
        color: #0F172A !important;
        font-weight: 800;
        font-size: 0.75rem;
        padding: 4px 12px;
        border-radius: 20px;
        text-transform: uppercase;
        margin-bottom: 12px;
        letter-spacing: 0.8px;
    }}
    .hero-subtitle {{
        color: var(--text-muted) !important;
        font-size: 1.1rem;
        margin-top: 8px;
        max-width: 820px;
        line-height: 1.5;
    }}

    /* Metric Cards */
    .metric-card {{
        background-color: var(--bg-card);
        border: 1px solid var(--border-card);
        border-radius: 14px;
        padding: 18px 20px;
        height: 100%;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }}
    .metric-card:hover {{
        border-color: var(--border-focus);
        transform: translateY(-2px);
    }}
    .metric-label {{
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 700;
        color: var(--text-muted) !important;
        margin-bottom: 6px;
    }}
    .metric-value {{
        font-size: 2rem;
        font-weight: 800;
        color: var(--text-title) !important;
        margin-bottom: 4px;
        line-height: 1.15;
    }}
    .metric-desc {{
        font-size: 0.86rem;
        color: #38BDF8 !important;
        line-height: 1.4;
    }}

    /* Movie Cards */
    .movie-card {{
        background-color: var(--bg-card);
        border: 1px solid var(--border-card);
        border-radius: 14px;
        overflow: hidden;
        transition: transform 0.2s ease, border-color 0.2s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
    }}
    .movie-card:hover {{
        border-color: #8B5CF6;
        transform: translateY(-3px);
    }}
    .movie-card-img {{
        width: 100%;
        height: 280px;
        object-fit: cover;
        background-color: #1E293B;
    }}
    .movie-card-body {{
        padding: 16px;
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}
    .movie-card-title {{
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text-title) !important;
        margin-bottom: 6px;
        line-height: 1.3;
    }}
    .movie-card-genres {{
        font-size: 0.78rem;
        color: #8B5CF6 !important;
        margin-bottom: 10px;
        font-weight: 600;
    }}
    .movie-card-meta {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 0.85rem;
        color: var(--text-muted) !important;
        border-top: 1px solid var(--border-card);
        padding-top: 10px;
        margin-top: 8px;
    }}
    .badge-star {{
        background-color: #F59E0B;
        color: #0F172A !important;
        font-weight: 800;
        padding: 2px 7px;
        border-radius: 6px;
        font-size: 0.82rem;
    }}

    /* Details Card */
    .detail-card {{
        background-color: var(--bg-card);
        border: 1px solid var(--border-card);
        border-radius: 16px;
        padding: 26px;
        margin-bottom: 24px;
    }}
    .detail-title {{
        font-size: 2.2rem;
        font-weight: 800;
        color: var(--text-title) !important;
        margin: 0 0 6px 0;
        line-height: 1.2;
    }}
    .genre-chip {{
        display: inline-block;
        background-color: var(--chip-bg);
        border: 1px solid #8B5CF6;
        color: var(--chip-text) !important;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 20px;
        margin-right: 6px;
        margin-bottom: 8px;
    }}
    .rating-box {{
        background-color: var(--explainer-bg);
        border: 1px solid var(--border-card);
        border-radius: 12px;
        padding: 16px 20px;
        margin-top: 16px;
        margin-bottom: 16px;
    }}

    /* Explainer Cards */
    .chart-explainer {{
        background-color: var(--explainer-bg);
        border-left: 4px solid #F59E0B;
        border-radius: 0 10px 10px 0;
        padding: 14px 18px;
        margin-top: 10px;
        margin-bottom: 24px;
        font-size: 0.92rem;
        color: var(--text-body) !important;
        line-height: 1.5;
    }}
    .chart-explainer strong {{
        color: #F59E0B !important;
    }}
    .chart-takeaway {{
        margin-top: 6px;
        color: #38BDF8 !important;
        font-weight: 600;
    }}

    .section-title {{
        font-size: 1.5rem;
        font-weight: 800;
        color: var(--text-title) !important;
        margin-top: 26px;
        margin-bottom: 6px;
    }}
    .section-desc {{
        color: var(--text-muted) !important;
        font-size: 0.95rem;
        margin-bottom: 20px;
        line-height: 1.45;
    }}

    .friendly-box {{
        background-color: var(--bg-card);
        border: 1px dashed #F59E0B;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        color: var(--text-title) !important;
        font-size: 1rem;
        margin: 20px 0;
    }}

    {focus_css}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. Data Loading & Caching (MovieLens + Links)
# -----------------------------------------------------------------------------
@st.cache_data
def load_movie_data():
    movies_path = os.path.join(base_dir, "data", "movies.csv")
    ratings_path = os.path.join(base_dir, "data", "ratings.csv")
    links_path = os.path.join(base_dir, "data", "links.csv")

    movies_df = pd.read_csv(movies_path)
    ratings_df = pd.read_csv(ratings_path)
    links_df = pd.read_csv(links_path) if os.path.exists(links_path) else pd.DataFrame(columns=["movieId", "imdbId", "tmdbId"])

    movies_df["year"] = movies_df["title"].str.extract(r"\((\d{4})\)").astype(float)
    movies_df["clean_title"] = movies_df["title"].str.replace(r"\s*\(\d{4}\)", "", regex=True).str.strip()

    stats = ratings_df.groupby("movieId").agg(
        rating_count=("rating", "count"),
        mean_rating=("rating", "mean")
    ).reset_index()

    merged = pd.merge(movies_df, stats, on="movieId", how="left")
    merged["rating_count"] = merged["rating_count"].fillna(0).astype(int)
    merged["mean_rating"] = merged["mean_rating"].fillna(0.0).round(2)

    if not links_df.empty:
        merged = pd.merge(merged, links_df[["movieId", "imdbId", "tmdbId"]], on="movieId", how="left")
    else:
        merged["imdbId"] = np.nan
        merged["tmdbId"] = np.nan

    # Fair Score (Bayesian Weighted Rating)
    C = ratings_df["rating"].mean() # ~3.50 global mean
    m = 50
    v = merged["rating_count"]
    R = merged["mean_rating"]
    merged["fair_score"] = ((v / (v + m)) * R + (m / (v + m)) * C).round(2)

    # Exploded Genres
    movies_genre = movies_df.copy()
    movies_genre["genre_list"] = movies_genre["genres"].str.split("|")
    exploded = movies_genre.explode("genre_list").rename(columns={"genre_list": "genre"})
    exploded = exploded[exploded["genre"] != "(no genres listed)"]

    genre_ratings = pd.merge(ratings_df, exploded[["movieId", "genre"]], on="movieId", how="inner")

    return movies_df, ratings_df, merged, exploded, genre_ratings

movies_df, ratings_df, merged_df, exploded_df, genre_ratings = load_movie_data()

total_movies = len(movies_df)
total_ratings = len(ratings_df)
total_users = ratings_df["userId"].nunique()
avg_rating_global = round(ratings_df["rating"].mean(), 2)
min_year = int(movies_df["year"].dropna().min())
max_year = int(movies_df["year"].dropna().max())
all_genres = sorted([g for g in exploded_df["genre"].dropna().unique() if g != "(no genres listed)"])

# -----------------------------------------------------------------------------
# 6. OMDb API Fetcher (Cached)
# -----------------------------------------------------------------------------
DEFAULT_OMDB_KEY = "trilogy"

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_omdb_details(imdb_id=None, title=None, year=None, custom_key=None):
    api_key = custom_key.strip() if custom_key and custom_key.strip() else os.environ.get("OMDB_API_KEY", DEFAULT_OMDB_KEY)
    params = {"apikey": api_key}
    
    if imdb_id and pd.notna(imdb_id):
        try:
            params["i"] = f"tt{int(imdb_id):07d}"
        except:
            params["i"] = str(imdb_id)
    elif title:
        params["t"] = str(title).strip()
        if year and pd.notna(year):
            params["y"] = str(int(year))
    else:
        return None

    url = f"https://www.omdbapi.com/?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "CineScope/2.0"})

    try:
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode())
            if data.get("Response") == "True":
                return {
                    "found": True,
                    "title": data.get("Title", title),
                    "year": data.get("Year", year),
                    "poster": data.get("Poster") if data.get("Poster") != "N/A" else None,
                    "plot": data.get("Plot") if data.get("Plot") != "N/A" else "No plot summary available.",
                    "director": data.get("Director") if data.get("Director") != "N/A" else "Unknown",
                    "actors": data.get("Actors") if data.get("Actors") != "N/A" else "Unknown",
                    "runtime": data.get("Runtime") if data.get("Runtime") != "N/A" else "Unknown",
                    "language": data.get("Language") if data.get("Language") != "N/A" else "English",
                    "released": data.get("Released") if data.get("Released") != "N/A" else "Unknown",
                    "imdb_rating": data.get("imdbRating") if data.get("imdbRating") != "N/A" else "N/A",
                    "imdb_votes": data.get("imdbVotes") if data.get("imdbVotes") != "N/A" else "N/A",
                    "imdb_id": data.get("imdbID")
                }
            else:
                return {"found": False, "error": data.get("Error", "Movie not found")}
    except Exception as e:
        return {"found": False, "error": str(e)}

# -----------------------------------------------------------------------------
# 7. Helper Utilities (Search, Posters, PDF Generator)
# -----------------------------------------------------------------------------
def search_local_movies(query, df):
    query = query.strip().lower()
    tokens = [t for t in query.split() if t]
    if not tokens:
        return df.head(0)
    mask = df["title"].str.lower().apply(lambda t: all(tok in t for tok in tokens))
    return df[mask]

def get_poster_html(poster_url, title):
    if poster_url:
        return f'<img src="{poster_url}" class="movie-card-img" alt="{title}">'
    else:
        return f'''
        <div class="movie-card-img" style="display:flex; flex-direction:column; align-items:center; justify-content:center; color:#94A3B8; padding:16px; text-align:center;">
            <span style="font-size:3rem; margin-bottom:8px;">🎬</span>
            <span style="font-size:0.85rem; font-weight:700; color:var(--text-title);">{title}</span>
        </div>
        '''

def generate_pdf_report(filtered_df):
    """Generate a clean, professional executive PDF report using fpdf2."""
    class ExecutivePDF(FPDF):
        def header(self):
            self.set_font('helvetica', 'B', 15)
            self.set_text_color(30, 41, 59)
            self.cell(0, 10, 'CineScope 2.0 - Executive Analytics Report', align='C', new_x='LMARGIN', new_y='NEXT')
            self.set_font('helvetica', 'I', 9)
            self.set_text_color(100, 116, 139)
            self.cell(0, 6, 'Movie Ratings & Genre Trends | Project ID: DA-006 | GroupLens MovieLens Benchmark', align='C', new_x='LMARGIN', new_y='NEXT')
            self.set_draw_color(245, 158, 11)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(4)

        def footer(self):
            self.set_y(-15)
            self.set_font('helvetica', 'I', 8)
            self.set_text_color(148, 163, 184)
            self.cell(0, 10, f'Page {self.page_no()}', align='C')

    pdf = ExecutivePDF()
    pdf.add_page()
    
    # 1. Executive Summary
    pdf.set_font('helvetica', 'B', 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, '1. Executive Project Summary', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('helvetica', '', 9.5)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(0, 5, 'This report presents an empirical analysis of over 100,000 real audience ratings across 9,742 movies spanning 1902 to 2018. It examines genre performance, temporal releases, and Bayesian fair ranking metrics to guide content curation and recommendation algorithms.')
    pdf.ln(3)

    # 2. Key Metrics
    pdf.set_font('helvetica', 'B', 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, '2. Verified Dataset Key Metrics', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('helvetica', '', 9)
    pdf.set_text_color(51, 65, 85)
    summary_data = [
        ('Total Catalog Movies:', f"{total_movies:,} unique titles"),
        ('Total Audience Ratings:', f"{total_ratings:,} verified reviews"),
        ('Active Reviewers:', f"{total_users:,} users (each rated >= 20 movies)"),
        ('Global Mean Rating:', f"{avg_rating_global} out of 5.0 stars"),
        ('Top Ranked Movie (Fair Score):', 'The Shawshank Redemption (4.43 stars, 317 votes)'),
        ('Most Rated Blockbuster:', 'Forrest Gump (329 votes, 4.16 stars)'),
        ('Most Popular Genre by Volume:', 'Drama (41,928 ratings)'),
        ('Highest Rated Niche Genre:', 'Film-Noir (3.92 average rating)')
    ]
    for k, v in summary_data:
        pdf.set_font('helvetica', 'B', 9)
        pdf.cell(65, 6, k)
        pdf.set_font('helvetica', '', 9)
        pdf.cell(0, 6, v, new_x='LMARGIN', new_y='NEXT')
    pdf.ln(4)

    # 3. Top 10 Leaderboard
    pdf.set_font('helvetica', 'B', 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, '3. Top 10 Ranked Movies (Fair Bayesian Scoring)', new_x='LMARGIN', new_y='NEXT')
    
    # Table Header
    pdf.set_fill_color(30, 41, 59)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('helvetica', 'B', 8.5)
    pdf.cell(85, 6, 'Movie Title', border=1, fill=True)
    pdf.cell(18, 6, 'Year', border=1, fill=True, align='C')
    pdf.cell(30, 6, 'Rating / 5.0', border=1, fill=True, align='C')
    pdf.cell(25, 6, 'Votes', border=1, fill=True, align='C')
    pdf.cell(32, 6, 'Fair Score', border=1, fill=True, align='C', new_x='LMARGIN', new_y='NEXT')

    # Table Rows
    pdf.set_text_color(51, 65, 85)
    pdf.set_font('helvetica', '', 8.5)
    top10_export = filtered_df[filtered_df["rating_count"] >= 50].sort_values("fair_score", ascending=False).head(10)
    for _, r in top10_export.iterrows():
        title_safe = str(r['clean_title'])[:42]
        yr_safe = str(int(r['year'])) if pd.notna(r['year']) else 'N/A'
        pdf.cell(85, 5.5, title_safe, border=1)
        pdf.cell(18, 5.5, yr_safe, border=1, align='C')
        pdf.cell(30, 5.5, f"{r['mean_rating']:.2f}", border=1, align='C')
        pdf.cell(25, 5.5, str(r['rating_count']), border=1, align='C')
        pdf.cell(32, 5.5, f"{r['fair_score']:.2f}", border=1, align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(4)

    # 4. Key Takeaways
    pdf.set_font('helvetica', 'B', 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, '4. Key Analytical Insights', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('helvetica', '', 8.5)
    pdf.set_text_color(51, 65, 85)
    insights = [
        "1. Film-Noir (3.92) and War (3.81) lead in average ratings due to dedicated, passionate audiences.",
        "2. Drama (41,928 ratings) and Comedy (39,053 ratings) generate over 40% of all catalog interactions.",
        "3. 4.0 stars is the single most common rating (26.6%), and 69.9% of all reviews use whole-star ratings.",
        "4. A minimum vote threshold (e.g. N >= 50) is vital to eliminate small-sample noise from 1-vote films."
    ]
    for ins in insights:
        pdf.multi_cell(0, 4.5, ins)
        pdf.ln(1)

    return bytes(pdf.output())

# -----------------------------------------------------------------------------
# 8. Top Navigation Bar
# -----------------------------------------------------------------------------
nav_c1, nav_c2, nav_c3, nav_c4 = st.columns([1.2, 5.5, 1.8, 1.8])

with nav_c1:
    if st.button("☰ Menu", key="btn_hamburger", use_container_width=True):
        st.session_state["sidebar_open"] = not st.session_state["sidebar_open"]
        st.rerun()

with nav_c2:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px; height:100%; padding-top:4px;">
        <span style="font-size:1.8rem;">🎬</span>
        <div>
            <span style="font-size:1.35rem; font-weight:800; color:var(--text-title); letter-spacing:-0.5px;">{t("app_title")}</span>
            <span style="font-size:0.8rem; color:#F59E0B; font-weight:700; margin-left:8px; text-transform:uppercase;">v2.0</span><br>
            <span style="font-size:0.8rem; color:var(--text-muted);">{t("app_tagline")}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with nav_c3:
    current_lang = st.session_state["language"]
    target_lang = "hi" if current_lang == "en" else "en"
    lang_btn_label = "🇮🇳 हिंदी" if current_lang == "en" else "🇬🇧 English"
    if st.button(lang_btn_label, key="btn_lang_switch", use_container_width=True):
        st.session_state["language"] = target_lang
        st.rerun()

with nav_c4:
    current_theme = st.session_state["theme"]
    target_theme = "light" if current_theme == "dark" else "dark"
    theme_btn_label = "☀️ Light Mode" if current_theme == "dark" else "🌙 Dark Mode"
    if st.button(theme_btn_label, key="btn_theme_switch", use_container_width=True):
        st.session_state["theme"] = target_theme
        st.rerun()

st.markdown("<hr style='margin: 8px 0 20px 0; border: none; border-top: 1px solid var(--border-card);'>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 9. Sidebar Navigation (Icons + Text Labels)
# -----------------------------------------------------------------------------
if st.session_state["sidebar_open"]:
    st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 10px 0 16px 0;">
        <span style="font-size: 2.3rem;">🎬</span>
        <h2 style="color: var(--text-title); font-size: 1.35rem; margin: 4px 0 0 0; font-weight: 800;">{t("app_title")} 2.0</h2>
        <p style="color: #F59E0B; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; margin: 0;">Movie Discovery & Analytics</p>
    </div>
    """, unsafe_allow_html=True)

    nav_map = {
        "home": t("nav_home"),
        "search": t("nav_search"),
        "compare": t("nav_compare"),
        "surprise": t("nav_surprise"),
        "analytics": t("nav_analytics"),
        "genres": t("nav_genres"),
        "top": t("nav_top"),
        "insights": t("nav_insights"),
        "watchlist": f"{t('nav_watchlist')} ({len(st.session_state['watchlist'])})",
        "reports": t("nav_reports"),
        "accessibility": t("nav_accessibility"),
        "about": t("nav_about")
    }

    keys = list(nav_map.keys())
    values = list(nav_map.values())
    curr_idx = keys.index(st.session_state["current_page"]) if st.session_state["current_page"] in keys else 0

    selected_nav_label = st.sidebar.radio(
        "Navigation Menu:",
        values,
        index=curr_idx,
        label_visibility="collapsed"
    )

    new_page_key = keys[values.index(selected_nav_label)]
    if new_page_key != st.session_state["current_page"]:
        st.session_state["current_page"] = new_page_key
        st.rerun()

    st.sidebar.markdown("---")
    
    # User Personal Ratings Count Badge
    rated_count = len(st.session_state["user_ratings"])
    st.sidebar.markdown(f"""
    <div style="background-color: var(--bg-card); border-radius: 10px; padding: 12px; border: 1px solid var(--border-card); margin-bottom: 12px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-weight:700; font-size:0.85rem; color:var(--text-title);">⭐ Rated Movies</span>
            <span style="background:#F59E0B; color:#0F172A; font-weight:800; font-size:0.75rem; padding:2px 8px; border-radius:12px;">{rated_count}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    custom_omdb_key = st.sidebar.text_input(
        "OMDb API Key:",
        value="",
        type="password",
        help="Optional personal key from omdbapi.com for unlimited worldwide search. A working fallback key is active by default."
    )
else:
    custom_omdb_key = ""

# =============================================================================
# PAGE 1: 🏠 HOME
# =============================================================================
if st.session_state["current_page"] == "home":
    st.markdown(f"""
    <div class="hero-banner">
        <span class="hero-tag">{t("hero_tag")}</span>
        <h1 class="hero-title">{t("hero_heading")}</h1>
        <p class="hero-subtitle">{t("hero_subtitle")}</p>
    </div>
    """, unsafe_allow_html=True)

    # Search Bar
    col_s1, col_s2 = st.columns([5, 1])
    with col_s1:
        home_query = st.text_input(
            "Search for any movie:",
            placeholder=t("search_placeholder"),
            label_visibility="collapsed"
        )
    with col_s2:
        btn_home_search = st.button(t("search_btn"), use_container_width=True, type="primary")

    if btn_home_search and home_query.strip():
        st.session_state["search_query"] = home_query.strip()
        st.session_state["current_page"] = "search"
        st.rerun()

    st.markdown(f"""
    <div style="margin-top: -6px; margin-bottom: 24px; font-size: 0.85rem; color: var(--text-muted);">
        <strong style="color: #F59E0B;">{t("quick_try")}</strong>
        <span>Interstellar • Inception • The Dark Knight • Titanic • 3 Idiots • Dangal • The Shawshank Redemption • Pulp Fiction</span>
    </div>
    """, unsafe_allow_html=True)

    # 4 Key Live Metric Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{t("total_movies")}</div>
            <div class="metric-value">{total_movies:,}</div>
            <div class="metric-desc">{t("total_movies_desc")}</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{t("total_ratings")}</div>
            <div class="metric-value">{total_ratings:,}</div>
            <div class="metric-desc">{t("total_ratings_desc")}</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{t("active_users")}</div>
            <div class="metric-value">{total_users:,}</div>
            <div class="metric-desc">{t("active_users_desc")}</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{t("avg_rating")}</div>
            <div class="metric-value">{avg_rating_global} <span style="font-size:1.1rem; color:#F59E0B;">★</span></div>
            <div class="metric-desc">{t("avg_rating_desc")}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Featured Blockbusters Showcase
    st.markdown(f'<div class="section-title">{t("featured_title")}</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-desc">{t("featured_desc")}</p>', unsafe_allow_html=True)

    featured_titles = ["The Shawshank Redemption", "The Dark Knight", "Inception", "Interstellar"]
    f_cols = st.columns(4)

    for idx, f_title in enumerate(featured_titles):
        with f_cols[idx]:
            matches = search_local_movies(f_title, merged_df)
            if not matches.empty:
                m_row = matches.iloc[0]
                omdb_info = fetch_omdb_details(imdb_id=m_row.get("imdbId"), title=m_row["clean_title"], year=m_row["year"], custom_key=custom_omdb_key)
                poster = omdb_info.get("poster") if omdb_info and omdb_info.get("found") else None

                st.markdown(f"""
                <div class="movie-card">
                    {get_poster_html(poster, m_row['clean_title'])}
                    <div class="movie-card-body">
                        <div>
                            <div class="movie-card-title">{m_row['clean_title']} ({int(m_row['year']) if pd.notna(m_row['year']) else 'N/A'})</div>
                            <div class="movie-card-genres">{m_row['genres'].replace('|', ' • ')}</div>
                        </div>
                        <div class="movie-card-meta">
                            <span><span class="badge-star">★ {m_row['mean_rating']}</span> ({m_row['rating_count']} votes)</span>
                            <span style="color: #38BDF8; font-weight:700;">Fair: {m_row['fair_score']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(t("view_details"), key=f"btn_feat_{m_row['movieId']}", use_container_width=True):
                    st.session_state["selected_movie_id"] = m_row["movieId"]
                    st.session_state["current_page"] = "search"
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # 3 Navigation Quick Banners
    c_b1, c_b2, c_b3 = st.columns(3)
    with c_b1:
        st.markdown(f"""
        <div style="background-color: var(--bg-card); border: 1px solid var(--border-card); border-radius: 14px; padding: 22px;">
            <h3 style="color: var(--text-title); margin: 0 0 6px 0; font-size: 1.25rem;">⚖️ {t('nav_compare')}</h3>
            <p style="color: var(--text-muted); font-size: 0.92rem; margin-bottom: 14px;">Compare two movies side by side with winner badges.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Compare Movies ➔", key="btn_cta_comp", use_container_width=True, type="primary"):
            st.session_state["current_page"] = "compare"
            st.rerun()

    with c_b2:
        st.markdown(f"""
        <div style="background-color: var(--bg-card); border: 1px solid var(--border-card); border-radius: 14px; padding: 22px;">
            <h3 style="color: var(--text-title); margin: 0 0 6px 0; font-size: 1.25rem;">🎲 {t('nav_surprise')}</h3>
            <p style="color: var(--text-muted); font-size: 0.92rem; margin-bottom: 14px;">Let CineScope discover a random great movie for you.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Surprise Me ➔", key="btn_cta_surp", use_container_width=True):
            st.session_state["current_page"] = "surprise"
            st.rerun()

    with c_b3:
        st.markdown(f"""
        <div style="background-color: var(--bg-card); border: 1px solid var(--border-card); border-radius: 14px; padding: 22px;">
            <h3 style="color: var(--text-title); margin: 0 0 6px 0; font-size: 1.25rem;">📥 {t('nav_reports')}</h3>
            <p style="color: var(--text-muted); font-size: 0.92rem; margin-bottom: 14px;">Download CSV tables and executive PDF analysis reports.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Get Reports ➔", key="btn_cta_rep", use_container_width=True):
            st.session_state["current_page"] = "reports"
            st.rerun()

# =============================================================================
# PAGE 2: 🔍 MOVIE SEARCH AND DETAILS (WITH PERSONAL RATING FEATURE)
# =============================================================================
elif st.session_state["current_page"] == "search":
    st.markdown(f'<div class="section-title">🔍 {t("nav_search")}</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-desc">{t("hero_subtitle")}</p>', unsafe_allow_html=True)

    search_col1, search_col2 = st.columns([5, 1])
    with search_col1:
        query_input = st.text_input(
            "Search movie title:",
            value=st.session_state["search_query"],
            placeholder=t("search_placeholder"),
            label_visibility="collapsed"
        )
    with search_col2:
        btn_search = st.button(t("search_btn"), use_container_width=True, type="primary")

    if btn_search or (query_input and query_input != st.session_state["search_query"]):
        st.session_state["search_query"] = query_input
        st.session_state["selected_movie_id"] = None
        st.rerun()

    active_query = st.session_state["search_query"].strip()

    # Detail View If Movie Selected
    if st.session_state["selected_movie_id"] is not None:
        sel_row = merged_df[merged_df["movieId"] == st.session_state["selected_movie_id"]]
        if not sel_row.empty:
            movie = sel_row.iloc[0]
            
            with st.spinner("Loading movie details, poster, and cast..."):
                omdb = fetch_omdb_details(imdb_id=movie.get("imdbId"), title=movie["clean_title"], year=movie["year"], custom_key=custom_omdb_key)

            if st.button(t("back_to_results"), type="secondary"):
                st.session_state["selected_movie_id"] = None
                st.rerun()

            d_col1, d_col2 = st.columns([1, 2.2])

            with d_col1:
                poster_url = omdb.get("poster") if omdb and omdb.get("found") else None
                if poster_url:
                    st.image(poster_url, use_container_width=True)
                else:
                    st.markdown(f"""
                    <div style="background-color: var(--bg-card); border-radius: 12px; height: 380px; display:flex; flex-direction:column; align-items:center; justify-content:center; color:#94A3B8; border:1px solid var(--border-card);">
                        <span style="font-size: 3.5rem;">🎬</span>
                        <p style="font-size: 0.9rem; margin-top:8px;">No Poster Available</p>
                    </div>
                    """, unsafe_allow_html=True)

                # Watchlist Action Button
                movie_key_str = str(movie["movieId"])
                is_in_watchlist = movie_key_str in st.session_state["watchlist"]

                if is_in_watchlist:
                    if st.button(f"✓ {t('in_watchlist')} ({t('remove_watchlist')})", use_container_width=True, type="secondary"):
                        del st.session_state["watchlist"][movie_key_str]
                        save_json(watchlist_file, st.session_state["watchlist"])
                        st.rerun()
                else:
                    if st.button(t("add_watchlist"), use_container_width=True, type="primary"):
                        st.session_state["watchlist"][movie_key_str] = {
                            "movieId": int(movie["movieId"]),
                            "title": str(movie["clean_title"]),
                            "year": int(movie["year"]) if pd.notna(movie["year"]) else None,
                            "genres": str(movie["genres"]),
                            "rating": float(movie["mean_rating"]),
                            "status": "Want to Watch"
                        }
                        save_json(watchlist_file, st.session_state["watchlist"])
                        st.rerun()

                # External Links
                if pd.notna(movie.get("imdbId")):
                    imdb_link = f"https://www.imdb.com/title/tt{int(movie['imdbId']):07d}/"
                    st.markdown(f'<a href="{imdb_link}" target="_blank" style="display:block; text-align:center; background-color:#F59E0B; color:#0F172A; font-weight:700; padding:8px; border-radius:8px; margin-top:10px; text-decoration:none;">View on IMDb ↗</a>', unsafe_allow_html=True)

            with d_col2:
                st.markdown(f"""
                <div class="detail-card">
                    <h1 class="detail-title">{movie['clean_title']} <span style="color:var(--text-muted); font-size:1.6rem;">({int(movie['year']) if pd.notna(movie['year']) else 'N/A'})</span></h1>
                """, unsafe_allow_html=True)

                genre_chips_html = "".join([f'<span class="genre-chip">{g.strip()}</span>' for g in movie["genres"].split("|") if g.strip()])
                st.markdown(genre_chips_html, unsafe_allow_html=True)

                # Ratings Breakdown Box
                existing_user_rating = st.session_state["user_ratings"].get(movie_key_str, {}).get("user_rating", None)

                st.markdown(f"""
                <div class="rating-box">
                    <div style="display: flex; gap: 24px; flex-wrap: wrap;">
                        <div>
                            <span style="font-size:0.75rem; text-transform:uppercase; color:var(--text-muted); font-weight:700;">{t("movielens_score")}</span>
                            <div style="font-size:1.6rem; font-weight:800; color:#F59E0B;">★ {movie['mean_rating']} <span style="font-size:0.9rem; color:var(--text-muted);">/ 5.0</span></div>
                            <span style="font-size:0.8rem; color:#38BDF8;">{movie['rating_count']} verified reviews</span>
                        </div>
                        <div>
                            <span style="font-size:0.75rem; text-transform:uppercase; color:var(--text-muted); font-weight:700;">{t("fair_score")}</span>
                            <div style="font-size:1.6rem; font-weight:800; color:#10B981;">{movie['fair_score']} <span style="font-size:0.9rem; color:var(--text-muted);">/ 5.0</span></div>
                            <span style="font-size:0.8rem; color:#10B981;">Bayesian vote-weighted score</span>
                        </div>
                        {f'''
                        <div>
                            <span style="font-size:0.75rem; text-transform:uppercase; color:var(--text-muted); font-weight:700;">{t("external_score")}</span>
                            <div style="font-size:1.6rem; font-weight:800; color:#38BDF8;">⭐ {omdb.get("imdb_rating")} <span style="font-size:0.9rem; color:var(--text-muted);">/ 10</span></div>
                            <span style="font-size:0.8rem; color:var(--text-muted);">{omdb.get("imdb_votes")} IMDb votes</span>
                        </div>
                        ''' if omdb and omdb.get("found") and omdb.get("imdb_rating") != "N/A" else ''}
                        {f'''
                        <div>
                            <span style="font-size:0.75rem; text-transform:uppercase; color:#EC4899; font-weight:700;">Your Personal Rating</span>
                            <div style="font-size:1.6rem; font-weight:800; color:#EC4899;">★ {existing_user_rating} <span style="font-size:0.9rem; color:var(--text-muted);">/ 5.0</span></div>
                            <span style="font-size:0.8rem; color:#F472B6;">Saved locally on device</span>
                        </div>
                        ''' if existing_user_rating is not None else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # NEW FEATURE 2: Personal Movie Rating Box
                st.markdown(f"#### {t('personal_rating_title')}")
                p_c1, p_c2 = st.columns([3, 1])
                with p_c1:
                    user_star_pick = st.slider(
                        t("rate_this_movie"),
                        min_value=1.0,
                        max_value=5.0,
                        value=float(existing_user_rating) if existing_user_rating else 4.0,
                        step=0.5,
                        key=f"star_pick_{movie['movieId']}"
                    )
                with p_c2:
                    st.write("")
                    st.write("")
                    if st.button(t("save_rating_btn"), key=f"save_rate_{movie['movieId']}", use_container_width=True, type="primary"):
                        st.session_state["user_ratings"][movie_key_str] = {
                            "movieId": int(movie["movieId"]),
                            "title": str(movie["clean_title"]),
                            "user_rating": user_star_pick,
                            "updated": datetime.now().strftime("%Y-%m-%d %H:%M")
                        }
                        save_json(ratings_file, st.session_state["user_ratings"])
                        st.success(t("rating_saved_msg"))
                        st.rerun()

                st.markdown("""
                <p style="font-size:0.82rem; color:var(--text-muted); margin-top:-4px; margin-bottom:16px;">
                    ℹ️ <em>Note: Your personal rating is stored locally on your device and does not modify the original MovieLens research dataset.</em>
                </p>
                """, unsafe_allow_html=True)

                # Plot Summary
                plot_text = omdb.get("plot") if omdb and omdb.get("found") else "This title is cataloged in the MovieLens benchmark dataset with complete audience review distributions."
                st.markdown(f"""
                <div style="margin-bottom: 16px;">
                    <h4 style="color:var(--text-title); font-size:1rem; margin:0 0 4px 0;">{t("plot_title")}</h4>
                    <p style="color:var(--text-body); font-size:0.95rem; line-height:1.5;">{plot_text}</p>
                </div>
                """, unsafe_allow_html=True)

                # Metadata Attributes
                if omdb and omdb.get("found"):
                    st.markdown(f"""
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; font-size:0.88rem; color:var(--text-body);">
                        <div><strong style="color:var(--text-muted);">{t('director')}:</strong> {omdb.get('director')}</div>
                        <div><strong style="color:var(--text-muted);">{t('runtime')}:</strong> {omdb.get('runtime')}</div>
                        <div><strong style="color:var(--text-muted);">{t('cast')}:</strong> {omdb.get('actors')}</div>
                        <div><strong style="color:var(--text-muted);">{t('language')}:</strong> {omdb.get('language')}</div>
                        <div><strong style="color:var(--text-muted);">{t('released')}:</strong> {omdb.get('released')}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

    elif active_query:
        local_results = search_local_movies(active_query, merged_df)

        if not local_results.empty:
            st.markdown(f"#### 🎯 Found {len(local_results)} Matching Movies in Dataset:")
            grid_cols = st.columns(3)
            for idx, (_, row) in enumerate(local_results.head(12).iterrows()):
                col_idx = idx % 3
                with grid_cols[col_idx]:
                    st.markdown(f"""
                    <div class="metric-card" style="margin-bottom: 16px;">
                        <h4 style="margin: 0 0 4px 0; color:var(--text-title); font-size:1.15rem;">{row['clean_title']} <span style="color:var(--text-muted); font-size:0.9rem;">({int(row['year']) if pd.notna(row['year']) else 'N/A'})</span></h4>
                        <p style="color:#8B5CF6; font-size:0.8rem; margin:0 0 10px 0; font-weight:600;">{row['genres'].replace('|', ' • ')}</p>
                        <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--border-card); padding-top:8px;">
                            <span class="badge-star">★ {row['mean_rating']}</span>
                            <span style="font-size:0.82rem; color:var(--text-muted);">{row['rating_count']} reviews</span>
                            <span style="font-size:0.82rem; color:#10B981; font-weight:700;">Fair: {row['fair_score']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button(t("view_details"), key=f"sel_res_{row['movieId']}", use_container_width=True):
                        st.session_state["selected_movie_id"] = row["movieId"]
                        st.rerun()
        else:
            # Fallback to Worldwide OMDb search
            st.markdown(f"""
            <div class="friendly-box">
                <span style="font-size: 2.2rem;">🔍</span>
                <h3 style="color: var(--text-title); margin: 8px 0 4px 0;">Searching Worldwide Movie Database...</h3>
                <p style="color: var(--text-muted); font-size: 0.95rem; margin-bottom: 0;">
                    '{active_query}' was not found in the local MovieLens dataset (which covers movies up to 2018).<br>
                    Querying external worldwide database via OMDb...
                </p>
            </div>
            """, unsafe_allow_html=True)

            with st.spinner("Connecting to external movie database..."):
                ext_result = fetch_omdb_details(title=active_query, custom_key=custom_omdb_key)

            if ext_result and ext_result.get("found"):
                st.success(f"Found worldwide match for '{ext_result.get('title')}'!")
                ext_c1, ext_c2 = st.columns([1, 2])
                with ext_c1:
                    if ext_result.get("poster"):
                        st.image(ext_result.get("poster"), use_container_width=True)
                    else:
                        st.markdown('<div style="background:var(--bg-card); height:320px; border-radius:12px;"></div>', unsafe_allow_html=True)
                with ext_c2:
                    st.markdown(f"""
                    <div class="detail-card">
                        <span style="background:#3B82F6; color:#FFF; font-size:0.75rem; font-weight:800; padding:3px 10px; border-radius:12px; text-transform:uppercase;">External Search Result</span>
                        <h2 style="color:var(--text-title); margin:8px 0 4px 0;">{ext_result.get('title')} ({ext_result.get('year')})</h2>
                        <div class="rating-box">
                            <span style="font-size:0.8rem; color:var(--text-muted); font-weight:700;">{t("external_score")}</span>
                            <div style="font-size:1.6rem; font-weight:800; color:#F59E0B;">⭐ {ext_result.get('imdb_rating')} <span style="font-size:0.9rem; color:var(--text-muted);">/ 10</span></div>
                            <span style="font-size:0.8rem; color:#38BDF8;">from {ext_result.get('imdb_votes')} external user votes</span>
                        </div>
                        <p style="color:var(--text-body); font-size:0.95rem; line-height:1.5;"><strong>Plot:</strong> {ext_result.get('plot')}</p>
                        <p style="color:var(--text-body); font-size:0.88rem; margin:0;">
                            <strong>Director:</strong> {ext_result.get('director')}<br>
                            <strong>Cast:</strong> {ext_result.get('actors')}<br>
                            <strong>Runtime:</strong> {ext_result.get('runtime')} • <strong>Language:</strong> {ext_result.get('language')}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning(f"Could not find any movie named '{active_query}'. Try checking the spelling or searching a famous title like Inception, Titanic, or Interstellar.")
    else:
        st.markdown(f"""
        <div class="friendly-box">
            <span style="font-size: 3rem;">🔎</span>
            <h3 style="color: var(--text-title); margin: 12px 0 6px 0;">{t("search_placeholder")}</h3>
            <p style="color: var(--text-muted); font-size: 0.95rem; max-width: 600px; margin: 0 auto;">
                Type any movie name in the box above to explore its verified ratings, release year, genres, plot summary, and director.
            </p>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# PAGE 3: ⚖️ MOVIE COMPARISON (NEW FEATURE 1)
# =============================================================================
elif st.session_state["current_page"] == "compare":
    st.markdown(f'<div class="section-title">⚖️ {t("compare_heading")}</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-desc">{t("compare_subtitle")}</p>', unsafe_allow_html=True)

    # Clean Movie Selector Options
    movie_options = merged_df[merged_df["rating_count"] >= 5].sort_values("clean_title")
    movie_choices = {f"{r['clean_title']} ({int(r['year']) if pd.notna(r['year']) else 'N/A'})": r['movieId'] for _, r in movie_options.iterrows()}

    c_sel1, c_sel2 = st.columns(2)
    with c_sel1:
        # Default Inception
        def_idx1 = 0
        names_list = list(movie_choices.keys())
        for idx, name in enumerate(names_list):
            if "Inception" in name:
                def_idx1 = idx
                break
        pick_1_name = st.selectbox(t("compare_select_1"), names_list, index=def_idx1)
        pick_1_id = movie_choices[pick_1_name]

    with c_sel2:
        # Default Interstellar
        def_idx2 = 0
        for idx, name in enumerate(names_list):
            if "Interstellar" in name:
                def_idx2 = idx
                break
        pick_2_name = st.selectbox(t("compare_select_2"), names_list, index=def_idx2)
        pick_2_id = movie_choices[pick_2_name]

    movie_a = merged_df[merged_df["movieId"] == pick_1_id].iloc[0]
    movie_b = merged_df[merged_df["movieId"] == pick_2_id].iloc[0]

    # Fetch OMDb details
    with st.spinner("Fetching comparison details and posters..."):
        omdb_a = fetch_omdb_details(imdb_id=movie_a.get("imdbId"), title=movie_a["clean_title"], year=movie_a["year"], custom_key=custom_omdb_key)
        omdb_b = fetch_omdb_details(imdb_id=movie_b.get("imdbId"), title=movie_b["clean_title"], year=movie_b["year"], custom_key=custom_omdb_key)

    # Determine Winner
    score_a = float(movie_a["mean_rating"])
    score_b = float(movie_b["mean_rating"])
    votes_a = int(movie_a["rating_count"])
    votes_b = int(movie_b["rating_count"])

    comp_c1, comp_c2 = st.columns(2)

    with comp_c1:
        is_winner_a = (score_a >= score_b)
        winner_badge_a = f'<div style="background:#10B981; color:#0F172A; font-weight:800; font-size:0.8rem; padding:4px 10px; border-radius:12px; display:inline-block; margin-bottom:8px;">{t("higher_rating_badge")}</div>' if is_winner_a else ''
        votes_badge_a = f'<div style="background:#F59E0B; color:#0F172A; font-weight:800; font-size:0.8rem; padding:4px 10px; border-radius:12px; display:inline-block; margin-bottom:8px; margin-left:6px;">{t("more_votes_badge")}</div>' if votes_a > votes_b else ''

        st.markdown(f"""
        <div class="detail-card" style="border: 2px solid {'#10B981' if is_winner_a else 'var(--border-card)'};">
            {winner_badge_a}{votes_badge_a}
            <h2 style="color:var(--text-title); margin:0 0 6px 0;">{movie_a['clean_title']} ({int(movie_a['year']) if pd.notna(movie_a['year']) else 'N/A'})</h2>
            <p style="color:#8B5CF6; font-size:0.85rem; font-weight:600; margin-bottom:12px;">{movie_a['genres'].replace('|', ' • ')}</p>
        """, unsafe_allow_html=True)

        if omdb_a and omdb_a.get("poster"):
            st.image(omdb_a.get("poster"), width=220)

        st.markdown(f"""
            <div class="rating-box" style="margin-top:14px;">
                <div style="font-size:1.8rem; font-weight:800; color:#F59E0B;">★ {movie_a['mean_rating']} <span style="font-size:0.9rem; color:var(--text-muted);">/ 5.0</span></div>
                <div style="font-size:0.85rem; color:#38BDF8;">{movie_a['rating_count']} verified reviews</div>
                <div style="font-size:0.85rem; color:#10B981; margin-top:4px;"><strong>Fair Score:</strong> {movie_a['fair_score']}</div>
                {f'<div style="font-size:0.85rem; color:var(--text-muted); margin-top:4px;"><strong>IMDb:</strong> ⭐ {omdb_a.get("imdb_rating")}/10 ({omdb_a.get("imdb_votes")} votes)</div>' if omdb_a and omdb_a.get('imdb_rating') != 'N/A' else ''}
            </div>
            <p style="font-size:0.9rem; color:var(--text-body); line-height:1.45;"><strong>Director:</strong> {omdb_a.get('director', 'Unknown')}<br>
            <strong>Runtime:</strong> {omdb_a.get('runtime', 'Unknown')} • <strong>Cast:</strong> {omdb_a.get('actors', 'Unknown')}</p>
        </div>
        """, unsafe_allow_html=True)

    with comp_c2:
        is_winner_b = (score_b >= score_a)
        winner_badge_b = f'<div style="background:#10B981; color:#0F172A; font-weight:800; font-size:0.8rem; padding:4px 10px; border-radius:12px; display:inline-block; margin-bottom:8px;">{t("higher_rating_badge")}</div>' if is_winner_b else ''
        votes_badge_b = f'<div style="background:#F59E0B; color:#0F172A; font-weight:800; font-size:0.8rem; padding:4px 10px; border-radius:12px; display:inline-block; margin-bottom:8px; margin-left:6px;">{t("more_votes_badge")}</div>' if votes_b > votes_a else ''

        st.markdown(f"""
        <div class="detail-card" style="border: 2px solid {'#10B981' if is_winner_b else 'var(--border-card)'};">
            {winner_badge_b}{votes_badge_b}
            <h2 style="color:var(--text-title); margin:0 0 6px 0;">{movie_b['clean_title']} ({int(movie_b['year']) if pd.notna(movie_b['year']) else 'N/A'})</h2>
            <p style="color:#8B5CF6; font-size:0.85rem; font-weight:600; margin-bottom:12px;">{movie_b['genres'].replace('|', ' • ')}</p>
        """, unsafe_allow_html=True)

        if omdb_b and omdb_b.get("poster"):
            st.image(omdb_b.get("poster"), width=220)

        st.markdown(f"""
            <div class="rating-box" style="margin-top:14px;">
                <div style="font-size:1.8rem; font-weight:800; color:#F59E0B;">★ {movie_b['mean_rating']} <span style="font-size:0.9rem; color:var(--text-muted);">/ 5.0</span></div>
                <div style="font-size:0.85rem; color:#38BDF8;">{movie_b['rating_count']} verified reviews</div>
                <div style="font-size:0.85rem; color:#10B981; margin-top:4px;"><strong>Fair Score:</strong> {movie_b['fair_score']}</div>
                {f'<div style="font-size:0.85rem; color:var(--text-muted); margin-top:4px;"><strong>IMDb:</strong> ⭐ {omdb_b.get("imdb_rating")}/10 ({omdb_b.get("imdb_votes")} votes)</div>' if omdb_b and omdb_b.get('imdb_rating') != 'N/A' else ''}
            </div>
            <p style="font-size:0.9rem; color:var(--text-body); line-height:1.45;"><strong>Director:</strong> {omdb_b.get('director', 'Unknown')}<br>
            <strong>Runtime:</strong> {omdb_b.get('runtime', 'Unknown')} • <strong>Cast:</strong> {omdb_b.get('actors', 'Unknown')}</p>
        </div>
        """, unsafe_allow_html=True)

    # Comparison Summary Card in Plain English
    diff = abs(score_a - score_b)
    higher_movie = movie_a['clean_title'] if score_a > score_b else (movie_b['clean_title'] if score_b > score_a else "Both movies")
    summary_text = (
        f"🎯 <strong>Takeaway:</strong> <strong>{higher_movie}</strong> leads with a higher average rating (+{diff:.2f} stars). "
        f"Meanwhile, {'Movie A' if votes_a > votes_b else 'Movie B'} has engaged more reviewers ({max(votes_a, votes_b)} votes vs {min(votes_a, votes_b)} votes)."
        if score_a != score_b else f"🎯 <strong>Takeaway:</strong> Both movies are tied with identical average ratings of ★ {score_a:.2f}!"
    )
    st.markdown(f"""
    <div class="chart-explainer">
        <strong>Comparison Summary:</strong><br>
        {summary_text}
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# PAGE 4: 🎲 SURPRISE ME! (NEW FEATURE 3)
# =============================================================================
elif st.session_state["current_page"] == "surprise":
    st.markdown(f'<div class="section-title">🎲 {t("surprise_heading")}</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-desc">{t("surprise_subtitle")}</p>', unsafe_allow_html=True)

    s_c1, s_c2 = st.columns([3, 1])
    with s_c1:
        surprise_genre = st.selectbox(t("surprise_genre"), ["Any Genre"] + all_genres)
    with s_c2:
        st.write("")
        st.write("")
        roll_btn = st.button(t("surprise_btn"), use_container_width=True, type="primary")

    if roll_btn or st.session_state["surprise_movie"] is None:
        if surprise_genre == "Any Genre":
            eligible = merged_df[merged_df["rating_count"] >= 10]
        else:
            eligible = merged_df[(merged_df["genres"].str.contains(surprise_genre, na=False)) & (merged_df["rating_count"] >= 10)]

        if not eligible.empty:
            st.session_state["surprise_movie"] = eligible.sample(n=1, random_state=random.randint(1, 100000)).iloc[0]

    s_movie = st.session_state["surprise_movie"]
    if s_movie is not None:
        with st.spinner("Fetching surprise film details..."):
            s_omdb = fetch_omdb_details(imdb_id=s_movie.get("imdbId"), title=s_movie["clean_title"], year=s_movie["year"], custom_key=custom_omdb_key)

        surp_col1, surp_col2 = st.columns([1, 2.2])

        with surp_col1:
            if s_omdb and s_omdb.get("poster"):
                st.image(s_omdb.get("poster"), use_container_width=True)
            else:
                st.markdown(f"""
                <div style="background-color: var(--bg-card); border-radius: 12px; height: 350px; display:flex; flex-direction:column; align-items:center; justify-content:center; color:#94A3B8; border:1px solid var(--border-card);">
                    <span style="font-size: 3.5rem;">🎲</span>
                    <p style="font-size: 0.9rem; margin-top:8px;">{s_movie['clean_title']}</p>
                </div>
                """, unsafe_allow_html=True)

            if st.button(t("surprise_another_btn"), use_container_width=True, type="secondary"):
                if surprise_genre == "Any Genre":
                    eligible = merged_df[merged_df["rating_count"] >= 10]
                else:
                    eligible = merged_df[(merged_df["genres"].str.contains(surprise_genre, na=False)) & (merged_df["rating_count"] >= 10)]
                st.session_state["surprise_movie"] = eligible.sample(n=1, random_state=random.randint(1, 100000)).iloc[0]
                st.rerun()

        with surp_col2:
            st.markdown(f"""
            <div class="detail-card">
                <span style="background:#F59E0B; color:#0F172A; font-weight:800; font-size:0.75rem; padding:3px 10px; border-radius:12px; text-transform:uppercase;">Surprise Pick</span>
                <h1 class="detail-title" style="margin-top:8px;">{s_movie['clean_title']} ({int(s_movie['year']) if pd.notna(s_movie['year']) else 'N/A'})</h1>
                <p style="color:#8B5CF6; font-size:0.85rem; font-weight:600; margin-bottom:12px;">{s_movie['genres'].replace('|', ' • ')}</p>
                <div class="rating-box">
                    <span style="font-size:0.75rem; text-transform:uppercase; color:var(--text-muted); font-weight:700;">MovieLens Rating</span>
                    <div style="font-size:1.6rem; font-weight:800; color:#F59E0B;">★ {s_movie['mean_rating']} <span style="font-size:0.9rem; color:var(--text-muted);">/ 5.0</span> ({s_movie['rating_count']} reviews)</div>
                    <span style="font-size:0.8rem; color:#10B981;">Fair Ranking Score: {s_movie['fair_score']}</span>
                </div>
                <p style="color:var(--text-body); font-size:0.95rem; line-height:1.5;"><strong>Plot:</strong> {s_omdb.get('plot', 'Cataloged in MovieLens benchmark dataset.')}</p>
                <p style="color:var(--text-body); font-size:0.88rem;"><strong>Director:</strong> {s_omdb.get('director', 'Unknown')} • <strong>Cast:</strong> {s_omdb.get('actors', 'Unknown')}</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("View Full Details & Recommendations ➔", key="btn_surp_det", use_container_width=True, type="primary"):
                st.session_state["selected_movie_id"] = s_movie["movieId"]
                st.session_state["current_page"] = "search"
                st.rerun()

# =============================================================================
# PAGE 5: 📊 ANALYTICS DASHBOARD
# =============================================================================
elif st.session_state["current_page"] == "analytics":
    st.markdown(f'<div class="section-title">📊 {t("analytics_heading")}</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-desc">{t("analytics_subtitle")}</p>', unsafe_allow_html=True)

    f_c1, f_c2 = st.columns(2)
    with f_c1:
        dash_years = st.slider(t("filter_years"), min_value=min_year, max_value=max_year, value=(1970, max_year))
    with f_c2:
        dash_min_votes = st.slider(t("filter_min_ratings"), min_value=1, max_value=200, value=50)

    f_merged = merged_df[(merged_df["year"] >= dash_years[0]) & (merged_df["year"] <= dash_years[1])]
    plot_template = "plotly_dark" if is_dark else "plotly_white"

    b1, b2, b3, b4 = st.columns(4)
    with b1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{t("total_movies")}</div>
            <div class="metric-value">{len(f_merged):,}</div>
            <div class="metric-desc">Filtered era: {dash_years[0]}–{dash_years[1]}</div>
        </div>
        """, unsafe_allow_html=True)
    with b2:
        top_fair = f_merged[f_merged["rating_count"] >= dash_min_votes].sort_values("fair_score", ascending=False)
        top_movie_name = top_fair.iloc[0]["clean_title"] if not top_fair.empty else "N/A"
        top_movie_score = top_fair.iloc[0]["fair_score"] if not top_fair.empty else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{t("top_ranked_movie")}</div>
            <div class="metric-value" style="font-size:1.45rem; color:#F59E0B;">{top_movie_name[:18]}</div>
            <div class="metric-desc">Fair Score: {top_movie_score} (Min {dash_min_votes} votes)</div>
        </div>
        """, unsafe_allow_html=True)
    with b3:
        most_voted_row = f_merged.sort_values("rating_count", ascending=False).iloc[0] if not f_merged.empty else None
        most_voted_title = most_voted_row["clean_title"] if most_voted_row is not None else "N/A"
        most_voted_count = most_voted_row["rating_count"] if most_voted_row is not None else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{t("most_rated_movie")}</div>
            <div class="metric-value" style="font-size:1.45rem; color:#38BDF8;">{most_voted_title[:18]}</div>
            <div class="metric-desc">{most_voted_count} verified reviews received</div>
        </div>
        """, unsafe_allow_html=True)
    with b4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{t("most_rated_genre")}</div>
            <div class="metric-value" style="font-size:1.7rem; color:#10B981;">Drama</div>
            <div class="metric-desc">41,928 ratings across catalog</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab_c1, tab_c2 = st.tabs(["Ratings & Genre Distributions", "Yearly Production & Leaderboards"])

    with tab_c1:
        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown("#### 1. How People Rate Movies (0.5 to 5.0 Stars)")
            score_df = ratings_df["rating"].value_counts().sort_index().reset_index()
            score_df.columns = ["rating", "count"]
            score_df["pct"] = (score_df["count"] / total_ratings * 100).round(1)

            fig_scores = px.bar(
                score_df, x="rating", y="count", text=score_df["pct"].apply(lambda p: f"{p}%"),
                color="count", color_continuous_scale=["#38BDF8", "#F59E0B"],
                labels={"rating": "Star Rating (0.5 to 5.0)", "count": "Count"}
            )
            fig_scores.update_layout(template=plot_template, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=380, coloraxis_showscale=False, xaxis=dict(tickmode="linear", tick0=0.5, dtick=0.5))
            fig_scores.update_traces(textposition="outside", cliponaxis=False)
            st.plotly_chart(fig_scores, use_container_width=True)

            st.markdown(f"""
            <div class="chart-explainer">
                <strong>{t("chart_explainer_prefix")}</strong> Frequency of each star rating from 0.5 to 5.0.<br>
                <span class="chart-takeaway">{t("chart_takeaway_prefix")} 4.0 stars is the #1 most common score (26.6%). Most reviewers rate movies positively because they pick films they expect to enjoy.</span>
            </div>
            """, unsafe_allow_html=True)

        with c_right:
            st.markdown("#### 2. Average Rating for Each Genre")
            g_summary = genre_ratings.groupby("genre").agg(avg_rating=("rating", "mean")).reset_index().sort_values("avg_rating", ascending=True)

            fig_genres = px.bar(
                g_summary, x="avg_rating", y="genre", orientation="h", text=g_summary["avg_rating"].round(2),
                color="avg_rating", color_continuous_scale=["#38BDF8", "#8B5CF6", "#F59E0B"],
                labels={"avg_rating": "Average Rating (out of 5)", "genre": "Genre"}
            )
            fig_genres.update_layout(template=plot_template, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=380, coloraxis_showscale=False)
            fig_genres.update_traces(textposition="outside", cliponaxis=False)
            st.plotly_chart(fig_genres, use_container_width=True)

            st.markdown(f"""
            <div class="chart-explainer">
                <strong>{t("chart_explainer_prefix")}</strong> The average rating across all 19 movie categories.<br>
                <span class="chart-takeaway">{t("chart_takeaway_prefix")} Film-Noir (3.92) and War (3.81) lead in average scores because their fans are passionate and selective.</span>
            </div>
            """, unsafe_allow_html=True)

    with tab_c2:
        c2_left, c2_right = st.columns(2)
        with c2_left:
            st.markdown("#### 3. Movies Released Each Year (1902–2018)")
            year_counts = f_merged.dropna(subset=["year"])["year"].astype(int).value_counts().sort_index().reset_index()
            year_counts.columns = ["year", "movie_count"]

            fig_year_prod = px.bar(
                year_counts, x="year", y="movie_count", color="movie_count",
                color_continuous_scale=["#38BDF8", "#F59E0B"],
                labels={"year": "Release Year", "movie_count": "Count"}
            )
            fig_year_prod.update_layout(template=plot_template, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=380, coloraxis_showscale=False)
            st.plotly_chart(fig_year_prod, use_container_width=True)

            st.markdown(f"""
            <div class="chart-explainer">
                <strong>{t("chart_explainer_prefix")}</strong> Total count of movie releases per calendar year.<br>
                <span class="chart-takeaway">{t("chart_takeaway_prefix")} Production increased sharply in the 1990s and peaked between 2002 and 2014 as digital filming lowered production barriers.</span>
            </div>
            """, unsafe_allow_html=True)

        with c2_right:
            st.markdown("#### 4. Top 10 Ranked Movies (Fair Bayesian Score)")
            top10 = f_merged[f_merged["rating_count"] >= dash_min_votes].sort_values("fair_score", ascending=True).tail(10)

            fig_top10 = px.bar(
                top10, x="fair_score", y="clean_title", orientation="h", text="fair_score",
                color="fair_score", color_continuous_scale=["#38BDF8", "#F59E0B"],
                labels={"fair_score": "Fair Score", "clean_title": "Movie Title"}
            )
            fig_top10.update_layout(template=plot_template, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=380, coloraxis_showscale=False)
            fig_top10.update_traces(textposition="outside", cliponaxis=False)
            st.plotly_chart(fig_top10, use_container_width=True)

            st.markdown(f"""
            <div class="chart-explainer">
                <strong>{t("chart_explainer_prefix")}</strong> Top movies ranked using Bayesian weighting with minimum {dash_min_votes} votes.<br>
                <span class="chart-takeaway">{t("chart_takeaway_prefix")} Timeless masterworks like The Shawshank Redemption and The Godfather rank at the top because they excel in both score and votes.</span>
            </div>
            """, unsafe_allow_html=True)

# =============================================================================
# PAGE 6: 🎭 EXPLORE GENRES
# =============================================================================
elif st.session_state["current_page"] == "genres":
    st.markdown(f'<div class="section-title">🎭 {t("genres_heading")}</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-desc">{t("genres_subtitle")}</p>', unsafe_allow_html=True)

    selected_genre_pick = st.selectbox("Select a Genre to Explore:", all_genres, index=all_genres.index("Action"))

    g_movies = merged_df[merged_df["genres"].str.contains(selected_genre_pick, na=False, regex=False)]
    g_ratings = genre_ratings[genre_ratings["genre"] == selected_genre_pick]
    g_avg = round(g_ratings["rating"].mean(), 2)
    g_count = len(g_ratings)
    g_movies_count = len(g_movies)

    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Average Score</div>
            <div class="metric-value">★ {g_avg}</div>
            <div class="metric-desc">Average rating for {selected_genre_pick} movies</div>
        </div>
        """, unsafe_allow_html=True)
    with g2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Catalog Movies</div>
            <div class="metric-value">{g_movies_count:,}</div>
            <div class="metric-desc">Movies categorized under {selected_genre_pick}</div>
        </div>
        """, unsafe_allow_html=True)
    with g3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Audience Reviews</div>
            <div class="metric-value">{g_count:,}</div>
            <div class="metric-desc">Total ratings submitted for {selected_genre_pick}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"#### 🏆 Top Ranked Movies in {selected_genre_pick} (Min 30 Votes)")
    top_in_genre = g_movies[g_movies["rating_count"] >= 30].sort_values("fair_score", ascending=False).head(12)

    gen_cols = st.columns(3)
    for idx, (_, grow) in enumerate(top_in_genre.iterrows()):
        with gen_cols[idx % 3]:
            st.markdown(f"""
            <div class="metric-card" style="margin-bottom: 16px;">
                <h4 style="margin: 0 0 4px 0; color:var(--text-title); font-size:1.15rem;">{grow['clean_title']} <span style="color:var(--text-muted); font-size:0.9rem;">({int(grow['year']) if pd.notna(grow['year']) else 'N/A'})</span></h4>
                <p style="color:#8B5CF6; font-size:0.8rem; margin:0 0 10px 0; font-weight:600;">{grow['genres'].replace('|', ' • ')}</p>
                <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--border-card); padding-top:8px;">
                    <span class="badge-star">★ {grow['mean_rating']}</span>
                    <span style="font-size:0.82rem; color:var(--text-muted);">{grow['rating_count']} reviews</span>
                    <span style="font-size:0.82rem; color:#10B981; font-weight:700;">Fair: {grow['fair_score']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(t("view_details"), key=f"btn_genre_{grow['movieId']}", use_container_width=True):
                st.session_state["selected_movie_id"] = grow["movieId"]
                st.session_state["current_page"] = "search"
                st.rerun()

# =============================================================================
# PAGE 7: ⭐ TOP RATED MOVIES
# =============================================================================
elif st.session_state["current_page"] == "top":
    st.markdown(f'<div class="section-title">⭐ {t("top_heading")}</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-desc">{t("top_subtitle")}</p>', unsafe_allow_html=True)

    top_c1, top_c2, top_c3 = st.columns(3)
    with top_c1:
        top_genre_pick = st.selectbox("Filter by Genre:", ["All Genres"] + all_genres)
    with top_c2:
        top_min_ratings = st.slider("Minimum ratings required:", min_value=1, max_value=250, value=50, step=5)
    with top_c3:
        top_sort_by = st.selectbox("Sort Leaderboard By:", ["Fair Score (Recommended)", "Highest Average Rating", "Most Number of Ratings"])

    top_df = merged_df[merged_df["rating_count"] >= top_min_ratings].copy()
    if top_genre_pick != "All Genres":
        top_df = top_df[top_df["genres"].str.contains(top_genre_pick, na=False, regex=False)]

    if "Fair Score" in top_sort_by:
        top_df = top_df.sort_values("fair_score", ascending=False)
    elif "Highest Average" in top_sort_by:
        top_df = top_df.sort_values(["mean_rating", "rating_count"], ascending=[False, False])
    else:
        top_df = top_df.sort_values("rating_count", ascending=False)

    top_20 = top_df.head(20).reset_index(drop=True)

    table_disp = top_20[["clean_title", "year", "genres", "mean_rating", "rating_count", "fair_score"]].copy()
    table_disp.index = table_disp.index + 1
    table_disp["year"] = table_disp["year"].fillna(0).astype(int)
    table_disp.columns = ["Movie Title", "Release Year", "Genres", "Average Rating", "Total Votes", "Fair Ranking Score"]
    
    st.dataframe(table_disp, use_container_width=True)

    st.markdown(f"""
    <div class="chart-explainer">
        <strong>{t("chart_explainer_prefix")}</strong> The Fair Score formula balances review scores with vote counts.<br>
        <span class="chart-takeaway">{t("chart_takeaway_prefix")} This prevents a movie with 1 single 5-star rating from unfairly ranking above masterworks with hundreds of verified reviews.</span>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# PAGE 8: 📈 RATING INSIGHTS
# =============================================================================
elif st.session_state["current_page"] == "insights":
    st.markdown(f'<div class="section-title">📈 {t("insights_heading")}</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-desc">{t("insights_subtitle")}</p>', unsafe_allow_html=True)

    insights = [
        ("1. Most Loved Genres: Film-Noir (3.92) & War (3.81)", "Film-Noir achieved the highest average rating in our entire dataset, followed closely by War and Documentaries. Viewers who watch these genres are thoughtful and rate them generously."),
        ("2. Most Popular Genre: Drama (41,928 Ratings)", "Drama and Comedy attract the largest volume of audience engagement. Over 40% of all ratings belong to Drama movies, proving that character-driven storytelling reaches the widest audience."),
        ("3. The 4.0 Star Phenomenon (People Are Generous Reviewers)", "4.0 stars is the #1 most common rating, making up 26.6% of all ratings. Furthermore, 69.9% of all ratings are whole stars (1, 2, 3, 4, 5). People choose movies they expect to enjoy."),
        ("4. Why Minimum Rating Filters Are Essential", "Over 3,400 movies in the dataset have only a single rating! Without a threshold, an obscure 1-vote movie would unfairly dominate the #1 spot. Requiring at least 50 ratings surfaces true classics like The Shawshank Redemption and The Godfather."),
        ("5. Movie Production Peak (1990s–2010s)", "The volume of movie releases grew rapidly starting in the 1990s and peaked between 2002 and 2014, reflecting the boom of independent film studios and digital production techniques."),
        ("6. Practical Business Uses for Streaming Platforms", "Streaming services like Netflix and Prime Video can apply these findings to: (1) License high-rating classic films to build catalog prestige, (2) Feature Drama and Comedy prominently on home screens for broad appeal, and (3) Use fair scoring to keep recommendation algorithms fair.")
    ]

    for title, text in insights:
        st.markdown(f"""
        <div style="background-color: var(--bg-card); border: 1px solid var(--border-card); border-radius: 12px; padding: 18px 22px; margin-bottom: 14px;">
            <h4 style="color: var(--text-title); font-size: 1.1rem; margin: 0 0 6px 0;">{title}</h4>
            <p style="color: var(--text-body); font-size: 0.94rem; margin: 0; line-height: 1.5;">{text}</p>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# PAGE 9: ❤️ MY WATCHLIST
# =============================================================================
elif st.session_state["current_page"] == "watchlist":
    st.markdown(f'<div class="section-title">❤️ {t("watchlist_heading")}</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-desc">{t("watchlist_subtitle")}</p>', unsafe_allow_html=True)

    w_dict = st.session_state["watchlist"]

    if not w_dict:
        st.markdown(f"""
        <div class="friendly-box">
            <span style="font-size: 3rem;">❤️</span>
            <h3 style="color: var(--text-title); margin: 12px 0 6px 0;">{t("empty_watchlist")}</h3>
            <p style="color: var(--text-muted); font-size: 0.95rem;">Search for any title in CineScope and click 'Add to Watchlist' to build your personal queue.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        w_tab1, w_tab2, w_tab3 = st.tabs(["All Movies", "Want to Watch", "Watched"])
        
        def render_watchlist_items(items):
            if not items:
                st.info("No movies in this list yet.")
                return
            
            w_cols = st.columns(3)
            for idx, (m_id, m_data) in enumerate(items.items()):
                with w_cols[idx % 3]:
                    status_badge = "✅ Watched" if m_data.get("status") == "Watched" else "⏳ Want to Watch"
                    st.markdown(f"""
                    <div class="metric-card" style="margin-bottom: 16px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                            <span style="font-size:0.75rem; font-weight:800; background:#3B82F6; color:#FFF; padding:2px 8px; border-radius:10px;">{status_badge}</span>
                            <span class="badge-star">★ {m_data.get('rating', 'N/A')}</span>
                        </div>
                        <h4 style="margin: 0 0 4px 0; color:var(--text-title); font-size:1.1rem;">{m_data.get('title')} ({m_data.get('year', 'N/A')})</h4>
                        <p style="color:#8B5CF6; font-size:0.78rem; margin:0 0 10px 0;">{m_data.get('genres', '').replace('|', ' • ')}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    btn_c1, btn_c2 = st.columns(2)
                    with btn_c1:
                        new_status = "Watched" if m_data.get("status") == "Want to Watch" else "Want to Watch"
                        toggle_label = "Mark Watched" if new_status == "Watched" else "Want to Watch"
                        if st.button(toggle_label, key=f"btn_toggle_{m_id}", use_container_width=True):
                            st.session_state["watchlist"][m_id]["status"] = new_status
                            save_json(watchlist_file, st.session_state["watchlist"])
                            st.rerun()
                    with btn_c2:
                        if st.button(t("remove_watchlist"), key=f"btn_del_{m_id}", use_container_width=True):
                            del st.session_state["watchlist"][m_id]
                            save_json(watchlist_file, st.session_state["watchlist"])
                            st.rerun()

        with w_tab1:
            render_watchlist_items(w_dict)
        with w_tab2:
            render_watchlist_items({k: v for k, v in w_dict.items() if v.get("status") == "Want to Watch"})
        with w_tab3:
            render_watchlist_items({k: v for k, v in w_dict.items() if v.get("status") == "Watched"})

# =============================================================================
# PAGE 10: 📥 DOWNLOAD REPORTS (NEW FEATURE 4)
# =============================================================================
elif st.session_state["current_page"] == "reports":
    st.markdown(f'<div class="section-title">📥 {t("reports_heading")}</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-desc">{t("reports_subtitle")}</p>', unsafe_allow_html=True)

    rep_col1, rep_col2 = st.columns(2)

    with rep_col1:
        st.markdown(f"""
        <div class="detail-card">
            <span style="background:#10B981; color:#0F172A; font-weight:800; font-size:0.75rem; padding:3px 10px; border-radius:12px; text-transform:uppercase;">Data Export</span>
            <h3 style="color:var(--text-title); margin:8px 0 6px 0;">CSV Leaderboard Data</h3>
            <p style="color:var(--text-muted); font-size:0.92rem; line-height:1.5;">
                Download top-rated catalog movies with release years, genres, average ratings, vote counts, and Fair Ranking Scores in standard CSV format.
            </p>
        </div>
        """, unsafe_allow_html=True)

        top_export_df = merged_df[merged_df["rating_count"] >= 30].sort_values("fair_score", ascending=False).head(50)
        csv_data = top_export_df[["movieId", "clean_title", "year", "genres", "mean_rating", "rating_count", "fair_score"]].to_csv(index=False).encode('utf-8')

        st.download_button(
            label=t("download_csv_btn"),
            data=csv_data,
            file_name="CineScope_Top_Movies_Data.csv",
            mime="text/csv",
            use_container_width=True,
            type="secondary"
        )

    with rep_col2:
        st.markdown(f"""
        <div class="detail-card">
            <span style="background:#F59E0B; color:#0F172A; font-weight:800; font-size:0.75rem; padding:3px 10px; border-radius:12px; text-transform:uppercase;">Executive Report</span>
            <h3 style="color:var(--text-title); margin:8px 0 6px 0;">PDF Analytics Report</h3>
            <p style="color:var(--text-muted); font-size:0.92rem; line-height:1.5;">
                Download a clean, presentation-ready PDF report summarizing project methodology, key dataset metrics, top 10 movies table, and analytical takeaways.
            </p>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("Generating PDF report..."):
            pdf_bytes = generate_pdf_report(merged_df)

        st.download_button(
            label=t("download_pdf_btn"),
            data=pdf_bytes,
            file_name="CineScope_Executive_Analytics_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )

# =============================================================================
# PAGE 11: ♿ ACCESSIBILITY SETTINGS (NEW FEATURE 5)
# =============================================================================
elif st.session_state["current_page"] == "accessibility":
    st.markdown(f'<div class="section-title">♿ {t("acc_heading")}</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-desc">{t("acc_subtitle")}</p>', unsafe_allow_html=True)

    with st.form("form_accessibility"):
        font_options = ["Normal", "Large", "Extra Large"]
        curr_font_idx = font_options.index(st.session_state["font_size"]) if st.session_state["font_size"] in font_options else 0
        new_font = st.selectbox(t("acc_font_size"), font_options, index=curr_font_idx)

        new_contrast = st.checkbox(t("acc_high_contrast"), value=st.session_state["high_contrast"])
        new_focus = st.checkbox(t("acc_focus"), value=st.session_state["focus_indicators"])

        submitted = st.form_submit_button(t("acc_save_btn"), type="primary")
        if submitted:
            st.session_state["font_size"] = new_font
            st.session_state["high_contrast"] = new_contrast
            st.session_state["focus_indicators"] = new_focus
            
            save_json(acc_file, {
                "font_size": new_font,
                "high_contrast": new_contrast,
                "focus_indicators": new_focus
            })
            st.success("Accessibility settings saved successfully!")
            st.rerun()

    # Live Preview Card
    st.markdown("""
    <div class="detail-card" style="margin-top: 24px;">
        <h3 style="color:var(--text-title); margin-top:0;">Live Accessibility Preview</h3>
        <p style="color:var(--text-body); font-size:1rem; line-height:1.5;">
            This card demonstrates your current font scaling and contrast settings. Notice how text remains crisp, legible, and comfortable to read across all backgrounds.
        </p>
        <span class="genre-chip">High-Contrast Compliant</span>
        <span class="genre-chip">Keyboard Navigable</span>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# PAGE 12: ℹ️ ABOUT PROJECT
# =============================================================================
elif st.session_state["current_page"] == "about":
    st.markdown(f'<div class="section-title">ℹ️ {t("about_heading")}</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-desc">{t("about_subtitle")}</p>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background-color: var(--bg-card); border: 1px solid var(--border-card); border-radius: 14px; padding: 24px; margin-bottom: 24px;">
        <h3 style="color: #F59E0B; margin: 0 0 14px 0; font-size: 1.25rem;">{t("team_title")}</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px;">
            <div>
                <p style="margin:4px 0; color:var(--text-body); font-weight:600;">• DHRUV VERMA</p>
                <p style="margin:4px 0; color:var(--text-body); font-weight:600;">• YUVRAJ SINGH YADAV</p>
                <p style="margin:4px 0; color:var(--text-body); font-weight:600;">• PIYUSH SINGH RATHORE</p>
                <p style="margin:4px 0; color:var(--text-body); font-weight:600;">• RISHU GUPTA</p>
                <p style="margin:4px 0; color:var(--text-body); font-weight:600;">• YATHARTH PRAKASH ANUBHAV</p>
            </div>
            <div>
                <p style="margin:4px 0; color:var(--text-body); font-weight:600;">• ATUL SAXENA</p>
                <p style="margin:4px 0; color:var(--text-body); font-weight:600;">• VIPIN KUMAR</p>
                <p style="margin:4px 0; color:var(--text-body); font-weight:600;">• KHUSHI</p>
                <p style="margin:4px 0; color:var(--text-body); font-weight:600;">• PRIYANSHI</p>
            </div>
            <div>
                <p style="margin:4px 0; color:var(--text-body); font-weight:600;">• NITESH</p>
                <p style="margin:4px 0; color:var(--text-body); font-weight:600;">• AMBIKA YADAV</p>
                <p style="margin:4px 0; color:var(--text-body); font-weight:600;">• PANKAJ YADAV</p>
                <p style="margin:4px 0; color:var(--text-body); font-weight:600;">• SACHIN YADAV</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background-color: var(--bg-card); border: 1px solid var(--border-card); border-radius: 14px; padding: 24px;">
        <h3 style="color: var(--text-title); margin: 0 0 10px 0; font-size: 1.25rem;">{t("dataset_title")}</h3>
        <p style="color: var(--text-body); line-height: 1.5; font-size: 0.95rem;">
            This project utilizes the official <strong>MovieLens Latest-Small</strong> dataset from GroupLens Research at the University of Minnesota.
            It comprises <strong>100,836 real user ratings</strong> across <strong>9,742 movies</strong> spanning from 1902 to 2018.
        </p>
        <h4 style="color: var(--text-title); margin: 16px 0 8px 0; font-size: 1.1rem;">{t("tech_title")}</h4>
        <p style="color: var(--text-muted); font-size: 0.9rem; line-height: 1.5;">
            • <strong>Frontend & Framework:</strong> Streamlit 1.66 with responsive CSS design tokens<br>
            • <strong>Visualizations:</strong> Plotly Express & Plotly Graph Objects (Responsive 1080p)<br>
            • <strong>Data Engine:</strong> Pandas 3.1 & NumPy 2.5<br>
            • <strong>Report Generator:</strong> fpdf2 Executive PDF & CSV exporter<br>
            • <strong>External API:</strong> OMDb API for high-res posters and worldwide discovery
        </p>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 10. Footer
# -----------------------------------------------------------------------------
st.markdown("<hr style='margin: 30px 0 16px 0; border: none; border-top: 1px solid var(--border-card);'>", unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align: center; color: var(--text-muted); font-size: 0.86rem; padding-bottom: 20px;">
    {t("footer_text")}
</div>
""", unsafe_allow_html=True)
