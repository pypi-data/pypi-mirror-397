"""
Author: Wang Zilu
Email: 1923524070@qq.com
Date: 2025.8.20
Description: CCI_tools
"""

def build_interaction_dicts(
    interaction_df,
    species="human"
):
    """
    Build interaction-to-genes and interaction-to-pathway mappings.

    Parameters
    ----------
    interaction_df : pd.DataFrame
        Must contain the following columns:
        ["ligand", "receptor", "source", "target", "pathway_name", "prob", "pval"]
    species : {"human", "mouse"}, default "human"
        If "human": ligand/receptor names are forced to UPPERCASE.
        If "mouse": ligand/receptor names are formatted as Capitalized (Title case).

    Returns
    -------
    interaction_dict : dict
        Mapping {interaction: [ligand_genes + receptor_genes]}.
    interaction_to_pathway : dict
        Mapping {interaction: pathway}.
    """
    import pandas as pd
    
    required_cols = ["ligand", "receptor", "source", "target", "pathway_name", "prob", "pval"]
    missing = [c for c in required_cols if c not in interaction_df.columns]
    if missing:
        raise ValueError(f"interaction_df missing required columns: {missing}")

    if species.lower() == "human":
        interaction_df["ligand"] = interaction_df["ligand"].str.upper()
        interaction_df["receptor"] = interaction_df["receptor"].str.upper()
    elif species.lower() == "mouse":
        interaction_df["ligand"] = interaction_df["ligand"].str.capitalize()
        interaction_df["receptor"] = interaction_df["receptor"].str.capitalize()
    else:
        raise ValueError("species must be either 'human' or 'mouse'")

    interaction_df["interaction"] = interaction_df["ligand"] + "_" + interaction_df["receptor"]

    def extract_genes(name: str):
        name = str(name).split("-")[-1]
        return list(name.split("_"))

    interaction_dict = {}
    for _, row in interaction_df.iterrows():
        ligand_genes = extract_genes(row["ligand"])
        receptor_genes = extract_genes(row["receptor"])
        interaction = row["interaction"]
        interaction_dict[interaction] = ligand_genes + receptor_genes

    interaction_to_pathway = {
        row["interaction"]: row["pathway_name"]
        for _, row in interaction_df.iterrows()
    }

    return interaction_dict, interaction_to_pathway

def compute_interaction_score(
    adata,
    interaction_dict,
    groupby_keys=None,
    grid_size=100,
    library_id_key=None,
    output_dir=None,
    verbose=True,
    plot_name_prefix="result",
):
    """
    Compute and visualize interaction scores for a set of gene pairs/groups.

    Parameters
    ----------
    adata : AnnData
        AnnData object containing spatial transcriptomics data. 
        Must have `.var_names` for genes and `.obsm["spatial"]` for coordinates.

    interaction_dict : dict
        Dictionary where keys are interaction names (str) and values are lists of genes (list of str).
        Example: {"InteractionA": ["Gene1", "Gene2"], "InteractionB": ["Gene3", "Gene4", "Gene5"]}

    groupby_keys : list of str, optional (default: None)
        Keys from `adata.obs` to group cells/spots before computing scores. 
        If None, scores will be aggregated only by spatial grid bins.

    grid_size : int, optional (default: 100)
        Size of the grid bin for spatial aggregation (in pixels).

    library_id_key : str, optional (default: None)
        Column in `adata.obs` specifying multiple library/chip IDs.
        If None, all data will be treated as a single library.

    output_dir : str
        Directory where output files (PDF of plots and CSV of scores) will be saved.

    verbose : bool, optional (default: True)
        If True, print progress and warnings (e.g., skipped interactions).

    plot_name_prefix : str, optional (default: "result")
        Prefix for output file names. Will generate:
        - "<prefix>.pdf" for batch plots
        - "<prefix>_scores.csv" for interaction scores matrix

    Returns
    -------
    heatmap_wide : pandas.DataFrame
        Wide-format matrix of interaction scores. Rows = interactions,
        columns = groups (from `groupby_keys` or spatial bins).

    skipped_pairs : list
        List of interactions that were skipped due to missing genes or errors.
    """
    import os
    import pandas as pd
    import numpy as np
    from matplotlib.backends.backend_pdf import PdfPages
    import matplotlib.pyplot as plt
    from .pl import plot_genes_grid_expression

    if output_dir is None:
        raise ValueError("output_dir must be specified")
    os.makedirs(output_dir, exist_ok=True)

    pdf_path = os.path.join(output_dir, f"{plot_name_prefix}_LRpairs.pdf")
    csv_path = os.path.join(output_dir, f"{plot_name_prefix}_scores.csv")

    heatmap_matrix_long = []
    skipped_pairs = []

    with PdfPages(pdf_path) as pdf:
        for interaction, genes in interaction_dict.items():
            try:
                missing_genes = [g for g in genes if g not in adata.var_names]
                if missing_genes:
                    skipped_pairs.append(interaction)
                    if verbose:
                        print(f"{interaction} skipped, missing genes: {missing_genes}")
                    continue

                fig, score_grid, grouped = plot_genes_grid_expression(
                    adata=adata,
                    genes=genes,
                    grid_size=grid_size,
                    groupby_keys =groupby_keys,
                    mode="normal",
                    celltype_key="subclass",
                    library_id_key=library_id_key
                )
                pdf.savefig(fig)
                plt.close(fig)

                if "score" not in grouped.columns:
                    skipped_pairs.append(interaction)
                    if verbose:
                        print(f"{interaction} skipped, no 'score' in grouped")
                    continue

                non_zero = grouped["score"][grouped["score"] > 0]
                score_max = non_zero.quantile(0.995) if len(non_zero) > 0 else 1.0
                grouped["score_capped"] = grouped["score"].clip(upper=score_max)

                if groupby_keys is not None:
                    missing = [col for col in groupby_keys if col not in grouped.columns]
                    if missing:
                        skipped_pairs.append(interaction)
                        if verbose:
                            print(f"{interaction} missing columns {missing}, skipped")
                        continue
                    df_grouped = grouped.groupby(groupby_keys)["score_capped"].mean().reset_index()
                    df_grouped["interaction"] = interaction
                    heatmap_matrix_long.append(df_grouped)
                else:
                    grouped["interaction"] = interaction
                    grouped["group_key"] = grouped["x_bin"].astype(str) + "_" + grouped["y_bin"].astype(str)
                    heatmap_matrix_long.append(grouped)

            except Exception as e:
                skipped_pairs.append(interaction)
                if verbose:
                    print(f"Skipping {interaction} due to error: {e}")

    if heatmap_matrix_long:
        heatmap_df = pd.concat(heatmap_matrix_long, axis=0)
        if groupby_keys is not None:
            group_cols = groupby_keys + ["interaction"]
            heatmap_wide = heatmap_df.pivot_table(index="interaction", columns=groupby_keys[0] if len(groupby_keys)==1 else groupby_keys, values="score_capped")
        else:
            heatmap_wide = heatmap_df.pivot(index="interaction", columns="group_key", values="score_capped")
        heatmap_wide.to_csv(csv_path)
        if verbose:
            print(f"Score matrix saved to: {csv_path}")
    else:
        heatmap_wide = pd.DataFrame()
        if verbose:
            print("No valid interaction scores generated.")

    if verbose:
        print("Batch plotting complete.")
        print(f"Skipped interactions: {skipped_pairs if skipped_pairs else 'None'}")

    return heatmap_wide, skipped_pairs



