import csv
def export_rows_to_csv(path, headers, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        if headers: writer.writerow(headers)
        for r in rows: writer.writerow(r)
