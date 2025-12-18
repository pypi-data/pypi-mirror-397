import ast
import numpy as np
from kt_base import CommonUtils
from matplotlib import pyplot as plt, ticker
from kt_text.Config import Config

class BarAndLineChartUtils:
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
        self.key = param.get("key")
        if self.key is None:
            raise Exception("X轴取数标识：key，不能为空")
        
        # 柱状图颜色配置
        self.bar_color = param.get("barColor")
        if self.bar_color is None:
            raise Exception("柱状图颜色：barColor，不能为空")
        
        # 折线图颜色配置
        self.line_color = param.get("lineColor")
        if self.line_color is None:
            raise Exception("折线图颜色：lineColor，不能为空")
        
        # 柱状图标签名称
        self.bar_label_name = param.get("barLabelName", "barData")
        
        # 折线图标签名称
        self.line_label_name = param.get("lineLabelName", "lineData")
        
        # Y轴数值是否展示
        self.show_y_ticks = param.get("showYTicks", True)
        
        # 数据配置
        self.data = param.get("data")
        if self.data is None:
            raise Exception("用于生成图表的数据：data，不能为空")
        if isinstance(self.data, str):
            self.data = ast.literal_eval(self.data)
    
    def __str__(self):
        fields = vars(self)
        field_str = ', '.join([f"{k}={v}" for k, v in fields.items()])
        return f"BarAndLineChartUtils({field_str})"
    
    def generate_bar_and_line_chart(self):
        # 准备数据
        x = []
        bar_data = []
        line_data = []
        
        for item in self.data:
            x.append(item.get(self.key))
            bar_data.append(item.get("barData"))
            line_data.append(item.get("lineData"))
        
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
            # 每超过5个字符，高度增加0.15
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
        width = 0.8  # 柱状图宽度
        
        rects = ax.bar(x_pos, bar_data, width, 
                      label=self.bar_label_name, color=self.bar_color, alpha=0.9)
        
        # 生成折线图
        ax.plot(x_pos, line_data, label=self.line_label_name, color=self.line_color, 
               linestyle='-', linewidth=1.2, alpha=0.9, marker='o', markersize=3)
        
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
        ax.set_xticks(x_pos)
        ax.set_xticklabels(x, rotation=45, va='top', ha='right', rotation_mode='anchor')
        
        # 输出调试信息，查看标签长度和计算结果
        print(f"DEBUG: 最大标签长度: {max_label_length}")
        
        # 根据标签最大长度调整参数，使用更明显的调整幅度
        if max_label_length <= 5:
            legend_y = -0.13
            bottom_margin = 0.15
        elif max_label_length <= 10:
            legend_y = -0.2
            bottom_margin = 0.2
        elif max_label_length <= 15:
            legend_y = -0.25
            bottom_margin = 0.25
        elif max_label_length <= 20:
            legend_y = -0.3
            bottom_margin = 0.3
        elif max_label_length <= 25:
            legend_y = -0.35
            bottom_margin = 0.35
        else:  # 标签较长
            legend_y = -0.4
            bottom_margin = 0.4
        
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
        # 使用Windows兼容的路径
        plt.savefig(Config.BASE_PATH + file_name)  # 保存到当前目录
        return file_name


if __name__ == "__main__":
    # 测试用例：同时包含柱状图和折线图的组合图表
    param = {
        "titleName": "PV和UV趋势图",
        "titleColor": "#333333",
        "titleFontSize": 12,
        "titleFontWeight": "bold",
        "key": "hour",
        "barColor": "#AF7000",
        "lineColor": "#8ECBE2",
        "barLabelName": "页面访问量(PV)",
        "lineLabelName": "独立访客数(UV)",
        "xLabelName": "小时",
        "xLabelColor": "#333333",
        "xLabelFontSize": 9,
        "yLabelName": "数量",
        "yLabelColor": "#333333",
        "yLabelFontSize": 9,
        "showYTicks": True, 
        "data": [
            {"hour": "2025-12-01 00", "barData": 1200000, "lineData": 1400000},
            {"hour": "2025-12-01 01", "barData": 2000000, "lineData": 1200000},
            {"hour": "2025-12-01 02", "barData": 1500000, "lineData": 1300000},
            {"hour": "2025-12-01 03", "barData": 1300000, "lineData": 1200000},
            {"hour": "2025-12-01 04", "barData": 1200000, "lineData": 1600000},
            {"hour": "2025-12-01 05", "barData": 1200000, "lineData": 1600000},
            {"hour": "2025-12-01 06", "barData": 1100000, "lineData": 1700000},
            {"hour": "2025-12-01 07", "barData": 1000000, "lineData": 1300000},
            {"hour": "2025-12-01 08", "barData": 1700000, "lineData": 1000000},
            {"hour": "2025-12-01 09", "barData": 1200000, "lineData": 1600000},
            {"hour": "2025-12-01 10", "barData": 1100000, "lineData": 1700000},
            {"hour": "2025-12-01 11", "barData": 1000000, "lineData": 1300000},
            {"hour": "2025-12-01 12", "barData": 1200000, "lineData": 1600000},
            {"hour": "2025-12-01 13", "barData": 1100000, "lineData": 1700000},
            {"hour": "2025-12-01 14", "barData": 1000000, "lineData": 1300000},
            {"hour": "2025-12-01 15", "barData": 1200000, "lineData": 1600000},
            {"hour": "2025-12-01 16", "barData": 1100000, "lineData": 1700000},
            {"hour": "2025-12-01 17", "barData": 1000000, "lineData": 1300000}
        ]
    }
    
    # 运行测试用例
    print("生成柱状图和折线图组合图表...")
    chart_utils = BarAndLineChartUtils(param)
    filename = chart_utils.generate_bar_and_line_chart()
    print(f"图片已保存：{filename}")
