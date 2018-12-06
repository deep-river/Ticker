# Ticker
A web-app that synchronizes data between databases and visualize data using Flask + Echars.
A project for my 2018 summer internship. 

执行环境：  
Python3.6.5 + Flask框架 + Echarts4  
Python包依赖：  
	Flask  
	Flask-APScheduler  
	pymongo  
	SQLAlchemy  
	
**************************************************************************

模块说明：  
-DBConn.py  
	数据库连接、关闭连接，及增、查操作的封装函数  
	
-DBConn_config.ini  
	源数据库[Oracle]及目标数据库[Mongodb]的连接配置文件  
	
-Main.py  
	后端程序入口  
	从目标数据库获取查询语句，然后对源数据库执行查询。查询结果计算后以json格式存入目标数据库[Records]集合。  
	
-QueryMath.py  
	Main.py中所需的计算函数  
	
-SendNotification.py  
	发送提醒邮件模块  
	
-Notification_config.ini  
	SendNotification.py所需的邮箱账号配置文件  
	
-Ticker-Flask.py  
	前端程序入口  
	处理数据并与前端页面交互  
	定义了路由及api  
	设置了默认每隔一个小时执行一次Main.py中的main_func函数  
	
-templates/Ticker-view.html  
	前端页面  
	由Ticker-Flask.py渲染  
	定义了Echarts图表的相关配置  
	
-static/*  
	前端页面依赖的js文件  

**************************************************************************

API说明：
- */api/v1.0/data/<string:query>/all/
	以Json格式返回<指定类目>中全部数据查询结果
	示例 */api/v1.0/data/A/all/
	*/api/v1.0/data/all/all/ 返回全部数据查询结果
	地址区分大小写
	
- */api/v1.0/data/<string:query>/<int:numlimit>/
	以Json格式返回<指定类目-指定条数>的数据查询结果
	示例 */api/v1.0/data/A/25
	*/api/v1.0/data/all/<int:numlimit>/返回<全部类目-指定条数>的数据查询结果
	地址区分大小写

- */api/v1.0/data/<string:datefrom>/<string:dateto>/<string:query>/all/
    以Json格式返回<指定日期区间内-指定类目>中全部数据查询结果
    起始日期格式必须为 yyyy-mm-dd，如 2018-10-1、2018-6-6，程序中实际执行时会按该日期的当日00:00:00作为时间戳查询数据库， 即2018-10-1 00:00:00、2018-6-6 00:00:00
    示例 */api/v1.0/data/2018-7-16/2018-7-19/F/all/
    */api/v1.0/data/yyyy-mm-dd/yyyy-mm-dd/all/all/返回<指定日期区间内全部类目>的数据查询结果
    地址区分大小写

**************************************************************************

Mongodb数据存储：
[Records]集合为主要操作集合，存储60天内所有记录
[Old_records]为旧记录存档，存储180天前到60天前时间段内所有记录
超过180天前的记录会被删除

**************************************************************************

文件配置说明：
-Notification_config.ini中Method字段为加密方法，参考具体邮件服务提供方的POP3/SMTP/IMAP设置页面，支持STARTTLS，SSL（如：163，QQ等）两种加密方式
 Content字段为自定义邮件内容，可缺省

    163邮箱配置示例：
    [Mail]
    Host_server=smtp.163.com
    Port=465
    Method=SSL
    Sender=xxxxxx
    Password=xxxxxx
    Sender_mail=xxxxxx@163.com
    Receiver=xxxxxx@gmail.com, xxxxxx@qq.com
    Content=

**************************************************************************

定时执行参数定义在Ticker-Flask.py的class Config(object)类的JOBS列表中。
'func'字段为定时执行的函数名，
'trigger'为定时执行方式，默认为'interval'即间隔一定时间执行，
'minutes'字段为函数执行间隔，默认定义为每30分钟执行一次，即'minutes': 30 。修改该字段即可自定义执行间隔，如每一小时执行一次则修改为'hours': 1。
