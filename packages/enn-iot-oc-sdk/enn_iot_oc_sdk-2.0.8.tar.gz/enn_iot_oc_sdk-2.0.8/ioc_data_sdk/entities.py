"""
实体类定义模块

此模块包含所有预定义的实体类，用户可以直接使用这些类进行数据访问。

推荐使用方式：
    from enn_iot_oc.infrastructure.model import Customer, CustomerRepoImpl
"""

# 从 enn_iot_oc 导入生成的实体类
from enn_iot_oc.infrastructure.model.Customer import Customer
from enn_iot_oc.infrastructure.model.CustomerProfile import CustomerProfile
from enn_iot_oc.infrastructure.model.CustomerCategory import CustomerCategory
from enn_iot_oc.infrastructure.model.ProfileDimension import ProfileDimension
from enn_iot_oc.infrastructure.model.CategoryRequirement import CategoryRequirement

__all__ = [
    "Customer",
    "CustomerProfile",
    "CustomerCategory",
    "ProfileDimension",
    "CategoryRequirement"
]