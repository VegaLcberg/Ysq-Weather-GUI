\# 🌤️ Ysq-Weather-GUI / 全球天气预报桌面应用



一个基于 Python 和 Tkinter 开发的图形界面天气预报应用，支持全球 50+ 个主要城市。数据来源于免费的 Open-Meteo API，无需申请密钥即可使用。



> \*\*致谢：\*\* 本项目的开发得到了 AI 助手 \[DeepSeek](https://chat.deepseek.com/) 的全程编码协助、问题调试与解决方案支持，特此感谢。



\## ✨ 功能特点



\*   \*\*🖥️ 本地桌面应用\*\*：使用 Tkinter 开发，无需浏览器，双击即可运行。

\*   \*\*🌍 多城市支持\*\*：内置 50+ 个国内外主要城市（如北京、上海、东京、纽约等），并支持搜索更多城市。

\*   \*\*📊 信息全面\*\*：显示当前温度、体感温度、天气状况、湿度、风速/风向、气压等。

\*   \*\*📅 7 日预报\*\*：提供未来一周的天气趋势和温度范围。

\*   \*\*⚡ 实时数据\*\*：每次查询都会从 Open-Meteo 获取最新天气数据。

\*   \*\*🆓 完全免费\*\*：无需注册或申请任何 API 密钥。

\*   \*\*📦 可执行文件\*\*：可使用 PyInstaller 打包为独立的 `.exe` 文件，方便分享。



\## 🚀 快速开始



\### 前提条件

确保你的系统已安装 \[Python 3.7+](https://www.python.org/downloads/)。



\### 方法一：直接运行源代码

1\.  克隆或下载本项目。

2\.  在终端中进入项目目录，安装依赖：

&nbsp;   ```bash

&nbsp;   pip install requests pytz

&nbsp;   ```

3\.  运行主程序：

&nbsp;   ```bash

&nbsp;   python weather\_app\_fixed.py

&nbsp;   ```



\### 方法二：使用打包好的程序 (仅限 Windows)

1\.  前往项目的 \[Release](https://github.com/Vega_Lcberg/Ysq-Weather-GUI/releases) 页面。

2\.  下载最新版本的 `Ysq-Weather-GUI.exe` 文件。

3\.  双击即可运行。



\## 🛠️ 手动打包（供开发者）



如果你想自行修改代码并打包：



```bash

\# 1. 安装打包工具

pip install pyinstaller



\# 2. 执行打包命令（推荐在项目根目录下运行）

pyinstaller --onefile --windowed --name "WeatherForecast" weather\_app\_fixed.py



\# 打包完成后，可执行文件位于 ./dist/ 目录下

