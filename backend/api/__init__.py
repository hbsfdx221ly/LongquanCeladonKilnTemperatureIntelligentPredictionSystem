"""
API蓝图包
"""

from flask import Blueprint

api_bp = Blueprint('api', __name__)

# 导入所有API路由
from .batch_api import *
from .prediction_api import *
from .sensor_api import *
from .image_api import *