def compute_cci_score_sum(
    adata,
    source_type,
    target_type,
    L_gene,
    R_gene,
    celltype_key="subclass",
    spatial_key="spatial",
    library_key="chip",
    grid_size=400
):
    """
    Compute total colocalization score between source and target cell types
    using ligand-receptor product expression on spatial grid.

    Parameters
    ----------
    adata : AnnData
        Annotated data matrix with spatial and expression data.
    source_type : str
        Cell type label for ligand-expressing source cells.
    target_type : str
        Cell type label for receptor-expressing target cells.
    L_gene : list of str
        List of ligand gene names.
    R_gene : list of str
        List of receptor gene names.
    celltype_key : str, default "subclass"
        Column in `adata.obs` containing cell type labels.
    spatial_key : str, default "spatial"
        Key in `adata.obsm` for spatial coordinates.
    library_key : str, default "chip"
        Column in `adata.obs` identifying different tissue slices or chips.
    grid_size : int, default 400
        Grid bin size (in microns) used to group cells spatially.

    Returns
    -------
    total_score : float
        Total colocalization interaction score across all chips.
    """

    import pandas as pd
    import numpy as np
    import seaborn as sns
    import matplotlib.pyplot as plt
    from scipy.sparse import issparse
    from tqdm import tqdm

    total_score = 0
    for chip_id in adata.obs[library_key].unique():
        adata_chip = adata[adata.obs[library_key] == chip_id].copy()
        coords = adata_chip.obsm[spatial_key]
        x = coords[:, 0]
        y = coords[:, 1]
        x_bin = (x // grid_size).astype(int)
        y_bin = (y // grid_size).astype(int)

        df = pd.DataFrame({"x_bin": x_bin, "y_bin": y_bin})
        df[celltype_key] = adata_chip.obs[celltype_key].values

        genes = L_gene + R_gene
        for gene in genes:
            assert gene in adata.var_names

        X = adata_chip[:, genes].X
        if issparse(X):
            X = X.toarray()

        df_L = df[df[celltype_key] == source_type].copy()
        for i, gene in enumerate(L_gene):
            df_L[gene] = X[df[celltype_key] == source_type, i]

        df_R = df[df[celltype_key] == target_type].copy()
        for j, gene in enumerate(R_gene):
            df_R[gene] = X[df[celltype_key] == target_type, len(L_gene) + j]

        if df_L.empty or df_R.empty:
            continue

        grouped_L = df_L.groupby(["x_bin", "y_bin"])[L_gene].mean()
        grouped_L["L_expr"] = grouped_L.prod(axis=1)

        grouped_R = df_R.groupby(["x_bin", "y_bin"])[R_gene].mean()
        grouped_R["R_expr"] = grouped_R.prod(axis=1)

        merged = pd.merge(grouped_L["L_expr"], grouped_R["R_expr"], left_index=True, right_index=True)
        merged["score"] = merged["L_expr"] * merged["R_expr"]

        total_score += merged["score"].sum()

    return total_score


def generate_cci_heatmap(
    adata,
    source_subclasses=None,
    target_subclasses=None,
    subclass_key="subclass",
    celltype_key=None,  
    L_gene=["SLC1A3", "GLS"],
    R_gene=["GRM7"],
    grid_size=400,
    spatial_key="spatial",
    library_key="chip",
    cmap="Reds"
):
    """
    Generate a heatmap of total colocalization interaction scores
    between source and target cell types or subclasses.

    Parameters
    ----------
    adata : AnnData
        Annotated data matrix with spatial and expression data.
    source_subclasses : list of str
        List of source subclasses (or cell types) to evaluate as ligand producers.
    target_subclasses : list of str
        List of target subclasses (or cell types) to evaluate as receptor producers.
    subclass_key : str, default "subclass"
        Column in `adata.obs` with subclass annotations.
    celltype_key : str or None, default None
        Column in `adata.obs` with finer cell type annotations.
        If None, subclass_key will be used as default.
    L_gene : list of str
        List of ligand gene names.
    R_gene : list of str
        List of receptor gene names.
    grid_size : int, default 400
        Grid bin size (in microns) used to group cells spatially.
    spatial_key : str, default "spatial"
        Key in `adata.obsm` for spatial coordinates.
    library_key : str, default "chip"
        Column in `adata.obs` identifying different tissue slices or chips.
    cmap : str, default "Reds"
        Colormap used for heatmap display.

    Returns
    -------
    heatmap_df : pd.DataFrame
        Heatmap matrix of colocalization interaction scores between each source-target pair.
    """
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from tqdm import tqdm
    import anndata as ad

    if celltype_key is not None:
        df = adata.obs[[subclass_key, celltype_key]]

        source_annots = df[df[subclass_key].isin(source_subclasses)][celltype_key].unique()
        target_annots = df[df[subclass_key].isin(target_subclasses)][celltype_key].unique()

        heatmap_df = pd.DataFrame(index=target_annots, columns=source_annots, dtype=float)

        for t_ann in tqdm(target_annots, desc="Target"):
            for s_ann in source_annots:
                score = compute_cci_score_sum(
                    adata=adata,
                    source_type=s_ann,
                    target_type=t_ann,
                    L_gene=L_gene,
                    R_gene=R_gene,
                    celltype_key=celltype_key,
                    spatial_key=spatial_key,
                    library_key=library_key,
                    grid_size=grid_size
                )
                heatmap_df.at[t_ann, s_ann] = score
    else:
        subclasses = adata.obs[subclass_key]
        source_set = sorted(set(source_subclasses))
        target_set = sorted(set(target_subclasses))

        heatmap_df = pd.DataFrame(index=target_set, columns=source_set, dtype=float)

        for t in tqdm(target_set, desc="Target"):
            for s in source_set:
                score = compute_cci_score_sum(
                    adata=adata,
                    source_type=s,
                    target_type=t,
                    L_gene=L_gene,
                    R_gene=R_gene,
                    celltype_key=subclass_key,  
                    spatial_key=spatial_key,
                    library_key=library_key,
                    grid_size=grid_size
                )
                heatmap_df.at[t, s] = score

    heatmap_df = heatmap_df.fillna(0)

    plt.figure(figsize=(6, 4))
    sns.heatmap(heatmap_df, cmap=cmap, annot=False, fmt=".1f")
    plt.title("CCI Score Sum by Source/Target")
    plt.xlabel("Source Cell Types")
    plt.ylabel("Target Cell Types")
    plt.tight_layout()
    plt.show()

    return heatmap_df

####wispra2.0
import numpy as np
import pandas as pd
import anndata as ad
from collections import defaultdict
from scipy.spatial import cKDTree
from tqdm import tqdm
import torch
from statsmodels.stats.multitest import multipletests

def find_cell_neighbors_label(adata, distance_threshold=50):
    coords = np.asarray(adata.obsm["spatial"])
    labels = np.asarray(adata.obs.index).astype(str)
    tree = cKDTree(coords)
    pairs = tree.query_pairs(r=distance_threshold, output_type="ndarray")
    neigh = defaultdict(list)
    for i, j in pairs:
        neigh[i].append(j)
        neigh[j].append(i)
    return neigh, labels

def preprocess_lr_db(lr_db, var_names, gene_upper=True):
    if gene_upper:
        var_set = set([g.upper() for g in var_names])
    else:
        var_set = set(var_names)

    valid_pairs = []
    for _, row in lr_db.iterrows():
        lig = str(row['ligand']).strip()
        rec = str(row['receptor']).strip()
        if gene_upper:
            lig = lig.upper()
            rec = rec.upper()
        if lig in var_set and rec in var_set:
            valid_pairs.append((lig, rec))
    return valid_pairs

def count_events_cpu_bidirectional(adata, lr_db, expr_thresh=0.1, distance_threshold=50):
    if hasattr(adata.X, "toarray"):
        expr = adata.X.toarray()
    else:
        expr = np.asarray(adata.X)
    n_cells, n_genes = expr.shape

    var_names = np.array(adata.var.index)
    valid_pairs = preprocess_lr_db(lr_db, var_names)
    if len(valid_pairs) == 0:
        print("No valid LR pairs.")
        return pd.DataFrame(columns=["niche","event","intensity","counts","direction"])

    lig_idx_list = np.array([np.where(var_names == lp[0])[0][0] for lp in valid_pairs])
    rec_idx_list = np.array([np.where(var_names == lp[1])[0][0] for lp in valid_pairs])
    lr_strings = [f"{lp[0]}-{lp[1]}" for lp in valid_pairs]

    annotations = adata.obs['annotation'].astype(str).values  
    neighbors, labels = find_cell_neighbors_label(adata, distance_threshold=distance_threshold)
    label_to_idx = {lab: i for i, lab in enumerate(labels)}

    all_niche, all_event, all_intensity, all_direction = [], [], [], []

    for center_lab in tqdm(labels, desc="Processing niches"):
        center_idx = label_to_idx[center_lab]
        neighbor_idx_list = neighbors.get(center_idx, [])
        if len(neighbor_idx_list) == 0:
            continue

        for k, (lig_idx, rec_idx) in enumerate(zip(lig_idx_list, rec_idx_list)):
            # ---- out: center -> neighbors ----
            lig_val = expr[center_idx, lig_idx]
            if lig_val > expr_thresh:
                rec_vals = expr[neighbor_idx_list, rec_idx]
                mask_pos = rec_vals > expr_thresh
                for ni, rec_val in zip(np.array(neighbor_idx_list)[mask_pos], rec_vals[mask_pos]):
                    intensity = lig_val * rec_val
                    all_niche.append(labels[center_idx])
                    all_event.append(f"{annotations[center_idx]}->{annotations[ni]}:{lr_strings[k]}")
                    all_intensity.append(intensity)
                    all_direction.append("out")

            # ---- in: neighbors -> center ----
            rec_val_center = expr[center_idx, rec_idx]
            if rec_val_center > expr_thresh:
                lig_vals = expr[neighbor_idx_list, lig_idx]
                mask_pos = lig_vals > expr_thresh
                for ni, lig_val in zip(np.array(neighbor_idx_list)[mask_pos], lig_vals[mask_pos]):
                    intensity = lig_val * rec_val_center
                    all_niche.append(labels[center_idx])
                    all_event.append(f"{annotations[ni]}->{annotations[center_idx]}:{lr_strings[k]}")
                    all_intensity.append(intensity)
                    all_direction.append("in")

    df_raw = pd.DataFrame({
        "niche": all_niche, 
        "event": all_event, 
        "intensity": all_intensity,
        "direction": all_direction
    })
    df = df_raw.groupby(["niche", "event", "direction"]).agg(
        intensity=("intensity", "mean"),
        counts=("intensity", "size")
    ).reset_index()

    df["prob"] = df["intensity"] * df["counts"]
    df['cellpairs'] = df['event'].str.split(':', n=1).str[0]
    df['interaction'] = df['event'].str.split(':', n=1).str[1]
    df['source'] = df['cellpairs'].str.split('->', n=1).str[0]
    df['target'] = df['cellpairs'].str.split('->', n=1).str[1]
    df['ligand'] = df['interaction'].str.split('-', n=1).str[0]
    df['receptor'] = df['interaction'].str.split('-', n=1).str[1]    
    return df

def listen_to_whispers(adata, lr_db, n_perm=1000, expr_thresh=0.1, distance_threshold=50, device='cuda'):
    df_obs = count_events_cpu_bidirectional(adata, lr_db, expr_thresh, distance_threshold)
    if df_obs.empty:
        print("No observed events found.")
        return pd.DataFrame()
    
    if hasattr(adata.X, "toarray"):
        expr = torch.tensor(adata.X.toarray(), dtype=torch.float32, device=device)
    else:
        expr = torch.tensor(adata.X, dtype=torch.float32, device=device)
        
    n_cells = expr.shape[0]
    var_names = np.array(adata.var.index)
    valid_pairs = preprocess_lr_db(lr_db, var_names)
    if not valid_pairs:
        print("No valid LR pairs found.")
        return pd.DataFrame()

    lig_idx_list = torch.tensor([np.where(var_names == lp[0])[0][0] for lp in valid_pairs], device=device, dtype=torch.long)
    rec_idx_list = torch.tensor([np.where(var_names == lp[1])[0][0] for lp in valid_pairs], device=device, dtype=torch.long)
    lr_strings = [f"{lp[0]}-{lp[1]}" for lp in valid_pairs]
    
    neighbors_cpu, labels = find_cell_neighbors_label(adata, distance_threshold=distance_threshold)
    
    adj_rows, adj_cols = [], []
    for i, neighbors in neighbors_cpu.items():
        for j in neighbors:
            adj_rows.append(i)
            adj_cols.append(j)
    
    adj_rows_tensor = torch.tensor(adj_rows, dtype=torch.long, device=device)
    adj_cols_tensor = torch.tensor(adj_cols, dtype=torch.long, device=device)
    adj_values = torch.ones(len(adj_rows), dtype=torch.bool, device=device)

    null_distributions = defaultdict(list)
    
    for _ in tqdm(range(n_perm), desc="Permutation test (GPU)"):
        shuffled_indices = torch.randperm(n_cells, device=device)
        perm_rows = shuffled_indices[adj_rows_tensor]
        perm_cols = shuffled_indices[adj_cols_tensor]
        perm_adj_indices = torch.stack([perm_rows, perm_cols], dim=0)
        perm_sparse_adj_matrix = torch.sparse_coo_tensor(
            perm_adj_indices, adj_values, (n_cells, n_cells), device=device
        )
        
        coo_indices = perm_sparse_adj_matrix.coalesce().indices()
        interacting_lig_indices = coo_indices[0]
        interacting_rec_indices = coo_indices[1]
        
        for k, (lig_idx, rec_idx) in enumerate(zip(lig_idx_list, rec_idx_list)):
            # ---- out: row=lig, col=rec ----
            perm_lig_vals = expr[interacting_lig_indices, lig_idx].squeeze()
            perm_rec_vals = expr[interacting_rec_indices, rec_idx].squeeze()
            intensities_out = perm_lig_vals * perm_rec_vals
            valid_out = intensities_out[(perm_lig_vals > expr_thresh) & (perm_rec_vals > expr_thresh)]
            if valid_out.numel() > 0:
                null_distributions[(lr_strings[k], "out")].append(valid_out.mean().item())

            # ---- in: row=rec, col=lig ----
            perm_lig_vals_in = expr[interacting_rec_indices, lig_idx].squeeze()
            perm_rec_vals_in = expr[interacting_lig_indices, rec_idx].squeeze()
            intensities_in = perm_lig_vals_in * perm_rec_vals_in
            valid_in = intensities_in[(perm_lig_vals_in > expr_thresh) & (perm_rec_vals_in > expr_thresh)]
            if valid_in.numel() > 0:
                null_distributions[(lr_strings[k], "in")].append(valid_in.mean().item())
            
    pvals = []
    for _, row in df_obs.iterrows():
        event_parts = row["event"].split(':')
        if len(event_parts) < 2:
            lr_pair_str = ""
        else:
            lr_pair_str = event_parts[1] 
        
        direction = row["direction"]
        null_vals = np.array(null_distributions.get((lr_pair_str, direction), []))
        
        if len(null_vals) == 0:
            p = 1.0
        else:
            p = (np.sum(null_vals >= row["intensity"]) + 1) / (len(null_vals) + 1)
        pvals.append(p)

    df_obs["pval"] = pvals
    if len(pvals) > 0:
        rejected, fdr_values, _, _ = multipletests(pvals, alpha=0.05, method='fdr_bh')
        df_obs["fdr"] = fdr_values
    else:
        df_obs["fdr"] = []

    return df_obs



def build_anndata(events_df, adata, obs_cols=None, layers_col=None, X_col="prob"):
    if events_df.empty:
        print("events_df empty -> return empty AnnData")
        return ad.AnnData()
    
    if X_col is None:
        raise ValueError("X_col cannot be None, must be one of: 'prob', 'counts', 'fdr', 'pval', 'interaction', 'cellpairs'")
    
    valid_cols = ['prob', 'counts', 'fdr', 'pval', 'interaction', 'cellpairs']
    if X_col not in valid_cols:
        raise ValueError(f"X_col must be one of {valid_cols}, got '{X_col}'")

    needed_cols = set([X_col])
    
    if layers_col is not None:
        if layers_col != X_col: 
            needed_cols.add(layers_col)
    
    # X
    if X_col == "counts":
        aggfunc_X = "sum"
    else:
        aggfunc_X = "mean"
    mat_X = events_df.pivot_table(index="niche", columns="event", values=X_col, aggfunc=aggfunc_X, fill_value=0)
    
    # layers
    layers = {}
    
    if layers_col is not None and layers_col != X_col:
        if layers_col == "counts":
            aggfunc_layer = "sum"
        else:
            aggfunc_layer = "mean"
        
        mat_layer = events_df.pivot_table(index="niche", columns="event", values=layers_col, aggfunc=aggfunc_layer, fill_value=0)
        layers[layers_col] = mat_layer.values
    
    # var
    var_df = pd.DataFrame(index=mat_X.columns)
    # obs
    obs_dict = {"niche_id": mat_X.index.values}
    if obs_cols:
        for c in obs_cols:
            if c in adata.obs.columns:
                obs_dict[c] = adata.obs.loc[mat_X.index, c].values
    obs_df = pd.DataFrame(obs_dict).set_index("niche_id")

    ad_niche = ad.AnnData(X=mat_X.values, obs=obs_df, var=var_df)

    for layer_name, layer_values in layers.items():
        ad_niche.layers[layer_name] = layer_values
    
    return ad_niche

def addcolumn(events_df, adata, obs_col=["x","y"]):
    """ 
    Add multiple columns to events_df DataFrame
    
    Parameters:
    events_df: DataFrame, containing columns such as event, prob, pval, fdr, etc.
    adata: AnnData object, used to obtain meta information
    obs_col: list, column names to add, default is ["x","y"]

    Returns:
    DataFrame: DataFrame with added columns
    """
    df_add = events_df.copy()
    # Extract x,y coordinates from spatial coordinates
    adata.obs["x"] = adata.obsm["spatial"][:, 0]
    adata.obs["y"] = adata.obsm["spatial"][:, 1]
    meta = adata.obs
    
    for col in obs_col:
        if col in meta.columns:
            df_add[col] = df_add["niche"].map(meta[col])
        else:
            print(f"Warning: Column '{col}' not found in adata.obs")
    
    return df_add

import numpy as np
import pandas as pd
import torch
from tqdm import tqdm
from collections import defaultdict
from scipy.spatial import cKDTree
from statsmodels.stats.multitest import multipletests
import anndata as ad

def find_cell_neighbors_label(adata=None, distance_threshold=50, coords=None):
    """
    use:
    1. find_cell_neighbors_label(adata, distance_threshold)
        -> from adata.obsm['spatial'] get coords
    2. find_cell_neighbors_label(None, distance_threshold, coords=array)
        -> use coords to bulid KDTree

    return: neigh (defaultdict), labels (np.array), all_pairs (np.array, i, j), all_dists (np.array)
    """
    if coords is None:
        if adata is None:
            raise ValueError("please input adata or coords.")
        coords = np.asarray(adata.obsm["spatial"])
    else:
        coords = np.asarray(coords)

    # 获取标签
    if adata is not None:
        labels = np.asarray(adata.obs.index).astype(str)
    else:
        labels = np.arange(coords.shape[0]).astype(str)

    # --- KDTree 查询邻居 (获取所有对及其距离) ---
    tree = cKDTree(coords)
    
    # 使用 query_pairs 快速获取所有对 (i < j)
    pairs = tree.query_pairs(r=distance_threshold, output_type="ndarray")
    if len(pairs) == 0:
        return defaultdict(list), labels, np.empty((0, 2), dtype=int), np.empty(0)

    # 距离计算 (使用 L2 范数)
    coords_i = coords[pairs[:, 0]]
    coords_j = coords[pairs[:, 1]]
    dists = np.linalg.norm(coords_i - coords_j, axis=1)

    # 构建邻居表 (用于旧代码兼容)
    neigh = defaultdict(list)
    for i, j in pairs:
        neigh[i].append(j)
        neigh[j].append(i)
        
    return neigh, labels, pairs, dists # 返回 i < j 的对及其距离


def preprocess_lr_db(lr_db, var_names, gene_upper=False):
    var_map = {}
    var_set = set()

    if gene_upper:
        for g in var_names:
            var_map[g.upper()] = g
            var_set.add(g.upper())
    else:
        for g in var_names:
            title_g = g[0].upper() + g[1:].lower() if len(g) > 0 else g
            var_map[title_g] = g
            var_set.add(title_g)

    simple_pairs_list = []
    complex_pairs_list = []
    complex_lig_components_list = []
    complex_rec_components_list = []

    def get_components(gene_str):
        components = [c.strip() for c in gene_str.split('_')]
        found_genes = []
        for c in components:
            if len(c) > 0:
                c_title = c[0].upper() + c[1:].lower()
            else:
                c_title = c
            if c_title in var_set:
                found_genes.append(var_map[c_title])
            else:
                return None
        return found_genes if len(found_genes) > 0 else None

    for _, row in lr_db.iterrows():
        lig = str(row['ligand']).strip()
        rec = str(row['receptor']).strip()
        lig_comps = get_components(lig)
        rec_comps = get_components(rec)
        if lig_comps and rec_comps:
            if len(lig_comps) == 1 and len(rec_comps) == 1:
                simple_pairs_list.append((lig_comps[0], rec_comps[0]))
            else:
                complex_pairs_list.append((lig, rec))
                complex_lig_components_list.append(lig_comps)
                complex_rec_components_list.append(rec_comps)

    return simple_pairs_list, complex_pairs_list, complex_lig_components_list, complex_rec_components_list

def compute_distance_weight(distances, scale=1.0, epsilon=1e-6, device='cpu', dtype=torch.float16):
    """
    计算逆距离权重 (Weight = 1 / (scale + distance))。
    对距离进行张量化并在 GPU 上处理。
    """
    dist_t = torch.tensor(distances, dtype=dtype, device=device)
    # 使用 1 / (scale + d) 避免除以 0，并对距离进行平滑。
    weights = 1.0 / (scale + dist_t)
    return weights

def calculate_complex_expression_gpu_optimized(expr, cell_indices, comp_gene_indices_tensor):
    if comp_gene_indices_tensor.numel() == 0:
        return torch.ones(cell_indices.shape[0], dtype=expr.dtype, device=expr.device)

    # 使用索引进行查找
    complex_components_expr = expr[cell_indices.unsqueeze(1), comp_gene_indices_tensor.unsqueeze(0)]
    return torch.prod(complex_components_expr, dim=1)


def count_events_gpu_bidirectional(adata, lr_db, expr_thresh=0.1, distance_threshold=50, device='cuda', dist_scale=1.0,celltype_key="celltype"):
    """
    使用 GPU 张量向量化计算所有观察到的 LR 强度，并优化了数据累积。
    """
    if 'torch' not in globals():
        raise ImportError("PyTorch must be imported.")
    if device == 'cuda' and not torch.cuda.is_available():
        print("Warning: CUDA requested but not available, falling back to CPU for initial count.")
        device = 'cpu'
        
    # --- 1. 数据准备 ---
    dtype = torch.float16 if device == 'cuda' else torch.float32

    if hasattr(adata.X, "toarray"):
        expr = torch.tensor(adata.X.toarray(), dtype=dtype, device=device)
    else:
        expr = torch.tensor(adata.X, dtype=dtype, device=device)
        
    thresh_tensor = torch.tensor(expr_thresh, dtype=expr.dtype, device=device) 
    n_cells = expr.shape[0]
    var_names = np.array(adata.var.index)
    gene_name_to_idx = {name: i for i, name in enumerate(var_names)}

    # --- 2. LR 对索引准备 ---
    simple_pairs, complex_pairs_str, complex_lig_components_list, complex_rec_components_list = \
        preprocess_lr_db(lr_db, var_names) 

    simple_lig_idx_list = torch.tensor([gene_name_to_idx[lp[0]] for lp in simple_pairs], device=device, dtype=torch.long)
    simple_rec_idx_list = torch.tensor([gene_name_to_idx[lp[1]] for lp in simple_pairs], device=device, dtype=torch.long)
    simple_lr_strings = [f"{lp[0]}-{lp[1]}" for lp in simple_pairs]
    
    complex_lig_idx_lists = [torch.tensor([gene_name_to_idx[g] for g in comps], device=device, dtype=torch.long) for comps in complex_lig_components_list]
    complex_rec_idx_lists = [torch.tensor([gene_name_to_idx[g] for g in comps], device=device, dtype=torch.long) for comps in complex_rec_components_list]
    complex_lr_strings = [f"{lp[0]}-{lp[1]}" for lp in complex_pairs_str]
    
    all_lr_strings = simple_lr_strings + complex_lr_strings
    dir_to_idx = {"out": 0, "in": 1}

    # --- 3. 邻居、距离和交互对准备 ---
    _, labels, pairs_orig, dists_orig = find_cell_neighbors_label(adata, distance_threshold=distance_threshold)
    
    if len(pairs_orig) == 0:
        return pd.DataFrame()
        
    # 展开为双向交互对
    adj_rows, adj_cols, dists = [], [], []
    for i, j, d in zip(pairs_orig[:, 0], pairs_orig[:, 1], dists_orig):
        adj_rows.extend([i, j])
        adj_cols.extend([j, i])
        dists.extend([d, d])    
    interacting_lig_indices = torch.tensor(adj_rows, dtype=torch.long, device=device)
    interacting_rec_indices = torch.tensor(adj_cols, dtype=torch.long, device=device)
    num_interactions = interacting_lig_indices.shape[0]

    interacting_weights = compute_distance_weight(
        dists, scale=dist_scale, device=device, dtype=dtype
    )
    annotations = adata.obs[celltype_key].astype(str).values
    # 🌟 优化：用于最终聚合的 GPU 列表 (存储张量)
    final_lig_indices_gpu, final_rec_indices_gpu = [], []
    final_intensity_gpu, final_lr_index_gpu, final_direction_index_gpu = [], [], []

    BATCH_SIZE = 20000000 
    # --- 4. 核心 GPU 计算和过滤 (优化：在 GPU 上累积结果) ---
    for start_idx in tqdm(range(0, num_interactions, BATCH_SIZE), desc="Observed Events Count (with distance weight)"):
        end_idx = min(start_idx + BATCH_SIZE, num_interactions)
        batch_lig_indices = interacting_lig_indices[start_idx:end_idx] # 细胞 A 索引
        batch_rec_indices = interacting_rec_indices[start_idx:end_idx] # 细胞 B 索引
        batch_weights = interacting_weights[start_idx:end_idx] # 距离权重

        # --- 4.1 简单对计算 ---
        for lr_idx, (lig_idx, rec_idx) in enumerate(zip(simple_lig_idx_list, simple_rec_idx_list)):
            lr_index_t = torch.tensor(lr_idx, device=device, dtype=torch.long)
            
            # a) out: L(A) -> R(B)
            perm_lig_vals = expr[batch_lig_indices, lig_idx].squeeze() 
            perm_rec_vals = expr[batch_rec_indices, rec_idx].squeeze() 
            mask_out = (perm_lig_vals > thresh_tensor) & (perm_rec_vals > thresh_tensor)
            if mask_out.any():
                raw_intensities_out = perm_lig_vals[mask_out] * perm_rec_vals[mask_out]
                weighted_intensities_out = raw_intensities_out * batch_weights[mask_out]
                valid_indices = torch.where(mask_out)[0]
                # 累积结果 (GPU 张量)
                final_lig_indices_gpu.append(batch_lig_indices[valid_indices])
                final_rec_indices_gpu.append(batch_rec_indices[valid_indices])
                final_intensity_gpu.append(torch.log1p(weighted_intensities_out))
                final_lr_index_gpu.append(lr_index_t.repeat(len(valid_indices)))
                final_direction_index_gpu.append(torch.full((len(valid_indices),), dir_to_idx["out"], device=device, dtype=torch.long))
                
            # b) in: L(B) -> R(A)
            perm_lig_vals_in = expr[batch_rec_indices, lig_idx].squeeze()
            perm_rec_vals_in = expr[batch_lig_indices, rec_idx].squeeze()
            mask_in = (perm_lig_vals_in > thresh_tensor) & (perm_rec_vals_in > thresh_tensor)
            if mask_in.any():
                raw_intensities_in = perm_lig_vals_in[mask_in] * perm_rec_vals_in[mask_in]
                weighted_intensities_in = raw_intensities_in * batch_weights[mask_in]
                valid_indices = torch.where(mask_in)[0]
                # 累积结果 (GPU 张量)
                final_lig_indices_gpu.append(batch_rec_indices[valid_indices])
                final_rec_indices_gpu.append(batch_lig_indices[valid_indices])
                final_intensity_gpu.append(torch.log1p(weighted_intensities_in))
                final_lr_index_gpu.append(lr_index_t.repeat(len(valid_indices)))
                final_direction_index_gpu.append(torch.full((len(valid_indices),), dir_to_idx["in"], device=device, dtype=torch.long))


        # --- 4.2 复杂对计算 ---
        lr_idx_base = len(simple_lr_strings)
        for lr_i, (lig_idxs_t, rec_idxs_t) in enumerate(zip(complex_lig_idx_lists, complex_rec_idx_lists)):
            lr_idx = lr_idx_base + lr_i
            lr_index_t = torch.tensor(lr_idx, device=device, dtype=torch.long)
            # a) out: L(A) -> R(B)
            perm_lig_vals_out = calculate_complex_expression_gpu_optimized(expr, batch_lig_indices, lig_idxs_t)
            perm_rec_vals_out = calculate_complex_expression_gpu_optimized(expr, batch_rec_indices, rec_idxs_t)
            mask_out = (perm_lig_vals_out > thresh_tensor) & (perm_rec_vals_out > thresh_tensor)
            if mask_out.any():
                raw_intensities_out = perm_lig_vals_out[mask_out] * perm_rec_vals_out[mask_out]
                weighted_intensities_out = raw_intensities_out * batch_weights[mask_out]
                valid_indices = torch.where(mask_out)[0]
                # 累积结果 (GPU 张量)
                final_lig_indices_gpu.append(batch_lig_indices[valid_indices])
                final_rec_indices_gpu.append(batch_rec_indices[valid_indices])
                final_intensity_gpu.append(torch.log1p(weighted_intensities_out)) 
                final_lr_index_gpu.append(lr_index_t.repeat(len(valid_indices)))
                final_direction_index_gpu.append(torch.full((len(valid_indices),), dir_to_idx["out"], device=device, dtype=torch.long))
            # b) in: L(B) -> R(A)
            perm_lig_vals_in = calculate_complex_expression_gpu_optimized(expr, batch_rec_indices, lig_idxs_t)
            perm_rec_vals_in = calculate_complex_expression_gpu_optimized(expr, batch_lig_indices, rec_idxs_t)
            mask_in = (perm_lig_vals_in > thresh_tensor) & (perm_rec_vals_in > thresh_tensor)
            
            if mask_in.any():
                raw_intensities_in = perm_lig_vals_in[mask_in] * perm_rec_vals_in[mask_in]
                weighted_intensities_in = raw_intensities_in * batch_weights[mask_in]
                valid_indices = torch.where(mask_in)[0]
                # 累积结果 (GPU 张量)
                final_lig_indices_gpu.append(batch_rec_indices[valid_indices])
                final_rec_indices_gpu.append(batch_lig_indices[valid_indices])
                final_intensity_gpu.append(torch.log1p(weighted_intensities_in)) 
                final_lr_index_gpu.append(lr_index_t.repeat(len(valid_indices)))
                final_direction_index_gpu.append(torch.full((len(valid_indices),), dir_to_idx["in"], device=device, dtype=torch.long))
                
            # 强制清理 GPU 缓存
            if device == 'cuda':
                torch.cuda.synchronize()
                torch.cuda.empty_cache()

    # --- 5. Pandas 聚合 (CPU) 🌟 关键优化：一次性合并和转移 ---
    if not final_intensity_gpu:
        print("No observed events found after GPU filtering.")
        return pd.DataFrame()

    # 1. 在 GPU 上合并所有张量
    all_lig_idx_t = torch.cat(final_lig_indices_gpu)
    all_rec_idx_t = torch.cat(final_rec_indices_gpu)
    all_intensity_t = torch.cat(final_intensity_gpu)
    all_lr_index_t = torch.cat(final_lr_index_gpu)
    all_direction_index_t = torch.cat(final_direction_index_gpu)
    
    # 2. 一次性转移到 CPU NumPy 数组和 Pandas DataFrame
    df_raw = pd.DataFrame({
        "lig_idx": all_lig_idx_t.cpu().numpy(),
        "rec_idx": all_rec_idx_t.cpu().numpy(),
        "intensity": all_intensity_t.cpu().numpy(),
    })
    
    # 3. 映射索引回字符串
    df_raw['interaction'] = np.array(all_lr_strings)[all_lr_index_t.cpu().numpy()]
    df_raw['direction'] = np.array(list(dir_to_idx.keys()))[all_direction_index_t.cpu().numpy()]

    # 4. 使用细胞注释创建 "event" 和 "niche" 标签
    labels_map = {i: labels[i] for i in range(n_cells)}
    annotations_map = {i: annotations[i] for i in range(n_cells)}

    df_raw['source_anno'] = df_raw['lig_idx'].map(annotations_map)
    df_raw['target_anno'] = df_raw['rec_idx'].map(annotations_map)

    is_out = df_raw['direction'] == 'out'
    df_raw['niche_idx'] = np.where(is_out, df_raw['lig_idx'], df_raw['rec_idx'])
    df_raw['niche'] = df_raw['niche_idx'].map(labels_map)
    df_raw['event'] = df_raw['source_anno'] + '->' + df_raw['target_anno'] + ':' + df_raw['interaction']

    # 聚合到 niche-event-direction 级别
    df = df_raw.groupby(["niche", "event", "direction"]).agg(
        intensity=("intensity", "mean"),
        counts=("intensity", "size")
    ).reset_index()

    df["raw_prob"] = df["intensity"] * df["counts"]
    df['cellpairs'] = df['event'].str.split(':', n=1).str[0]
    df['interaction'] = df['event'].str.split(':', n=1).str[1]
    df['source'] = df['cellpairs'].str.split('->', n=1).str[0]
    df['target'] = df['cellpairs'].str.split('->', n=1).str[1]
    df['ligand'] = df['interaction'].str.split('-', n=1).str[0]
    df['receptor'] = df['interaction'].str.split('-', n=1).str[1]
    return df
def listen_to_whispers_spatial_perm(
    adata, lr_db, n_perm=100, expr_thresh=0.1, distance_threshold=50,
    device='cuda', events_df=None, obs_col=["x","y"], dist_scale=1.0
):
    """
    使用空间坐标打乱的 permutation 测试。
    Null Model 统计量和 Denoised Prob 计算逻辑已修正为统计一致。
    """
    if 'torch' not in globals():
        raise ImportError("需要先 import torch")

    if device == 'cuda' and not torch.cuda.is_available():
        print("⚠️ CUDA 不可用，改用 CPU。")
        device = 'cpu'
        
    # Step 1. 计算原始观测事件（Observed events）
    if events_df is None:
        print("⚙️ Computing observed events (use GPU if available)...")
        # 调用优化后的函数
        df_obs = count_events_gpu_bidirectional(adata, lr_db, expr_thresh, distance_threshold, device=device, dist_scale=dist_scale)
    else:
        df_obs = events_df.copy()

    if df_obs.empty:
        print("❌ No observed events found.")
        return df_obs

    # 为后续合并准备观测值的平均强度和查找键
    df_obs['lookup_key'] = list(zip(df_obs['interaction'], df_obs['direction']))
    #df_obs['obs_mean_intensity'] = df_obs['intensity']
    df_obs['intensity']
    # Step 2. 预处理表达矩阵和 LR 对索引 (保持不变)
    dtype = torch.float16 if device == 'cuda' else torch.float32
    expr = torch.tensor(
        adata.X.toarray() if hasattr(adata.X, "toarray") else adata.X,
        dtype=dtype, device=device
    )
    var_names = np.array(adata.var.index)
    gene_idx = {g: i for i, g in enumerate(var_names)}
    thresh_tensor = torch.tensor(expr_thresh, dtype=dtype, device=device)

    simple_pairs, complex_pairs_str, complex_lig_components_list, complex_rec_components_list = \
        preprocess_lr_db(lr_db, var_names)
    
    simple_lr_list = [
        (torch.tensor(gene_idx[l], device=device, dtype=torch.long), 
         torch.tensor(gene_idx[r], device=device, dtype=torch.long), 
         f"{l}-{r}") for l, r in simple_pairs
    ]
    complex_lr_list = [
        (torch.tensor([gene_idx[g] for g in ligs], device=device, dtype=torch.long), 
         torch.tensor([gene_idx[g] for g in recs], device=device, dtype=torch.long), 
         f"{lig}-{rec}")
        for (lig, rec), ligs, recs in zip(complex_pairs_str, complex_lig_components_list, complex_rec_components_list)
    ]

    # 辅助函数：GPU上计算复合物表达
    def calc_complex_expr(expr, cell_idx_t, comp_gene_idx_t):
        if comp_gene_idx_t.numel() == 0:
            return torch.ones(cell_idx_t.shape[0], device=device, dtype=dtype)
        complex_components_expr = expr[cell_idx_t.unsqueeze(1), comp_gene_idx_t.unsqueeze(0)]
        return torch.prod(complex_components_expr, dim=1)

    # Step 3. 获取真实空间坐标
    coords_orig = np.asarray(adata.obsm["spatial"])

    # 存储所有置换结果 (lr_str, direction, perm_mean_intensity)
    null_results_list = [] 

    print("🔁 Running spatial-coordinate permutation test (with distance weight)...")
    for perm_i in tqdm(range(n_perm), desc="Spatial permutations"):
        # Step 3.1 随机打乱空间坐标
        shuffled_indices = np.random.permutation(len(coords_orig))
        shuffled_coords = coords_orig[shuffled_indices]
        
        # Step 3.2 基于打乱坐标重建邻居 (此步是瓶颈，但对于空间置换是必须的)
        tree = cKDTree(shuffled_coords)
        pairs_shuf = np.array(list(tree.query_pairs(r=distance_threshold)))
        if len(pairs_shuf) == 0:
            continue
        
        coords_i = shuffled_coords[pairs_shuf[:, 0]]
        coords_j = shuffled_coords[pairs_shuf[:, 1]]
        dists_shuf = np.linalg.norm(coords_i - coords_j, axis=1)

        row_idx, col_idx, dists = [], [], []
        for i, j, d in zip(pairs_shuf[:, 0], pairs_shuf[:, 1], dists_shuf):
            row_idx.extend([i, j])
            col_idx.extend([j, i])
            dists.extend([d, d])
            
        # 实际参与 LR 评分的细胞对 (原始细胞 ID):
        row_t = torch.tensor(shuffled_indices[row_idx], device=device, dtype=torch.long)
        col_t = torch.tensor(shuffled_indices[col_idx], device=device, dtype=torch.long)
        weights_t = compute_distance_weight(dists, scale=dist_scale, device=device, dtype=dtype) 

        # Step 3.3 批次处理（防OOM）
        BATCH_SIZE = 20000000
        # 临时聚合：(lr_str, direction) -> (sum_log1p_weighted_intensity, count)
        temp_accum = defaultdict(lambda: {"sum_int": 0.0, "count": 0}) 

        for start in range(0, len(row_t), BATCH_SIZE):
            end = min(start + BATCH_SIZE, len(row_t))
            lig_t = row_t[start:end] # L 细胞的原始 ID 
            rec_t = col_t[start:end] # R 细胞的原始 ID
            batch_weights = weights_t[start:end]

            # --- 简单对 ---
            for lig_idx_t, rec_idx_t, lr_str in simple_lr_list:
                # out: L(lig_t) -> R(rec_t)
                lig_val_out = expr[lig_t, lig_idx_t]
                rec_val_out = expr[rec_t, rec_idx_t]
                mask_out = (lig_val_out > thresh_tensor) & (rec_val_out > thresh_tensor)
                if mask_out.any():
                    raw_int_out = lig_val_out[mask_out] * rec_val_out[mask_out]
                    weighted_log_int_out = torch.log1p(raw_int_out * batch_weights[mask_out])
                    temp_accum[(lr_str, "out")]["sum_int"] += weighted_log_int_out.sum().item()
                    temp_accum[(lr_str, "out")]["count"] += mask_out.sum().item()
                    
                # in: L(rec_t) -> R(lig_t)
                lig_val_in = expr[rec_t, lig_idx_t]
                rec_val_in = expr[lig_t, rec_idx_t]
                mask_in = (lig_val_in > thresh_tensor) & (rec_val_in > thresh_tensor)
                if mask_in.any():
                    raw_int_in = lig_val_in[mask_in] * rec_val_in[mask_in]
                    weighted_log_int_in = torch.log1p(raw_int_in * batch_weights[mask_in])
                    temp_accum[(lr_str, "in")]["sum_int"] += weighted_log_int_in.sum().item()
                    temp_accum[(lr_str, "in")]["count"] += mask_in.sum().item()

            # --- 复杂对 ---
            for lig_tens, rec_tens, lr_str in complex_lr_list:
                # out: L(lig_t) -> R(rec_t)
                lig_val_out = calc_complex_expr(expr, lig_t, lig_tens)
                rec_val_out = calc_complex_expr(expr, rec_t, rec_tens)
                mask_out = (lig_val_out > thresh_tensor) & (rec_val_out > thresh_tensor)
                if mask_out.any():
                    raw_int_out = lig_val_out[mask_out] * rec_val_out[mask_out]
                    weighted_log_int_out = torch.log1p(raw_int_out * batch_weights[mask_out])
                    temp_accum[(lr_str, "out")]["sum_int"] += weighted_log_int_out.sum().item()
                    temp_accum[(lr_str, "out")]["count"] += mask_out.sum().item()

                # in: L(rec_t) -> R(lig_t)
                lig_val_in = calc_complex_expr(expr, rec_t, lig_tens)
                rec_val_in = calc_complex_expr(expr, lig_t, rec_tens)
                mask_in = (lig_val_in > thresh_tensor) & (rec_val_in > thresh_tensor)
                if mask_in.any():
                    raw_int_in = lig_val_in[mask_in] * rec_val_in[mask_in]
                    weighted_log_int_in = torch.log1p(raw_int_in * batch_weights[mask_in])
                    temp_accum[(lr_str, "in")]["sum_int"] += weighted_log_int_in.sum().item()
                    temp_accum[(lr_str, "in")]["count"] += mask_in.sum().item()

            # 强制清理 GPU 缓存
            if device == 'cuda':
                torch.cuda.synchronize()
                torch.cuda.empty_cache()

        # Step 3.4 保存本轮结果 (平均 log(1 + 加权强度))
        for (lr_str, direction), val in temp_accum.items():
            if val["count"] > 0:
                mean_log_int = val["sum_int"] / val["count"]
                null_results_list.append((lr_str, direction, mean_log_int))

    # Step 4. 统计空模型分布 (Null Distribution)
    print("📊 Aggregating null distributions...")
    if not null_results_list:
        print("❌ No events found in permutation tests. Cannot calculate p-values.")
        # ... (处理空结果的逻辑) ...
        df_obs["pval"] = 1.0
        df_obs["fdr"] = 1.0
        df_obs["denoised_prob"] = 0.0
        df_obs.rename(columns={'zscore': 'zscore_prob'}, inplace=True) # 保持原列名
        df_obs = df_obs.drop(columns=['lookup_key', 'intensity'])
        df_obs = addcolumn(df_obs, adata, lr_db, obs_col) # 假设 addcolumn 存在
        return df_obs

    df_null = pd.DataFrame(null_results_list, columns=['interaction', 'direction', 'perm_mean_intensity'])
    df_null['lookup_key'] = list(zip(df_null['interaction'], df_null['direction']))
    
    null_dists = defaultdict(list)
    for key, group in df_null.groupby('lookup_key'):
        null_dists[key] = group['perm_mean_intensity'].values.tolist()

    # Step 5. 计算 P 值、FDR 和 zscore (基于平均强度)
    print("📊 Computing p-values, FDR, and Z-scores...")
    pvals = []
    
    for _, row in df_obs.iterrows():
        null_vals = np.array(null_dists.get(row['lookup_key'], []))
        if len(null_vals) < 5: 
            pvals.append(1.0)
        else:
            pvals.append((np.sum(null_vals >= row['intensity']) + 1) / (len(null_vals) + 1))
    
    df_obs["pval"] = pvals
    df_obs["fdr"] = multipletests(df_obs["pval"], method='fdr_bh')[1]

    # Z-score normalization
    stats_dict = {}
    for key, vals in null_dists.items():
        vals = np.array(vals, dtype=float)
        if len(vals) > 5:
            mu = vals.mean()
            sigma = vals.std(ddof=0)
            stats_dict[key] = (mu, max(sigma, 1e-6))
        else:
            stats_dict[key] = (np.nan, np.nan) 

    df_stats = pd.DataFrame.from_dict(stats_dict, orient='index', columns=['mu', 'sigma'])
    df_stats.index.name = 'lookup_key'
    df_stats.reset_index(inplace=True)
    df_obs = df_obs.merge(df_stats, on='lookup_key', how='left')
    
    # 🌟 Z-score 基于平均强度 (统计一致)
    df_obs["zscore_prob"] = (df_obs["intensity"] - df_obs["mu"]) / (df_obs["sigma"] + 1e-6)

    # 🌟 Denoised Prob 基于总强度差异 (统计一致)
    # raw_prob = intensity * counts = 观测总强度
    df_obs["denoised_prob"] = (df_obs["raw_prob"] - df_obs["mu"] * df_obs["counts"]).clip(lower=0) * (1 - df_obs["pval"])
    #df_obs.loc[df_obs["denoised_prob"] < 0, "denoised_prob"] = 0 # clip(lower=0) 已经确保了非负

    # 最终清理
    df_obs = df_obs.drop(columns=['lookup_key', 'mu', 'sigma'])
    # df_obs.rename(columns={'zscore': 'zscore_prob'}, inplace=True) # Z-score 改名已移除
    
    print("Spatial permutation completed.")
    # 假设 addcolumn 函数存在于您的环境中
    print("Adding columns from .obs and lr_db...")     
    df_obs = addcolumn(df_obs, adata, lr_db, obs_col)
    print("Done!")
    return df_obs

def addcolumn(events_df, adata, lr_db=None, obs_col=["x","y"]):
    """ 
    Add multiple columns to events_df DataFrame, including spatial coordinates 
    and optional LR database information (pathway, type).
    """
    df_add = events_df.copy()
    
    # 1. 添加空间坐标 (基于 Niche/中心细胞)
    if "spatial" in adata.obsm:
        adata.obs["x"] = adata.obsm["spatial"][:, 0]
        adata.obs["y"] = adata.obsm["spatial"][:, 1]
        meta = adata.obs
        
        for col in obs_col:
            if col in meta.columns:
                # 使用 'niche' (即中心细胞标签) 来映射空间坐标
                df_add[col] = df_add["niche"].map(meta[col])
            else:
                print(f"Warning: Column '{col}' not found in adata.obs")
    else:
        print("Warning: adata.obsm['spatial'] not found. Skipping coordinate mapping.")


    # 2. 添加 LR 数据库信息 (pathway, type)
    if lr_db is not None:
        # 创建用于合并的键，格式为 'ligand-receptor'
        lr_db_map = lr_db.copy()
        
        # 确保列名是小写且无空格，以便匹配
        lr_db_map.columns = [c.lower().strip() for c in lr_db_map.columns]
        
        # 尝试使用 'from' 和 'to' 作为配体和受体
        # 假设 lr_db 包含 'from', 'to', 'pathway' (或 'pathway_name'), 'type' (或 'interaction_type')
        if 'from' in lr_db_map.columns and 'to' in lr_db_map.columns:
            lr_db_map['interaction'] = lr_db_map['from'].astype(str) + '-' + lr_db_map['to'].astype(str)
        else:
             # 如果没有 from/to，则尝试使用 ligand/receptor (与 preprocess_lr_db 逻辑一致)
             if 'ligand' in lr_db_map.columns and 'receptor' in lr_db_map.columns:
                 lr_db_map['interaction'] = lr_db_map['ligand'].astype(str) + '-' + lr_db_map['receptor'].astype(str)
             else:
                 print("Warning: Could not find 'from'/'to' or 'ligand'/'receptor' columns in lr_db for merge key.")
                 return df_add
                 
        # 提取需要添加的列
        cols_to_add = {}
        if 'pathway' in lr_db_map.columns:
            cols_to_add['pathway'] = 'pathway'
        elif 'pathway_name' in lr_db_map.columns:
            cols_to_add['pathway'] = 'pathway_name'
            
        if 'type' in lr_db_map.columns:
            cols_to_add['type'] = 'type'
        elif 'interaction_type' in lr_db_map.columns:
            cols_to_add['type'] = 'interaction_type'

        if not cols_to_add:
            print("Warning: Could not find 'pathway' or 'type' columns in lr_db.")
            return df_add
            
        # 准备合并的子集 DataFrame
        db_subset = lr_db_map[['interaction'] + list(cols_to_add.values())].drop_duplicates()
        
        # 使用 df_add['interaction'] (例如 CXCL12-CXCR4) 进行左合并
        df_add = pd.merge(
            df_add,
            db_subset,
            on='interaction',
            how='left'
        ).rename(columns={v: k for k, v in cols_to_add.items()})
    
    return df_add

def build_anndata(events_df, adata, var_names="event", obs_cols=None, layers_col=None, X_col="prob"):
    if events_df.empty:
        print("events_df empty -> return empty AnnData")
        return ad.AnnData()
    
    if X_col is None:
        raise ValueError("X_col cannot be None, must be one of events_df's colname")
    
    #valid_cols = ['prob', 'counts', 'fdr', 'pval', 'interaction', 'cellpairs','denoised_prob',"raw_prob", "zscore_prob"]
    # 修正 'prob' 为 'raw_prob' 或 'denoised_prob'，这里假设 'prob' 指 'denoised_prob' 或直接使用 'raw_prob'
    # if X_col == "prob":
    #     X_col = "denoised_prob" # 默认使用去噪后的概率
        
    # if X_col not in valid_cols:
    #     raise ValueError(f"X_col must be one of {valid_cols}, got '{X_col}'")

    needed_cols = set([X_col])
    
    if layers_col is not None:
        if layers_col != X_col: 
            needed_cols.add(layers_col)
    
    # 获取所有细胞和所有事件类型
    all_cells = adata.obs_names 
    all_events = events_df[var_names].unique() 
    
    # X矩阵 - 先构建有数据的部分
    if X_col in ["counts"]:
        aggfunc_X = "sum"
    else:
        aggfunc_X = "mean"
    
    mat_X_with_data = events_df.pivot_table(
        index="niche", 
        columns=var_names, 
        values=X_col, 
        aggfunc=aggfunc_X, 
        fill_value=0
    )
    
    # 创建完整的矩阵 - 使用reindex快速补全
    mat_X_full = mat_X_with_data.reindex(index=all_cells, columns=all_events, fill_value=0)
    
    # 对于pval/fdr等统计量，将填充值改为1
    if X_col in ['pval', 'fdr']:
        # 找到需要填充为1的位置（原来填充为0的位置）
        # 这里需要注意，reindex 已经将没有 niche 的细胞填充为 0，这对于 pval/fdr 是错误的。
        # 正确的做法是只对那些存在 niche 但在该 event 上没有数据的格子进行处理。
        # 简单处理：将所有缺失值（0）都改为 1，这是保守的。
        mat_X_full.replace(0, 1, inplace=True)
    # layers矩阵
    layers = {}
    
    if layers_col is not None and layers_col != X_col:
        if layers_col in ["counts"]:
            aggfunc_layer = "sum"
        else:
            aggfunc_layer = "mean"
        
        mat_layer_with_data = events_df.pivot_table(
            index="niche", 
            columns=var_names, 
            values=layers_col, 
            aggfunc=aggfunc_layer, 
            fill_value=0
        )
        # 创建完整的layer矩阵
        mat_layer_full = mat_layer_with_data.reindex(index=all_cells, columns=all_events, fill_value=0)
        
        # 对于pval/fdr等统计量，将填充值改为1
        if layers_col in ['pval', 'fdr']:
            mat_layer_full.replace(0, 1, inplace=True)
        
        layers[layers_col] = mat_layer_full.values
    # var
    var_map = events_df[[var_names, 'interaction']].drop_duplicates(subset=[var_names])#, 'source', 'target', 'ligand', 'receptor', 'pathway', 'type'
    var_map = var_map.set_index(var_names)
    var_df = pd.DataFrame(index=mat_X_full.columns)
    var_df = var_df.join(var_map, on=var_names)

    # obs
    obs_dict = {"niche_id": mat_X_full.index.values}
    if obs_cols:
        for c in obs_cols:
            if c in adata.obs.columns:
                obs_dict[c] = adata.obs.loc[mat_X_full.index, c].values
    
    obs_df = adata.obs.loc[mat_X_full.index].copy()
    
    ad_niche = ad.AnnData(X=mat_X_full.values, obs=obs_df, var=var_df)

    for layer_name, layer_values in layers.items():
        ad_niche.layers[layer_name] = layer_values
    
    print(f"构建完成: {ad_niche.shape[0]}个细胞 × {ad_niche.shape[1]}个事件")
    # print(f"有互作事件的细胞: {len(mat_X_with_data)}个")
    # print(f"无互作事件的细胞: {len(all_cells) - len(mat_X_full[mat_X_full.sum(axis=1) == 0])}个") 
    
    return ad_niche