import os
import functions_framework
import requests
import feedparser
from google.cloud import firestore
from telegram import Bot
import asyncio
from config import JAPAN_REGIONS, MIN_LOCAL_SHINDO, MIN_GLOBAL_SHINDO, PREFECTURE_TRANSLATIONS

# Initialize clients
db = firestore.Client()
telegram_token = os.environ.get("TELEGRAM_TOKEN")
# Note: In a real Cloud Function, you might want to initialize the bot inside the function 
# or use a global variable pattern if it's reused. 
# For now, we'll instantiate it when we need it or check if we can reuse.
# However, python-telegram-bot's Bot class is synchronous-compatible in generic usage, 
# but mostly async in v20+. We will use the async approach where possible or sync for simplicity if appropriate.
# Since Cloud Functions are often synchronous, we'll use asyncio.run() for the bot methods.

P2P_API_URL = "https://api.p2pquake.net/v2/history?codes=551&limit=10"
NHK_RSS_URL = "https://www3.nhk.or.jp/nhkworld/en/rss/all/index.xml"

def get_nhk_headlines():
    """Fetches the top 3 headlines from NHK World-Japan RSS."""
    try:
        feed = feedparser.parse(NHK_RSS_URL)
        headlines = []
        for entry in feed.entries[:3]:
            headlines.append(f"- [{entry.title}]({entry.link})")
        return "\n".join(headlines)
    except Exception as e:
        print(f"Error serving NHK RSS: {e}")
        return "Unable to fetch news."

def get_users_to_alert(region: str, shindo: int):
    """
    Returns a list of Telegram user IDs to alert based on region and shindo.
    Logic:
    - Global Alert: If shindo >= MIN_GLOBAL_SHINDO, alert everyone (or a specific 'global' topic if we had one).
      For this MVP, we will fetch ALL users if global, or filter by region if local.
    """
    users_to_alert = set()
    
    # 1. Fetch all users from Firestore
    users_ref = db.collection("users")
    docs = users_ref.stream()

    for doc in docs:
        user_data = doc.to_dict()
        user_id = doc.id
        user_regions = user_data.get("regions", [])

        # Check Global
        if shindo >= MIN_GLOBAL_SHINDO:
             users_to_alert.add(user_id)
             continue

        # Check Local
        if shindo >= MIN_LOCAL_SHINDO:
            if region in user_regions:
                users_to_alert.add(user_id)
            # We also need to check if the specific prefecture is in the user's mapping?
            # specified in PRD: "User selects regions (e.g., Kanto) to monitor."
            # stored in config.py: JAPAN_REGIONS maps Region -> Prefectures.
            # The API returns prefectures or area names. We need to map APIm data -> Region.

    return list(users_to_alert)

def map_prefectures_to_region(points):
    """
    Maps the 'points' (prefectures/areas) from P2P data to our defined Regions.
    Returns a set of affected Regions (e.g., {'Kanto', 'Tohoku'}).
    """
    affected_regions = set()
    for point in points:
        pref = point.get("pref")
        if not pref:
            continue
        
        # Find which Region this prefecture belongs to
        for region, prefs in JAPAN_REGIONS.items():
            if pref in prefs:
                affected_regions.add(region)
    return affected_regions

async def send_telegram_alert(user_id, message):
    print(f"DEBUG: Attempting to send message to {user_id}...")
    if not telegram_token:
        print("ERROR: TELEGRAM_TOKEN not set.")
        return
    bot = Bot(token=telegram_token)
    try:
        await bot.send_message(chat_id=user_id, text=message, parse_mode="Markdown")
        print(f"DEBUG: Successfully sent message to {user_id}")
    except Exception as e:
        print(f"ERROR: Failed to send to {user_id}: {e}")

