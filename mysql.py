#!/usr/bin/env python3
# encoding: utf-8
"""
@author: souno.io
@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.
@contact: souno@qq.com
@file: mysql.py
@time: 18-11-7 下午4:49
@desc:
"""

import pymysql
import configparser

class Pysql(object):
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("lpr.conf", encoding="utf-8-sig")
        self.get_conn()

    def get_conn(self):
        try:
            self.a = 1
            self.conn = pymysql.connect(
                host=self.config['DATABASE']['host'],
                port=int(self.config['DATABASE']['port']),
                user=self.config['DATABASE']['user'],
                password=self.config['DATABASE']['passwd'],
                charset=self.config['DATABASE']['charset'],
                database=self.config['DATABASE']['db']
            )
        except pymysql.Error as e:
            print(e)

    def close_conn(self):
        try:
            if self.conn:
                self.conn.close()
        except pymysql.Error as e:
            print(e)

    def get(self):
        """
        :return: 获取数据库中的一条数据返回这条数据的title字段
        """
        # 准备sql
        sql = 'SELECT * FROM `chepai`'
        # 获取cursor
        cursor = self.conn.cursor()
        # 执行sql
        cursor.execute(sql)
        # 拿到结果   dict(zip(['a','b'],(1,2)))  ==> {'a': 1, 'b': 2}  cursor.fetchone 拿到的是这条数据的元祖格式
        res = dict(zip([x[0] for x in cursor.description], cursor.fetchone()))
        # 处理结果
        print(res['chepai'])
        # 关闭cursor/连接
        cursor.close()
        self.close_conn()

    # def get_more(self, page, page_size):
    #     """
    #     :param page: 显示当前页面
    #     :param page_size: 每页显示的行数
    #     :return: 获取数据库中的多条数据的title字段
    #     """
    #     # 准备sql
    #     offset = (page - 1) * page_size
    #     sql = 'SELECT * FROM `news` WHERE `types`=%s ORDER BY `create_at` DESC LIMIT %s,%s;'
    #     # 获取cursor
    #     cursor = self.conn.cursor()
    #     # 执行sql
    #     cursor.execute(sql, ('腾讯', offset, page_size))
    #     # 拿到结果
    #     # print(cursor.fetchall())
    #     res = [dict(zip([x[0] for x in cursor.description], row)) for row in cursor.fetchall()]
    #     # 处理结果
    #     for ele in res:
    #         print(ele['title'])
    #     # 关闭cursor/连接
    #     cursor.close()
    #     self.close_conn()

    def add_one(self, chepai, shijian):
        try:
            # 准备sql
            sql = ("INSERT INTO `chepai`(`chepai`,`time`) VALUES"
                   "(%s,%s);"
                   )
            # 获取cursor
            cursor = self.conn.cursor()
            # 执行sql
            cursor.execute(sql, (chepai, shijian))
            # cursor.execute(sql, (chepai, shijian, 1))
            # 提交事务
            self.conn.commit()
        except:
            print('error')
            self.conn.commit()  # 如果上面的提交有错误，那么只执行对的那一个提交
            # self.conn.rollback()   # 如果有错误，就回滚
        # 关闭连接
        cursor.close()
        self.close_conn()




