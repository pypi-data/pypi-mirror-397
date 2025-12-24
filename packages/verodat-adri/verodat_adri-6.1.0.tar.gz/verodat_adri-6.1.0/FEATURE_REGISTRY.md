# ADRI Feature Registry

**Last Generated:** 2025-10-24 10:18:27

**Total Features:** 13

---

## Statistics

- **Open Source Features (OPEN_SOURCE + SHARED):** 12
- **Enterprise-Only Features:** 1
- **Total Features:** 13

## Dependency Graph

The features are organized in dependency order. When syncing to open source,
features will be extracted in the order that respects their dependencies.


## OPEN_SOURCE Features (9)

| Feature | Description | Files | Status | Dependencies |
|---------|-------------|-------|--------|--------------|
| analysis_contract_generator | Auto-generates ADRI contracts from data profiling and rule inference | contract_generator.py | ✅ ACTIVE | - |
| analysis_data_profiler | Data profiling engine for analyzing dataset patterns and quality | data_profiler.py | ✅ ACTIVE | - |
| cli_assess_command | CLI assess command for running data quality assessments | assess.py | ✅ ACTIVE | - |
| cli_generate_contract | CLI command for auto-generating ADRI contracts from data analysis | generate_contract.py | ✅ ACTIVE | analysis_contract_generator |
| cli_view_logs | CLI command for viewing and analyzing ADRI audit logs | view_logs.py | ✅ ACTIVE | - |
| contracts_parser | YAML contract parsing and validation for ADRI data quality contracts | parser.py | ✅ ACTIVE | - |
| decorator_adri_protected | Core @adri_protected decorator for data quality protection in agent workflows | decorator.py | ✅ ACTIVE | - |
| guard_protection_modes | Data protection modes (fail-fast, selective, warn-only) for guard decorator | modes.py | ✅ ACTIVE | - |
| validator_data_loaders | Data and contract loading utilities for CSV, JSON, Parquet, and YAML files | loaders.py | ✅ ACTIVE | - |

## SHARED Features (3)

| Feature | Description | Files | Status | Dependencies |
|---------|-------------|-------|--------|--------------|
| config_loader | Configuration management and environment-based contract resolution | loader.py | ✅ ACTIVE | - |
| core_validator_engine | Core validation engine for data quality assessment used by both enterprise and open source | engine.py | ✅ ACTIVE | - |
| logging_local_jsonl | Local JSONL audit logging system used by both enterprise and open source | local.py | ✅ ACTIVE | - |

## ENTERPRISE Features (1)

| Feature | Description | Files | Status | Dependencies |
|---------|-------------|-------|--------|--------------|
| api_verodat_bridge | Basic Verodat API integration bridge for enterprise users | enterprise.py | ✅ ACTIVE | - |

---

## Notes

This registry is auto-generated. Do not edit manually.
To update, run: `python scripts/generate_feature_registry.py`

Review this file in git diffs to approve feature scope decisions before committing.
