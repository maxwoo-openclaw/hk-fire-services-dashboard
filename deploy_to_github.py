#!/usr/bin/env python3
"""
將香港消防處服務儀表板上傳到GitHub
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import requests

def check_git_installed():
    """檢查Git是否已安裝"""
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def initialize_git_repo():
    """初始化Git倉庫"""
    print("🔧 初始化Git倉庫...")
    
    # 檢查是否已經是Git倉庫
    if Path(".git").exists():
        print("✅ Git倉庫已存在")
        return True
    
    try:
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "branch", "-M", "main"], check=True, capture_output=True)
        print("✅ Git倉庫初始化成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 初始化Git倉庫失敗: {e}")
        return False

def create_github_repo(token, repo_name, description, is_private=False):
    """在GitHub創建倉庫"""
    print(f"🌐 在GitHub創建倉庫 '{repo_name}'...")
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "name": repo_name,
        "description": description,
        "private": is_private,
        "auto_init": False,
        "has_issues": True,
        "has_projects": True,
        "has_wiki": True
    }
    
    try:
        response = requests.post(
            "https://api.github.com/user/repos",
            headers=headers,
            json=data
        )
        
        if response.status_code == 201:
            repo_info = response.json()
            print(f"✅ 倉庫創建成功: {repo_info['html_url']}")
            return repo_info
        elif response.status_code == 422:
            # 倉庫可能已存在
            print("⚠️  倉庫可能已存在，嘗試獲取現有倉庫信息...")
            return get_existing_repo(token, repo_name)
        else:
            print(f"❌ 創建倉庫失敗: {response.status_code}")
            print(f"錯誤信息: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 創建倉庫時發生錯誤: {e}")
        return None

def get_existing_repo(token, repo_name):
    """獲取現有倉庫信息"""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(
            f"https://api.github.com/repos/{repo_name}",
            headers=headers
        )
        
        if response.status_code == 200:
            repo_info = response.json()
            print(f"✅ 獲取現有倉庫: {repo_info['html_url']}")
            return repo_info
        else:
            print(f"❌ 獲取倉庫信息失敗: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 獲取倉庫信息時發生錯誤: {e}")
        return None

def add_files_to_git():
    """添加文件到Git"""
    print("📁 添加文件到Git...")
    
    try:
        # 添加所有文件
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        
        # 提交更改
        commit_message = """初始提交：香港消防處服務儀表板

