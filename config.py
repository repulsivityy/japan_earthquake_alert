# JAPAN_REGIONS maps the 8 major regions to all 47 prefectures.
# The keys are English (for user selection), values are Japanese (for API matching).

JAPAN_REGIONS = {
    "Hokkaido": ["北海道"],
    "Tohoku": ["青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県"],
    "Kanto": ["東京都", "神奈川県", "千葉県", "埼玉県", "茨城県", "栃木県", "群馬県"],
    "Chubu": ["新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県"],
    "Kansai": ["京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "滋賀県", "三重県"],
    "Chugoku": ["鳥取県", "島根県", "岡山県", "広島県", "山口県"],
    "Shikoku": ["徳島県", "香川県", "愛媛県", "高知県"],
    "Kyushu": ["福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]
}

# JMA Seismic Intensity Scale for reference in logic
# 30 = Shindo 3, 40 = Shindo 4, 50 = Shindo 5-Lower, etc.
MIN_LOCAL_SHINDO = 40
MIN_GLOBAL_SHINDO = 50

PREFECTURE_TRANSLATIONS = {
    "北海道": "Hokkaido",
    "青森県": "Aomori", "岩手県": "Iwate", "宮城県": "Miyagi", "秋田県": "Akita", "山形県": "Yamagata", "福島県": "Fukushima",
    "東京都": "Tokyo", "神奈川県": "Kanagawa", "千葉県": "Chiba", "埼玉県": "Saitama", "茨城県": "Ibaraki", "栃木県": "Tochigi", "群馬県": "Gunma",
    "新潟県": "Niigata", "富山県": "Toyama", "石川県": "Ishikawa", "福井県": "Fukui", "山梨県": "Yamanashi", "長野県": "Nagano", "岐阜県": "Gifu", "静岡県": "Shizuoka", "愛知県": "Aichi",
    "京都府": "Kyoto", "大阪府": "Osaka", "兵庫県": "Hyogo", "奈良県": "Nara", "和歌山県": "Wakayama", "滋賀県": "Shiga", "三重県": "Mie",
    "鳥取県": "Tottori", "島根県": "Shimane", "岡山県": "Okayama", "広島県": "Hiroshima", "山口県": "Yamaguchi",
    "徳島県": "Tokushima", "香川県": "Kagawa", "愛媛県": "Ehime", "高知県": "Kochi",
    "福岡県": "Fukuoka", "佐賀県": "Saga", "長崎県": "Nagasaki", "熊本県": "Kumamoto", "大分県": "Oita", "宮崎県": "Miyazaki", "鹿児島県": "Kagoshima", "沖縄県": "Okinawa"
}