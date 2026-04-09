import os
import pandas as pd
import VisumPy.helpers as h

proj_dir = Visum.GetPath(2)
data_dir = os.path.join(proj_dir, 'inputs')

def get_zone_udas():
    """Return a set of existing user-defined zone attribute names."""
    return {
        i.Name
        for i in Visum.Net.Zones.Attributes.GetAll
        if i.Category == "User-defined attributes"
    }

def ensure_uda(name, uda_type, dec_places=None):
    """Add a zone UDA only if it doesn't already exist."""
    if name not in get_zone_udas():
        kwargs = {"DecPlaces": dec_places} if dec_places is not None else {}
        Visum.Net.Zones.AddUserDefinedAttribute(name, name, name, uda_type, **kwargs)

def import_marginal_split(filepath):
    """
    Import a marginal split CSV into Visum zone UDAs.
    - Creates float UDAs (type=2) for each percentage column in the CSV.
    - Creates integer UDAs (type=1) for corresponding TOT_ columns.
    - Loads CSV values into Visum zones.
    """
    marginal = pd.read_csv(filepath)
    udas_pct = marginal.columns.to_list()

    # Ensure float UDAs exist for percentage columns, then load data
    for uda in udas_pct:
        ensure_uda(uda, uda_type=2, dec_places=2)   # 2 = float
    Visum.Net.Zones.SetMultipleAttributes(udas_pct, marginal.to_numpy())

    # Ensure integer UDAs exist for TOT_ columns
    for uda in udas_pct:
        ensure_uda("TOT_" + uda, uda_type=1)         # 1 = int

import_marginal_split(os.path.join(data_dir, "TourBasedMarginalSplit_POP.csv"))
import_marginal_split(os.path.join(data_dir, "TourBasedMarginalSplit_EMP.csv"))
