#!/usr/bin/env python3
"""
OpenCode Project ID 重置工具

功能：
1. 备份 opencode.db
2. 删除 global project 记录
3. 触发 opencode 重新生成新的 project.id

用途：绕过基于 project.id 的免费配额限制
"""

import os
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime


def get_db_path():
    """获取 opencode 数据库路径"""
    home = Path.home()
    db_path = home / ".local/share/opencode/opencode.db"
    return db_path


def backup_db(db_path):
    """备份数据库"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.parent / f"opencode.db.backup_{timestamp}"
    shutil.copy2(db_path, backup_path)
    print(f"✅ 数据库已备份到: {backup_path}")
    return backup_path


def reset_project_id(db_path):
    """删除 global project 记录"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询当前 global project
    cursor.execute("SELECT id, time_created FROM project WHERE id='global'")
    result = cursor.fetchone()
    
    if result:
        project_id, time_created = result
        print(f"📋 当前 global project ID: {project_id}")
        print(f"📅 创建时间: {datetime.fromtimestamp(time_created/1000)}")
        
        # 删除记录
        cursor.execute("DELETE FROM project WHERE id='global'")
        conn.commit()
        print(f"🗑️  已删除 global project 记录")
    else:
        print("⚠️  未找到 global project 记录")
    
    conn.close()


def main():
    print("=" * 60)
    print("OpenCode Project ID 重置工具")
    print("=" * 60)
    
    db_path = get_db_path()
    
    if not db_path.exists():
        print(f"❌ 数据库不存在: {db_path}")
        return
    
    print(f"📂 数据库路径: {db_path}")
    
    # 备份
    backup_path = backup_db(db_path)
    
    # 重置
    reset_project_id(db_path)
    
    print("\n" + "=" * 60)
    print("✅ 重置完成！")
    print("=" * 60)
    print("\n下次启动 opencode 时，会自动生成新的 project.id")
    print(f"如需恢复，运行: cp {backup_path} {db_path}")


if __name__ == "__main__":
    main()
