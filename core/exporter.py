import pandas as pd


def export_to_excel(df: pd.DataFrame, path: str) -> None:
    export_cols = [
        'Name', 'Sex', 'Qualification', 'University',
        'Year of Completion', 'National Identification Number',
        'Nationality', 'Assigned Health Facility'
    ]
    cols = [c for c in export_cols if c in df.columns]
    out = df[cols].copy()
    out = out.sort_values(by='Assigned Health Facility', na_position='last')

    with pd.ExcelWriter(path, engine='openpyxl') as writer:
        out.to_excel(writer, index=False, sheet_name='Intern Schedule')

        worksheet = writer.sheets['Intern Schedule']
        for col_cells in worksheet.columns:
            max_len = max(len(str(cell.value or '')) for cell in col_cells)
            header_len = len(str(col_cells[0].value or ''))
            worksheet.column_dimensions[col_cells[0].column_letter].width = max(max_len, header_len) + 2
