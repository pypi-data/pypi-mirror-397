import ast

from kt_base import CommonUtils
from matplotlib import pyplot as plt, ticker
from kt_text.Config import Config

class AlignTickLabelsUtils:
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
        
        # Y轴刻度标签对齐配置
        self.y_tick_alignment = param.get("yTickAlignment", "left")  # 可选值: left, right, center
        ## self.y_tick_pad = param.get("yTickPad", 20)  # 刻度标签内边距
        self.y_tick_pad = 5
        
        # 柱状图颜色配置
        self.bar_colors = param.get("barColors", "#1f77b4")  # 默认蓝色
        
        # 数据配置
        self.data = param.get("data")
        if self.data is None:
            raise Exception("用于生成对齐刻度标签图表的数据：data，不能为空")
        if isinstance(self.data, str):
            self.data = ast.literal_eval(self.data)
    
    def __str__(self):
        fields = vars(self)
        field_str = ', '.join([f"{k}={v}" for k, v in fields.items()])
        return f"AlignTickLabelsUtils({field_str})"
    
    def generate_align_tick_labels_chart(self):
        # 准备数据
        labels = list(self.data.keys())
        values = list(self.data.values())
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimSun']  # 使用宋体
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        
        # 计算Y轴标签的最大长度，用于动态调整画布宽度
        max_label_length = max(len(label) for label in labels)
        
        # 计算Y轴标题的长度，用于动态调整左侧边距
        # max_label_length = len(self.y_label_name) if self.y_label_name else 0
        
        # 设置图表大小，根据标签长度动态调整宽度
        fig_width = 10  # 默认宽度
        fig_height = 7.5  # 默认高度
        
        # 根据标签长度调整画布宽度
        if max_label_length > 5:
            # 每超过5个字符，宽度增加0.3
            fig_width = 10 + (max_label_length - 5) * 0.3
            # 设置最大宽度限制
            fig_width = min(fig_width, 20.0)
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=200)
        fig.patch.set_facecolor('#FFFFFF')
        
        # 设置图表背景色
        ax.set_facecolor('#FFFFFF')
        # 调整子图位置，根据Y轴标题长度动态调整左侧边距
        ax.set_position([0.1, 0.1, 0.8, 0.8])
        
        # 设置边框样式，只显示底部和左侧边框
        for spine_name, spine in ax.spines.items():
            if spine_name == 'top' or spine_name == 'right':
                spine.set_visible(False)  # 隐藏顶部和右侧边框
            else:
                spine.set_color('#d7d7d7')  # 设置底部和左侧边框颜色
        
        # 绘制水平柱状图
        ax.barh(labels, values, color=self.bar_colors)
        
        # 反转Y轴，使第一个数据显示在顶部
        ax.invert_yaxis()
        
        # 设置标题
        if self.title_name != '':
            ax.set_title(self.title_name, color=self.title_color, 
                        fontsize=self.title_font_size, 
                        fontweight=self.title_font_weight, 
                        pad=20)
        
        # 设置X轴名称（标题）
        if self.x_label_name != '':
            ax.set_xlabel(self.x_label_name, color=self.x_label_color, 
                         fontsize=self.x_label_font_size, labelpad=10)
        
        # 设置Y轴名称（标题）
        if self.y_label_name != '':
            ax.set_ylabel(self.y_label_name, color=self.y_label_color, 
                         fontsize=self.y_label_font_size, labelpad=5)
        
        # 对齐Y轴刻度标签
        for ticklabel in ax.get_yticklabels():
            ticklabel.set_horizontalalignment('right')  # 设置为右对齐，使标签靠近Y轴
        
        # 调整Y轴刻度标签内边距
        ax.tick_params("y", pad=self.y_tick_pad, direction='out', length=4, width=0, color='#d7d7d7')
        
        # 设置刻度样式
        ax.tick_params(axis="x", labelsize=8, colors="#111111", pad=3)
        ax.tick_params(axis="y", labelsize=8, colors="#111111")
        
        # 设置X轴刻度格式，不使用科学计数法
        ax.get_xaxis().set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        
        # 设置X轴范围从0开始
        ax.set_xlim(left=0)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图片
        filename = self.save_img()
        plt.close(fig)
        return filename
    
    def save_img(self):
        file_name = CommonUtils.generate_uuid() + ".png"
        plt.savefig(Config.BASE_PATH + file_name)  # 保存到当前目录
        return file_name