@functions_framework.http
def poll_quakes(request):
    """
    Background Cloud Function to poll P2P-Quake API data.
    """
    
    # 1. Fetch Quake Data
    try:
        resp = requests.get(P2P_API_URL)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return f"Error fetching quake data: {e}", 500

    if not data:
        return "No data received", 200

    # 2. Process each quake
    # We generally only want to process the latest one, or any we haven't seen.
    # For MVP, let's keep track of processed IDs in Firestore.
    
    processed_ref = db.collection("system").document("processed_quakes")
    processed_doc = processed_ref.get()
    processed_ids = []
    if processed_doc.exists:
        processed_ids = processed_doc.to_dict().get("ids", [])

    new_processed_ids = list(processed_ids)
    
    alerts_sent = 0

    for quake in data:
        quake_id = quake.get("id")
        if quake_id in processed_ids:
            continue
        
        # New Quake!
        earthquake_info = quake.get("earthquake", {})
        hypocenter = earthquake_info.get("hypocenter", {})
        max_scale = earthquake_info.get("maxScale", 0) # Reported as integer e.g. 30, 40, 50
        
        # Convert P2P scale to human readable if needed, or check threshold
        # Scale: 10, 20, 30, 40, 45, 50, 55, 60, 70
        
        if max_scale < MIN_LOCAL_SHINDO:
            # Too small to bother anyone
            new_processed_ids.append(quake_id)
            continue
            
        # Determine Affected Regions
        points = quake.get("points", [])
        affected_regions = map_prefectures_to_region(points)
        
        # Prepare Affected Areas String (English)
        affected_prefs_en = []
        for point in points:
            pref_jp = point.get("pref")
            if pref_jp in PREFECTURE_TRANSLATIONS:
                affected_prefs_en.append(PREFECTURE_TRANSLATIONS[pref_jp])
            elif pref_jp:
                affected_prefs_en.append(pref_jp)
        
        affected_areas_str = ", ".join(sorted(list(set(affected_prefs_en))))

        # Prepare Message
        name = hypocenter.get("name", "Unknown Location")
        depth = hypocenter.get("depth", "Unknown")
        magnitude = hypocenter.get("magnitude", "Unknown")
        
        # JMA Map (P2P doesn't give a direct map link usually, but we can link to the generic JMA page or similar)
        # Using the generic JMA Quake info page for now as requested by PRD "Link to JMA Seismic Map"
        jma_url = "https://www.data.jma.go.jp/multi/quake/index.html"
        p2p_url = "https://www.p2pquake.net/web/"

        headlines = get_nhk_headlines()
        
        message = (
            f"🚨 **Earthquake Alert** 🚨\n\n"
            f"**Location:** {name}\n"
            f"**Affected Areas:** {affected_areas_str}\n"
            f"**Max Intensity:** {max_scale/10}\n"
            f"**Magnitude:** {magnitude}\n"
            f"**Depth:** {depth}km\n\n"
            f"🔗 [JMA Seismic Map]({jma_url})\n\n"
            f"🔗 [P2P Quake]({p2p_url})\n\n"
            f"📰 **Latest News:**\n{headlines}"
        )
        
        # Identify users
        # We need to union the users of all affected regions
        target_users = set()
        
        # Logic: 
        # If Global (>= 50), alert ALL users.
        # If Local (>= 30 < 50), alert users in 'affected_regions'
        
        all_users_ref = db.collection("users").stream()
        all_users = {doc.id: doc.to_dict() for doc in all_users_ref}
        
        for uid, udata in all_users.items():
            if max_scale >= MIN_GLOBAL_SHINDO:
                target_users.add(uid)
            else:
                user_regions = udata.get("regions", [])
                # If any of the user's regions are in the affected_regions
                if not affected_regions.isdisjoint(user_regions):
                    target_users.add(uid)

        # Send Alerts
        for uid in target_users:
            asyncio.run(send_telegram_alert(uid, message))
            
        alerts_sent += 1
        new_processed_ids.append(quake_id)

    # 3. Update Processed IDs
    # Keep list from growing infinitely - maybe keep last 50
    if len(new_processed_ids) > 50:
        new_processed_ids = new_processed_ids[-50:]
        
    processed_ref.set({"ids": new_processed_ids})

    return f"Processed scan. Alerts sent: {alerts_sent}", 200
