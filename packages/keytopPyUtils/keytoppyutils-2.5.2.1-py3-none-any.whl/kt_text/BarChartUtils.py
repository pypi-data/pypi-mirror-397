import ast
import numpy as np
from kt_base import CommonUtils
from matplotlib import pyplot as plt, ticker
from kt_text.Config import Config

class BarChartUtils:
    def __init__(self, param):
        # 标题配置
        self.title_name = param.get("titleName", "")
        self.title_color = param.get("titleColor", "#333333")
        self.title_font_size = param.get("titleFontSize", 10)
        self.title_font_weight = param.get("titleFontWeight", "bold")
        
        # X轴标题配置
        self.x_label_name = param.get("xLabelName", "")
        self.x_label_color = param.get("xLabelColor", "#333333")
        self.x_label_font_size = param.get("xLabelFontSize", 8)
        
        # Y轴标题配置
        self.y_label_name = param.get("yLabelName", "")
        self.y_label_color = param.get("yLabelColor", "#333333")
        self.y_label_font_size = param.get("yLabelFontSize", 8)
        
        # X轴数据配置
        self.x_key = param.get("xKey")
        if self.x_key is None:
            raise Exception("X轴取数标识：xKey，不能为空")
        
        # Y轴数据配置
        self.y_keys = param.get("yKeys")
        if self.y_keys is None:
            raise Exception("Y轴取数标识：yKeys，不能为空")
        self.y_keys = ast.literal_eval("{" + self.y_keys + "}")
        
        # Y轴数值是否展示
        self.show_y_ticks = param.get("showYTicks", True)
        
        # 数据配置
        self.data = param.get("data")
        if self.data is None:
            raise Exception("用于生成柱状图的数据：data，不能为空")
        if isinstance(self.data, str):
            self.data = ast.literal_eval(self.data)
        
        # 处理数据中的arr数组，实现长度不一致时的0填充
        # 首先获取所有arr的最大长度
        max_arr_length = 0
        for item in self.data:
            if isinstance(item, dict) and "arr" in item:
                arr_length = len(item["arr"])
                if arr_length > max_arr_length:
                    max_arr_length = arr_length
        
        # 然后对每个arr进行填充，确保长度一致
        for item in self.data:
            if isinstance(item, dict) and "arr" in item:
                current_length = len(item["arr"])
                if current_length < max_arr_length:
                    # 用0填充到最大长度
                    item["arr"] += [0] * (max_arr_length - current_length)
    
    def __str__(self):
        fields = vars(self)
        field_str = ', '.join([f"{k}={v}" for k, v in fields.items()])
        return f"BarChartUtils({field_str})"
    
    def generate_bar_chart(self):
        # 准备数据
        x = []
        grouped_data = {key: [] for key in self.y_keys}
        
        for item in self.data:
            x.append(item.get(self.x_key))
            # 使用arr数组获取Y轴数据，而不是硬编码的键
            if isinstance(item, dict) and "arr" in item:
                arr_data = item["arr"]
                # 确保arr_data的长度与y_keys的数量匹配
                for i, (key, _) in enumerate(self.y_keys.items()):
                    if i < len(arr_data):
                        grouped_data[key].append(arr_data[i])
                    else:
                        grouped_data[key].append(0)
            else:
                # 兼容旧的数据格式
                for key in self.y_keys:
                    grouped_data[key].append(item.get(key, 0))
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimSun']  # 使用宋体
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        
        # 计算X轴标签的最大长度，用于动态调整画布高度
        max_label_length = max(len(label) for label in x)
        
        # 设置图表大小，根据标签长度动态调整高度
        fig_width = 10
        fig_height = 5.5  # 默认高度
        
        # 根据标签长度调整画布高度
        if max_label_length > 5:
            # 每超过5个字符，高度增加0.5
            fig_height = 5.5 + (max_label_length - 5) * 0.15
            # 设置最大高度限制
            fig_height = min(fig_height, 10.0)
        
        if len(self.data) > 10:
            fig_width = 10.5
            
        fig_size = (fig_width, fig_height)
        print(f"DEBUG: 画布大小设置为: {fig_size} (基于最大标签长度: {max_label_length})")
        
        fig, ax = plt.subplots(figsize=fig_size, dpi=200)
        fig.patch.set_facecolor('#FFFFFF')
        
        # 设置图表背景色
        ax.set_facecolor('#FFFFFF')
        
        # 设置边框样式，只显示底部和左侧边框
        for spine_name, spine in ax.spines.items():
            if spine_name == 'top' or spine_name == 'right':
                spine.set_visible(False)  # 隐藏顶部和右侧边框
            else:
                spine.set_color('#d7d7d7')  # 设置底部和左侧边框颜色
        
        # 生成柱状图
        x_pos = np.arange(len(x))  # X轴位置
        width = 0.8 / len(self.y_keys)  # 柱状图宽度
        multiplier = 0
        
        for attribute, color in self.y_keys.items():
            offset = width * multiplier
            rects = ax.bar(x_pos + offset, grouped_data[attribute], width, 
                          label=attribute, color=color, alpha=0.9)
            # 添加数据标签
            ax.bar_label(rects, padding=3, fontsize=8, color='#333333')
            multiplier += 1
        
        # 设置标题
        if self.title_name != '':
            ax.set_title(self.title_name, color=self.title_color, 
                        fontsize=self.title_font_size, 
                        fontweight=self.title_font_weight, 
                        pad=20)
        
        # 设置X轴名称
        if self.x_label_name != '':
            ax.set_xlabel(self.x_label_name, color=self.x_label_color, 
                         fontsize=self.x_label_font_size, labelpad=10)
        
        # 设置Y轴名称
        if self.y_label_name != '':
            ax.set_ylabel(self.y_label_name, color=self.y_label_color, 
                         fontsize=self.y_label_font_size, labelpad=10)
        
        # 设置X轴刻度
        ax.set_xticks(x_pos + width * (len(self.y_keys) - 1) / 2)
        ax.set_xticklabels(x, rotation=45, va='top', ha='right', rotation_mode='anchor')
        
        # 输出调试信息，查看标签长度和计算结果
        print(f"DEBUG: 最大标签长度: {max_label_length}")
        
        # 根据标签最大长度调整参数，使用更明显的调整幅度
        if max_label_length <= 5:
            legend_y = -0.1
            bottom_margin = 0.15
        elif max_label_length <= 10:
            legend_y = -0.25
            bottom_margin = 0.25
        elif max_label_length <= 15:
            legend_y = -0.3
            bottom_margin = 0.3
        elif max_label_length <= 20:
            legend_y = -0.35
            bottom_margin = 0.35
        elif max_label_length <= 25:
            legend_y = -0.4
            bottom_margin = 0.4
        else:  # 标签较长
            legend_y = -0.5
            bottom_margin = 0.5
        
        # 设置Y轴数值是否展示
        if not self.show_y_ticks:
            ax.set_yticks([])
        
        # 设置刻度样式
        ax.tick_params(direction='out', length=4, width=0, color='#d7d7d7', pad=5)
        ax.tick_params(axis="y", labelsize=8, colors="#111111", pad=3)
        
        # 设置网格线
        ax.grid(True, axis='y', linestyle="-", color="#d7d7d7", linewidth=0.3, alpha=0.5)
        
        # 设置Y轴刻度格式，不使用科学计数法
        ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        
        # 设置Y轴范围从0开始
        ax.set_ylim(bottom=0)
        
        # 设置图例，动态调整位置
        ax.legend(
            loc='upper center',
            bbox_to_anchor=(0.5, legend_y),  # 动态调整图例Y位置
            ncol=10,  # 动态调整列数
            handlelength=0.5,
            handletextpad=0.5,
            frameon=False,
            prop={'size': 8},  # 字体大小
            labelcolor='#333333'  # 字体颜色
        )
        
        # 调整布局，动态调整底部边距
        plt.tight_layout()
        plt.subplots_adjust(bottom=bottom_margin)  # 动态调整底部边距
        
        # 保存图片
        filename = self.save_img()
        plt.close(fig)
        return filename
    
    def save_img(self):
        file_name = CommonUtils.generate_uuid() + ".png"
        plt.savefig(Config.BASE_PATH + file_name)  # 保存到当前目录
        return file_name


