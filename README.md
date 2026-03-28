**回测采用自建框架**

股票池-单因子选股-仓位分配-单因子回测

多因子回测-barbell组合优化

eod_prices文件因为太大没有放进来，项目同步时需要手动上传

util.py记录公用工具函数

mv.ipynb记录小市值单因子回测

选股情况记录在records/目录下

红利+低波因子composite基准为等权z-score；目前使用的复合方式是使用IC加权；低波因子采用1/log（downside deviation）的方式
