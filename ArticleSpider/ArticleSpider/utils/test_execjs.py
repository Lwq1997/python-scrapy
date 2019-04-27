# -*- coding: utf-8 -*-
# @Time    : 2019/4/27 11:43
# @Author  : Lwq
# @File    : test_execjs.py
# @Software: PyCharm
import execjs

print(execjs.get().name)  # 查看调用的环境

with open('./test.js') as f:  # 执行 JS 文件
    ctx = execjs.compile(f.read())
    print(ctx.call('add', 1, 2))
