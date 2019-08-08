# -*- coding: UTF-8 -*-
from package.config import config           #导入固件配置
from package.include.mylib import mylib     #我的类库
from package.include.logbug import log      #我的类库
from package.data import data               #数据库接口


class Base():
    """基本类（会被所有类继承）"""

    config = config

    mylib = mylib()

    data = data()