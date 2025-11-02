#!/usr/bin/env python3
"""
Legacy Connector - Bridges new DB utility with both MCP and mysql.connector

This module provides backward compatibility while migrating to MCP-based database operations.
It tries to use MCP first, falls back to mysql.connector if needed.
"""

import mysql.connector
from mysql.connector import Error
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


def get_connection(config: Dict[str, str]):
    """
    Get a database connection using mysql.connector (legacy).
    
    Args:
        config: Dictionary with host, user, password, database
        
    Returns:
        MySQL connection object
    """
    return mysql.connector.connect(
        host=config['host'],
        user=config['user'],
        password=config['password'],
        database=config['database']
    )


def get_tables(config: Dict[str, str]) -> List[str]:
    """
    Get list of all tables in the database.
    
    Args:
        config: Database configuration
        
    Returns:
        List of table names
    """
    conn = get_connection(config)
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return tables


def describe_table(config: Dict[str, str], table_name: str) -> List[Dict[str, Any]]:
    """
    Describe table structure.
    
    Args:
        config: Database configuration
        table_name: Name of the table
        
    Returns:
        List of column definitions
    """
    conn = get_connection(config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"DESCRIBE {table_name}")
    columns = cursor.fetchall()
    cursor.close()
    conn.close()
    return columns


def select_data(
    config: Dict[str, str],
    table: str,
    columns: Optional[List[str]] = None,
    where: Optional[str] = None,
    order_by: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Select data from a table.
    
    Args:
        config: Database configuration
        table: Table name
        columns: Columns to select
        where: WHERE clause
        order_by: ORDER BY clause
        limit: LIMIT value
        offset: OFFSET value
        
    Returns:
        List of dictionaries containing row data
    """
    # Build query
    cols = ', '.join(columns) if columns else '*'
    query = f"SELECT {cols} FROM {table}"
    
    if where:
        query += f" WHERE {where}"
    
    if order_by:
        query += f" ORDER BY {order_by}"
    
    if limit is not None:
        query += f" LIMIT {limit}"
        
    if offset is not None:
        query += f" OFFSET {offset}"
    
    return execute_query(config, query)


def execute_query(config: Dict[str, str], query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
    """
    Execute a raw SQL query.
    
    Args:
        config: Database configuration
        query: SQL query
        params: Optional parameters for parameterized queries
        
    Returns:
        List of dictionaries containing row data
    """
    conn = get_connection(config)
    cursor = conn.cursor(dictionary=True)
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    # Check if it's a SELECT query
    if query.strip().upper().startswith('SELECT') or query.strip().upper().startswith('SHOW') or query.strip().upper().startswith('DESCRIBE'):
        results = cursor.fetchall()
    else:
        conn.commit()
        results = []
    
    cursor.close()
    conn.close()
    return results


def execute_many(config: Dict[str, str], query: str, data: List[Tuple]) -> int:
    """
    Execute a query with multiple parameter sets.
    
    Args:
        config: Database configuration
        query: SQL query with placeholders
        data: List of tuples with parameter values
        
    Returns:
        Number of affected rows
    """
    conn = get_connection(config)
    cursor = conn.cursor()
    cursor.executemany(query, data)
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()
    return affected


def insert_row(config: Dict[str, str], table: str, data: Dict[str, Any]) -> int:
    """
    Insert a single row.
    
    Args:
        config: Database configuration
        table: Table name
        data: Dictionary of column:value pairs
        
    Returns:
        Last inserted ID
    """
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['%s'] * len(data))
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    
    conn = get_connection(config)
    cursor = conn.cursor()
    cursor.execute(query, tuple(data.values()))
    conn.commit()
    last_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return last_id


def update_rows(
    config: Dict[str, str],
    table: str,
    data: Dict[str, Any],
    where: str,
    params: Optional[Tuple] = None
) -> int:
    """
    Update rows in a table.
    
    Args:
        config: Database configuration
        table: Table name
        data: Dictionary of column:value pairs to update
        where: WHERE clause
        params: Optional parameters for WHERE clause
        
    Returns:
        Number of affected rows
    """
    set_clause = ', '.join([f"{col} = %s" for col in data.keys()])
    query = f"UPDATE {table} SET {set_clause} WHERE {where}"
    
    # Combine data values and where params
    all_params = list(data.values())
    if params:
        all_params.extend(params)
    
    conn = get_connection(config)
    cursor = conn.cursor()
    cursor.execute(query, tuple(all_params))
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()
    return affected


def delete_rows(config: Dict[str, str], table: str, where: str, params: Optional[Tuple] = None) -> int:
    """
    Delete rows from a table.
    
    Args:
        config: Database configuration
        table: Table name
        where: WHERE clause
        params: Optional parameters
        
    Returns:
        Number of affected rows
    """
    query = f"DELETE FROM {table} WHERE {where}"
    
    conn = get_connection(config)
    cursor = conn.cursor()
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()
    return affected


@contextmanager
def transaction_context(config: Dict[str, str]):
    """
    Context manager for transactions.
    
    Args:
        config: Database configuration
        
    Yields:
        MySQL connection object
    """
    conn = get_connection(config)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
