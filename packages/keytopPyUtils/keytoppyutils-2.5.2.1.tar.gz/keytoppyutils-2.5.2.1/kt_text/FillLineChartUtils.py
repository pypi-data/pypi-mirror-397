import ast

from kt_base import CommonUtils
from matplotlib import pyplot as plt, ticker
from kt_text.Config import Config

class FillLineChartUtils:
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
            raise Exception("用于生成折线图的数据：data，不能为空")
        if isinstance(self.data, str):
            self.data = ast.literal_eval(self.data)
    
    def __str__(self):
        fields = vars(self)
        field_str = ', '.join([f"{k}={v}" for k, v in fields.items()])
        return f"FillLineChartUtils({field_str})"
    
    def generate_fill_line_chart(self):
        # 准备数据
        x = []
        grouped_data = {key: [] for key in self.y_keys}
        
        for item in self.data:
            x.append(item.get(self.x_key))
            for key in self.y_keys:
                grouped_data[key].append(item[key])
        
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
        print(f"DEBUG: 填充折线图画布大小设置为: {fig_size} (基于最大标签长度: {max_label_length})")
        
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
        
        # 绘制多条折线并添加填充
        for key in self.y_keys:
            ax.plot(x, grouped_data[key], label=key, color=self.y_keys[key], 
                   linestyle='-', linewidth=0.8, alpha=0.9)
            # 添加折线和X轴之间的填充
            ax.fill_between(x, 0, grouped_data[key], color=self.y_keys[key], alpha=0.2)
        
        # 设置标题
        if self.title_name != '':
            ax.set_title(self.title_name, color=self.title_color, 
                        fontsize=self.title_font_size, 
                        fontweight=self.title_font_weight, 
                        pad=20)
        
        # 设置X轴名称（标题），恢复正常labelpad
        if self.x_label_name != '':
            ax.set_xlabel(self.x_label_name, color=self.x_label_color, 
                         fontsize=self.x_label_font_size, labelpad=10)
        
        # 设置Y轴名称（标题），恢复正常labelpad
        if self.y_label_name != '':
            ax.set_ylabel(self.y_label_name, color=self.y_label_color, 
                         fontsize=self.y_label_font_size, labelpad=10)
        
        # 设置X轴刻度倾斜45度
        ax.set_xticks(range(len(x)))
        ax.set_xticklabels(x, rotation=45, va='top', ha='right', rotation_mode='anchor')
        
        # 设置Y轴数值是否展示
        if not self.show_y_ticks:
            ax.set_yticks([])
        
        # 设置刻度样式，调整刻度标签与坐标轴的距离
        ax.tick_params(direction='out', length=4, width=0, color='#d7d7d7', pad=5)
        ax.tick_params(axis="y", labelsize=8, colors="#111111", pad=3)  # 减小Y轴刻度标签与Y轴的距离
        
        # 调整X轴刻度字体大小和与X轴的距离，确保长标签不会重叠
        if 8 <= len(self.data) < 12:
            ax.tick_params(axis="x", labelsize=7, colors="#111111", pad=5)
        elif 12 <= len(self.data) < 18:
            ax.tick_params(axis="x", labelsize=6, colors="#111111", pad=5)
        elif len(self.data) >= 18:
            ax.tick_params(axis="x", labelsize=5, colors="#111111", pad=5)
        else:
            ax.tick_params(axis="x", labelsize=8, colors="#111111", pad=5)
        
        # 设置网格线
        ax.grid(True, axis='y', linestyle="-", color="#d7d7d7", linewidth=0.3, alpha=0.5)
        
        # 设置Y轴刻度格式，不使用科学计数法
        ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        
        # 设置坐标轴范围，确保从(0,0)开始
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)
        
        # 根据标签最大长度调整图例位置和底部边距参数
        print(f"DEBUG: 填充折线图最大标签长度: {max_label_length}")
        if max_label_length >= 5:
            # 根据标签最大长度调整参数
            if max_label_length <= 10:
                legend_y = -0.18
                bottom_margin = 0.2
            elif max_label_length <= 20:
                legend_y = -0.23
                bottom_margin = 0.23
            elif max_label_length <= 30:
                legend_y = -0.28
                bottom_margin = 0.28
            elif max_label_length <= 40:
                legend_y = -0.35
                bottom_margin = 0.35
            else:  # 标签较长
                legend_y = -0.5
                bottom_margin = 0.5
        
        # 设置图例在图表下方，动态调整位置
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
    param = {
        "titleName": "填充折线图",
        "titleColor": "#333333",
        "titleFontSize": 12,
        "titleFontWeight": "bold",
        "xKey": "date",
        "yKeys": "'折线1':'#FF5733', '折线2':'#33FF57', '折线3':'#3357FF'",
        "xLabelName": "日期",
        "xLabelColor": "#333333",
        "xLabelFontSize": 9,
        "yLabelName": "数值",
        "yLabelColor": "#333333",
        "yLabelFontSize": 9,
        "showYTicks": True, 
        "data": [
            {"date": "01-01", "折线1": 100000, "折线2": 200000, "折线3": 300000},
            {"date": "01-02", "折线1": 150000, "折线2": 250000, "折线3": 350000},
            {"date": "01-03", "折线1": 200000, "折线2": 300000, "折线3": 400000},
            {"date": "01-04", "折线1": 250000, "折线2": 350000, "折线3": 250000},
            {"date": "01-05", "折线1": 300000, "折线2": 400000, "折线3": 500000}
        ]
    }
        
    fill_line_chart_utils = FillLineChartUtils(param)
    fill_line_chart_utils.generate_fill_line_chart()
