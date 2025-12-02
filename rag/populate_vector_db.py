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
from openai import OpenAI
import chromadb
from chromadb.config import Settings
from tqdm import tqdm
from typing import List, Dict, Any
import time
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import new database utility
from database.db_utils import get_db

# Load environment variables
load_dotenv()


class VectorDBPopulator:
    """Populates ChromaDB with embeddings from MySQL data using OpenAI"""

    def __init__(self, chroma_path: str = "./chroma_db"):
        """
        Initialize the populator.

        Args:
            chroma_path: Path to store ChromaDB data (persistent storage)
        """
        self.chroma_path = chroma_path

        print("🚀 Initializing Vector DB Populator (Cadillac Edition)...")

        # Initialize database utility
        self.db = get_db()

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

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results"""
        return self.db.execute_query(query)

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

        Includes: name, class, type, damage, perks, mechanics, and build context
        """
        text_parts = []

        # Basic info
        text_parts.append(f"Weapon: {weapon['weapon_name']}")
        if weapon.get('weapon_class'):
            weapon_class = weapon['weapon_class']
            text_parts.append(f"Class: {weapon_class}")

            # Add build archetype context for better semantic matching
            if weapon_class:
                class_lower = weapon_class.lower()
                text_parts.append(f"Suitable for {class_lower} builds")

        if weapon.get('weapon_type'):
            text_parts.append(f"Type: {weapon['weapon_type']}")

        if weapon.get('damage'):
            damage_str = str(weapon['damage'])
            text_parts.append(f"Damage: {damage_str}")

            # Add damage tier context (helps with "best" queries)
            # Extract first damage value for categorization
            try:
                # Handle damage ranges (e.g., "80.00-75.00")
                damage_parts = damage_str.replace('-', '/').split('/')
                first_damage = float(damage_parts[0].strip())

                if first_damage >= 100:
                    text_parts.append("Very high damage output weapon excellent for DPS builds")
                elif first_damage >= 70:
                    text_parts.append("High damage output weapon good for damage builds")
                elif first_damage >= 40:
                    text_parts.append("Moderate damage weapon suitable for balanced builds")
                elif first_damage >= 15:
                    text_parts.append("Lower damage weapon niche or specialized use")
            except:
                pass

        # Weapon mechanics (CRITICAL for charge, spin-up, chain lightning, etc.)
        if weapon.get('mechanics'):
            mechanics_text = weapon['mechanics']
            text_parts.append(f"Special mechanics: {mechanics_text}")

        # Associated perks (important for semantic search)
        if weapon.get('regular_perks'):
            perks = weapon['regular_perks'].replace(';', ',')
            text_parts.append(f"Affected by perks: {perks}")

        if weapon.get('legendary_perks'):
            leg_perks = weapon['legendary_perks'].replace(';', ',')
            text_parts.append(f"Legendary perks: {leg_perks}")

        # Add universal build viability terms (helps match "full health", "bloodied", etc.)
        # All weapons work with any build type - it's about optimization, not exclusion
        text_parts.append("Viable for bloodied builds, full-health builds, stealth builds, tank builds, DPS builds")

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

    def create_collectible_text(self, collectible: Dict[str, Any]) -> str:
        """Create text representation of collectible for embedding"""
        text_parts = []

        text_parts.append(f"Collectible: {collectible['collectible_name']}")
        if collectible.get('collectible_type'):
            text_parts.append(f"Type: {collectible['collectible_type']}")
        if collectible.get('series_name'):
            text_parts.append(f"Series: {collectible['series_name']}")
        if collectible.get('duration'):
            text_parts.append(f"Duration: {collectible['duration']}")
        if collectible.get('effects'):
            text_parts.append(f"Effects: {collectible['effects']}")
        if collectible.get('special_modifiers'):
            text_parts.append(f"SPECIAL: {collectible['special_modifiers']}")

        return ". ".join(text_parts)

    def create_legendary_effect_text(self, effect: Dict[str, Any]) -> str:
        """Create text representation of legendary effect for embedding"""
        text_parts = []

        text_parts.append(f"Legendary Effect: {effect['effect_name']}")
        if effect.get('item_type'):
            text_parts.append(f"For: {effect['item_type']}")
        if effect.get('star_level'):
            text_parts.append(f"{effect['star_level']}-star")
        if effect.get('category'):
            text_parts.append(f"Category: {effect['category']}")
        if effect.get('description'):
            text_parts.append(f"Description: {effect['description']}")
        if effect.get('effect_value'):
            text_parts.append(f"Value: {effect['effect_value']}")
        if effect.get('conditions'):
            text_parts.append(f"Conditions: {effect['conditions']}")

        # Add context for bloodied builds if relevant
        effect_name_lower = effect['effect_name'].lower()
        if 'bloodied' in effect_name_lower or 'low health' in effect.get('description', '').lower():
            text_parts.append("Critical for bloodied builds, synergizes with Adrenal Reaction mutation and Nerd Rage perk")
        elif 'unyielding' in effect_name_lower:
            text_parts.append("Essential for bloodied builds, provides massive SPECIAL bonuses at low health")

        return ". ".join(text_parts)

    def create_weapon_mod_text(self, mod: Dict[str, Any]) -> str:
        """Create text representation of weapon mod for embedding"""
        text_parts = []

        # Basic identification
        text_parts.append(f"Weapon Mod: {mod['mod_name']}")
        text_parts.append(f"For weapon: {mod['weapon_name']}")
        text_parts.append(f"Mod slot: {mod['slot_name']}")

        # Stat changes (the important part for build optimization)
        stat_changes = []

        if mod.get('damage_change'):
            unit = "%" if mod.get('damage_is_percent') else " points"
            stat_changes.append(f"damage {mod['damage_change']:+g}{unit}")

        if mod.get('fire_rate_change'):
            stat_changes.append(f"fire rate {mod['fire_rate_change']:+g}")

        if mod.get('range_change'):
            stat_changes.append(f"range {mod['range_change']:+g}")

        if mod.get('accuracy_change'):
            stat_changes.append(f"accuracy {mod['accuracy_change']:+g}")

        if mod.get('ap_cost_change'):
            stat_changes.append(f"AP cost {mod['ap_cost_change']:+g}")

        if mod.get('recoil_change'):
            stat_changes.append(f"recoil {mod['recoil_change']:+g}")

        if mod.get('spread_change'):
            stat_changes.append(f"spread {mod['spread_change']:+g}")

        if mod.get('mag_size_change'):
            stat_changes.append(f"magazine size {mod['mag_size_change']:+g}")

        if mod.get('reload_speed_change'):
            stat_changes.append(f"reload speed {mod['reload_speed_change']:+g}")

        if stat_changes:
            text_parts.append(f"Modifies: {', '.join(stat_changes)}")

        # Special properties
        if mod.get('converts_to_auto'):
            text_parts.append("Converts weapon to automatic fire")

        if mod.get('converts_to_semi'):
            text_parts.append("Converts weapon to semi-automatic fire")

        if mod.get('crit_damage_bonus'):
            text_parts.append(f"Critical damage bonus: +{mod['crit_damage_bonus']}%")

        if mod.get('hip_fire_accuracy_bonus'):
            text_parts.append(f"Hip fire accuracy bonus: +{mod['hip_fire_accuracy_bonus']}%")

        if mod.get('armor_penetration'):
            text_parts.append(f"Armor penetration: +{mod['armor_penetration']}%")

        if mod.get('is_suppressed'):
            text_parts.append("Suppresses weapon (reduces noise and visibility)")

        if mod.get('is_scoped'):
            text_parts.append("Adds scope for improved aiming")

        # Crafting requirements
        if mod.get('required_perk'):
            perk_rank = mod.get('required_perk_rank', 1)
            text_parts.append(f"Requires: {mod['required_perk']} rank {perk_rank}")

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
                    elif item_type == "collectibles":
                        db_id = item['collectible_id']
                    elif item_type == "legendary effects":
                        db_id = item['effect_id']
                    elif item_type == "weapon mods":
                        db_id = item['mod_id']
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
                    elif item_type == "weapon mods":
                        name = item.get('mod_name')
                    elif item_type == "armor":
                        name = item.get('name')
                    elif item_type == "mutations":
                        name = item.get('mutation_name')
                    elif item_type == "consumables":
                        name = item.get('consumable_name')
                    elif item_type == "collectibles":
                        name = item.get('collectible_name')
                    elif item_type == "legendary effects":
                        name = item.get('effect_name')
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
                    elif item_type == "weapon mods":
                        if item.get('weapon_name'):
                            metadata['weapon_name'] = item['weapon_name']
                        if item.get('slot_name'):
                            metadata['slot_name'] = item['slot_name']
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
                    elif item_type == "legendary effects":
                        if item.get('item_type'):
                            metadata['item_type'] = item['item_type']
                        if item.get('star_level'):
                            metadata['star_level'] = str(item['star_level'])
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
            "weapon mods": "🔧",
            "armor": "🛡️",
            "perks": "⭐",
            "legendary perks": "💎",
            "legendary effects": "✨",
            "mutations": "🧬",
            "consumables": "🍖",
            "collectibles": "🎁"
        }
        return emojis.get(item_type, "📦")

    def populate_weapons(self):
        """Load weapons from MySQL and add to ChromaDB"""
        # Get weapons with perks using new DB utility
        weapons = self.execute_query("SELECT * FROM v_weapons_with_perks")
        self.populate_batch(weapons, "weapons", self.create_weapon_text, "weapon_")

    def populate_armor(self):
        """Load armor from MySQL and add to ChromaDB"""
        armor_pieces = self.execute_query("SELECT * FROM v_armor_complete")
        self.populate_batch(armor_pieces, "armor", self.create_armor_text, "armor_")

    def populate_perks(self):
        """Load regular perks from MySQL and add to ChromaDB"""
        perks = self.execute_query("SELECT * FROM v_perks_all_ranks")
        self.populate_batch(perks, "perks", self.create_perk_text, "perk_")

    def populate_legendary_perks(self):
        """Load legendary perks from MySQL and add to ChromaDB"""
        perks = self.execute_query("SELECT * FROM v_legendary_perks_all_ranks")
        self.populate_batch(perks, "legendary perks", self.create_legendary_perk_text, "legendary_perk_")

    def populate_mutations(self):
        """Load mutations from MySQL and add to ChromaDB"""
        mutations = self.execute_query("SELECT * FROM v_mutations_complete")
        self.populate_batch(mutations, "mutations", self.create_mutation_text, "mutation_")

    def populate_consumables(self):
        """Load consumables from MySQL and add to ChromaDB"""
        consumables = self.execute_query("SELECT * FROM v_consumables_complete")
        self.populate_batch(consumables, "consumables", self.create_consumable_text, "consumable_")

    def populate_collectibles(self):
        """Load collectibles from MySQL and add to ChromaDB"""
        collectibles = self.execute_query("SELECT * FROM v_collectibles_complete")
        self.populate_batch(collectibles, "collectibles", self.create_collectible_text, "collectible_")

    def populate_legendary_effects(self):
        """Load legendary effects from MySQL and add to ChromaDB"""
        effects = self.execute_query("SELECT * FROM v_legendary_effects_complete")
        self.populate_batch(effects, "legendary effects", self.create_legendary_effect_text, "legendary_effect_")

    def populate_weapon_mods(self):
        """Load weapon mods from MySQL and add to ChromaDB"""
        weapon_mods = self.execute_query("SELECT * FROM v_weapon_mods_complete")
        self.populate_batch(weapon_mods, "weapon mods", self.create_weapon_mod_text, "weapon_mod_")

    def populate_all(self):
        """Populate all data types"""
        print("\n" + "="*60)
        print("🚀 POPULATING VECTOR DATABASE (CADILLAC EDITION)")
        print("="*60)

        self.populate_weapons()
        self.populate_weapon_mods()
        self.populate_armor()
        self.populate_perks()
        self.populate_legendary_perks()
        self.populate_legendary_effects()
        self.populate_mutations()
        self.populate_consumables()
        self.populate_collectibles()

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

    # Path for ChromaDB storage
    chroma_path = os.path.join(os.path.dirname(__file__), "chroma_db")

    try:
        # Database config is now handled by the centralized db_utils module
        populator = VectorDBPopulator(chroma_path)
        populator.populate_all()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure MySQL is running and environment variables are set (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME).")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
