from flask import Flask, render_template, request
from flask import redirect, url_for

from datetime import datetime
import requests
from json import loads

#flask型を作る
app = Flask(__name__) #丸かっこ内は必ずこれ

# 気象庁のエリアコード（各都道府県の代表的な予報区コード）
# 例: 東京都(130000), 大阪府(270000) など
jp_47 = {
    "北海道": "016000", "青森県": "020000", "岩手県": "030000", "宮城県": "040000",
    "秋田県": "050000", "山形県": "060000", "福島県": "070000", "茨城県": "080000",
    "栃木県": "090000", "群馬県": "100000", "埼玉県": "110000", "千葉県": "120000",
    "東京都": "130000", "神奈川県": "140000", "新潟県": "150000", "富山県": "160000",
    "石川県": "170000", "福井県": "180000", "山梨県": "190000", "長野県": "200000",
    "岐阜県": "210000", "静岡県": "220000", "愛知県": "230000", "三重県": "240000",
    "滋賀県": "250000", "京都府": "260000", "大阪府": "270000", "兵庫県": "280000",
    "奈良県": "290000", "和歌山県": "300000", "鳥取県": "310000", "島根県": "320000",
    "岡山県": "330000", "広島県": "340000", "山口県": "350000", "徳島県": "360000",
    "香川県": "370000", "愛媛県": "380000", "高知県": "390000", "福岡県": "400000",
    "佐賀県": "410000", "長崎県": "420000", "熊本県": "430000", "大分県": "440000",
    "宮崎県": "450000", "鹿児島県": "460001", "沖縄県": "471000"
}


@app.route("/") 


def index():
    #return文で「render_template」を使い、トップページにどのhtmlを使うか指定
    return render_template("index.html", val1 = jp_47.keys())
    #キーワード引数の先頭の変数は好きな名前でOK。今回は「val1」、「val2」。
    #index.htmlの中で「val」という変数が使えるようになった。


#今度はサブページにルール付け

@app.route('/result', methods=['POST'])
def result():

    key = request.form.get("pref") #県名取得

    if not key or key not in jp_47:
        return redirect('/') 
    
    ken_code = jp_47[key] #コード取得

    res = requests.get(f"https://www.jma.go.jp/bosai/forecast/data/forecast/{ken_code}.json")

    li = loads(res.text)

    forecast_data = li[0]

    ts_weather = forecast_data["timeSeries"][0] # 天気と風
    ts_pop     = forecast_data["timeSeries"][1] # 降水確率
    ts_temp    = forecast_data["timeSeries"][2] # 気源


    dates = ts_weather["timeDefines"]

    area_forecast = ts_weather["areas"][0]

    weathers = area_forecast["weathers"]

    winds = area_forecast["winds"]

    weather_codes = area_forecast["weatherCodes"]

    pops_data = ts_pop["areas"][0]["pops"]

    temps_data = ts_temp["areas"][0]["temps"]

    weather_list = []

    for i, (date_str, weather, wind, code) in enumerate(zip(dates, weathers, winds, weather_codes)):

        dt = datetime.strptime(date_str[:19], "%Y-%m-%dT%H:%M:%S")

        f_date = f"{dt.month}月{dt.day}日"

        c_weather = weather.replace("\u3000", "")

        c_wind = wind.replace("\u3000", "")

        icon = f"https://tpf.weathernews.jp/wxicon/152/{code}.png"

        pop = f"{pops_data[i]}%" if i < len(pops_data) else "データなし"

        temp = f"{temps_data[i]}℃" if i < len(temps_data) else "データなし"

        weather_list.append(
            {
                "date": f_date,
                "weather": c_weather,
                "wind": c_wind,
                "icon": icon,
                "pop": pop,
                "temp": temp
            }
        )

    return render_template("result.html", val1 = weather_list, val2= key, val3 = ken_code)

@app.route('/detail', methods=['GET'])
def detail():
    key = request.args.get("id", 0) 

    ken_code = jp_47[key] #コード取得

    res = requests.get(f"https://www.jma.go.jp/bosai/forecast/data/overview_forecast/{ken_code}.json")

    li = loads(res.text) 

    dt = datetime.strptime(li["reportDatetime"][:19], "%Y-%m-%dT%H:%M:%S")
    
    f_date = f"{dt.month}月{dt.day}日"

    text = li["text"]

    return render_template("detail.html", val1 = key, val2 = f_date, val3 = text )



#ルール付けが終わったら実行（複数のページにルール付けしても絶対一番最後）
if __name__ == "__main__": #このappファイルが直接実行されたとき～という意味
    
    app.run(debug=True) #開発中にわかりやすいように、エラーを表示するよう設定
    # ↑ 公開時はFalseがおすすめ


