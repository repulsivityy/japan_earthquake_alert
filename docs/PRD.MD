# PRD: Japan Safety Alert System (JSAS)

## 1. Objective
A traveler-centric safety system providing real-time earthquake alerts with NHK News context and JMA visual maps, filtered by the user's current regional location.

## 2. Core Features
- **Region-Aware Filtering:** User selects regions (e.g., Kanto) to monitor. 
- **Tiered Alerting:** - **Local:** Alert if Shindo >= 3 in user-selected region.
    - **Global:** Alert if Shindo >= 5 anywhere in Japan.
- **Rich Notifications:** Telegram messages must include:
    - Epicenter, Depth, and Max Intensity.
    - Link to JMA Seismic Map.
    - Recent headlines from **NHK World-Japan RSS**.
- **Visual Dashboard:** A Streamlit page showing a map of recent quakes and current safety status.

## 3. Technical Requirements
- **Compute:** GCP Cloud Run Function (Python) & GCP Cloud Run (Streamlit).
- **Database:** Firestore (Native Mode) to store `users/{telegram_id}` preferences.
- **Sources:** - Quake Data: `https://api.p2pquake.net/v2/history?codes=551&limit=5`
    - News Data: `https://www3.nhk.or.jp/nhkworld/en/rss/all/index.xml`
- **Secrets:** `TELEGRAM_TOKEN` via GCP Secret Manager.