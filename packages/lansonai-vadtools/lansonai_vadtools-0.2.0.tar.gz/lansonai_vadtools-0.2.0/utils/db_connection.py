"""
数据库连接工具模块
提供PostgreSQL数据库连接和基本操作功能
"""

import os
# Attempt to import psycopg2; if unavailable (e.g., in Modal sandbox), provide a graceful fallback.
try:
    # 尝试导入 psycopg2，如果不可用则提供占位实现
    try:
        import psycopg2
    except Exception:
        # 创建一个最小的占位模块，提供 extensions 子模块和 connection 类型占位
        class _DummyExtensions:
            class connection:
                pass
        class _DummyPsycopg2:
            extensions = _DummyExtensions
        psycopg2 = _DummyPsycopg2()
    import psycopg2.extras
except ImportError:
    psycopg2 = None
    psycopg2_extras = None
    # Define a minimal placeholder for the RealDictCursor to avoid attribute errors.
    class _DummyCursor:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        def execute(self, *args, **kwargs):
            raise RuntimeError("psycopg2 is not installed; database operations are unavailable.")
        def fetchall(self):
            return []
        def fetchone(self):
            return None
        @property
        def description(self):
            return None
        @property
        def rowcount(self):
            return 0

    class _DummyExtras:
        RealDictCursor = _DummyCursor

    psycopg2 = type('psycopg2', (), {'connect': lambda *a, **k: None, 'extras': _DummyExtras})
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
import json
from datetime import datetime
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """数据库连接管理类"""
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        初始化数据库连接
        
        Args:
            connection_string: PostgreSQL连接字符串，如果为None则从环境变量或配置文件读取
        """
        self.connection_string = connection_string or self._get_connection_string()
        self.connection = None
        
    def _get_connection_string(self) -> str:
        """
        获取数据库连接字符串
        优先级：环境变量 > .kysely-codegenrc.json > 抛出异常
        """
        # 1. 尝试从环境变量获取
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            return db_url
            
        # 2. 尝试从项目根目录的 .kysely-codegenrc.json 获取
        try:
            # 获取项目根目录（相对于当前文件的5级父目录）
            project_root = Path(__file__).parent.parent.parent.parent.parent
            config_file = project_root / '.kysely-codegenrc.json'
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    db_url = config.get('url')
                    if db_url:
                        logger.info(f"从配置文件获取数据库连接: {config_file}")
                        return db_url
        except Exception as e:
            logger.warning(f"读取配置文件失败: {e}")
            
        # 3. 尝试从 .env 文件获取
        try:
            project_root = Path(__file__).parent.parent.parent.parent.parent
            env_file = project_root / '.env'
            if env_file.exists():
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('DATABASE_URL='):
                            db_url = line.split('=', 1)[1].strip().strip('"\'')
                            if db_url:
                                logger.info(f"从.env文件获取数据库连接")
                                return db_url
        except Exception as e:
            logger.warning(f"读取.env文件失败: {e}")
            
        raise ValueError("无法获取数据库连接字符串。请设置 DATABASE_URL 环境变量或在项目根目录创建 .kysely-codegenrc.json 配置文件")
    
    from typing import Any
    def connect(self) -> Any:
        """建立数据库连接"""
        try:
            # 解析连接字符串以获取主机名
            import re
            match = re.match(r"postgresql://[^/]+@([^:]+):", self.connection_string)
            host = match.group(1) if match else None

            # 尝试解析主机名为 IPv4 地址
            if host:
                try:
                    import socket
                    ipv4_address = socket.gethostbyname(host)
                    # 替换连接字符串中的主机名为 IPv4 地址
                    conn_str = self.connection_string.replace(host, ipv4_address)
                except socket.gaierror:
                    # 如果无法解析为 IPv4，则使用原始连接字符串
                    conn_str = self.connection_string
            else:
                conn_str = self.connection_string

            conn = psycopg2.connect(
                conn_str,
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            if conn:
                self.connection = conn
                self.connection.autocommit = False
                logger.info("数据库连接成功")
                return self.connection
            else:
                # 如果 psycopg2.connect 返回 None，则显式抛出异常
                raise RuntimeError("psycopg2.connect 返回了 None，无法建立数据库连接。")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            # 重新抛出异常，以便上层调用者可以捕获
            raise RuntimeError(f"数据库连接失败: {e}") from e
    
    def disconnect(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("数据库连接已关闭")
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """
        执行查询语句
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        if not self.connection:
            self.connect()
            
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                if cursor.description:  # SELECT查询
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                else:  # INSERT/UPDATE/DELETE查询
                    return []
        except Exception as e:
            self.connection.rollback()
            logger.error(f"查询执行失败: {e}")
            logger.error(f"SQL: {query}")
            logger.error(f"参数: {params}")
            raise
    
    def execute_update(self, query: str, params: Optional[Tuple] = None) -> int:
        """
        执行更新语句（INSERT/UPDATE/DELETE）
        
        Args:
            query: SQL更新语句
            params: 更新参数
            
        Returns:
            受影响的行数
        """
        if not self.connection:
            self.connect()
            
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                affected_rows = cursor.rowcount
                self.connection.commit()
                logger.info(f"更新成功，影响行数: {affected_rows}")
                return affected_rows
        except Exception as e:
            self.connection.rollback()
            logger.error(f"更新执行失败: {e}")
            logger.error(f"SQL: {query}")
            logger.error(f"参数: {params}")
            raise
    
    def execute_transaction(self, operations: List[Tuple[str, Optional[Tuple]]]) -> bool:
        """
        执行事务操作
        
        Args:
            operations: 操作列表，每个操作为 (sql, params) 元组
            
        Returns:
            是否成功
        """
        if not self.connection:
            self.connect()
            
        try:
            with self.connection.cursor() as cursor:
                for query, params in operations:
                    cursor.execute(query, params)
                self.connection.commit()
                logger.info(f"事务执行成功，包含 {len(operations)} 个操作")
                return True
        except Exception as e:
            self.connection.rollback()
            logger.error(f"事务执行失败: {e}")
            raise
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            if not self.connection:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                logger.info("数据库连接测试成功")
                return result is not None
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()


def get_db_connection() -> DatabaseConnection:
    """获取数据库连接实例（工厂函数）"""
    return DatabaseConnection()


def test_database_connection():
    """测试数据库连接的独立函数"""
    try:
        with get_db_connection() as db:
            success = db.test_connection()
            if success:
                print("✅ 数据库连接测试成功")
                
                # 测试查询现有表
                tables = db.execute_query("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name
                """)
                print(f"📋 发现数据库表: {[t['table_name'] for t in tables]}")
                
                # 测试查询audio_tasks表结构
                columns = db.execute_query("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'audio_tasks' 
                    ORDER BY ordinal_position
                """)
                print(f"🔍 audio_tasks表字段数: {len(columns)}")
                
                return True
            else:
                print("❌ 数据库连接测试失败")
                return False
    except Exception as e:
        print(f"❌ 数据库连接测试异常: {e}")
        return False


if __name__ == "__main__":
    # 直接运行此文件时进行连接测试
    test_database_connection()
