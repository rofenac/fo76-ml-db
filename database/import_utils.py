#!/usr/bin/env python3
"""
Optimized Import Utilities for Database Operations

This module provides high-level helpers for import scripts, using the
centralized database utility (db_utils.py) for optimal performance.

Features:
- Batch operations with automatic transaction management
- Progress tracking with visual feedback
- Lookup table caching for fast foreign key resolution
- Connection pooling and query optimization
- Error handling and rollback support
"""

import sys
from typing import Dict, List, Any, Optional, Callable
import logging

# Optional tqdm for progress bars
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    # Fallback if tqdm not available
    def tqdm(iterable, **kwargs):
        return iterable

try:
    from db_utils import get_db
except ImportError:
    from database.db_utils import get_db

logger = logging.getLogger(__name__)


class ImportHelper:
    """
    High-level helper for database import operations.
    
    Provides simplified interface for common import tasks:
    - Bulk inserts with progress bars
    - Foreign key lookups with caching
    - Transaction management
    - Error handling and logging
    """
    
    def __init__(self, show_progress: bool = True):
        """
        Initialize import helper.
        
        Args:
            show_progress: Whether to show progress bars
        """
        self.db = get_db()
        self.show_progress = show_progress
        
        # Statistics
        self.stats = {
            'inserted': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
    
    def bulk_insert(
        self,
        table: str,
        columns: List[str],
        data: List[tuple],
        batch_size: int = 1000,
        description: str = None
    ) -> int:
        """
        Insert multiple rows efficiently with batching.
        
        Args:
            table: Table name
            columns: List of column names
            data: List of tuples containing row data
            batch_size: Number of rows per batch
            description: Description for progress bar
            
        Returns:
            Number of rows inserted
        """
        if not data:
            return 0
        
        desc = description or f"Inserting into {table}"
        total_inserted = 0
        
        # Process in batches
        iterator = range(0, len(data), batch_size)
        if self.show_progress:
            iterator = tqdm(iterator, desc=desc, unit='batch')
        
        for i in iterator:
            batch = data[i:i + batch_size]
            try:
                count = self.db.insert_many(table, columns, batch)
                total_inserted += count
                self.stats['inserted'] += count
            except Exception as e:
                logger.error(f"Error inserting batch into {table}: {e}")
                self.stats['errors'] += len(batch)
                raise
        
        return total_inserted
    
    def bulk_upsert(
        self,
        table: str,
        columns: List[str],
        data: List[tuple],
        unique_columns: List[str],
        batch_size: int = 1000,
        description: str = None
    ) -> Dict[str, int]:
        """
        Insert or update multiple rows (upsert operation).
        
        Args:
            table: Table name
            columns: List of column names
            data: List of tuples containing row data
            unique_columns: Columns that define uniqueness
            batch_size: Number of rows per batch
            description: Description for progress bar
            
        Returns:
            Dictionary with counts of inserted and updated rows
        """
        if not data:
            return {'inserted': 0, 'updated': 0}
        
        desc = description or f"Upserting into {table}"
        result = {'inserted': 0, 'updated': 0}
        
        # Build ON DUPLICATE KEY UPDATE clause
        update_clause = ', '.join([f"{col} = VALUES({col})" for col in columns if col not in unique_columns])
        
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join(columns)
        
        query = f"""
            INSERT INTO {table} ({columns_str}) 
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {update_clause}
        """
        
        # Process in batches
        iterator = range(0, len(data), batch_size)
        if self.show_progress:
            iterator = tqdm(iterator, desc=desc, unit='batch')
        
        for i in iterator:
            batch = data[i:i + batch_size]
            try:
                count = self.db.execute_many(query, batch)
                # MySQL doesn't distinguish insert vs update in affected rows for ON DUPLICATE KEY
                result['inserted'] += count
            except Exception as e:
                logger.error(f"Error upserting batch into {table}: {e}")
                self.stats['errors'] += len(batch)
                raise
        
        return result
    
    def get_lookup_id(
        self,
        table: str,
        name_column: str,
        name_value: str,
        auto_create: bool = True
    ) -> Optional[int]:
        """
        Get ID for a lookup table entry, optionally creating it if not found.
        
        Uses caching for performance.
        
        Args:
            table: Lookup table name
            name_column: Column containing the name/value
            name_value: Value to look up
            auto_create: Whether to create entry if not found
            
        Returns:
            ID of the entry, or None if not found and auto_create is False
        """
        # Get cached reverse lookup
        cache = self.db.get_reverse_lookup(table, name_column, 'id')
        
        if name_value in cache:
            return cache[name_value]
        
        if auto_create:
            return self.db.get_or_create_lookup(table, name_column, name_value)
        
        return None
    
    def process_csv_with_transform(
        self,
        csv_data: List[Dict[str, Any]],
        transform_func: Callable[[Dict[str, Any]], Optional[tuple]],
        table: str,
        columns: List[str],
        description: str = None
    ) -> int:
        """
        Process CSV data, transform each row, and insert into database.
        
        Args:
            csv_data: List of dictionaries from CSV
            transform_func: Function to transform each row (returns tuple or None to skip)
            table: Target table name
            columns: Column names for insert
            description: Description for progress bar
            
        Returns:
            Number of rows inserted
        """
        transformed_data = []
        
        iterator = csv_data
        if self.show_progress:
            iterator = tqdm(csv_data, desc=description or "Processing", unit='row')
        
        for row in iterator:
            try:
                transformed = transform_func(row)
                if transformed is not None:
                    transformed_data.append(transformed)
                else:
                    self.stats['skipped'] += 1
            except Exception as e:
                logger.error(f"Error transforming row: {e}")
                self.stats['errors'] += 1
        
        return self.bulk_insert(table, columns, transformed_data)
    
    def test_connection(self) -> bool:
        """Test database connection."""
        return self.db.test_connection()
    
    def clear_cache(self):
        """Clear all cached lookups."""
        self.db.clear_cache()
    
    def print_stats(self):
        """Print import statistics."""
        print("\n" + "=" * 60)
        print("IMPORT STATISTICS")
        print("=" * 60)
        print(f"✓ Inserted:  {self.stats['inserted']:,}")
        print(f"⟳ Updated:   {self.stats['updated']:,}")
        print(f"⊗ Skipped:   {self.stats['skipped']:,}")
        print(f"✗ Errors:    {self.stats['errors']:,}")
        print("=" * 60)


class BulkImporter:
    """
    Context manager for bulk import operations with transaction support.
    
    Usage:
        with BulkImporter() as importer:
            importer.insert('weapons', ['name', 'damage'], data)
            importer.insert('perks', ['name', 'special'], perk_data)
            # Automatically commits on success, rolls back on error
    """
    
    def __init__(self):
        self.db = get_db()
        self.helper = ImportHelper()
        self.transaction = None
    
    def __enter__(self):
        """Start transaction."""
        self.transaction = self.db.transaction()
        self.transaction.__enter__()
        return self.helper
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Commit or rollback transaction."""
        if exc_type is None:
            # Success - commit
            print("\n✓ All operations completed successfully")
        else:
            # Error - rollback
            print(f"\n✗ Error occurred: {exc_val}")
            print("  Rolling back all changes...")
        
        self.transaction.__exit__(exc_type, exc_val, exc_tb)
        return False


# Convenience functions for common operations

def get_race_id(race_name: str) -> Optional[int]:
    """Get race ID by name."""
    return get_db().get_races().get(race_name)


def get_special_id(special_code: str) -> Optional[int]:
    """Get SPECIAL attribute ID by code."""
    return get_db().get_special_attributes().get(special_code)


def get_damage_type_id(damage_type: str) -> Optional[int]:
    """Get damage type ID by name."""
    return get_db().get_damage_types().get(damage_type)


def get_weapon_type_id(weapon_type: str) -> Optional[int]:
    """Get weapon type ID by name."""
    return get_db().get_weapon_types().get(weapon_type)


def get_weapon_class_id(weapon_class: str) -> Optional[int]:
    """Get weapon class ID by name."""
    return get_db().get_weapon_classes().get(weapon_class)


def get_armor_type_id(armor_type: str) -> Optional[int]:
    """Get armor type ID by name."""
    return get_db().get_armor_types().get(armor_type)


def get_armor_slot_id(slot_name: str) -> Optional[int]:
    """Get armor slot ID by name."""
    return get_db().get_armor_slots().get(slot_name)


if __name__ == "__main__":
    # Test the import utilities
    print("Testing Import Utilities...")
    print("-" * 60)
    
    helper = ImportHelper()
    
    if helper.test_connection():
        print("✓ Database connection successful!")
        
        # Test lookup caching
        print("\nTesting lookup caching...")
        races = get_db().get_races()
        print(f"✓ Loaded {len(races)} races")
        
        specials = get_db().get_special_attributes()
        print(f"✓ Loaded {len(specials)} SPECIAL attributes")
        
        print("\n✓ Import utilities are ready!")
    else:
        print("✗ Database connection failed!")
        sys.exit(1)
