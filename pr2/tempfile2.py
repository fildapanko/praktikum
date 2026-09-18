import matplotlib.pyplot as plt
from pathlib import Path

# Cesta do Downloads funguje stejně na Windows i Linuxu
downloads_dir = Path.home() / "Downloads"

# Ujistíme se, že složka existuje (kdyby náhodou ne)
downloads_dir.mkdir(parents=True, exist_ok=True)

# Příklad grafu
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6])

# Uložení - Path se automaticky převede na string se správnými lomítky
output_path = downloads_dir / "muj_graf.png"
fig.savefig(output_path, dpi=300, bbox_inches="tight")

print(f"Graf uložen do: {output_path}")
