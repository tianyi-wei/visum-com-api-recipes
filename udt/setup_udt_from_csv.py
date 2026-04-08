"""
Creates (or resets) a User-Defined Table (UDT) in PTV Visum
and populates it from a CSV file.
"""

import os
import pandas as pd

PRIO = 20480
UDT_NAME = "USER_DEFINED_TABLE_NAME"


def get_udt_names(visum_instance):
    """Return list of all existing UDT names."""
    return [t.AttValue("Name") for t in visum_instance.Net.TableDefinitions.GetAll]


def ensure_udt_exists(visum_instance, udt_name):
    """Create the UDT if it doesn't already exist."""
    if udt_name not in get_udt_names(visum_instance):
        visum_instance.Net.AddTableDefinition(udt_name)


def reset_udt(visum_instance, udt_name):
    """Clear all rows and user-defined attribute columns from the UDT."""
    table = visum_instance.Net.TableDefinitions.ItemByKey(udt_name)
    table.TableEntries.RemoveAll()
    return table


def get_existing_uda_names(table):
    """Return names of existing user-defined attributes on the table."""
    return [
        a.Name
        for a in table.TableEntries.Attributes.GetAll
        if a.Category == "User-defined attributes"
    ]


def add_missing_udas(table, columns):
    """Add user-defined attributes for any columns not yet on the table."""
    existing = get_existing_uda_names(table)
    for col in columns:
        if col not in existing:
            table.TableEntries.AddUserDefinedAttribute(col, col, col, 2, DecPlaces=3)  #1=int, 2=float, 5=text


def populate_udt(table, df):
    """Write DataFrame rows into the UDT."""
    table.AddMultiTableEntries(len(df))
    table.TableEntries.SetMultipleAttributes(df.columns.tolist(), df.to_numpy())


# --- Main ---
proj_dir = Visum.GetPath(2)
data_path = os.path.join(proj_dir, "inputs", f"{UDT_NAME}.csv")

coeffs = pd.read_csv(data_path)

ensure_udt_exists(Visum, UDT_NAME)
table = reset_udt(Visum, UDT_NAME)
add_missing_udas(table, coeffs.columns)
populate_udt(table, coeffs)