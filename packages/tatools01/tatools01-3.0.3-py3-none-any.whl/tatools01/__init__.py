"""

tatools01


An python parametters library.
"""


__version__ = "3.0.3" # Nhớ update cả Readme.md


__author__ = "Nguyễn Tuấn Anh - nt.anh.fai@gmail.com"

__credits__ = "MIT License"
__console__ = "tact"
import os

import sys

import argparse

import json
 
   

from . import ParamsBase

from tatools01.Thoi_gian.taTimers import MultiTimer


__help__ = """
"""


from tatools01.md_word.convert_md_to_word import md2w_main

def md2w():
    print("Chạy md2w() để chuyển đổi file Markdown (.md) thành file Word (.docx)")
    md2w_main()
    


def console_main():
    print(
        """


1. tact
        """
    )
    
    print("""

        """

    )

    

    print("""

from tatools01.ParamsBase import TactParameters 

AppName = 'My_Project_Name'
            
_03(TactParameters):
        def __init__(self):

            super().__init__(ModuleName
="chatbotAPI", params_dir='./')
            self.HD = ["Chương trình
 chatbot"]
            
            
class clsMinio:
                IP = "192.168.3.3:8
800"
                access_key 
= "admin"
                secret_key = "Proton"

            
            self.M
inio = clsMinio()
            self.in_var = 1

            self.load_then_save_to_yaml(file_path=f"
{AppName}.yml")


mPs3 = Params_03()

print(f"Minio



print(f"type(Minio) = {type(mPs3.Minio)}")
print("✓ OK")







class Params_01(TactParame
ters):
    def __init__(self):

        super().__init__(ModuleName="
Module 01", params_dir='./')
        self.HD = ["Chương trình này nhằm xây dựng tham số
 cho các chương trình khác"]
        self.test1 = "123"

        self.in_var = 
1
        self.myList = [1, 
2, 3, 4, 5]
        self.myDict = {"key1": "val
ue1", "key2": "value2"}
        self.Multi_types_param
 = {
            "int": 42,

         
   "float": 3.14,
            "str": "Hello, World!",

            "list": [1, 2, 3],
            "dict": {"k
ey": "value"},
        }

        self.load_then_save_to_yaml(file_path=f"{AppName}.yml")


# Tạo instance đầu tiên

mPs1 = Params_01()



class Params_02(TactParameters):

    def __init__(self):

        super().__init_
_(ModuleName="Module 02", params_dir='./')
        self.HD = ["Chương trình này nhằm xây dựng tham số cho 

        self.test1 = "456"  # Giá trị khác để test
        self.test2 = "
New param"  # Thêm param mới
        self.in_va

        self.load_then_save_to_yaml(file_path=f"{AppName}.yml")


# Tạo instance thứ hai

mPs2 = Params_02()


# Test logging

mPs1.mlog("hello from module 01")

mPs2.mlog("hello from module 02")


print("Module 01 test1
:", mPs1.test1)
print("Module 02 test1:", mPs2.test1)

print("Module 02 test2:", 
mPs2.test2)


# Test đọc lại từ file

print("\n--- Test đọc lại từ file ---")

test_params1 = Params_01()
          """)

rint("Module 01 test1 (from file):", test_params1.test1)
print("Module 02 test1 (from file):", test_params2.test1)
print("Module 02 test2 (from file):", test_params2.test2)       
          """)