if __name__ == "__main__":
    # 测试用例1：短标签，使用arr数组（长度一致）
    param_short = {
        "titleName": "企鹅属性对比（短标签，arr长度一致）",
        "titleColor": "#333333",
        "titleFontSize": 12,
        "titleFontWeight": "bold",
        "xKey": "species",
        "yKeys": "'Bill Depth':'#4169E1', 'Bill Length':'#87CEFA', 'Flipper Length':'#D3D3D3'",
        "xLabelName": "企鹅种类",
        "xLabelColor": "#333333",
        "xLabelFontSize": 9,
        "yLabelName": "长度 (mm)",
        "yLabelColor": "#333333",
        "yLabelFontSize": 9,
        "showYTicks": True, 
        "data": [
            {"species": "Adelie", "arr": [18.35, 38.79, 189.95]},
            {"species": "Chinstrap", "arr": [18.43, 48.83, 195.82]},
            {"species": "Gentoo", "arr": [14.98, 47.50, 217.19]},
            {"species": "Gentoo11", "arr": [10, 60, 200]}
        ]
    }
    
    # 测试用例2：长标签，使用arr数组（长度不一致，测试0填充）
    param_long = {
        "titleName": "企鹅属性对比（长标签，arr长度不一致）",
        "titleColor": "#333333",
        "titleFontSize": 12,
        "titleFontWeight": "bold",
        "xKey": "species",
        "yKeys": "'Bill Depth':'#4169E1', 'Bill Length':'#87CEFA', 'Flipper Length':'#D3D3D3'",
        "xLabelName": "企鹅种类（详细名称）",
        "xLabelColor": "#333333",
        "xLabelFontSize": 9,
        "yLabelName": "长度 (mm)",
        "yLabelColor": "#333333",
        "yLabelFontSize": 9,
        "showYTicks": True, 
        "data": [
            {"species": "Adelie Penguin", "arr": [18.35, 38.79]},  # 缺少Flipper Length，应该填充0
            {"species": "Chinstrap Penguin", "arr": [18.43]},  # 缺少Bill Length和Flipper Length，应该填充0
            {"species": "Gentoo Penguin", "arr": [14.98, 47.50, 217.19]}  # 完整数据
        ]
    }
    
    # 测试用例3：arr长度超过y_keys数量（测试兼容性）
    param_extra = {
        "titleName": "企鹅属性对比（arr长度超过y_keys）",
        "titleColor": "#333333",
        "titleFontSize": 12,
        "titleFontWeight": "bold",
        "xKey": "species",
        "yKeys": "'Bill Depth':'#4BB9E1', 'Bill Length':'#87CEFA', 'Flipper Length':'#D3D3D3'",
        "xLabelName": "企鹅种类",
        "xLabelColor": "#333333",
        "xLabelFontSize": 9,
        "yLabelName": "长度 (mm)",
        "yLabelColor": "#333333",
        "yLabelFontSize": 9,
        "showYTicks": False, 
        "data": [
            {"species": "Adelie", "arr": [18.35, 38.79, 189.95, 50, 60]},  # 超过y_keys数量，多余数据会被忽略
            {"species": "Chinstrap", "arr": [18.43, 48.83, 195.82]},
            {"species": "Gentoo", "arr": [14.98]}
        ]
    }
    
    # 运行测试用例1
    print("生成短标签柱状图（arr长度一致）...")
    bar_chart_utils_short = BarChartUtils(param_short)
    filename_short = bar_chart_utils_short.generate_bar_chart()
    print(f"短标签图片已保存：{filename_short}")
    
    # 运行测试用例2
    print("\n生成长标签柱状图（arr长度不一致，测试0填充）...")
    bar_chart_utils_long = BarChartUtils(param_long)
    filename_long = bar_chart_utils_long.generate_bar_chart()
    print(f"长标签图片已保存：{filename_long}")
    
    # 运行测试用例3
    print("\n生成arr长度超过y_keys的柱状图...")
    bar_chart_utils_extra = BarChartUtils(param_extra)
    filename_extra = bar_chart_utils_extra.generate_bar_chart()
    print(f"arr超长图片已保存：{filename_extra}")
