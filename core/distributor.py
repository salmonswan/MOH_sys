import random
import pandas as pd


def distribute(interns_df: pd.DataFrame, facilities_df: pd.DataFrame,
               seed: int = 42, locked: pd.DataFrame | None = None) -> tuple[pd.DataFrame, list[str]]:
    """
    Assign interns to facilities based on qualification and capacity.

    Args:
        interns_df: DataFrame with intern data including 'Qualification'.
        facilities_df: Unpivoted DataFrame with 'Internship Training Centre',
                       'Qualification', 'Available Positions'.
        seed: Random seed for reproducibility.
        locked: Optional DataFrame of already-assigned interns (must have
                'Assigned Health Facility' column). These are kept as-is.

    Returns:
        (result_df, warnings): result_df has 'Assigned Health Facility' column,
        warnings is a list of warning messages.
    """
    rng = random.Random(seed)
    warnings = []

    # Build mutable capacity dict: {(centre, qual): remaining}
    capacity = {}
    for _, row in facilities_df.iterrows():
        key = (row['Internship Training Centre'], row['Qualification'])
        capacity[key] = capacity.get(key, 0) + int(row['Available Positions'])

    result = interns_df.copy()

    # Handle locked assignments
    if locked is not None and not locked.empty and 'Assigned Health Facility' in locked.columns:
        result['Assigned Health Facility'] = None
        for idx, row in locked.iterrows():
            if idx in result.index and pd.notna(row.get('Assigned Health Facility')):
                facility = row['Assigned Health Facility']
                qual = result.at[idx, 'Qualification']
                result.at[idx, 'Assigned Health Facility'] = facility
                key = (facility, qual)
                if key in capacity:
                    capacity[key] = max(0, capacity[key] - 1)
    else:
        result['Assigned Health Facility'] = None

    # Get indices of unassigned interns
    unassigned_mask = result['Assigned Health Facility'].isna()
    unassigned_indices = result.index[unassigned_mask].tolist()

    # Phase 1: Gender-proportional assignment within capacity
    # Group unassigned interns by qualification
    qual_groups: dict[str, list] = {}
    for idx in unassigned_indices:
        qual = result.at[idx, 'Qualification']
        qual_groups.setdefault(qual, []).append(idx)

    overflow_indices = []

    for qual, indices in qual_groups.items():
        # Compute gender ratio for this qualification
        sexes = [result.at[idx, 'Sex'] for idx in indices]
        sex_values = sorted(set(s for s in sexes if pd.notna(s)))
        sex_buckets: dict[str, list] = {s: [] for s in sex_values}
        for idx in indices:
            s = result.at[idx, 'Sex']
            if pd.notna(s) and s in sex_buckets:
                sex_buckets[s].append(idx)
            else:
                # Unknown sex — put in largest bucket
                sex_buckets[sex_values[0]].append(idx) if sex_values else None

        # Shuffle each gender bucket
        for bucket in sex_buckets.values():
            rng.shuffle(bucket)

        total_interns = len(indices)
        if total_interns == 0:
            continue

        gender_ratios = {s: len(b) / total_interns for s, b in sex_buckets.items()}

        # Get available facilities for this qualification, sorted randomly
        avail_keys = [(c, q) for (c, q), cap in capacity.items() if q == qual and cap > 0]
        rng.shuffle(avail_keys)

        for key in avail_keys:
            cap = capacity[key]
            if cap <= 0:
                continue

            # Allocate slots proportionally by gender
            slots_by_sex: dict[str, int] = {}
            remaining_cap = cap
            for i, sex in enumerate(sex_values):
                if i == len(sex_values) - 1:
                    slots_by_sex[sex] = remaining_cap  # last sex gets remainder
                else:
                    n = round(cap * gender_ratios[sex])
                    n = min(n, remaining_cap, len(sex_buckets[sex]))
                    slots_by_sex[sex] = n
                    remaining_cap -= n

            # Track university counts at this facility for diversity
            uni_counts: dict[str, int] = {}

            assigned_this_facility = 0
            for sex in sex_values:
                n = slots_by_sex[sex]
                if n <= 0 or not sex_buckets[sex]:
                    continue

                # Sort bucket so interns from least-represented universities come first
                def _uni_sort_key(idx):
                    uni = result.at[idx, 'University'] if pd.notna(result.at[idx, 'University']) else ''
                    return uni_counts.get(uni, 0)

                sex_buckets[sex].sort(key=_uni_sort_key)

                for _ in range(n):
                    if sex_buckets[sex]:
                        idx = sex_buckets[sex].pop(0)  # take from front (least represented uni)
                        result.at[idx, 'Assigned Health Facility'] = key[0]
                        uni = result.at[idx, 'University'] if pd.notna(result.at[idx, 'University']) else ''
                        uni_counts[uni] = uni_counts.get(uni, 0) + 1
                        assigned_this_facility += 1

            capacity[key] -= assigned_this_facility

        # Any remaining in buckets are overflow
        for bucket in sex_buckets.values():
            overflow_indices.extend(bucket)

    # Build overflow info by qualification
    overflow_info: dict[str, dict] = {}
    if overflow_indices:
        overflow_by_qual: dict[str, list] = {}
        for idx in overflow_indices:
            qual = result.at[idx, 'Qualification']
            overflow_by_qual.setdefault(qual, []).append(idx)

        all_facilities_by_qual: dict[str, list[str]] = {}
        for _, row in facilities_df.iterrows():
            qual = row['Qualification']
            centre = row['Internship Training Centre']
            all_facilities_by_qual.setdefault(qual, [])
            if centre not in all_facilities_by_qual[qual]:
                all_facilities_by_qual[qual].append(centre)

        for qual, indices in overflow_by_qual.items():
            overflow_info[qual] = {
                'count': len(indices),
                'indices': indices,
                'facilities': all_facilities_by_qual.get(qual, []),
            }

    return result, warnings, overflow_info, capacity


def apply_overflow_action(result: pd.DataFrame, overflow_info: dict,
                          actions: dict[str, str], rng: random.Random) -> tuple[pd.DataFrame, list[str]]:
    """
    Apply user-chosen actions for each qualification's overflow.

    actions: {qualification: "spread" | "leave_unassigned"}
    """
    warnings = []
    for qual, info in overflow_info.items():
        action = actions.get(qual, 'leave_unassigned')
        indices = info['indices']
        facilities = info['facilities']

        if action == 'spread' and facilities:
            rng.shuffle(facilities)
            for i, idx in enumerate(indices):
                result.at[idx, 'Assigned Health Facility'] = facilities[i % len(facilities)]
            warnings.append(
                f"{qual}: {len(indices)} intern(s) spread evenly beyond capacity"
            )
        else:
            warnings.append(
                f"{qual}: {len(indices)} intern(s) left unassigned (no capacity)"
            )

    return result, warnings
