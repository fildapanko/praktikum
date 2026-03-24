import matplotlib.pyplot as plt
import pandas as pd

# nacteni google tabulek
sheet_id = "1SabDjWsPIsUqenpKLWSS_sL0DrfNNjyDOQ5PH-PDqho"
gid = "408060846"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
df_relax = pd.read_csv(url)


# fit a graf
# graf hodnot
plt.plot(df_relax['cas'], df_relax['napeti'])
plt.savefig('ykouska.png')