完整嘅Streamlit應用，顯示香港消防處數據：
- 救護站和消防局位置地圖
- 交互式數據可視化
- 地區分布分析
- 數據搜索和過濾
- CSV數據導出
- 完整文檔和安裝指南"""
        
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            check=True,
            capture_output=True
        )
        
        print("✅ 文件添加和提交成功")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 添加文件到Git失敗: {e}")
        return False

def push_to_github(token, repo_info):
    """推送到GitHub"""
    print("🚀 推送到GitHub...")
    
    # 設置遠程倉庫URL（包含令牌）
    repo_url = repo_info["clone_url"]
    username = repo_info["owner"]["login"]
    
    # 將令牌嵌入URL
    auth_url = repo_url.replace(
        "https://",
        f"https://{username}:{token}@"
    )
    
    try:
        # 添加遠程倉庫
        subprocess.run(
            ["git", "remote", "add", "origin", auth_url],
            check=True,
            capture_output=True
        )
        
        # 推送到GitHub
        subprocess.run(
            ["git", "push", "-u", "origin", "main"],
            check=True,
            capture_output=True
        )
        
        print(f"✅ 成功推送到GitHub: {repo_info['html_url']}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 推送到GitHub失敗: {e}")
        return False

def main():
    """主函數"""
    print("=" * 60)
    print("  香港消防處服務儀表板 - GitHub上傳腳本")
    print("=" * 60)
    print()
    
    # 檢查當前目錄
    current_dir = Path.cwd()
    if not (current_dir / "requirements.txt").exists():
        print("❌ 請在項目根目錄運行此腳本")
        return False
    
    # 檢查Git是否安裝
    if not check_git_installed():
        print("❌ 請先安裝Git")
        print("  下載地址: https://git-scm.com/downloads")
        return False
    
    # 獲取GitHub令牌
    print("🔐 GitHub配置")
    print("-" * 40)
    
    token = input("請輸入GitHub個人訪問令牌 (PAT): ").strip()
    if not token:
        print("❌ 需要GitHub個人訪問令牌")
        return False
    
    # 獲取倉庫信息
    repo_name = input("倉庫名稱 [hk-fire-services-dashboard]: ") or "hk-fire-services-dashboard"
    description = input("倉庫描述 [香港消防處服務儀表板]: ") or "香港消防處服務儀表板"
    
    private_input = input("是否設置為私有倉庫？ (y/n) [n]: ") or "n"
    is_private = private_input.lower() in ['y', 'yes']
    
    # 設置Git用戶信息
    print("\n👤 Git用戶配置")
    print("-" * 40)
    
    git_name = input("Git用戶名 [HK Fire Services Dashboard]: ") or "HK Fire Services Dashboard"
    git_email = input("Git郵箱 [hk-fire-services@example.com]: ") or "hk-fire-services@example.com"
    
    try:
        subprocess.run(["git", "config", "user.name", git_name], check=True)
        subprocess.run(["git", "config", "user.email", git_email], check=True)
        print("✅ Git用戶信息設置成功")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  設置Git用戶信息失敗: {e}")
    
    # 執行步驟
    steps = [
        ("初始化Git倉庫", lambda: initialize_git_repo()),
        ("創建GitHub倉庫", lambda: create_github_repo(token, repo_name, description, is_private)),
        ("添加文件到Git", lambda: add_files_to_git()),
    ]
    
    repo_info = None
    for step_name, step_func in steps:
        print(f"\n{'='*40}")
        print(f"步驟: {step_name}")
        print(f"{'='*40}")
        
        result = step_func()
        if not result:
            print(f"\n❌ 上傳失敗於: {step_name}")
            return False
        
        # 保存倉庫信息
        if step_name == "創建GitHub倉庫" and result:
            repo_info = result
    
    if not repo_info:
        print("❌ 無法獲取倉庫信息")
        return False
    
    # 推送到GitHub
    print(f"\n{'='*40}")
    print("步驟: 推送到GitHub")
    print(f"{'='*40}")
    
    if not push_to_github(token, repo_info):
        return False
    
    # 打印成功信息
    print("\n" + "=" * 60)
    print("      🎉 GitHub上傳完成！")
    print("=" * 60)
    print()
    print("📦 倉庫信息：")
    print(f"  名稱: {repo_info['name']}")
    print(f"  URL: {repo_info['html_url']}")
    print(f"  描述: {repo_info['description']}")
    print(f"  私有: {'是' if repo_info['private'] else '否'}")
    print()
    print("🚀 下一步操作：")
    print("  1. 訪問倉庫頁面查看代碼")
    print("  2. 設置Streamlit Cloud部署（可選）")
    print("  3. 配置CI/CD（可選）")
    print("  4. 邀請協作者（可選）")
    print()
    print("🔧 本地開發：")
    print("  git clone", repo_info['clone_url'])
    print("  cd", repo_info['name'])
    print("  chmod +x setup.sh && ./setup.sh")
    print("  streamlit run app.py")
    print()
    print("🌐 Streamlit Cloud部署：")
    print("  1. 訪問 https://streamlit.io/cloud")
    print("  2. 連接GitHub倉庫")
    print("  3. 選擇主分支")
    print("  4. 設置主文件為 app.py")
    print("  5. 點擊部署")
    print()
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n上傳被用戶中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 上傳過程中發生錯誤: {e}")
        sys.exit(1)