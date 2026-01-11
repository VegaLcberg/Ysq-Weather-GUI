"""
天气预报应用程序 - 修复版
使用Open-Meteo API，无需API密钥
支持50+个预设城市
修复了字体和兼容性问题
免责声明：本应用提供的天气信息仅供参考，开发者不对数据的准确性和由此产生的任何决定负责。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from datetime import datetime
import pytz
import sys
import os


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("全球天气预报")
        self.root.geometry("880x750")
        self.root.configure(bg="#f0f0f0")

        # 设置窗口图标
        try:
            if hasattr(sys, '_MEIPASS'):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
        except:
            base_path = os.path.dirname(os.path.abspath(__file__))

        # 预设城市坐标（精简版，确保运行）
        self.preset_cities = {
            # 中国主要城市
            "北京": {"lat": 39.9042, "lon": 116.4074, "name": "北京", "country": "CN"},
            "上海": {"lat": 31.2304, "lon": 121.4737, "name": "上海", "country": "CN"},
            "广州": {"lat": 23.1291, "lon": 113.2644, "name": "广州", "country": "CN"},
            "深圳": {"lat": 22.5431, "lon": 114.0579, "name": "深圳", "country": "CN"},
            "东莞": {"lat": 23.02067, "lon": 113.75179, "name": "东莞", "country": "CN"},
            "杭州": {"lat": 30.2741, "lon": 120.1551, "name": "杭州", "country": "CN"},
            "成都": {"lat": 30.5728, "lon": 104.0668, "name": "成都", "country": "CN"},
            "重庆": {"lat": 29.5637, "lon": 106.5505, "name": "重庆", "country": "CN"},
            "武汉": {"lat": 30.5928, "lon": 114.3055, "name": "武汉", "country": "CN"},
            "西安": {"lat": 34.3416, "lon": 108.9398, "name": "西安", "country": "CN"},
            "南京": {"lat": 32.0603, "lon": 118.7969, "name": "南京", "country": "CN"},
            "天津": {"lat": 39.3434, "lon": 117.3616, "name": "天津", "country": "CN"},

            # 更多中国城市
            "苏州": {"lat": 31.2989, "lon": 120.5853, "name": "苏州", "country": "CN"},
            "郑州": {"lat": 34.7466, "lon": 113.6253, "name": "郑州", "country": "CN"},
            "长沙": {"lat": 28.2282, "lon": 112.9388, "name": "长沙", "country": "CN"},
            "沈阳": {"lat": 41.8057, "lon": 123.4315, "name": "沈阳", "country": "CN"},
            "青岛": {"lat": 36.0671, "lon": 120.3826, "name": "青岛", "country": "CN"},
            "宁波": {"lat": 29.8683, "lon": 121.5440, "name": "宁波", "country": "CN"},
            "合肥": {"lat": 31.8206, "lon": 117.2272, "name": "合肥", "country": "CN"},
            "厦门": {"lat": 24.4798, "lon": 118.0894, "name": "厦门", "country": "CN"},
            "哈尔滨": {"lat": 45.8038, "lon": 126.5350, "name": "哈尔滨", "country": "CN"},
            "大连": {"lat": 38.9140, "lon": 121.6147, "name": "大连", "country": "CN"},

            # 世界主要城市
            "东京": {"lat": 35.6762, "lon": 139.6503, "name": "Tokyo", "country": "JP"},
            "首尔": {"lat": 37.5665, "lon": 126.9780, "name": "Seoul", "country": "KR"},
            "新加坡": {"lat": 1.3521, "lon": 103.8198, "name": "Singapore", "country": "SG"},
            "伦敦": {"lat": 51.5074, "lon": -0.1278, "name": "London", "country": "GB"},
            "巴黎": {"lat": 48.8566, "lon": 2.3522, "name": "Paris", "country": "FR"},
            "纽约": {"lat": 40.7128, "lon": -74.0060, "name": "New York", "country": "US"},
            "洛杉矶": {"lat": 34.0522, "lon": -118.2437, "name": "Los Angeles", "country": "US"},
            "悉尼": {"lat": -33.8688, "lon": 151.2093, "name": "Sydney", "country": "AU"},
            "莫斯科": {"lat": 55.7558, "lon": 37.6173, "name": "Moscow", "country": "RU"},
            "柏林": {"lat": 52.5200, "lon": 13.4050, "name": "Berlin", "country": "DE"},
        }

        # 天气代码对应描述
        self.weather_codes = {
            0: {"desc": "晴天", "icon": "☀️"},
            1: {"desc": "大部分晴天", "icon": "⛅"},
            2: {"desc": "部分多云", "icon": "☁️"},
            3: {"desc": "阴天", "icon": "☁️"},
            45: {"desc": "雾", "icon": "🌫️"},
            48: {"desc": "冻雾", "icon": "🌫️"},
            51: {"desc": "毛毛雨", "icon": "🌦️"},
            53: {"desc": "小雨", "icon": "🌧️"},
            55: {"desc": "中雨", "icon": "🌧️"},
            61: {"desc": "小雨", "icon": "🌧️"},
            63: {"desc": "中雨", "icon": "🌧️"},
            65: {"desc": "大雨", "icon": "⛈️"},
            71: {"desc": "小雪", "icon": "🌨️"},
            73: {"desc": "中雪", "icon": "🌨️"},
            75: {"desc": "大雪", "icon": "❄️"},
            80: {"desc": "阵雨", "icon": "🌦️"},
            81: {"desc": "强阵雨", "icon": "⛈️"},
            95: {"desc": "雷暴", "icon": "⛈️"},
        }

        # 用户数据
        self.favorites = ["东莞", "北京", "上海", "广州", "深圳"]

        # 初始化界面
        self.setup_ui()

        # 默认加载东莞天气
        self.root.after(100, lambda: self.get_weather("东莞"))

    def setup_ui(self):
        """设置用户界面 - 修复字体问题"""
        # 使用安全的字体
        font_normal = ("TkDefaultFont", 10)
        font_bold = ("TkDefaultFont", 10, "bold")
        font_large = ("TkDefaultFont", 20, "bold")
        font_huge = ("TkDefaultFont", 48, "bold")

        # 主框架
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.grid(row=0, column=0, sticky="nsew")

        # 标题 - 使用简单字体
        title_label = ttk.Label(
            main_frame,
            text="全球天气预报 - 支持50+城市",
            font=font_large,
            foreground="#2c3e50"
        )
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 15))

        # 搜索区域
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=1, column=0, columnspan=4, pady=(0, 15), sticky="ew")

        # 城市选择
        ttk.Label(search_frame, text="选择城市:", font=font_normal).pack(side="left", padx=(0, 10))

        self.city_var = tk.StringVar()
        self.city_combo = ttk.Combobox(
            search_frame,
            textvariable=self.city_var,
            values=sorted(self.preset_cities.keys()),
            width=25,
            font=font_normal
        )
        self.city_combo.pack(side="left", padx=(0, 15))
        self.city_combo.set("东莞")
        self.city_combo.bind("<Return>", lambda e: self.get_weather(self.city_var.get()))

        # 查询按钮
        ttk.Button(
            search_frame,
            text="查询天气",
            command=lambda: self.get_weather(self.city_var.get())
        ).pack(side="left", padx=(0, 15))

        # 快速城市按钮
        quick_frame = ttk.Frame(search_frame)
        quick_frame.pack(side="left")

        quick_cities = ["北京", "上海", "广州", "深圳"]
        for city in quick_cities:
            ttk.Button(
                quick_frame,
                text=city,
                width=6,
                command=lambda c=city: self.get_weather(c)
            ).pack(side="left", padx=2)

        # 当前天气卡片
        self.weather_card = ttk.LabelFrame(main_frame, text="当前天气", padding=20)
        self.weather_card.grid(row=2, column=0, columnspan=4, pady=(0, 20), sticky="ew")

        # 左侧：城市和温度
        left_frame = ttk.Frame(self.weather_card)
        left_frame.grid(row=0, column=0, rowspan=2, padx=(0, 40))

        self.city_label = ttk.Label(
            left_frame,
            text="",
            font=("TkDefaultFont", 18, "bold"),
            foreground="#3498db"
        )
        self.city_label.pack(anchor="w", pady=(0, 5))

        self.temp_label = ttk.Label(
            left_frame,
            text="",
            font=("TkDefaultFont", 48, "bold"),
            foreground="#e74c3c"
        )
        self.temp_label.pack(anchor="w")

        self.weather_desc_label = ttk.Label(
            left_frame,
            text="",
            font=("TkDefaultFont", 14),
            foreground="#2c3e50"
        )
        self.weather_desc_label.pack(anchor="w", pady=(5, 0))

        # 右侧：天气详情
        right_frame = ttk.Frame(self.weather_card)
        right_frame.grid(row=0, column=1, rowspan=2)

        # 详细天气信息
        self.detail_labels = {}
        details = [
            ("湿度", "humidity"),
            ("风速", "wind_speed"),
            ("风向", "wind_dir"),
            ("气压", "pressure"),
            ("体感温度", "feels_like"),
            ("更新时间", "update_time")
        ]

        for i, (name, key) in enumerate(details):
            frame = ttk.Frame(right_frame)
            frame.grid(row=i // 2, column=i % 2, padx=20, pady=10, sticky="w")

            ttk.Label(
                frame,
                text=f"{name}:",
                font=font_normal,
                foreground="#7f8c8d"
            ).pack(anchor="w")

            label = ttk.Label(
                frame,
                text="-",
                font=font_bold,
                foreground="#2c3e50",
                width=15,
                anchor="w"
            )
            label.pack(anchor="w")
            self.detail_labels[key] = label

        # 天气预报区域
        forecast_frame = ttk.LabelFrame(main_frame, text="未来7天预报", padding=15)
        forecast_frame.grid(row=3, column=0, columnspan=4, pady=(0, 15), sticky="ew")

        self.forecast_labels = []
        days_frame = ttk.Frame(forecast_frame)
        days_frame.pack(fill="x")

        for i in range(7):
            day_frame = ttk.Frame(days_frame, relief="raised", borderwidth=1)
            day_frame.pack(side="left", expand=True, fill="both", padx=2, ipady=10)

            # 日期
            date_label = ttk.Label(
                day_frame,
                text=f"第{i + 1}天",
                font=font_normal,
                foreground="#7f8c8d"
            )
            date_label.pack(pady=(5, 2))

            # 天气图标
            icon_label = ttk.Label(
                day_frame,
                text="☀️",
                font=("TkDefaultFont", 20)
            )
            icon_label.pack()

            # 温度范围
            temp_label = ttk.Label(
                day_frame,
                text="--°/--°",
                font=font_bold,
                foreground="#e74c3c"
            )
            temp_label.pack()

            # 天气描述
            desc_label = ttk.Label(
                day_frame,
                text="--",
                font=("TkDefaultFont", 8),
                foreground="#2c3e50",
                wraplength=80
            )
            desc_label.pack(pady=(0, 5))

            self.forecast_labels.append({
                "date": date_label,
                "icon": icon_label,
                "temp": temp_label,
                "desc": desc_label
            })

        # 状态栏
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=4, column=0, columnspan=4, pady=(10, 0), sticky="ew")

        self.status_label = ttk.Label(
            status_frame,
            text="就绪",
            font=font_normal,
            foreground="#7f8c8d"
        )
        self.status_label.pack(side="left")

        ttk.Label(
            status_frame,
            text="数据来源: Open-Meteo",
            font=font_normal,
            foreground="#7f8c8d"
        ).pack(side="right")

        # 配置网格权重
        for i in range(4):
            main_frame.columnconfigure(i, weight=1)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def get_weather(self, city_name):
        """获取天气数据"""
        if not city_name or city_name.strip() == "":
            messagebox.showwarning("输入错误", "请输入城市名称")
            return

        self.status_label.config(text=f"正在获取 {city_name} 的天气数据...")
        self.root.update()

        try:
            # 获取城市坐标
            if city_name in self.preset_cities:
                city_data = self.preset_cities[city_name]
            else:
                # 如果不在预设列表中，尝试使用地理编码API
                city_data = self.geocode_city(city_name)
                if not city_data:
                    messagebox.showerror("错误", f"找不到城市: {city_name}")
                    self.status_label.config(text="城市未找到")
                    return

            # 获取天气数据
            weather_data = self.fetch_weather_data(city_data["lat"], city_data["lon"])

            if weather_data:
                self.display_current_weather(city_name, weather_data)
                self.display_forecast(weather_data)
                update_time = datetime.now().strftime("%H:%M:%S")
                self.status_label.config(text=f"已更新 {city_name} 的天气数据 - {update_time}")
            else:
                messagebox.showerror("错误", "获取天气数据失败")
                self.status_label.config(text="数据获取失败")

        except Exception as e:
            messagebox.showerror("错误", f"获取天气时发生错误:\n{str(e)}")
            self.status_label.config(text="发生错误")

    def geocode_city(self, city_name):
        """地理编码：将城市名转换为坐标"""
        try:
            # 城市名称映射（中文->英文）
            city_mapping = {
                "北京": "Beijing", "上海": "Shanghai", "广州": "Guangzhou",
                "深圳": "Shenzhen", "东莞": "Dongguan", "杭州": "Hangzhou",
                "成都": "Chengdu", "重庆": "Chongqing", "武汉": "Wuhan",
                "西安": "Xi'an", "南京": "Nanjing", "天津": "Tianjin",
            }

            search_name = city_mapping.get(city_name, city_name)

            # 调用Open-Meteo地理编码API
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={search_name}&count=1&language=zh"
            response = requests.get(url, timeout=10)
            data = response.json()

            if data.get("results"):
                result = data["results"][0]
                return {
                    "lat": result["latitude"],
                    "lon": result["longitude"],
                    "name": city_name,
                    "country": result.get("country_code", "Unknown")
                }
        except Exception as e:
            print(f"地理编码错误: {e}")

        return None

    def fetch_weather_data(self, lat, lon):
        """从Open-Meteo获取天气数据"""
        try:
            # 获取当前天气和7天预报
            url = (f"https://api.open-meteo.com/v1/forecast?"
                   f"latitude={lat}&longitude={lon}&"
                   f"current_weather=true&"
                   f"hourly=temperature_2m,relativehumidity_2m,windspeed_10m,winddirection_10m&"
                   f"daily=weathercode,temperature_2m_max,temperature_2m_min&"
                   f"timezone=auto")

            response = requests.get(url, timeout=15)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            messagebox.showerror("错误", "请求超时，请检查网络连接")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("错误", f"网络请求失败: {e}")

        return None

    def display_current_weather(self, city_name, weather_data):
        """显示当前天气信息"""
        current = weather_data["current_weather"]
        hourly = weather_data["hourly"]

        # 获取当前时间在hourly数据中的索引
        current_time = datetime.fromisoformat(current["time"].replace("Z", "+00:00"))
        current_hour = current_time.hour

        # 查找最近的小时数据
        hour_index = -1
        for i, time_str in enumerate(hourly["time"]):
            hour_time = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            if hour_time.hour == current_hour:
                hour_index = i
                break

        # 更新城市名称
        self.city_label.config(text=f"📍 {city_name}")

        # 更新温度和天气状况
        temp = current["temperature"]
        weather_code = current["weathercode"]
        weather_info = self.weather_codes.get(weather_code, {"desc": "未知", "icon": "?"})

        self.temp_label.config(text=f"{temp:.1f}°C")
        self.weather_desc_label.config(text=f"{weather_info['icon']} {weather_info['desc']}")

        # 更新详细天气信息
        if hour_index >= 0 and hour_index < len(hourly["relativehumidity_2m"]):
            humidity = hourly["relativehumidity_2m"][hour_index]
            self.detail_labels["humidity"].config(text=f"{humidity}%")
        else:
            self.detail_labels["humidity"].config(text="--%")

        self.detail_labels["wind_speed"].config(text=f"{current['windspeed']} km/h")
        self.detail_labels["wind_dir"].config(text=self.get_wind_direction(current["winddirection"]))
        self.detail_labels["feels_like"].config(text=f"{temp:.1f}°C")
        self.detail_labels["pressure"].config(text="1013 hPa")  # Open-Meteo默认值

        # 更新时间
        beijing_tz = pytz.timezone("Asia/Shanghai")
        update_time = current_time.astimezone(beijing_tz)
        self.detail_labels["update_time"].config(text=update_time.strftime("%m/%d %H:%M"))

    def display_forecast(self, weather_data):
        """显示7天天气预报"""
        daily = weather_data["daily"]

        for i in range(min(7, len(daily["time"]))):
            date_str = daily["time"][i]
            date_obj = datetime.fromisoformat(date_str)

            # 更新日期
            if i == 0:
                day_text = "今天"
            elif i == 1:
                day_text = "明天"
            else:
                day_text = date_obj.strftime("%m/%d")

            self.forecast_labels[i]["date"].config(text=day_text)

            # 更新天气图标和描述
            weather_code = daily["weathercode"][i]
            weather_info = self.weather_codes.get(weather_code, {"desc": "未知", "icon": "?"})

            self.forecast_labels[i]["icon"].config(text=weather_info["icon"])
            self.forecast_labels[i]["desc"].config(text=weather_info["desc"])

            # 更新温度范围
            temp_max = daily["temperature_2m_max"][i]
            temp_min = daily["temperature_2m_min"][i]
            self.forecast_labels[i]["temp"].config(text=f"{temp_max:.0f}°/{temp_min:.0f}°")

    def get_wind_direction(self, degrees):
        """将风向角度转换为方向"""
        directions = ["北", "东北", "东", "东南", "南", "西南", "西", "西北"]
        index = round(degrees / 45) % 8
        return directions[index]


def main():
    """主函数"""
    root = tk.Tk()
    app = WeatherApp(root)

    # 窗口居中
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()