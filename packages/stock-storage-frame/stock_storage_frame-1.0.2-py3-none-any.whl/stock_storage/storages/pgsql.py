"""
PostgreSQL storage implementation.
"""

import asyncio
from typing import Any, Dict, List, Optional
from datetime import date, datetime
import pandas as pd

from .base import BaseStorage
from ..models import BatchStockData, StockData, StorageConfig, StorageType
from sqlalchemy.engine.url import URL


class PostgreSQLStorage(BaseStorage):
    """Storage implementation for PostgreSQL database."""
    
    def __init__(self, config: StorageConfig):
        super().__init__(config)
        self.host = config.config.get("host", "localhost")
        self.port = config.config.get("port", 5432)
        self.database = config.config.get("database", "stock_data")
        self.username = config.config.get("username", "postgres")
        self.password = config.config.get("password", "")
        self.schema = config.config.get("schema", "public")
        
        self.connection = None
        self.engine = None
    
    def get_required_config_fields(self) -> List[str]:
        """Get required configuration fields."""
        return ["host", "database", "username"]
    
    async def connect(self) -> None:
        """Connect to PostgreSQL database."""
        try:
            import sqlalchemy as sa
            from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
            from sqlalchemy.orm import sessionmaker
        except ImportError:
            raise ImportError(
                "SQLAlchemy and async PostgreSQL driver are required. "
                "Install with: pip install sqlalchemy asyncpg"
            )
        
        # Create connection URL
        connection_url = URL.create(
            drivername="postgresql+asyncpg",
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
        )
        
        # Create async engine
        self.engine = create_async_engine(
            connection_url,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        
        # Create session factory
        self.session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    
    async def disconnect(self) -> None:
        """Disconnect from PostgreSQL database."""
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.session_factory = None
    
    async def save(self, data: pd.DataFrame, table_name: str, **kwargs) -> int:
        """
        Save stock data to PostgreSQL database.
        
        Args:
            data: pandas DataFrame containing stock data
            table_name: Name of the table to save to
            **kwargs: Additional parameters
            
        Returns:
            Number of records saved
        """
        if not self.engine:
            await self.connect()
        
        if data.empty:
            return 0
        
        # Simply use pandas to_sql with SQLAlchemy connection
        # Let pandas handle table creation and schema
        if_exists = kwargs.get('if_exists', 'append')
        
        # Use run_sync to execute pandas to_sql in sync context
        async with self.session_factory() as session:
            try:
                # Define a sync function for pandas to_sql
                def sync_save():
                    data.to_sql(
                        table_name,
                        self.engine.sync_engine,
                        if_exists=if_exists,
                        index=False,
                        method="multi",
                        schema=self.schema
                    )
                
                # Run in sync context
                await session.run_sync(lambda _: sync_save())
                await session.commit()
                return len(data)
                
            except Exception as e:
                await session.rollback()
                raise
    
    async def load(
        self,
        table_name: str,
        symbols: Optional[List[str]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load stock data from PostgreSQL database.
        
        Args:
            table_name: Name of the table to load from
            symbols: List of stock symbols to filter by
            start_date: Start date for data range
            end_date: End date for data range
            **kwargs: Additional parameters
            
        Returns:
            Loaded pandas DataFrame
        """
        if not self.engine:
            await self.connect()
        
        async with self.session_factory() as session:
            try:
                import sqlalchemy as sa
                
                # Create table metadata with schema
                metadata = sa.MetaData(schema=self.schema)
                table = sa.Table(
                    table_name,
                    metadata,
                    autoload_with=self.engine.sync_engine
                )
                
                # Build query
                query = sa.select(table)
                
                conditions = []
                if symbols:
                    conditions.append(table.c.symbol.in_(symbols))
                
                if start_date:
                    conditions.append(table.c.date >= start_date.isoformat())
                
                if end_date:
                    conditions.append(table.c.date <= end_date.isoformat())
                
                if conditions:
                    query = query.where(sa.and_(*conditions))
                
                # Execute query and convert to DataFrame
                result = await session.execute(query)
                rows = result.fetchall()
                
                if not rows:
                    return pd.DataFrame()
                
                # Convert to DataFrame
                df = pd.DataFrame([dict(row._mapping) for row in rows])
                
                # Convert date column from string to date object if present
                if 'date' in df.columns and df['date'].dtype == 'object':
                    try:
                        df['date'] = pd.to_datetime(df['date']).dt.date
                    except:
                        pass
                
                return df
                
            except Exception as e:
                raise
    
    async def delete(
        self,
        table_name: str,
        symbols: Optional[List[str]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs
    ) -> int:
        """
        Delete stock data from PostgreSQL database.
        
        Args:
            table_name: Name of the table to delete from
            symbols: List of stock symbols to filter by
            start_date: Start date for data range
            end_date: End date for data range
            **kwargs: Additional parameters
            
        Returns:
            Number of records deleted
        """
        if not self.engine:
            await self.connect()
        
        async with self.session_factory() as session:
            try:
                import sqlalchemy as sa
                
                # Create table metadata with schema
                metadata = sa.MetaData(schema=self.schema)
                table = sa.Table(
                    table_name,
                    metadata,
                    autoload_with=self.engine.sync_engine
                )
                
                # Build DELETE statement
                delete_stmt = sa.delete(table)
                
                conditions = []
                if symbols:
                    conditions.append(table.c.symbol.in_(symbols))
                
                if start_date:
                    conditions.append(table.c.date >= start_date.isoformat())
                
                if end_date:
                    conditions.append(table.c.date <= end_date.isoformat())
                
                if conditions:
                    delete_stmt = delete_stmt.where(sa.and_(*conditions))
                
                # Execute DELETE
                result = await session.execute(delete_stmt)
                deleted_count = result.rowcount
                
                await session.commit()
                return deleted_count
                
            except Exception as e:
                await session.rollback()
                raise
    
    async def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get information about a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary containing table information
        """
        if not self.engine:
            await self.connect()
        
        async with self.session_factory() as session:
            try:
                import sqlalchemy as sa
                
                # Get table information using SQL
                queries = [
                    f'SELECT COUNT(*) as row_count FROM "{self.schema}"."{table_name}"'
                ]
                
                results = {}
                for query in queries:
                    result = await session.execute(sa.text(query))
                    row = result.fetchone()
                    if row:
                        results.update(dict(row._mapping))
                
                # Get column information
                column_query = """
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default
                    FROM information_schema.columns
                    WHERE table_schema = :schema
                    AND table_name = :table_name
                    ORDER BY ordinal_position
                """
                
                result = await session.execute(
                    sa.text(column_query),
                    {"schema": self.schema, "table_name": table_name}
                )
                columns = [dict(row._mapping) for row in result.fetchall()]
                
                return {
                    "table_name": table_name,
                    "schema": self.schema,
                    "database": self.database,
                    "columns": columns,
                    "row_count": results.get("row_count", 0)
                }
                
            except Exception as e:
                raise
    
    async def drop_table(self, table_name: str) -> None:
        """
        Drop a table.
        
        Args:
            table_name: Name of the table to drop
        """
        if not self.engine:
            await self.connect()
        
        async with self.session_factory() as session:
            try:
                import sqlalchemy as sa
                
                drop_stmt = sa.text(f'DROP TABLE IF EXISTS "{self.schema}"."{table_name}"')
                await session.execute(drop_stmt)
                await session.commit()
                
            except Exception as e:
                await session.rollback()
                raise
    
    async def list_tables(self) -> List[str]:
        """
        List all tables in the database schema.
        
        Returns:
            List of table names
        """
        if not self.engine:
            await self.connect()
        
        async with self.session_factory() as session:
            try:
                import sqlalchemy as sa
                
                query = sa.text("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = :schema
                    AND table_type = 'BASE TABLE'
                """)
                
                result = await session.execute(query, {"schema": self.schema})
                tables = [row[0] for row in result.fetchall()]
                
                return tables
                
            except Exception as e:
                raise
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a custom SQL query.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            List of result rows as dictionaries
        """
        if not self.engine:
            await self.connect()
        
        async with self.session_factory() as session:
            try:
                import sqlalchemy as sa
                
                result = await session.execute(
                    sa.text(query),
                    params or {}
                )
                rows = result.fetchall()
                
                return [dict(row._mapping) for row in rows]
                
            except Exception as e:
                raise
    
    async def create_index(self, table_name: str, column: str, index_name: Optional[str] = None) -> None:
        """
        Create an index on a table column.
        
        Args:
            table_name: Name of the table
            column: Column to index
            index_name: Optional index name
        """
        if not self.engine:
            await self.connect()
        
        if index_name is None:
            index_name = f"idx_{table_name}_{column}"
        
        async with self.session_factory() as session:
            try:
                import sqlalchemy as sa
                
                create_index_stmt = sa.text(
                    f'CREATE INDEX IF NOT EXISTS "{index_name}" ON "{self.schema}"."{table_name}" ("{column}")'
                )
                await session.execute(create_index_stmt)
                await session.commit()
                
            except Exception as e:
                await session.rollback()
                raise
    
    async def create_schema(self, schema_name: Optional[str] = None) -> None:
        """
        Create a new schema in the database.
        
        Args:
            schema_name: Name of the schema to create (defaults to current schema)
        """
        if not self.engine:
            await self.connect()
        
        schema_to_create = schema_name or self.schema
        
        async with self.session_factory() as session:
            try:
                import sqlalchemy as sa
                
                create_schema_stmt = sa.text(f'CREATE SCHEMA IF NOT EXISTS "{schema_to_create}"')
                await session.execute(create_schema_stmt)
                await session.commit()
                
            except Exception as e:
                await session.rollback()
                raise
