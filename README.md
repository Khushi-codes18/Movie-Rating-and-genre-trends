# 🎬 CineScope — Movie Ratings & Discovery Platform

> **Discover Movies. Explore Ratings. Find Your Next Favourite.**  
> A complete, interactive movie discovery and analytics platform built with Python, Streamlit, Pandas, Plotly, and the MovieLens benchmark dataset.

---

## 📌 Table of Contents
1. [Overview & Project Highlights](#overview--project-highlights)
2. [Why This Project Is Useful](#why-this-project-is-useful)
3. [The 6 Main Pages](#the-6-main-pages)
4. [How the Movie Search Works](#how-the-movie-search-works)
5. [The Dataset We Used](#the-dataset-we-used)
6. [Tools & Technologies](#tools--technologies)
7. [How to Run the Project on Windows 11](#how-to-run-the-project-on-windows-11)
8. [Configuring the Optional Free OMDb API Key](#configuring-the-optional-free-omdb-api-key)
9. [What We Learned from the Data (Key Findings)](#what-we-learned-from-the-data-key-findings)
10. [Project Limitations](#project-limitations)
11. [Project Files Overview](#project-files-overview)

---

## 🌟 Overview & Project Highlights

**CineScope** is a modern movie analytics and discovery web application. It is designed to be beautiful, beginner-friendly, and completely interactive.

### Key Features:
- **Cinematic Dark Theme:** Premium midnight-blue and deep-black aesthetic with radiant gold (`#F59E0B`), purple (`#8B5CF6`), and sky-blue (`#38BDF8`) accents.
- **Smart Movie Search:** Search for any movie title (e.g. *Inception*, *The Dark Knight*, *Titanic*, *Interstellar*, *3 Idiots*, *The Shawshank Redemption*).
- **Dual Rating Insights:** Displays verified **MovieLens audience ratings** alongside **External IMDb ratings**, clearly distinguishing local data from external provider data.
- **Interactive Visualizations:** 8 interactive Plotly charts with tooltips, zooming, and 1-2 sentence explanations below every chart.
- **Fair Ranking Formula:** Uses Bayesian weighted rating to prevent obscure 1-vote movies from dominating the top-rated list.
- **100% Simple English:** Every heading, filter, button, and chart explanation is written in plain everyday English that anyone can understand.

---

## 🎯 Why This Project Is Useful

Streaming entertainment services (like Netflix, Prime Video, and Disney+) host thousands of titles. To license the best movies and recommend content effectively, platforms need data-driven insights:
1. **Catalog Planning:** Understand which genres attract dedicated fans (Film-Noir, War, Documentaries) versus broad audiences (Drama, Comedy).
2. **Recommendation Algorithms:** Ensure recommendations are fair by prioritizing movies with high scores AND many reviews.
3. **Audience Behavior:** Learn how people score movies (people give 4.0 stars more than any other score!).

---

## 🖥️ The 6 Main Pages

### 1. 🏠 Home Page
- **Cinematic Hero Banner:** CineScope logo and tagline.
- **Large Search Bar:** Search any movie immediately from the homepage.
- **4 Key Live Metrics:** Total Movies (9,742), Total Ratings (100,836), Active Reviewers (610), Global Average (3.50 ★).
- **Featured Blockbusters Showcase:** Movie cards with real posters, release years, genre chips, star badges, and "View Details" buttons.
- **Quick Navigation CTAs:** One-click shortcuts to the Analytics Dashboard or Top Movie Leaderboard.

### 2. 🔍 Movie Search and Details (Core Feature)
- **Token-Based Search:** Case-insensitive search that handles partial titles, punctuation, and articles (e.g. searching "Dark Knight" or "The Dark Knight" both find *The Dark Knight (2008)*).
- **Matching Movie Grid:** When multiple movies match a query (e.g. "Titanic"), CineScope shows a card grid so you can pick the exact film you want.
- **Full Movie Details View:**
  - High-resolution movie poster (with fallback graphic).
  - Title, release year, and genre badges.
  - **Ratings Breakdown:** MovieLens Rating (out of 5.0), Fair Ranking Score, and External IMDb Rating (out of 10).
  - Director, main cast, runtime, language, and release date.
  - Plot overview summary.
  - Direct 1-click links to view on IMDb or search on Google.
- **Worldwide Fallback:** If a movie is not in our 2018 dataset (e.g. *Oppenheimer* or *Dune 2*), CineScope automatically searches the worldwide OMDb database and displays full details!

### 3. 📊 Movie Analytics Dashboard
- Comprehensive metrics with dynamic release-year and minimum-vote sliders.
- **8 Interactive Charts:**
  1. *How People Rate Movies (0.5 to 5.0 Stars)*
  2. *Average Rating for Each Genre*
  3. *Total Movies per Genre*
  4. *Total Ratings per Genre*
  5. *How Movie Releases Have Changed Over the Years (1902–2018)*
  6. *Average Movie Ratings by Release Year*
  7. *Most-Rated Blockbusters in Cinema History*
  8. *Top-Rated Movies Using Fair Scoring*
- Every chart has a dedicated card with **"What this chart shows"** and **"🎯 Key takeaway"**.

### 4. 🎭 Explore Genres
- Multi-genre selector to compare any combination of genres side-by-side (e.g. Action vs. Sci-Fi vs. Drama).
- Compare average rating, catalog size, and review volume.
- Educational note explaining why high-average niche genres (like Film-Noir) differ from high-volume genres (like Comedy).

### 5. ⭐ Top Movies
- Official cinema leaderboard.
- Filter by genre, release era, and minimum ratings count.
- Sort by **Fair Score (Recommended)**, **Highest Average Rating**, or **Most Number of Ratings**.
- Explains the Bayesian Fair Ranking rule in simple, easy words.

### 6. 💡 Rating Insights
- Deep look into audience psychology:
  - 4.0 stars is the #1 most common score (26.6%).
  - 69.9% of ratings are whole stars (1, 2, 3, 4, 5).
  - Over 3,400 movies have only 1 single rating (power-law distribution).
- **"What We Learned":** 6 auto-calculated genuine discoveries from the real dataset.

---

## 🔍 How the Movie Search Works

CineScope uses a smart two-tier search strategy:

```
User types movie title (e.g. "Interstellar" or "The Dark Knight")
                      │
                      ▼
    ┌───────────────────────────────────┐
    │  1. Primary Local Dataset Search  │
    │  (9,742 movies in MovieLens)      │
    └─────────────────┬─────────────────┘
                      │
           Found? ────┴──── Not Found?
             │                     │
             ▼                     ▼
┌─────────────────────────┐  ┌─────────────────────────────────┐
│ Display Local Movie     │  │ 2. Worldwide External Search    │
│ with MovieLens Ratings  │  │ (Searches OMDb API worldwide)   │
│ & Cached Poster/Details │  └─────────────────────────────────┘
└─────────────────────────┘
```

1. **Local Dataset (Primary):**
   - 9,742 movies and 100,836 ratings.
   - Works 100% offline without any internet connection.
   - Shows genuine MovieLens ratings, review counts, and Fair Scores.
2. **Worldwide OMDb Search (Secondary / Fallback):**
   - When a movie is not in our 2018 dataset (e.g. *Oppenheimer (2023)*), CineScope queries OMDb to fetch the official poster, plot, director, cast, and IMDb score worldwide.
   - Ratings are always clearly labeled (never confusing MovieLens ratings with external IMDb ratings).

---

## 📁 The Dataset We Used

We use the official **MovieLens Latest-Small** benchmark dataset created by **GroupLens Research** at the University of Minnesota:
- **Total Movies:** 9,742 movies in `data/movies.csv`
- **Total Ratings:** 100,836 ratings in `data/ratings.csv`
- **Movie ID Links:** 9,742 IMDb and TMDB identifiers in `data/links.csv`
- **Active Reviewers:** 610 users (each user rated at least 20 movies)
- **Time Span:** Movies released from 1902 through 2018
- **Rating Scale:** 0.5 to 5.0 stars with 0.5 step increments

---

## 🛠️ Tools & Technologies

| Tool / Technology | Role in This Project |
| :--- | :--- |
| **Python 3** | Core language for data processing and application logic. |
| **Streamlit** | Powers our modern, responsive cinematic web application. |
| **Plotly** | Renders interactive, zoomable charts with custom tooltips. |
| **Pandas** | Handles CSV parsing, table merging, aggregations, and cleaning. |
| **Matplotlib & Seaborn** | Used in the Jupyter Notebook to export static charts. |
| **OMDb API** | Provides high-resolution posters, plot summaries, and worldwide search. |

---

## 🚀 How to Run the Project on Windows 11

### Step 1: Open Terminal or Command Prompt
Open PowerShell or Command Prompt, and navigate to the project directory:
```powershell
cd "C:\Users\HP\Desktop\Movie Rating"
```

### Step 2: Install Required Libraries
```powershell
pip install -r requirements.txt
```

### Step 3: Launch CineScope Web Application
```powershell
streamlit run app.py
```
Your default web browser will automatically open with CineScope running live at:  
👉 **http://localhost:8501**

### Step 4: Open the Jupyter Notebook (Optional)
To inspect the beginner-friendly step-by-step analysis:
```powershell
jupyter notebook Movie_Ratings_and_Genre_Trends.ipynb
```

---

## ⚙️ Configuring the Optional Free OMDb API Key

CineScope includes a working fallback key by default. If you want your own personal key with 1,000 free requests per day:
1. Visit: **[https://www.omdbapi.com/apikey.aspx](https://www.omdbapi.com/apikey.aspx)**
2. Select **"FREE"** and enter your email.
3. Check your email for your free key (e.g., `abc12345`).
4. You can enter the key in two ways:
   - **Method A (Sidebar):** Open CineScope and type your key into the sidebar under **"⚙️ Optional Settings"**.
   - **Method B (`.env` file):** Copy `.env.example` as `.env` in the project folder and paste:
     ```env
     OMDB_API_KEY=your_key_here
     ```

---

## 📊 What We Learned from the Data (Key Findings)

1. **Which Genres Get the Best Ratings?**  
   **Film-Noir (3.92)**, **War (3.81)**, and **Documentary (3.80)** achieve the highest average ratings because their audiences are dedicated and rate thoughtfully.
2. **Which Genres Are Most Popular?**  
   **Drama (41,928 ratings)** and **Comedy (39,053 ratings)** receive the most ratings by far, accounting for over 40% of all ratings.
3. **Movie Production Peaked Between 2002 and 2014:**  
   Movie releases grew rapidly starting in the 1990s as independent cinema and digital cameras lowered the cost of making movies.
4. **Why We Need Minimum Rating Filters:**  
   Over 3,400 movies have only 1 single rating! Without a threshold, a 1-vote film would rank at #1. Requiring $\ge 50$ ratings surfaces timeless classics: ***The Shawshank Redemption* (4.43)**, ***The Godfather* (4.29)**, and ***Fight Club* (4.27)**.
5. **People Are Generous Reviewers:**  
   **4.0 stars is the #1 most common score (26.6%)**, and 69.9% of all ratings are whole stars.

---

## ⚠️ Project Limitations

- **Dataset Demographics:** The data comes from MovieLens community members, who may watch more movies than average viewers.
- **Survivorship Bias of Older Films:** Older films have higher average scores because only the greatest classics from those decades are still remembered and watched today.
- **Dataset Cutoff:** The local MovieLens Latest-Small dataset includes movies up to 2018. Titles released after 2018 are discovered via external worldwide search.

---

## 📁 Project Files Overview

```text
Movie Rating/
├── app.py                                      # Modern CineScope Web Application
├── .env.example                                # Example configuration for optional API key
├── Movie_Ratings_and_Genre_Trends.ipynb        # Complete Jupyter Notebook with 4-step guides
├── Movie_Ratings_and_Genre_Trends.html         # Pre-rendered HTML report for browser viewing
├── Movie_Ratings_and_Genre_Trends_Presentation.pptx # 10-slide PowerPoint presentation
├── README.md                                   # Comprehensive beginner-friendly documentation
├── requirements.txt                            # Python dependencies list
├── data/
│   ├── movies.csv                              # 9,742 movies metadata
│   ├── ratings.csv                             # 100,836 audience ratings
│   └── links.csv                               # IMDb and TMDB identifiers
├── figures/                                    # 7 high-resolution charts
│   ├── chart1_average_rating_by_genre.png
│   ├── chart2_movies_released_by_year.png
│   ├── chart3_average_rating_by_release_year.png
│   ├── chart4_highest_rated_movies_threshold.png
│   ├── chart5_rating_count_distribution.png
│   ├── chart6_rating_score_distribution.png
│   └── chart7_genre_engagement_vs_rating.png
└── slides/                                     # Exported 1080p slide PNG images
    ├── slide_1.png ... slide_10.png
```

---

*CineScope — Discover Movies. Explore Ratings. Find Your Next Favourite.*
