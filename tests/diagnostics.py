#!/usr/bin/env python3
"""
=============================================================================
FALLOUT 76 BUILD DATABASE - FULL SYSTEM DIAGNOSTIC
Engineering Officer: Geordi La Forge
=============================================================================
"""

import sys
import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime

sys.path.insert(0, 'rag')
from query_engine import FalloutRAG

# Load environment
load_dotenv()

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    """Print section header"""
    print(f"\n{CYAN}{BOLD}{'='*70}")
    print(f"{text}")
    print(f"{'='*70}{RESET}\n")

def print_status(test_name, passed, details=""):
    """Print test status"""
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"{status} | {test_name}")
    if details:
        print(f"       {details}")

def get_db_connection():
    """Get database connection"""
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'secret'),
        database=os.getenv('DB_NAME', 'f76')
    )


class SystemDiagnostic:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.warnings = []

    def run_test(self, test_name, test_func):
        """Run a single test"""
        self.total_tests += 1
        try:
            passed, details = test_func()
            if passed:
                self.passed_tests += 1
            else:
                self.failed_tests += 1
            print_status(test_name, passed, details)
            return passed
        except Exception as e:
            self.failed_tests += 1
            print_status(test_name, False, f"Exception: {e}")
            return False

    def test_database_connectivity(self):
        """Test database connection"""
        try:
            conn = get_db_connection()
            conn.close()
            return True, "Database connection successful"
        except Exception as e:
            return False, f"Connection failed: {e}"

    def test_table_exists(self, table_name):
        """Test if table exists"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result is not None, f"Table '{table_name}' found" if result else f"Table '{table_name}' missing"
        except Exception as e:
            return False, f"Error: {e}"

    def test_table_count(self, table_name, expected_min=0):
        """Test table row count"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            passed = count >= expected_min
            return passed, f"Count: {count} (expected >= {expected_min})"
        except Exception as e:
            return False, f"Error: {e}"

    def test_view_exists(self, view_name):
        """Test if view exists"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {view_name} LIMIT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            return True, f"View '{view_name}' is accessible"
        except Exception as e:
            return False, f"View error: {e}"

    def test_rag_query(self, query, expected_type='answer'):
        """Test RAG system query"""
        try:
            rag = FalloutRAG()
            response = rag.ask(query, skip_classification=True)
            passed = response['type'] == expected_type
            return passed, f"Response type: {response['type']}"
        except Exception as e:
            return False, f"Query failed: {e}"

    def test_data_integrity_weapons(self):
        """Test weapons data integrity"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Check for weapons with missing critical fields
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM weapons
                WHERE name IS NULL OR name = '' OR type IS NULL
            """)
            bad_count = cursor.fetchone()['count']

            cursor.close()
            conn.close()

            passed = bad_count == 0
            return passed, f"Weapons with missing critical fields: {bad_count}"
        except Exception as e:
            return False, f"Error: {e}"

    def test_data_integrity_perks(self):
        """Test perks data integrity"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Check for perks without ranks
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM perks p
                LEFT JOIN perk_ranks pr ON p.id = pr.perk_id
                WHERE pr.id IS NULL
            """)
            orphaned = cursor.fetchone()['count']

            cursor.close()
            conn.close()

            passed = orphaned == 0
            return passed, f"Perks without ranks: {orphaned}"
        except Exception as e:
            return False, f"Error: {e}"

    def test_mutation_exclusivity(self):
        """Test mutation exclusivity rules"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Check Carnivore/Herbivore exclusivity
            cursor.execute("""
                SELECT name, exclusive_with
                FROM mutations
                WHERE exclusive_with IS NOT NULL AND exclusive_with != ''
            """)
            exclusive = cursor.fetchall()

            cursor.close()
            conn.close()

            # Should have exactly 2 (Carnivore and Herbivore)
            passed = len(exclusive) == 2
            names = [m['name'] for m in exclusive]
            return passed, f"Exclusive mutations: {', '.join(names)}"
        except Exception as e:
            return False, f"Error: {e}"

    def run_full_diagnostic(self):
        """Run complete system diagnostic"""
        start_time = datetime.now()

        print(f"\n{BOLD}{BLUE}╔═══════════════════════════════════════════════════════════════════╗")
        print(f"║  FALLOUT 76 BUILD DATABASE - FULL SYSTEM DIAGNOSTIC             ║")
        print(f"║  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                                    ║")
        print(f"╚═══════════════════════════════════════════════════════════════════╝{RESET}\n")

        # ===== DATABASE CONNECTIVITY =====
        print_header("PHASE 1: DATABASE CONNECTIVITY")
        self.run_test("Database Connection", self.test_database_connectivity)

        # ===== TABLE STRUCTURE =====
        print_header("PHASE 2: TABLE STRUCTURE VALIDATION")
        tables = ['weapons', 'armor', 'perks', 'perk_ranks', 'legendary_perks',
                 'legendary_perk_ranks', 'mutations', 'consumables']
        for table in tables:
            self.run_test(f"Table: {table}", lambda t=table: self.test_table_exists(t))

        # ===== DATA COMPLETENESS =====
        print_header("PHASE 3: DATA COMPLETENESS VALIDATION")
        self.run_test("Weapons Count (>= 250)", lambda: self.test_table_count('weapons', 250))
        self.run_test("Armor Count (>= 400)", lambda: self.test_table_count('armor', 400))
        self.run_test("Perks Count (>= 200)", lambda: self.test_table_count('perks', 200))
        self.run_test("Legendary Perks Count (>= 25)", lambda: self.test_table_count('legendary_perks', 25))
        self.run_test("Mutations Count (= 19)", lambda: self.test_table_count('mutations', 19))
        self.run_test("Consumables Count (>= 10)", lambda: self.test_table_count('consumables', 10))

        # ===== VIEW VALIDATION =====
        print_header("PHASE 4: RAG-OPTIMIZED VIEW VALIDATION")
        views = ['v_weapons_with_perks', 'v_armor_complete', 'v_perks_all_ranks',
                'v_legendary_perks_all_ranks', 'v_mutations_complete', 'v_consumables_complete']
        for view in views:
            self.run_test(f"View: {view}", lambda v=view: self.test_view_exists(v))

        # ===== DATA INTEGRITY =====
        print_header("PHASE 5: DATA INTEGRITY CHECKS")
        self.run_test("Weapons Data Integrity", self.test_data_integrity_weapons)
        self.run_test("Perks Data Integrity", self.test_data_integrity_perks)
        self.run_test("Mutation Exclusivity Rules", self.test_mutation_exclusivity)

        # ===== RAG SYSTEM FUNCTIONALITY =====
        print_header("PHASE 6: RAG QUERY ENGINE FUNCTIONALITY")
        self.run_test("RAG: Weapon Query", lambda: self.test_rag_query("List 3 shotguns"))
        self.run_test("RAG: Armor Query", lambda: self.test_rag_query("Show power armor"))
        self.run_test("RAG: Perk Query", lambda: self.test_rag_query("What does Gunslinger do?"))
        self.run_test("RAG: Mutation Query", lambda: self.test_rag_query("What is Marsupial?"))
        self.run_test("RAG: Consumable Query", lambda: self.test_rag_query("What chems boost damage?"))
        self.run_test("RAG: Complex Query", lambda: self.test_rag_query("Best perks for shotgun build"))

        # ===== CALCULATE RESULTS =====
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # ===== FINAL REPORT =====
        print_header("DIAGNOSTIC SUMMARY")

        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0

        print(f"Total Tests Run:     {self.total_tests}")
        print(f"{GREEN}Tests Passed:        {self.passed_tests}{RESET}")
        print(f"{RED}Tests Failed:        {self.failed_tests}{RESET}")
        print(f"Success Rate:        {success_rate:.1f}%")
        print(f"Execution Time:      {duration:.2f}s")

        # System Status
        print(f"\n{BOLD}OVERALL SYSTEM STATUS:{RESET}")
        if self.failed_tests == 0:
            print(f"{GREEN}{BOLD}✓ ALL SYSTEMS OPERATIONAL{RESET}")
            print(f"{GREEN}The warp core is stable, shields are at maximum, and all systems are go!{RESET}")
        elif self.failed_tests <= 2:
            print(f"{YELLOW}{BOLD}⚠ MINOR ISSUES DETECTED{RESET}")
            print(f"{YELLOW}Some subsystems need attention, but primary systems are functional.{RESET}")
        else:
            print(f"{RED}{BOLD}✗ CRITICAL ISSUES DETECTED{RESET}")
            print(f"{RED}Multiple system failures detected. Engineering team needed!{RESET}")

        # Database Stats
        print(f"\n{BOLD}DATABASE STATISTICS:{RESET}")
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            stats = {}
            for table in ['weapons', 'armor', 'perks', 'legendary_perks', 'mutations', 'consumables']:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]

            cursor.close()
            conn.close()

            print(f"  Weapons:          {stats['weapons']:,}")
            print(f"  Armor Pieces:     {stats['armor']:,}")
            print(f"  Regular Perks:    {stats['perks']:,}")
            print(f"  Legendary Perks:  {stats['legendary_perks']:,}")
            print(f"  Mutations:        {stats['mutations']:,}")
            print(f"  Consumables:      {stats['consumables']:,}")
            print(f"  {BOLD}Total Items:      {sum(stats.values()):,}{RESET}")

        except Exception as e:
            print(f"  {RED}Unable to retrieve stats: {e}{RESET}")

        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{CYAN}Diagnostic complete. La Forge out. 🖖{RESET}\n")

        return self.failed_tests == 0


if __name__ == "__main__":
    diagnostic = SystemDiagnostic()
    success = diagnostic.run_full_diagnostic()
    sys.exit(0 if success else 1)
