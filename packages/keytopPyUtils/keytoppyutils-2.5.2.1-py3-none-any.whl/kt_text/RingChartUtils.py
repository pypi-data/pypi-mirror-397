import numpy as np
from kt_base import CommonUtils
from matplotlib import pyplot as plt
from kt_text.Config import Config

class RingChartUtils:
    def __init__(self, param):
        # 标题配置
        self.title_name = param.get("titleName", "")
        self.title_color = param.get("titleColor", "#333333")
        self.title_font_size = param.get("titleFontSize", 10)
        self.title_font_weight = param.get("titleFontWeight", "bold")
        
        # 环形宽度
        self.ring_width = param.get("ringWidth", 0.3)
        
        # 数据配置
        self.labels = param.get("labels")
        if self.labels is None:
            raise Exception("饼图标签：labels，不能为空")
        
        self.values = param.get("values")
        if self.values is None:
            raise Exception("饼图数值：values，不能为空")
        
        # 颜色配置
        self.colors = param.get("colors", None)
        
    def __str__(self):
        fields = vars(self)
        field_str = ', '.join([f"{k}={v}" for k, v in fields.items()])
        return f"RingChartUtils({field_str})"
    
    def generate_ring_chart(self):
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimSun']  # 使用宋体
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        
        # 设置图表大小
        fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
        fig.patch.set_facecolor('#FFFFFF')
        
        # 设置图表背景色
        ax.set_facecolor('#FFFFFF')
        
        # 生成环形图，不显示标签
        wedges, texts, autotexts = ax.pie(
            self.values, 
            labels=None,  # 去掉饼图上的名称
            autopct='',  # 不显示自动标签，后面手动添加
            startangle=90, 
            colors=self.colors,
            wedgeprops=dict(width=self.ring_width, edgecolor='w'),  # 环形宽度
            textprops={'color': '#333333', 'fontsize': 8}
        )
        
        # 手动添加外侧数值标签，使用折线连接
        for i, (wedge, value) in enumerate(zip(wedges, self.values)):
            # 获取饼图扇区的中心角度
            theta = wedge.theta2 - (wedge.theta2 - wedge.theta1) / 2
            theta_rad = theta * np.pi / 180
            
            # 计算外侧标签的位置
            radius = 1.2  # 标签距离中心的半径，略微增大
            label_radius = 1.27  # 数字标签距离中心的半径，比连线端点更远
            
            # 连线端点位置
            line_x = radius * np.cos(theta_rad)
            line_y = radius * np.sin(theta_rad)
            
            # 数字标签位置
            x = label_radius * np.cos(theta_rad)
            y = label_radius * np.sin(theta_rad)
            
            # 添加数值标签
            ax.text(
                x, y, f'{value}', 
                ha='center', va='center', 
                fontsize=10, color='#333333'
            )
            
            # 添加连接线段，使用灰色
            ax.plot(
                [wedge.r * np.cos(theta_rad), line_x], 
                [wedge.r * np.sin(theta_rad), line_y], 
                color='#999999', linewidth=0.5, linestyle='-'  # 灰色连线
            )
        
        # 设置标题
        if self.title_name != '':
            ax.set_title(
                self.title_name, 
                color=self.title_color, 
                fontsize=self.title_font_size, 
                fontweight=self.title_font_weight, 
                pad=20
            )
        
        # 设置图例在下方，横向排列，使用小方块，减小与饼图的距离
        ax.legend(
            wedges, 
            self.labels, 
            loc='upper center', 
            bbox_to_anchor=(0.5, 0),  # 减小y值，靠近饼图
            ncol=10,  # 横向排列
            handlelength=0.5,  # 减小图例形状长度
            handletextpad=0.5,  # 减小形状与文字间距
            columnspacing=1.0,  # 减小列间距
            prop={'size': 9},  # 字体大小
            labelcolor='#333333',  # 字体颜色
            frameon=False  # 去掉边框
        )
        
        # 设置等宽高比
        ax.set_aspect('equal')
        
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
    param = {
       # "titleName": "车标分布",
        "titleColor": "#333333",
        "titleFontSize": 12,
        "titleFontWeight": "bold",
        "labels": ["奔驰", "宝马", "大众","小米"],
        "values": [100, 200, 345,120],
        "colors": ["#4169E1", "#87CEFA", "#D3D3D3","#FF5733"],
        "ringWidth": 0.3
    }
        
    ring_chart_utils = RingChartUtils(param)
    filename = ring_chart_utils.generate_ring_chart()
    print(f"图片已保存：{filename}")
