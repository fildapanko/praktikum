import pandas as pd
# nacteni google tabulek
sheet_id = "1GyY4H-OTBL_kVIBzqRwe_UpJX8blSdwkcHyNo-NSDso"
gid = "0"

url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

df = pd.read_csv(url)
print(df)