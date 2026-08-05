import sqlite3
import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "on-this-day-reader" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import export_dayone_on_this_day as exporter


class TagJoinSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row

    def tearDown(self) -> None:
        self.conn.close()

    def create_relation(self, table: str, entry_column: str, tag_column: str) -> None:
        self.conn.execute(
            f'CREATE TABLE "{table}" ("{entry_column}" INTEGER, "{tag_column}" INTEGER)'
        )

    def test_discovers_current_generated_relation_table(self) -> None:
        self.create_relation("Z_8TAGS", "Z_8BOOKS2", "Z_67TAGS")
        self.create_relation("Z_18TAGS", "Z_18ENTRIES", "Z_67TAGS1")

        schema = exporter.get_tag_join_schema(self.conn)

        self.assertEqual(
            schema,
            exporter.TagJoinSchema("Z_18TAGS", "Z_18ENTRIES", "Z_67TAGS1"),
        )

    def test_discovers_legacy_generated_relation_table(self) -> None:
        self.create_relation("Z_17TAGS", "Z_17ENTRIES", "Z_67TAGS1")

        schema = exporter.get_tag_join_schema(self.conn)

        self.assertEqual(
            schema,
            exporter.TagJoinSchema("Z_17TAGS", "Z_17ENTRIES", "Z_67TAGS1"),
        )

    def test_fetch_tags_uses_discovered_relation(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE ZTAG (Z_PK INTEGER PRIMARY KEY, ZNAME TEXT);
            INSERT INTO ZTAG (Z_PK, ZNAME) VALUES (1, 'Travel');
            """
        )
        self.create_relation("Z_18TAGS", "Z_18ENTRIES", "Z_67TAGS1")
        self.conn.execute(
            'INSERT INTO Z_18TAGS (Z_18ENTRIES, Z_67TAGS1) VALUES (42, 1)'
        )

        schema = exporter.get_tag_join_schema(self.conn)

        self.assertEqual(exporter.fetch_tags(self.conn, 42, schema), ["Travel"])

    def test_fetch_entries_tag_filters_use_discovered_relation(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE ZTAG (Z_PK INTEGER PRIMARY KEY, ZNAME TEXT);
            INSERT INTO ZTAG (Z_PK, ZNAME) VALUES (1, 'Travel'), (2, 'Work');
            CREATE TABLE ZJOURNAL (
                Z_PK INTEGER PRIMARY KEY,
                ZNAME TEXT,
                ZISTRASHJOURNAL INTEGER,
                ZSHOULDBEINCLUDEDINONTHISDAY INTEGER
            );
            INSERT INTO ZJOURNAL
                (Z_PK, ZNAME, ZISTRASHJOURNAL, ZSHOULDBEINCLUDEDINONTHISDAY)
            VALUES (1, 'Journal', 0, 1);
            CREATE TABLE ZENTRY (
                Z_PK INTEGER PRIMARY KEY,
                ZUUID TEXT,
                ZGREGORIANYEAR INTEGER,
                ZGREGORIANMONTH INTEGER,
                ZGREGORIANDAY INTEGER,
                ZCREATIONDATE REAL,
                ZMODIFIEDDATE REAL,
                ZMARKDOWNTEXT TEXT,
                ZRICHTEXTJSON TEXT,
                ZISDRAFT INTEGER,
                ZJOURNAL INTEGER
            );
            INSERT INTO ZENTRY
                (Z_PK, ZUUID, ZGREGORIANYEAR, ZGREGORIANMONTH, ZGREGORIANDAY,
                 ZMARKDOWNTEXT, ZISDRAFT, ZJOURNAL)
            VALUES
                (101, 'entry-101', 2024, 8, 5, 'Travel entry', 0, 1),
                (102, 'entry-102', 2024, 8, 5, 'Work entry', 0, 1);
            CREATE TABLE ZATTACHMENT (
                Z_PK INTEGER PRIMARY KEY,
                ZENTRY INTEGER,
                ZTYPE TEXT,
                ZFILENAME TEXT,
                ZTITLE TEXT,
                ZCAPTION TEXT,
                ZDATE REAL,
                ZDURATION INTEGER,
                ZFILESIZE INTEGER,
                ZORDERINENTRY INTEGER
            );
            CREATE TABLE Z_18TAGS (Z_18ENTRIES INTEGER, Z_67TAGS1 INTEGER);
            INSERT INTO Z_18TAGS (Z_18ENTRIES, Z_67TAGS1)
            VALUES (101, 1), (102, 2);
            """
        )

        include_entries = exporter.fetch_entries(
            self.conn, 8, 5, True, [], [], ["Travel"], [], "any", "asc"
        )
        exclude_entries = exporter.fetch_entries(
            self.conn, 8, 5, True, [], [], [], ["Travel"], "any", "asc"
        )

        self.assertEqual([entry["entry_pk"] for entry in include_entries], [101])
        self.assertEqual([entry["entry_pk"] for entry in exclude_entries], [102])

    def test_discovers_relation_by_column_shape(self) -> None:
        self.create_relation("TAG_LINKS", "Z_18ENTRIES", "Z_67TAGS1")

        schema = exporter.get_tag_join_schema(self.conn)

        self.assertEqual(
            schema,
            exporter.TagJoinSchema("TAG_LINKS", "Z_18ENTRIES", "Z_67TAGS1"),
        )

    def test_ambiguous_generated_relations_fail_with_diagnostic(self) -> None:
        self.create_relation("Z_17TAGS", "Z_17ENTRIES", "Z_67TAGS1")
        self.create_relation("Z_18TAGS", "Z_18ENTRIES", "Z_67TAGS1")

        with self.assertRaisesRegex(RuntimeError, "uniquely identify"):
            exporter.get_tag_join_schema(self.conn)


if __name__ == "__main__":
    unittest.main()
