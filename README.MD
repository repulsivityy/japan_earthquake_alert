# Japan Safety Alert System (JSAS)
>disclaimer: entire project was vibe coded with anti-gravity gemini 3 pro, with some human intervention for security and logic verification. 

## Overview
This project is an automated earthquake monitoring/alerting system designed for residents and travelers in Japan. It continuously polls the [P2P Quake API](https://www.p2pquake.net/json_api_v2/) for real-time seismic data and delivers targeted alerts via a Telegram Bot. It also provides a centralized web dashboard to visualize recent activity and official safety information.

### Key Features
- **Real-time Monitoring**: Fetches earthquake data every 60 seconds via Cloud Scheduler.
- **Targeted Alerts**: Sends Telegram messages only to users in affected regions (e.g., alert hits "Kanto", only Kanto users are notified).
- **Rich Notifications**: Alerts include Shindo intensity, Magnitude, Depth, and relevant NHK World news headlines.
- **Web Dashboard**: A Streamlit frontend hosted on Cloud Run displaying an epicenter map, recent events log, and links to JMA warnings.

## File Structure
- `config.py`: Regional mapping dictionary.
- `main.py`: Main backend for polling quakes, parsing NHK RSS, and Telegram messaging.
- `app.py`: Streamlit dashboard for real-time visualization.
- `requirements.txt`: Project dependencies.
- `Dockerfile`: Container config for the Streamlit dashboard.

## Deployment Instructions
- DEPLOYMENT.md for deployment instructions.
