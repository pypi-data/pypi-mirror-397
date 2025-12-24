import sqlite3
import logging
from pathlib import Path
from typing import Dict

class PackageResolver:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def check_package(self, package_name: str) -> Dict[str, str]:
        """
        Checks a single package name against the local database.
        """
        package_name = package_name.lower()
        
        if not self.db_path.exists():
            return {"status": "WARN", "reason": "DB not found", "risk": "unknown"}

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT reason, risk_level FROM hallucinations WHERE name=?", (package_name,))
                block_hit = cursor.fetchone()
                if block_hit:
                    return {
                        "status": "BLOCK",
                        "reason": block_hit[0],
                        "risk": block_hit[1]
                    }

                cursor.execute("SELECT id FROM packages WHERE name=?", (package_name,))
                if not cursor.fetchone():
                    return {
                        "status": "WARN",
                        "reason": "Unknown package (not in local graph)",
                        "risk": "medium"
                    }

                return {
                    "status": "PASS",
                    "reason": "Verified in Knowledge Graph",
                    "risk": "low"
                }

        except Exception as e:
            logging.error(f"DB Error: {e}")
            return {"status": "WARN", "reason": "Internal Error", "risk": "unknown"}