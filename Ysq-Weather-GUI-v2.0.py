"""
增强版全球天气预报应用 - Ysq-Weather-GUI v2.0
使用Open-Meteo API，无需API密钥
支持200+个预设城市（从cities.json文件加载）
优化界面和性能，修复已知问题
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from datetime import datetime, timedelta
import pytz
import sys
import os
import threading
import traceback
import time


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("全球天气预报 - Ysq-Weather-GUI v2.0")
        self.root.geometry("900x750")  # 减小窗口高度
        self.root.configure(bg="#f0f0f0")

        # 尝试加载窗口图标
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))

            icon_path = os.path.join(base_path, "weather_icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"图标加载失败: {e}")

        # 加载城市数据
        self.preset_cities = self.load_cities_from_json()

        # 如果没有加载到城市数据，使用最小化备份
        if not self.preset_cities:
            self.preset_cities = {
                "北京": {"lat": 39.9042, "lon": 116.4074, "name": "北京", "country": "CN"},
                "上海": {"lat": 31.2304, "lon": 121.4737, "name": "上海", "country": "CN"},
                "广州": {"lat": 23.1291, "lon": 113.2644, "name": "广州", "country": "CN"},
                "深圳": {"lat": 22.5431, "lon": 114.0579, "name": "深圳", "country": "CN"},
                "东莞": {"lat": 23.02067, "lon": 113.75179, "name": "东莞", "country": "CN"},
                "纽约": {"lat": 40.7128, "lon": -74.0060, "name": "纽约", "country": "US"},
                "伦敦": {"lat": 51.5074, "lon": -0.1278, "name": "伦敦", "country": "GB"},
                "东京": {"lat": 35.6762, "lon": 139.6503, "name": "东京", "country": "JP"}
            }
            messagebox.showwarning("警告", "城市数据文件加载失败，使用内置的简化城市列表")

        # 天气代码对应描述（扩展版）
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
            56: {"desc": "冻毛毛雨", "icon": "🌨️"},
            57: {"desc": "强冻毛毛雨", "icon": "🌨️"},
            61: {"desc": "小雨", "icon": "🌧️"},
            63: {"desc": "中雨", "icon": "🌧️"},
            65: {"desc": "大雨", "icon": "⛈️"},
            66: {"desc": "冻雨", "icon": "🌨️"},
            67: {"desc": "强冻雨", "icon": "🌨️"},
            71: {"desc": "小雪", "icon": "🌨️"},
            73: {"desc": "中雪", "icon": "🌨️"},
            75: {"desc": "大雪", "icon": "❄️"},
            77: {"desc": "雪粒", "icon": "❄️"},
            80: {"desc": "阵雨", "icon": "🌦️"},
            81: {"desc": "强阵雨", "icon": "⛈️"},
            82: {"desc": "暴雨", "icon": "⛈️"},
            85: {"desc": "小雪", "icon": "🌨️"},
            86: {"desc": "大雪", "icon": "❄️"},
            95: {"desc": "雷暴", "icon": "⛈️"},
            96: {"desc": "雷暴伴有冰雹", "icon": "⛈️"},
            99: {"desc": "强雷暴伴有冰雹", "icon": "⛈️"},
        }

        # 用户收藏
        self.favorites = ["东莞", "北京", "上海", "广州", "深圳", "纽约", "伦敦", "东京"]

        # 缓存机制
        self.weather_cache = {}
        self.cache_timeout = 300  # 5分钟缓存

        # 初始化界面
        self.setup_ui()

        # 默认加载东莞天气
        self.root.after(100, lambda: self.get_weather("东莞"))

        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_cities_from_json(self):
        """从JSON文件加载城市数据"""
        cities = {}
        try:
            # 尝试多个可能的路径
            possible_paths = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "cities.json"),
                os.path.join(os.getcwd(), "cities.json"),
                "cities.json"
            ]

            json_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    json_path = path
                    break

            if json_path:
                with open(json_path, 'r', encoding='utf-8') as f:
                    city_data = json.load(f)

                # 将分组的城市数据转换为平铺的字典
                for region, city_list in city_data.items():
                    for city in city_list:
                        city_name = city["name"]
                        cities[city_name] = {
                            "lat": city["lat"],
                            "lon": city["lon"],
                            "name": city_name,
                            "country": city["country"],
                            "region": region
                        }

                print(f"成功加载 {len(cities)} 个城市数据")
            else:
                print("警告: 未找到 cities.json 文件")

        except Exception as e:
            print(f"加载城市数据失败: {e}")
            traceback.print_exc()

        return cities

    def setup_ui(self):
        """设置用户界面"""
        # 字体定义
        font_normal = ("TkDefaultFont", 10)
        font_bold = ("TkDefaultFont", 10, "bold")
        font_large = ("TkDefaultFont", 18, "bold")
        font_huge = ("TkDefaultFont", 48, "bold")

        # 主框架
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.grid(row=0, column=0, sticky="nsew")

        # 标题
        title_label = ttk.Label(
            main_frame,
            text="全球天气预报 - Ysq-Weather-GUI v2.0",
            font=font_large,
            foreground="#2c3e50"
        )
        title_label.grid(row=0, column=0, columnspan=5, pady=(0, 15))

        # 搜索区域
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=1, column=0, columnspan=5, pady=(0, 15), sticky="ew")

        # 城市选择
        ttk.Label(search_frame, text="选择城市:", font=font_normal).pack(side="left", padx=(0, 10))

        self.city_var = tk.StringVar()
        self.city_combo = ttk.Combobox(
            search_frame,
            textvariable=self.city_var,
            values=sorted(self.preset_cities.keys()),
            width=25,
            font=font_normal,
            state="normal"
        )
        self.city_combo.pack(side="left", padx=(0, 15))
        self.city_combo.set("东莞")
        self.city_combo.bind("<Return>", lambda e: self.get_weather(self.city_var.get()))

        # 查询按钮
        self.query_btn = ttk.Button(
            search_frame,
            text="查询天气",
            command=lambda: self.get_weather(self.city_var.get())
        )
        self.query_btn.pack(side="left", padx=(0, 15))

        # 快速城市按钮
        quick_frame = ttk.Frame(search_frame)
        quick_frame.pack(side="left")

        quick_cities = ["北京", "上海", "广州", "深圳", "纽约", "伦敦", "东京"]
        for city in quick_cities:
            ttk.Button(
                quick_frame,
                text=city,
                width=6,
                command=lambda c=city: self.get_weather(c)
            ).pack(side="left", padx=2)

        # 当前天气卡片
        self.weather_card = ttk.LabelFrame(main_frame, text="当前天气", padding=20)
        self.weather_card.grid(row=2, column=0, columnspan=5, pady=(0, 20), sticky="ew")

        # 左侧：城市和温度
        left_frame = ttk.Frame(self.weather_card)
        left_frame.grid(row=0, column=0, rowspan=2, padx=(0, 40))

        self.city_label = ttk.Label(
            left_frame,
            text="",
            font=("TkDefaultFont", 16, "bold"),
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
            ("降水概率", "precipitation"),
            ("能见度", "visibility"),
            ("更新时间", "update_time")
        ]

        for i, (name, key) in enumerate(details):
            row = i // 2
            col = i % 2

            frame = ttk.Frame(right_frame)
            frame.grid(row=row, column=col, padx=20, pady=10, sticky="w")

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

        # 7天预报（上移一行）
        forecast_frame = ttk.LabelFrame(main_frame, text="未来7天预报", padding=15)
        forecast_frame.grid(row=3, column=0, columnspan=5, pady=(0, 15), sticky="ew")  # 从row=3改为row=3

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

        # 状态栏（上移一行）
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=4, column=0, columnspan=5, pady=(10, 0), sticky="ew")  # 从row=5改为row=4

        self.status_label = ttk.Label(
            status_frame,
            text="就绪 - 选择城市开始查询",
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
        for i in range(5):
            main_frame.columnconfigure(i, weight=1)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def get_weather(self, city_name):
        """获取天气数据"""
        if not city_name or city_name.strip() == "":
            messagebox.showwarning("输入错误", "请输入城市名称")
            return

        # 禁用查询按钮防止重复点击
        self.query_btn.config(state="disabled")
        self.status_label.config(text=f"正在获取 {city_name} 的天气数据...")
        self.root.update()

        # 在新线程中执行网络请求，避免界面卡顿
        thread = threading.Thread(target=self._fetch_and_display_weather, args=(city_name,))
        thread.daemon = True
        thread.start()

    def _fetch_and_display_weather(self, city_name):
        """在新线程中获取并显示天气数据"""
        try:
            # 检查缓存
            cache_key = f"{city_name}_{datetime.now().strftime('%Y%m%d%H')}"
            if cache_key in self.weather_cache:
                cached_data, cache_timestamp = self.weather_cache[cache_key]
                if time.time() - cache_timestamp < self.cache_timeout:
                    # 使用缓存数据
                    self.root.after(0, lambda: self._update_ui_with_cached_data(city_name, cached_data))
                    return

            # 获取城市坐标
            if city_name in self.preset_cities:
                city_data = self.preset_cities[city_name]
            else:
                # 如果不在预设列表中，尝试使用地理编码API
                city_data = self.geocode_city(city_name)
                if not city_data:
                    self.root.after(0, lambda: messagebox.showerror("错误", f"找不到城市: {city_name}"))
                    self.root.after(0, lambda: self.status_label.config(text="城市未找到"))
                    self.root.after(0, lambda: self.query_btn.config(state="normal"))
                    return

            # 获取天气数据
            weather_data = self.fetch_weather_data(city_data["lat"], city_data["lon"])

            if weather_data:
                # 缓存数据
                self.weather_cache[cache_key] = (weather_data, time.time())

                # 在主线程中更新UI
                self.root.after(0, lambda: self._update_ui(city_name, weather_data))
            else:
                self.root.after(0, lambda: messagebox.showerror("错误", "获取天气数据失败"))
                self.root.after(0, lambda: self.status_label.config(text="数据获取失败"))
                self.root.after(0, lambda: self.query_btn.config(state="normal"))

        except Exception as e:
            error_msg = f"获取天气时发生错误:\n{str(e)}"
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
            self.root.after(0, lambda: self.status_label.config(text="发生错误"))
            self.root.after(0, lambda: self.query_btn.config(state="normal"))
            print(f"获取天气数据异常: {e}")
            traceback.print_exc()

    def _update_ui(self, city_name, weather_data):
        """更新UI显示天气数据"""
        try:
            self.display_current_weather(city_name, weather_data)
            self.display_forecast(weather_data)  # 只显示当前天气和7天预报
            update_time = datetime.now().strftime("%H:%M:%S")
            self.status_label.config(text=f"已更新 {city_name} 的天气数据 - {update_time}")
        finally:
            self.query_btn.config(state="normal")

    def _update_ui_with_cached_data(self, city_name, weather_data):
        """使用缓存数据更新UI"""
        try:
            self.display_current_weather(city_name, weather_data)
            self.display_forecast(weather_data)  # 只显示当前天气和7天预报
            update_time = datetime.now().strftime("%H:%M:%S")
            self.status_label.config(text=f"已更新 {city_name} 的天气数据 (缓存) - {update_time}")
        finally:
            self.query_btn.config(state="normal")

    def geocode_city(self, city_name):
        """地理编码：将城市名转换为坐标"""
        try:
            # 直接使用城市名进行地理编码（Open-Meteo API支持中文）
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=zh&format=json"
            response = requests.get(url, timeout=10)
            data = response.json()

            if data.get("results"):
                result = data["results"][0]
                return {
                    "lat": result["latitude"],
                    "lon": result["longitude"],
                    "name": result.get("name", city_name),
                    "country": result.get("country_code", "Unknown")
                }
        except Exception as e:
            print(f"地理编码错误: {e}")

        return None

    def fetch_weather_data(self, lat, lon):
        """从Open-Meteo获取天气数据"""
        try:
            # 修正API请求参数（移除不需要的小时预报数据）
            url = (f"https://api.open-meteo.com/v1/forecast?"
                   f"latitude={lat}&longitude={lon}&"
                   f"current_weather=true&"
                   f"hourly=temperature_2m,relativehumidity_2m,apparent_temperature,"
                   f"precipitation_probability,pressure_msl,visibility&"  # 移除了weathercode参数
                   f"daily=weathercode,temperature_2m_max,temperature_2m_min,"
                   f"precipitation_probability_max&"
                   f"timezone=auto&forecast_days=7")

            response = requests.get(url, timeout=15)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            self.root.after(0, lambda: messagebox.showerror("错误", "请求超时，请检查网络连接"))
        except requests.exceptions.RequestException as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"网络请求失败: {e}"))
        except Exception as e:
            print(f"获取天气数据异常: {e}")

        return None

    def display_current_weather(self, city_name, weather_data):
        """显示当前天气信息"""
        current = weather_data["current_weather"]
        hourly = weather_data["hourly"]

        # 获取当前时间在hourly数据中的索引
        current_time = datetime.fromisoformat(current["time"].replace("Z", "+00:00"))
        current_hour = current_time.hour

        # 查找最接近当前时间的小时数据
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
        # 湿度
        if hour_index >= 0 and hour_index < len(hourly["relativehumidity_2m"]):
            humidity = hourly["relativehumidity_2m"][hour_index]
            self.detail_labels["humidity"].config(text=f"{humidity}%")
        else:
            self.detail_labels["humidity"].config(text="--%")

        # 风速和风向
        self.detail_labels["wind_speed"].config(text=f"{current['windspeed']:.1f} km/h")
        self.detail_labels["wind_dir"].config(text=self.get_wind_direction(current["winddirection"]))

        # 体感温度
        if hour_index >= 0 and hour_index < len(hourly["apparent_temperature"]):
            feels_like = hourly["apparent_temperature"][hour_index]
            self.detail_labels["feels_like"].config(text=f"{feels_like:.1f}°C")
        else:
            self.detail_labels["feels_like"].config(text=f"{temp:.1f}°C")

        # 气压
        if hour_index >= 0 and hour_index < len(hourly["pressure_msl"]):
            pressure = hourly["pressure_msl"][hour_index]
            self.detail_labels["pressure"].config(text=f"{pressure:.0f} hPa")
        else:
            self.detail_labels["pressure"].config(text="-- hPa")

        # 降水概率
        if hour_index >= 0 and hour_index < len(hourly["precipitation_probability"]):
            precipitation = hourly["precipitation_probability"][hour_index]
            self.detail_labels["precipitation"].config(text=f"{precipitation}%")
        else:
            self.detail_labels["precipitation"].config(text="--%")

        # 能见度
        if hour_index >= 0 and hour_index < len(hourly["visibility"]):
            visibility = hourly["visibility"][hour_index]
            self.detail_labels["visibility"].config(text=f"{visibility / 1000:.1f} km")
        else:
            self.detail_labels["visibility"].config(text="-- km")

        # 更新时间
        beijing_tz = pytz.timezone("Asia/Shanghai")
        update_time = current_time.astimezone(beijing_tz)
        self.detail_labels["update_time"].config(text=update_time.strftime("%m/%d %H:%M"))

    def display_forecast(self, weather_data):
        """显示7天天气预报"""
        daily = weather_data["daily"]

        # 确保数据存在
        if "time" not in daily or len(daily["time"]) < 7:
            return

        today = datetime.now().date()

        for i in range(min(7, len(daily["time"]))):
            date_str = daily["time"][i]
            date_obj = datetime.fromisoformat(date_str).date()

            # 更新日期
            if i == 0:
                day_text = "今天"
            elif i == 1:
                day_text = "明天"
            elif i == 2:
                day_text = "后天"
            else:
                # 计算星期几
                weekday = date_obj.strftime("%a")
                day_text = f"{date_obj.month}/{date_obj.day} {weekday}"

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
        directions = ["北", "北东北", "东北", "东东北", "东", "东东南", "东南", "南东南",
                      "南", "南西南", "西南", "西西南", "西", "西西北", "西北", "北西北"]
        index = round(degrees / 22.5) % 16
        return directions[index]

    def on_closing(self):
        """窗口关闭时的清理工作"""
        self.root.destroy()


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