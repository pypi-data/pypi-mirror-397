import talib

from xmpy_ctastrategy import (
    类_CTA策略模板,
    类_停止单,
    类_行情数据,
    类_K线数据,
    类_成交数据,
    类_订单数据,
    类_K线生成器,
)

class 示例策略_技术指标合成教程(类_CTA策略模板):
    作者 = "bhzyxyqy"

    # 策略参数
    初始手数 = 0

    # 策略变量
    计数 = 0

    # 写入参数和变量列表的会分别写入到文件 cta_参数设置.json，cta_变量数据.json，没有写入列表的则不会
    参数列表 = ["初始手数"]
    变量列表 = ["计数"]

    def 初始化回调(self):
        self.记录日志("策略初始化回调")

        self.K线生成器 = 类_K线生成器(self.K线回调)

    def 启动回调(self):
        self.记录日志("策略启动")

    def 停止回调(self):
        self.记录日志("策略停止")

    def 行情回调(self, tick: 类_行情数据):
        self.K线生成器.更新Tick(tick)

    def K线回调(self, K线: 类_K线数据):
        self.计数 += 1
        self.记录日志(f'K线当前计数：{self.计数}')

        """
        先前的指标计算方法废弃了
        计算指标，调talib库的各种指标计算方法吧，懒得写了 
        """

    def 委托回调(self, 委托: 类_订单数据):
        self.记录日志(f'委托回报：{委托}')

    def 成交回调(self, 成交: 类_成交数据):
        self.记录日志(f'成交回报：{成交}')

    def 停止单回调(self, 停止单: 类_停止单):
        self.记录日志(f'停止单回调：{停止单}')
