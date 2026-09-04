"""
Data Access & Ingestion Layer for Manufacturing Identity & Access Risk Analysis.

This module provides the DataLoader class to ingest, clean, normalize, and index
the master audit and access risk datasets from the master Excel workbook:
'Audit_Driven_Access_Risk_Master_Data.xlsx'.
"""

from pathlib import Path
import re
from typing import Any, Dict, Optional, Union
import pandas as pd


class DataLoader:
    """
    Ingests and caches master risk datasets from Excel, providing normalized,
    case-insensitive, high-speed lookups for audit rules and risk scoring.
    """

    # Sheet name constants in the Master Excel workbook
    SHEET_GOLDEN_LAWS = "Audit Golden Laws"
    SHEET_ACTION_RISK = "Access Action Risk Index"
    SHEET_JOB_BASELINES = "Job Definition Baselines"
    SHEET_ROLE_CONFLICTS = "Role Conflict Matrix"
    SHEET_AUDIT_BENCHMARKS = "Audit Comparison Benchmark"

    # Known role aliases to handle minor spelling or nomenclature variations
    ROLE_ALIASES = {
        "quality engineer": "quality assurance engineer",
        "qa engineer": "quality assurance engineer",
        "job_qual_eng": "quality assurance engineer",
    }

    def __init__(
        self,
        excel_path: Union[str, Path] = "data/Audit_Driven_Access_Risk_Master_Data.xlsx",
    ) -> None:
        """
        Initialize DataLoader and cache all 5 sheets into normalized DataFrames.

        Args:
            excel_path: Path to the master Excel file.

        Raises:
            FileNotFoundError: If the specified Excel file cannot be found.
        """
        self.excel_path = self._resolve_path(excel_path)
        if not self.excel_path.exists():
            raise FileNotFoundError(
                f"Master Excel file not found at resolved path: {self.excel_path}"
            )

        # Load all sheets using pandas with openpyxl engine
        self._load_and_normalize_sheets()

        # Build fast lookup indexes
        self._build_indexes()

    @staticmethod
    def _resolve_path(path: Union[str, Path]) -> Path:
        """Resolve the Excel path across different execution working directories."""
        p = Path(path)
        if p.exists():
            return p.resolve()

        # Check relative to this module's directory (RiskAnalysisMicron/data)
        module_dir = Path(__file__).resolve().parent
        candidate_module = module_dir / p.name
        if candidate_module.exists():
            return candidate_module.resolve()

        # Check relative to project root (RiskAnalysisMicron/)
        project_root = module_dir.parent
        candidate_root = project_root / path
        if candidate_root.exists():
            return candidate_root.resolve()

        return p.resolve()

    @staticmethod
    def _normalize_string(val: Any) -> str:
        """Strip whitespace and collapse multiple spaces."""
        if val is None or pd.isna(val):
            return ""
        return re.sub(r"\s+", " ", str(val).strip().replace("\n", " ").replace("\r", ""))

    @staticmethod
    def _normalize_key(val: Any) -> str:
        """Normalize a string key for case-insensitive matching."""
        if val is None or pd.isna(val):
            return ""
        # Lowercase, strip, remove extra spaces
        return re.sub(r"\s+", " ", str(val).strip().lower())

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column headers and strip string cell values."""
        # Normalize column headers
        df.columns = [self._normalize_string(c) for c in df.columns]

        # Strip all string values
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].apply(
                    lambda v: self._normalize_string(v) if pd.notna(v) else v
                )

        return df.dropna(how="all").reset_index(drop=True)

    def _read_sheet(self, excel_file: pd.ExcelFile, sheet_name: str) -> pd.DataFrame:
        """
        Read a sheet from the workbook, auto-detecting the header row.
        """
        # Read raw to detect header row if metadata rows precede it
        raw_df = excel_file.parse(sheet_name, header=None)

        header_idx = 0
        for idx, row in raw_df.iterrows():
            non_null = row.dropna()
            if len(non_null) >= 4:
                row_text = " ".join([str(v) for v in non_null.values]).lower()
                if any(
                    k in row_text
                    for k in [
                        "id",
                        "code",
                        "role",
                        "law",
                        "task",
                        "multiplier",
                        "case",
                        "action",
                    ]
                ):
                    header_idx = int(idx)
                    break

        df = excel_file.parse(sheet_name, header=header_idx)
        return self._clean_dataframe(df)

    def _load_and_normalize_sheets(self) -> None:
        """Load and cache all 5 sheets into DataFrames."""
        excel_file = pd.ExcelFile(self.excel_path, engine="openpyxl")

        self.golden_laws_df: pd.DataFrame = self._read_sheet(
            excel_file, self.SHEET_GOLDEN_LAWS
        )
        self.action_risk_df: pd.DataFrame = self._read_sheet(
            excel_file, self.SHEET_ACTION_RISK
        )
        self.job_baselines_df: pd.DataFrame = self._read_sheet(
            excel_file, self.SHEET_JOB_BASELINES
        )
        self.role_conflicts_df: pd.DataFrame = self._read_sheet(
            excel_file, self.SHEET_ROLE_CONFLICTS
        )
        self.audit_benchmarks_df: pd.DataFrame = self._read_sheet(
            excel_file, self.SHEET_AUDIT_BENCHMARKS
        )

    def _canonical_role(self, role_name: str) -> str:
        """Convert a role name/title to its canonical normalized form."""
        norm = self._normalize_key(role_name)
        return self.ROLE_ALIASES.get(norm, norm)

    def _build_indexes(self) -> None:
        """Build high-speed lookup dictionaries."""
        # 1. Golden Laws lookup by ID
        self._laws_by_id: Dict[str, Dict[str, Any]] = {}
        for _, row in self.golden_laws_df.iterrows():
            row_dict = row.to_dict()
            law_id = str(row_dict.get("Golden Law ID", "")).strip()
            if law_id:
                self._laws_by_id[self._normalize_key(law_id)] = row_dict

        # 2. Action Multipliers lookup
        self._action_multipliers: Dict[str, float] = {}
        for _, row in self.action_risk_df.iterrows():
            code = str(row.get("Access Level Code", "")).strip()
            action_type = str(row.get("Access Action Type", "")).strip()
            mult = float(row.get("Base Risk Multiplier (M_p)", 1.0))

            if code:
                self._action_multipliers[code] = mult
                self._action_multipliers[self._normalize_key(code)] = mult
            if action_type:
                self._action_multipliers[action_type] = mult
                self._action_multipliers[self._normalize_key(action_type)] = mult

        # 3. Job Baselines lookup by Role Title and Role Code
        self._baselines_by_role: Dict[str, Dict[str, Any]] = {}
        for _, row in self.job_baselines_df.iterrows():
            row_dict = row.to_dict()
            code = str(row_dict.get("Job Role Code", "")).strip()
            title = str(row_dict.get("Job Role Title", "")).strip()

            if code:
                self._baselines_by_role[self._canonical_role(code)] = row_dict
            if title:
                self._baselines_by_role[self._canonical_role(title)] = row_dict

        # 4. Role Conflicts Matrix lookup (bidirectional pair mapping)
        self._conflicts_pair_map: Dict[tuple[str, str], Dict[str, Any]] = {}
        for _, row in self.role_conflicts_df.iterrows():
            row_dict = row.to_dict()
            role_1 = self._canonical_role(str(row_dict.get("Primary Base Role", "")))
            role_2 = self._canonical_role(str(row_dict.get("Added Secondary Role", "")))

            if role_1 and role_2:
                self._conflicts_pair_map[(role_1, role_2)] = row_dict
                self._conflicts_pair_map[(role_2, role_1)] = row_dict

    # --------------------------------------------------------------------------
    # Public Accessor Methods
    # --------------------------------------------------------------------------

    def get_golden_laws(self) -> pd.DataFrame:
        """
        Returns all 8 statutory laws as a DataFrame.

        Returns:
            pd.DataFrame: Cached Golden Laws DataFrame.
        """
        return self.golden_laws_df.copy()

    def get_law_by_id(self, law_id: str) -> Dict[str, Any]:
        """
        Returns the specific row for a law (e.g., 'GL-01') as a dictionary.

        Args:
            law_id: Golden Law identifier (e.g. 'GL-01', 'gl-01').

        Returns:
            Dict[str, Any]: Details of the requested statutory law.

        Raises:
            KeyError: If law_id is not found.
        """
        clean_key = self._normalize_key(law_id)
        if clean_key in self._laws_by_id:
            return dict(self._laws_by_id[clean_key])

        raise KeyError(
            f"Golden Law ID '{law_id}' not found. Available IDs: "
            f"{sorted(self.golden_laws_df['Golden Law ID'].dropna().unique())}"
        )

    def get_action_multipliers(self) -> Dict[str, float]:
        """
        Returns a dictionary mapping action level codes/names to their base risk multipliers.

        Example:
            {'ACT_VIEW': 0.2, 'ACT_EXEC': 1.0, 'ACT_MOD': 2.0, 'ACT_APPR': 2.5, 'ACT_ADM': 3.0}

        Returns:
            Dict[str, float]: Action multiplier dictionary.
        """
        # Primary code mapping
        multipliers: Dict[str, float] = {}
        for _, row in self.action_risk_df.iterrows():
            code = str(row.get("Access Level Code", "")).strip()
            mult = float(row.get("Base Risk Multiplier (M_p)", 1.0))
            if code:
                multipliers[code] = mult

        return multipliers

    def get_action_multiplier(self, action_key: str) -> float:
        """
        Returns the risk multiplier for a specific action code or action name.

        Args:
            action_key: Action code (e.g. 'ACT_MOD') or action name (e.g. 'Create / Edit / Modify').

        Returns:
            float: Base risk multiplier.

        Raises:
            KeyError: If action_key is not recognized.
        """
        norm_key = self._normalize_key(action_key)
        if norm_key in self._action_multipliers:
            return self._action_multipliers[norm_key]
        if action_key in self._action_multipliers:
            return self._action_multipliers[action_key]

        raise KeyError(
            f"Action identifier '{action_key}' not found in Access Action Risk Index."
        )

    def get_role_baseline(self, role_title: str) -> Dict[str, Any]:
        """
        Returns the baseline job definition dictionary for the given role, including
        Task 1, Task 2, Task 3, Maximum Authorized Action Level, and Strictly Forbidden capabilities.

        Args:
            role_title: Role title or role code (e.g. 'Production Operator', 'JOB_PROD_OPR').

        Returns:
            Dict[str, Any]: Baseline definition dictionary.

        Raises:
            KeyError: If role_title is not found.
        """
        clean_key = self._canonical_role(role_title)
        if clean_key in self._baselines_by_role:
            return dict(self._baselines_by_role[clean_key])

        # Substring / partial match fallback
        for key, row in self._baselines_by_role.items():
            if clean_key in key or key in clean_key:
                return dict(row)

        available_roles = sorted(
            self.job_baselines_df["Job Role Title"].dropna().unique()
        )
        raise KeyError(
            f"Role baseline for '{role_title}' not found. Available roles: {available_roles}"
        )

    def check_conflict(
        self, role_a: str, role_b: str
    ) -> Optional[Dict[str, Any]]:
        """
        Bidirectional query across the 'Role Conflict Matrix'. Checks if (role_a, role_b)
        OR (role_b, role_a) triggers an SoD conflict.

        Args:
            role_a: Primary role title or code.
            role_b: Secondary role title or code.

        Returns:
            Optional[Dict[str, Any]]: Conflict details dictionary if non-compliant / SoD conflict
                                      is triggered; None if compliant or no conflict found.
        """
        entry = self.get_conflict_entry(role_a, role_b)
        if entry is None:
            return None

        status = str(entry.get("Audit Compliance Status", "")).strip().upper()
        # If status indicates non-compliance / SoD breach, return conflict details
        if "NON-COMPLIANT" in status or "BREACH" in status or "DEFICIENCY" in status:
            return dict(entry)

        # If it is explicitly compliant ('AUDIT COMPLIANT'), return None
        return None

    def get_conflict_entry(
        self, role_a: str, role_b: str
    ) -> Optional[Dict[str, Any]]:
        """
        Returns the raw matrix entry for a role pair regardless of compliance status.

        Args:
            role_a: Primary role title or code.
            role_b: Secondary role title or code.

        Returns:
            Optional[Dict[str, Any]]: Matrix entry dict, or None if pair is not listed.
        """
        norm_a = self._canonical_role(role_a)
        norm_b = self._canonical_role(role_b)

        # Direct pair lookup
        if (norm_a, norm_b) in self._conflicts_pair_map:
            return dict(self._conflicts_pair_map[(norm_a, norm_b)])

        # Fuzzy / partial match lookup across mapped pairs
        for (k1, k2), entry in self._conflicts_pair_map.items():
            if (norm_a in k1 or k1 in norm_a) and (norm_b in k2 or k2 in norm_b):
                return dict(entry)

        return None

    def get_benchmark_cases(self) -> pd.DataFrame:
        """
        Returns the benchmark validation cases (AUD-01 to AUD-08) as a DataFrame.

        Returns:
            pd.DataFrame: Cached Audit Comparison Benchmark DataFrame.
        """
        return self.audit_benchmarks_df.copy()


if __name__ == "__main__":
    print("=" * 70)
    print("DataLoader Ingestion & Access Verification")
    print("=" * 70)

    loader = DataLoader()

    # 1. Print row counts for all 5 loaded sheets
    print(f"[1] Golden Laws Sheet:          {len(loader.golden_laws_df)} rows")
    print(f"[2] Action Risk Sheet:          {len(loader.action_risk_df)} rows")
    print(f"[3] Job Baselines Sheet:        {len(loader.job_baselines_df)} rows")
    print(f"[4] Role Conflicts Sheet:       {len(loader.role_conflicts_df)} rows")
    print(f"[5] Audit Benchmarks Sheet:     {len(loader.audit_benchmarks_df)} rows")

    # 2. Test lookup for GL-01
    print("\n" + "-" * 70)
    print("Test Lookup: Golden Law 'GL-01'")
    print("-" * 70)
    law = loader.get_law_by_id("GL-01")
    print(f"ID:        {law.get('Golden Law ID')}")
    print(f"Name:      {law.get('Law Name & Principle')}")
    print(f"Standard:  {law.get('Governing Standard')}")
    print(f"Mandate:   {law.get('Auditor Mandate / Legal Premise')}")
    print(f"Breach:    {law.get('Breach Condition (What Triggers Finding)')}")
    print(f"Severity:  {law.get('Audit Finding Classification')}")

    # 3. Test Action Multipliers
    print("\n" + "-" * 70)
    print("Action Multipliers:")
    print("-" * 70)
    multipliers = loader.get_action_multipliers()
    for code, mult in multipliers.items():
        print(f"  - {code}: {mult}x")

    # 4. Test Role Baseline
    print("\n" + "-" * 70)
    print("Test Role Baseline: 'Production Operator'")
    print("-" * 70)
    baseline = loader.get_role_baseline("Production Operator")
    print(f"Role:              {baseline.get('Job Role Title')} ({baseline.get('Job Role Code')})")
    print(f"Department:        {baseline.get('Department')}")
    print(f"Task 1:            {baseline.get('Task 1: Core Standard Task')}")
    print(f"Task 2:            {baseline.get('Task 2: Secondary Operational Task')}")
    print(f"Task 3:            {baseline.get('Task 3: Reporting / Monitoring Task')}")
    print(f"Max Action Level:  {baseline.get('Maximum Authorized Action Level')}")
    print(f"Forbidden:         {baseline.get('Strictly Forbidden / Unallowable Capabilities')}")

    # 5. Test Conflict Check: Production Operator vs Production Supervisor
    print("\n" + "-" * 70)
    print("Test Conflict Check: 'Production Operator' vs 'Production Supervisor'")
    print("-" * 70)
    conflict_1 = loader.check_conflict("Production Operator", "Production Supervisor")
    if conflict_1:
        print(f"Status:      {conflict_1.get('Audit Compliance Status')}")
        print(f"Rule ID:     {conflict_1.get('Conflict Rule ID')}")
        print(f"Risk:        {conflict_1.get('Inherent Conflict Risk')}")
        print(f"Law:         {conflict_1.get('Violated Audit Golden Law')}")
        print(f"Breach:      {conflict_1.get('Operational Breach / Vulnerability Created')}")
        print(f"Remediation: {conflict_1.get('Auditor Mandated Remediation')}")
    else:
        print("Result: COMPLIANT (No SoD conflict triggered)")

    # 6. Test Conflict Check: Production Operator vs Standard SOP Viewer
    print("\n" + "-" * 70)
    print("Test Conflict Check: 'Production Operator' vs 'Standard SOP Viewer'")
    print("-" * 70)
    conflict_2 = loader.check_conflict("Production Operator", "Standard SOP Viewer")
    if conflict_2:
        print(f"Status:      {conflict_2.get('Audit Compliance Status')}")
        print(f"Risk:        {conflict_2.get('Inherent Conflict Risk')}")
    else:
        print("Result: COMPLIANT (No SoD conflict triggered)")

    print("\n" + "=" * 70)
    print("All DataLoader verification checks passed successfully.")
    print("=" * 70)
