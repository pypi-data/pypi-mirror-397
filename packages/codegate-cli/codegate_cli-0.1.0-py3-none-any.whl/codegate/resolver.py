import sqlite3
import os
from typing import Optional, List, Tuple

class PackageResolver:
    def __init__(self, db_path: str = "data/knowledge_graph.db"):
        """
        Initialize the local dependency graph resolver.
        
        :param db_path: Path to the SQLite 'Truth' database.
        """
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"[CodeGate] Critical: Knowledge graph not found at {db_path}")
            
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def check_import_safety(self, package: str, import_name: str) -> dict:
        """
        Verifies if a package actually provides the requested import module.
        Returns a structured dictionary with risk analysis.
        """
        self.cursor.execute("SELECT id FROM packages WHERE name=?", (package,))
        pkg_row = self.cursor.fetchone()
        
        if not pkg_row:
            return {
                "status": "BLOCK",
                "reason": "unverified_package",
                "message": f"'{package}' is not in the verified registry."
            }

        pkg_id = pkg_row[0]
        self.cursor.execute("SELECT import_name FROM provided_imports WHERE package_id=?", (pkg_id,))
        valid_imports = [row[0] for row in self.cursor.fetchall()]
        
        if import_name in valid_imports:
            return {
                "status": "PASS",
                "reason": "verified_match",
                "message": f"'{package}' correctly provides module '{import_name}'."
            }
        else:
            return {
                "status": "WARNING",
                "reason": "import_mismatch",
                "message": f"'{package}' provides {valid_imports}, not '{import_name}'. Possible typo or hallucination."
            }

    def close(self):
        self.conn.close()