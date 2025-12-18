from sys import stderr
from typing import Dict, Optional
import os
def _get_fallback_username(cwd: Optional[str] = None) -> str:
    """
    获取系统用户名兜底方案
    参考JavaScript实现：name = process.env.USER || process.env.USERNAME || await runCmd('whoami', effectiveCwd) || 'unknown'
    """
    # 1. 尝试从环境变量 USER 获取
    name = os.environ.get('USER')
    if name:
        return name
    
    # 2. 尝试从环境变量 USERNAME 获取 (Windows)
    name = os.environ.get('USERNAME')
    if name:
        return name
    
    # 4. 最终兜底
    return 'unknown'

def get_user_info(cwd: Optional[str] = None) -> Dict[str, str]:
    """
    获取用户信息，优先从Git配置获取，失败时使用系统用户信息兜底
    """
    if cwd is None:
        cwd = os.getcwd()
    
    name = 'unknown'
    email = 'unknown'
    
    # 首先尝试从Git配置获取用户信息
    try:
        import git
        
        # 打开 Git 仓库
        repo = git.Repo(cwd, search_parent_directories=True)
        
        # 获取配置
        config = repo.config_reader()
        
        try:
            name = config.get('user', 'name')
        except (git.exc.ConfigError, ValueError):
            name = None
        
        try:
            email = config.get('user', 'email')
        except (git.exc.ConfigError, ValueError):
            email = 'unknown'
            
    except (ImportError, Exception):
        # Git不可用或其他异常
        pass
    
    # 如果从Git获取不到用户名，使用系统用户信息兜底
    if not name or name == 'unknown':
        name = _get_fallback_username(cwd)
    
    return {'name': name, 'email': email, 'cwd': cwd}

if __name__ == "__main__":
    user_info = _get_fallback_username("/Users/chenshuren.5/proj/coze-studio")
    print(user_info)