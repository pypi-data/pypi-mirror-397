# Snowflake Data Validation

[![License](https://img.shields.io/badge/License-Snowflake%20Conversion%20Software-blue)](https://www.snowflake.com/en/legal/technical-services-and-education/conversion-software-terms/)
[![Python](https://img.shields.io/badge/python-3.10--3.13-blue)](https://www.python.org/downloads/)

**Snowflake Data Validation** is a command-line tool and Python library for validating data migrations and ensuring data quality between source and target databases, with a focus on Snowflake and SQL Server.

> 📖 **For detailed usage instructions, configuration examples, and CLI reference, please check the [official documentation](https://docs.snowflake.com/en/migrations/snowconvert-docs/data-validation-cli/CLI_QUICK_REFERENCE).**

---

## 🚀 Features

- **Multi-level validation**: Schema validation, statistical metrics, and row-level data integrity checks.
- **Multiple source platforms**: SQL Server, Redshift, Teradata.
- **User-friendly CLI**: Comprehensive commands for automation and orchestration.
- **Parallel processing**: Multi-threaded table validation for faster execution.
- **Offline validation**: Extract source data as Parquet files for validation without source access.
- **Flexible configuration**: YAML-based workflows with per-table customization.
- **Partitioning support**: Row and column partitioning helpers for large table validation.
- **Detailed reporting**: CSV reports, console output, and comprehensive logging.
- **Extensible architecture**: Ready for additional database engines.

---

## 📦 Installation

```bash
pip install snowflake-data-validation
```

For SQL Server support:

```bash
pip install "snowflake-data-validation[sqlserver]"
```

For development and testing:

```bash
pip install "snowflake-data-validation[all]"
```

---

## 🔄 Execution Modes

| Mode | Command | Description |
|------|---------|-------------|
| **Sync Validation** | `run-validation` | Real-time comparison between source and target databases |
| **Source Extraction** | `source-validate` | Extract source data to Parquet files for offline validation |
| **Async Validation** | `run-async-validation` | Validate using pre-extracted Parquet files |
| **Script Generation** | `generate-validation-scripts` | Generate SQL scripts for manual execution |

**Supported Dialects**: `sqlserver`, `snowflake`, `redshift`, `teradata`

---

## 🔍 Validation Levels

### Schema Validation
Compares table structure between source and target:
- Column names and order
- Data types with mapping support
- Precision, scale, and length
- Nullable constraints

### Metrics Validation
Compares statistical metrics for each column:
- Row count
- Min/Max values
- Sum and Average
- Null count
- Distinct count

### Row Validation
Performs row-by-row comparison:
- Primary key matching
- Field-level value comparison
- Mismatch reporting

---

## 📊 Reports

- **Console Output**: Real-time progress with success/failure indicators
- **CSV Reports**: Detailed validation results with all comparison data
- **Log Files**: Comprehensive debug and error logging

---

## 📚 Documentation

For complete command reference, configuration options, and examples, see the [Data Validation CLI](https://docs.snowflake.com/en/migrations/snowconvert-docs/data-validation-cli/CLI_QUICK_REFERENCE).

---

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](../../CONTRIBUTING.md) for details on how to collaborate, set up your development environment, and submit PRs.

---

## 📄 License

This project is licensed under the Snowflake Conversion Software Terms. See the [LICENSE](../../LICENSE) file for the full text or visit the [Conversion Software Terms](https://www.snowflake.com/en/legal/technical-services-and-education/conversion-software-terms/) for more information.

---

## 🆘 Support

- **Documentation**: [Full documentation](https://docs.snowflake.com/en/migrations/snowconvert-docs/data-validation-cli/CLI_QUICK_REFERENCE)
- **Issues**: [GitHub Issues](https://github.com/snowflakedb/migrations-data-validation/issues)

---

**Developed with ❄️ by Snowflake**
