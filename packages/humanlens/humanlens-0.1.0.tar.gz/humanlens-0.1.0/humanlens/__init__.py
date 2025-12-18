"""
humanlens
---------

A lightweight fairness and compliance auditing toolkit for AI/ML models.

Provides:
  • CLI interface (future) →  `humanlens data.csv`
  • Python API            →  `import humanlens as hl`

Main functions exposed:
  - show_model_catalog()    : Optional UI selector for model type
  - test()                  : Run fairness + compliance audit
  - run_fairness_audit()    : Core fairness audit engine
  - save_results()          : Save standardized JSON audit report
  - submit_for_review()     : Mock governance approval workflow
  - compare_from_raw_csv()  : Compare fairness across two datasets
"""

from .core import (
    test, run_fairness_audit, save_results, show_model_catalog,
    submit_for_review, compare_from_raw_csv, get_group_metrics, print_group_table
)

__all__ = [
    "test",
    "run_fairness_audit",
    "save_results",
    "show_model_catalog",
    "submit_for_review",
    "compare_from_raw_csv",
    "get_group_metrics",
    "print_group_table"
]

__version__ = "0.1.0"