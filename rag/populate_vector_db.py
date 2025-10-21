#!/usr/bin/env python3
"""
Populate ChromaDB vector database with Fallout 76 game data.

🚗 CADILLAC EDITION - Using OpenAI's text-embedding-3-small 🚗

This script:
1. Loads all data from MySQL database (weapons, armor, perks, mutations, consumables)
2. Generates high-quality embeddings using OpenAI's text-embedding-3-small
3. Stores embeddings in ChromaDB for semantic search

Cost: ~$0.001 to populate entire database (less than a penny!)
Quality: Premium - 1536 dimensions, trained on massive datasets
"""

import os
import sys
import mysql.connector
from openai import OpenAI
import chromadb
from chromadb.config import Settings
from tqdm import tqdm
from typing import List, Dict, Any
import time


class VectorDBPopulator:
    """Populates ChromaDB with embeddings from MySQL data using OpenAI"""

    def __init__(self, db_config: Dict[str, str], chroma_path: str = "./chroma_db"):
        """
        Initialize the populator.

        Args:
            db_config: MySQL connection config (host, user, password, database)
            chroma_path: Path to store ChromaDB data (persistent storage)
        """
        self.db_config = db_config
        self.chroma_path = chroma_path

        print("🚀 Initializing Vector DB Populator (Cadillac Edition)...")

        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable not set!\n"
                "Get your API key from: https://platform.openai.com/api-keys\n"
                "Then set it: export OPENAI_API_KEY='your-key-here'"
            )

        print("🔑 Connecting to OpenAI API...")
        self.openai_client = OpenAI(api_key=api_key)
        self.embedding_model = "text-embedding-3-small"  # 1536 dimensions, $0.02/1M tokens
        print(f"   ✓ Using {self.embedding_model} (1536-dimensional embeddings)")

        # Initialize ChromaDB client with persistent storage
        print(f"💾 Initializing ChromaDB at {chroma_path}...")
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)

        # Create or get collection
        try:
            # Try to delete existing collection to start fresh
            self.chroma_client.delete_collection(name="fallout76")
            print("   ⚠ Deleted existing collection")
        except:
            pass

        self.collection = self.chroma_client.create_collection(
            name="fallout76",
            metadata={"description": "Fallout 76 game data for semantic search (OpenAI embeddings)"}
        )
        print("   ✓ Collection created!")

        # Rate limiting
        self.batch_size = 100  # OpenAI allows up to 2048 items per batch
        self.delay_between_batches = 0.5  # Small delay to be polite

    def connect_db(self):
        """Connect to MySQL database"""
        return mysql.connector.connect(**self.db_config)

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using OpenAI API.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            print(f"\n⚠️  OpenAI API error: {e}")
            raise

    def create_weapon_text(self, weapon: Dict[str, Any]) -> str:
        """
        Create text representation of weapon for embedding.

        Includes: name, class, type, damage, and associated perks
        """
        text_parts = []

        # Basic info
        text_parts.append(f"Weapon: {weapon['weapon_name']}")
        if weapon.get('weapon_class'):
            text_parts.append(f"Class: {weapon['weapon_class']}")
        if weapon.get('weapon_type'):
            text_parts.append(f"Type: {weapon['weapon_type']}")
        if weapon.get('damage'):
            text_parts.append(f"Damage: {weapon['damage']}")

        # Associated perks (important for semantic search)
        if weapon.get('regular_perks'):
            perks = weapon['regular_perks'].replace(';', ',')
            text_parts.append(f"Affected by perks: {perks}")

        if weapon.get('legendary_perks'):
            leg_perks = weapon['legendary_perks'].replace(';', ',')
            text_parts.append(f"Legendary perks: {leg_perks}")

        return ". ".join(text_parts)

    def create_armor_text(self, armor: Dict[str, Any]) -> str:
        """Create text representation of armor for embedding"""
        text_parts = []

        text_parts.append(f"Armor: {armor['name']}")
        if armor.get('armor_type'):
            text_parts.append(f"Type: {armor['armor_type']}")
        if armor.get('class'):
            text_parts.append(f"Class: {armor['class']}")
        if armor.get('slot'):
            text_parts.append(f"Slot: {armor['slot']}")
        if armor.get('set_name'):
            text_parts.append(f"Set: {armor['set_name']}")

        # Resistance values
        resistances = []
        if armor.get('damage_resistance'):
            resistances.append(f"DR: {armor['damage_resistance']}")
        if armor.get('energy_resistance'):
            resistances.append(f"ER: {armor['energy_resistance']}")
        if armor.get('radiation_resistance'):
            resistances.append(f"RR: {armor['radiation_resistance']}")

        if resistances:
            text_parts.append(f"Resistances: {', '.join(resistances)}")

        return ". ".join(text_parts)

    def create_perk_text(self, perk: Dict[str, Any]) -> str:
        """Create text representation of regular perk for embedding"""
        text_parts = []

        text_parts.append(f"Perk: {perk['perk_name']}")
        if perk.get('special'):
            text_parts.append(f"SPECIAL: {perk['special']}")
        if perk.get('rank_description'):
            text_parts.append(f"Effect: {perk['rank_description']}")

        return ". ".join(text_parts)

    def create_legendary_perk_text(self, perk: Dict[str, Any]) -> str:
        """Create text representation of legendary perk for embedding"""
        text_parts = []

        text_parts.append(f"Legendary Perk: {perk['perk_name']}")
        if perk.get('base_description'):
            text_parts.append(f"Description: {perk['base_description']}")
        if perk.get('rank_description'):
            text_parts.append(f"Effect: {perk['rank_description']}")

        return ". ".join(text_parts)

    def create_mutation_text(self, mutation: Dict[str, Any]) -> str:
        """Create text representation of mutation for embedding"""
        text_parts = []

        text_parts.append(f"Mutation: {mutation['mutation_name']}")
        if mutation.get('positive_effects'):
            text_parts.append(f"Positive: {mutation['positive_effects']}")
        if mutation.get('negative_effects'):
            text_parts.append(f"Negative: {mutation['negative_effects']}")

        return ". ".join(text_parts)

    def create_consumable_text(self, consumable: Dict[str, Any]) -> str:
        """Create text representation of consumable for embedding"""
        text_parts = []

        text_parts.append(f"Consumable: {consumable['consumable_name']}")
        if consumable.get('category'):
            text_parts.append(f"Category: {consumable['category']}")
        if consumable.get('effects'):
            text_parts.append(f"Effects: {consumable['effects']}")
        if consumable.get('special_modifiers'):
            text_parts.append(f"SPECIAL: {consumable['special_modifiers']}")

        return ". ".join(text_parts)

    def populate_batch(self, items: List[Dict], item_type: str, text_creator_func, id_prefix: str):
        """
        Generic batch populator for any item type.

        Args:
            items: List of items from database
            item_type: Type name for display (e.g., "weapons")
            text_creator_func: Function to create text from item
            id_prefix: Prefix for ChromaDB IDs (e.g., "weapon_")
        """
        print(f"\n{self._get_emoji(item_type)} Processing {item_type}...")

        total_batches = (len(items) + self.batch_size - 1) // self.batch_size

        for batch_num in range(total_batches):
            start_idx = batch_num * self.batch_size
            end_idx = min((batch_num + 1) * self.batch_size, len(items))
            batch = items[start_idx:end_idx]

            # Prepare batch data
            ids = []
            texts = []
            metadatas = []

            for item in batch:
                text = text_creator_func(item)
                texts.append(text)

                # Build ID and metadata based on item type
                if item_type in ["perks", "legendary perks"]:
                    item_id = f"{id_prefix}{item['perk_id'] if 'perk_id' in item else item['legendary_perk_id']}_rank_{item['rank']}"
                    ids.append(item_id)

                    metadata = {
                        'type': id_prefix.rstrip('_'),
                        'id': str(item.get('perk_id', item.get('legendary_perk_id'))),
                        'rank': str(item['rank'])
                    }
                    if item.get('perk_name'):
                        metadata['name'] = item['perk_name']

                    metadatas.append(metadata)
                else:
                    # Handle different ID column names
                    if item_type == "mutations":
                        db_id = item['mutation_id']
                    elif item_type == "consumables":
                        db_id = item['consumable_id']
                    else:
                        db_id = item['id']

                    item_id = f"{id_prefix}{db_id}"
                    ids.append(item_id)

                    # Create metadata dict based on item type
                    metadata = {
                        'type': id_prefix.rstrip('_'),
                        'id': str(db_id)
                    }

                    # Add name if available (handle different column naming)
                    if item_type == "weapons":
                        name = item.get('weapon_name')
                    elif item_type == "armor":
                        name = item.get('name')
                    elif item_type == "mutations":
                        name = item.get('mutation_name')
                    elif item_type == "consumables":
                        name = item.get('consumable_name')
                    else:
                        name = item.get('name')

                    if name:
                        metadata['name'] = name

                    # Add type-specific metadata (filter out None/empty values)
                    if item_type == "weapons":
                        if item.get('weapon_class'):
                            metadata['class'] = item['weapon_class']
                        if item.get('damage'):
                            metadata['damage'] = str(item['damage'])
                    elif item_type == "armor":
                        if item.get('armor_type'):
                            metadata['armor_type'] = item['armor_type']
                        if item.get('class'):  # Note: armor uses 'class' not 'armor_class'
                            metadata['armor_class'] = item['class']
                        if item.get('set_name'):
                            metadata['set_name'] = item['set_name']
                    elif item_type == "consumables":
                        if item.get('category'):
                            metadata['category'] = item['category']

                    metadatas.append(metadata)

            # Generate embeddings for batch
            embeddings = self.generate_embeddings(texts)

            # Add to ChromaDB
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )

            # Progress indicator
            if total_batches > 1:
                print(f"   Batch {batch_num + 1}/{total_batches} ({len(batch)} items)", end='\r')

            # Small delay between batches
            if batch_num < total_batches - 1:
                time.sleep(self.delay_between_batches)

        print(f"   ✓ Added {len(items)} {item_type}                    ")

    def _get_emoji(self, item_type: str) -> str:
        """Get emoji for item type"""
        emojis = {
            "weapons": "🔫",
            "armor": "🛡️",
            "perks": "⭐",
            "legendary perks": "💎",
            "mutations": "🧬",
            "consumables": "🍖"
        }
        return emojis.get(item_type, "📦")

    def populate_weapons(self):
        """Load weapons from MySQL and add to ChromaDB"""
        db = self.connect_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM v_weapons_with_perks")
        weapons = cursor.fetchall()
        cursor.close()
        db.close()

        self.populate_batch(weapons, "weapons", self.create_weapon_text, "weapon_")

    def populate_armor(self):
        """Load armor from MySQL and add to ChromaDB"""
        db = self.connect_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM v_armor_complete")
        armor_pieces = cursor.fetchall()
        cursor.close()
        db.close()

        self.populate_batch(armor_pieces, "armor", self.create_armor_text, "armor_")

    def populate_perks(self):
        """Load regular perks from MySQL and add to ChromaDB"""
        db = self.connect_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM v_perks_all_ranks")
        perks = cursor.fetchall()
        cursor.close()
        db.close()

        self.populate_batch(perks, "perks", self.create_perk_text, "perk_")

    def populate_legendary_perks(self):
        """Load legendary perks from MySQL and add to ChromaDB"""
        db = self.connect_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM v_legendary_perks_all_ranks")
        perks = cursor.fetchall()
        cursor.close()
        db.close()

        self.populate_batch(perks, "legendary perks", self.create_legendary_perk_text, "legendary_perk_")

    def populate_mutations(self):
        """Load mutations from MySQL and add to ChromaDB"""
        db = self.connect_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM v_mutations_complete")
        mutations = cursor.fetchall()
        cursor.close()
        db.close()

        self.populate_batch(mutations, "mutations", self.create_mutation_text, "mutation_")

    def populate_consumables(self):
        """Load consumables from MySQL and add to ChromaDB"""
        db = self.connect_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM v_consumables_complete")
        consumables = cursor.fetchall()
        cursor.close()
        db.close()

        self.populate_batch(consumables, "consumables", self.create_consumable_text, "consumable_")

    def populate_all(self):
        """Populate all data types"""
        print("\n" + "="*60)
        print("🚀 POPULATING VECTOR DATABASE (CADILLAC EDITION)")
        print("="*60)

        self.populate_weapons()
        self.populate_armor()
        self.populate_perks()
        self.populate_legendary_perks()
        self.populate_mutations()
        self.populate_consumables()

        # Get stats
        stats = self.collection.count()

        print("\n" + "="*60)
        print("✅ VECTOR DATABASE POPULATED!")
        print("="*60)
        print(f"📊 Total embeddings: {stats}")
        print(f"💾 Stored at: {self.chroma_path}")
        print(f"🚗 Quality: Premium (OpenAI text-embedding-3-small)")
        print(f"💰 Estimated cost: ~$0.001 (less than a penny!)")
        print("\nReady for semantic search! 🎉")


def main():
    """Main entry point"""

    # Database configuration
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', 'secret'),
        'database': os.getenv('DB_NAME', 'f76')
    }

    # Path for ChromaDB storage
    chroma_path = os.path.join(os.path.dirname(__file__), "chroma_db")

    try:
        populator = VectorDBPopulator(db_config, chroma_path)
        populator.populate_all()

    except mysql.connector.Error as e:
        print(f"\n❌ Database error: {e}")
        print("Make sure MySQL is running and credentials are correct.")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