if __name__ == "__main__":
    # 基本测试用例
    print("生成基本对齐刻度标签图表...")
    param_basic = {
        "titleName": "基本对齐刻度标签图表",
        "titleColor": "#333333",
        "titleFontSize": 12,
        "titleFontWeight": "bold",
        "xLabelName": "数值",
        "xLabelColor": "#333333",
        "xLabelFontSize": 9,
        "yLabelName": "类别",
        "yLabelColor": "#333333",
        "yLabelFontSize": 9,
        "yTickAlignment": "left",
        "yTickPad": 70,
        "data": {
            "Sydney": 5.2,
            "Mexico City": 8.8,
            "São Paulo": 12.2,
            "Istanbul": 15.9,
            "Lagos": 15.9,
            "Shanghai": 21.9
        }
    }
    
    align_tick_labels_utils = AlignTickLabelsUtils(param_basic)
    filename = align_tick_labels_utils.generate_align_tick_labels_chart()
    print(f"基本对齐刻度标签图表已保存：{filename}")
    
    # 自定义颜色测试用例
    print("\n生成自定义颜色对齐刻度标签图表...")
    param_color = {
        "titleName": "自定义颜色对齐刻度标签图表",
        "titleColor": "#333333",
        "titleFontSize": 12,
        "titleFontWeight": "bold",
        "xLabelName": "数值",
        "xLabelColor": "#333333",
        "xLabelFontSize": 9,
        "yLabelName": "类别",
        "yLabelColor": "#333333",
        "yLabelFontSize": 9,
        "yTickAlignment": "left",
        "yTickPad": 70,
        "barColors": "#ff7f0e",  # 橙色
        "data": {
            "Sydney": 5.2,
            "Mexico City": 8.8,
            "São Paulo": 12.2,
            "Istanbul": 15.9,
            "Lagos": 15.9,
            "Shanghai": 21.9
        }
    }
    
    align_tick_labels_utils_color = AlignTickLabelsUtils(param_color)
    filename_color = align_tick_labels_utils_color.generate_align_tick_labels_chart()
    print(f"自定义颜色对齐刻度标签图表已保存：{filename_color}")
    
    # 多颜色测试用例
    print("\n生成多颜色对齐刻度标签图表...")
    param_multi_color = {
        "titleName": "多颜色对齐刻度标签图表",
        "titleColor": "#333333",
        "titleFontSize": 12,
        "titleFontWeight": "bold",
        "xLabelName": "数值",
        "xLabelColor": "#333333",
        "xLabelFontSize": 9,
        "yLabelName": "类别",
        "yLabelColor": "#333333",
        "yLabelFontSize": 9,
        "yTickAlignment": "left",
        "yTickPad": 70,
        "barColors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],  # 多种颜色
        "data": {
            "Sydney": 5.2,
            "Mexico City": 8.8,
            "São Paulo": 12.2,
            "Istanbul": 15.9,
            "Lagos": 15.9,
            "Shanghai": 21.9
        }
    }
    
    align_tick_labels_utils_multi_color = AlignTickLabelsUtils(param_multi_color)
    filename_multi_color = align_tick_labels_utils_multi_color.generate_align_tick_labels_chart()
    print(f"多颜色对齐刻度标签图表已保存：{filename_multi_color}")
    
    # 中文标签测试用例
    print("\n生成中文标签对齐刻度标签图表...")
    param_chinese = {
        "titleName": "中文标签对齐刻度标签图表",
        "titleColor": "#333333",
        "titleFontSize": 12,
        "titleFontWeight": "bold",
        "xLabelName": "数值",
        "xLabelColor": "#333333",
        "xLabelFontSize": 9,
        "yLabelName": "城市",
        "yLabelColor": "#333333",
        "yLabelFontSize": 9,
        "yTickAlignment": "left",
        "yTickPad": 80,
        "data": {
            "北京": 21.54,
            "上海": 24.28,
            "广州": 18.67,
            "深圳": 17.56,
            "成都": 21.19,
            "杭州": 12.20
        }
    }
    
    align_tick_labels_utils_chinese = AlignTickLabelsUtils(param_chinese)
    filename_chinese = align_tick_labels_utils_chinese.generate_align_tick_labels_chart()
    print(f"中文标签对齐刻度标签图表已保存：{filename_chinese}")
    
    # 长标签测试用例
    print("\n生成长标签对齐刻度标签图表...")
    param_long = {
        "titleName": "长标签对齐刻度标签图表",
        "titleColor": "#333333",
        "titleFontSize": 12,
        "titleFontWeight": "bold",
        "xLabelName": "数值",
        "xLabelColor": "#333333",
        "xLabelFontSize": 9,
        "yLabelName": "项目",
        "yLabelColor": "#333333",
        "yLabelFontSize": 9,
        "yTickAlignment": "left",
        "yTickPad": 100,
        "data": {
            "2025年第一季度销售数据": 1250000,
            "2025年第二季度销售数据": 1560000,
            "2025年第三季度销售数据": 1890000,
            "2025年第四季度销售数据": 2150000,
            "2025年年度销售总额": 6850000
        }
    }
    
    align_tick_labels_utils_long = AlignTickLabelsUtils(param_long)
    filename_long = align_tick_labels_utils_long.generate_align_tick_labels_chart()
    print(f"长标签对齐刻度标签图表已保存：{filename_long}")
    
    # 不同对齐方式测试用例
    print("\n生成右对齐刻度标签图表...")
    param_right = {
        "titleName": "右对齐刻度标签图表",
        "titleColor": "#333333",
        "titleFontSize": 12,
        "titleFontWeight": "bold",
        "xLabelName": "数值",
        "xLabelColor": "#333333",
        "xLabelFontSize": 9,
        "yLabelName": "类别",
        "yLabelColor": "#333333",
        "yLabelFontSize": 9,
        "yTickAlignment": "right",
        "yTickPad": 50,
        "data": {
            "Sydney": 5.2,
            "Mexico City": 8.8,
            "São Paulo": 12.2,
            "Istanbul": 15.9,
            "Lagos": 15.9,
            "Shanghai": 21.9,
            "Shanghai1": 21,
            "Shanghai3": 25,
            "Shanghai4": 15
        }
    }
    
    align_tick_labels_utils_right = AlignTickLabelsUtils(param_right)
    filename_right = align_tick_labels_utils_right.generate_align_tick_labels_chart()
    print(f"右对齐刻度标签图表已保存：{filename_right}")
    
    # 长Y轴标题测试用例
    print("\n生成长Y轴标题对齐刻度标签图表...")
    param_long_y_label = {
        "titleName": "长Y轴标题对齐刻度标签图表",
        "titleColor": "#333333",
        "titleFontSize": 12,
        "titleFontWeight": "bold",
        "xLabelName": "数值",
        "xLabelColor": "#333333",
        "xLabelFontSize": 9,
        "yLabelName": "这是一个非常长的Y轴标题名称",
        "yLabelColor": "#333333",
        "yLabelFontSize": 9,
        "yTickAlignment": "left",
        "yTickPad": 70,
        "data": {
            "Sydney": 5.2,
            "Mexico City": 8.8,
            "São Paulo": 12.2,
            "Istanbul": 15.9,
            "Lagos": 15.9,
            "Shanghai": 21.9
        }
    }
    
    align_tick_labels_utils_long_y = AlignTickLabelsUtils(param_long_y_label)
    filename_long_y = align_tick_labels_utils_long_y.generate_align_tick_labels_chart()
    print(f"长Y轴标题对齐刻度标签图表已保存：{filename_long_y}")
