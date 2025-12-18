# Changelog

All notable changes to this project will be documented in this file.
Format based on Path of Building changelog style, adapted for MCP tooling.

> **Community Project**: This is an independent, fan-made project built out of love for Path of Exile 2. Not affiliated with or endorsed by Grinding Gear Games.

---

## Version 1.0.0 (2025-12-16) - First Major Release

The first stable release of the PoE2 Build Optimizer MCP server. Provides 32 MCP tools for AI-powered character analysis and build optimization.

--- Core Features ---
* 32 registered MCP tools for character analysis, validation, and optimization
* Multi-source character fetching (poe.ninja, official API, HTML scrape fallback)
* Path of Building import/export support
* Comprehensive game mechanics knowledge base

--- MCP Tools ---
* Character analysis: `analyze_character`, `compare_to_top_players`, `import_poe_ninja_url`
* Validation tools: `validate_support_combination`, `validate_build_constraints`
* Gem inspection: `inspect_support_gem`, `inspect_spell_gem`, `list_all_supports`, `list_all_spells`
* Passive tree: `list_all_keystones`, `inspect_keystone`, `list_all_notables`, `inspect_passive_node`
* Base items: `list_all_base_items`, `inspect_base_item`
* Item mods: `inspect_mod`, `list_all_mods`, `search_mods_by_stat`, `get_mod_tiers`, `validate_item_mods`
* Path of Building: `import_pob`, `export_pob`, `get_pob_code`
* Knowledge: `explain_mechanic`, `get_formula`

--- Token Optimization ---
* Pagination support with `limit` (default 20) and `offset` parameters
* Detail level filtering (`summary`, `standard`, `full`) for response verbosity control
* Compact output format with abbreviated JSON keys for programmatic consumption

--- Data Sources ---
* 4,975+ passive tree nodes with full stat text
* 335+ ascendancy nodes (99% coverage)
* 14,269 item modifiers (prefixes, suffixes, implicits)
* Complete skill gem data from Path of Building
* Support gem effects and interaction data

--- Infrastructure ---
* SQLite database with async support (aiosqlite)
* Multi-tier caching (memory -> Redis optional -> SQLite)
* Rate limiting with exponential backoff
* Comprehensive test suite

---

## Prior Development History

See git commits before 2025-12-16 for development history leading to v1.0.0.
