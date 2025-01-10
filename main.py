#from iteration1.simulation.GeneralGameTheory import ClassicPublicGoodsGame
import numpy as np

from iteration2.simulation.PublicGoodsGame import ClassicPublicGoodsGame
import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

def plot_all_agents_contribution_over_time(df_all, simulation_name, vis_dir):
    """Zeitverlauf der Beiträge aller Agenten (bekannt aus dem alten Skript)."""
    plt.figure(figsize=(10, 6))

    for agent_name, subdf in df_all.groupby("agent_name"):
        plt.plot(subdf["Runde"], subdf["Contribution"], label=agent_name, marker='o')

    plt.title(f"Zeitverlauf der Beiträge aller Agenten\nSimulation: {simulation_name}")
    plt.xlabel("Runde")
    plt.ylabel("Beitrag (Contribution)")
    plt.legend()
    plt.grid(True)

    out_filename = f"{simulation_name}-all_agents-contribution_over_time.png"
    out_path = os.path.join(vis_dir, out_filename)
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


def plot_cognitive_algebra(df_all, simulation_name, vis_dir):
    """Kognitive Algebra / Beliebtheit pro Agent (bekannt aus dem alten Skript)."""
    if "Cognitive Algebra" not in df_all.columns:
        print(f"Spalte 'Cognitive Algebra' nicht vorhanden – überspringe diesen Plot.")
        return

    for agent_name, subdf in df_all.groupby("agent_name"):
        subdf = subdf.sort_values(by="Runde").reset_index(drop=True)

        popularity_map = {}
        last_known = {}

        for _, row in subdf.iterrows():
            runde = row["Runde"]
            raw_cog = row["Cognitive Algebra"]

            if pd.isna(raw_cog) or str(raw_cog).strip() == "":
                # Keine Aktualisierung
                for other_person, val in last_known.items():
                    popularity_map.setdefault(other_person, {})[runde] = val
            else:
                entries = [x.strip() for x in raw_cog.split(",")]
                for e in entries:
                    parts = e.split(":")
                    if len(parts) == 2:
                        other_person = parts[0].strip()
                        popularity = float(parts[1].strip())
                        last_known[other_person] = popularity

                for other_person, val in last_known.items():
                    popularity_map.setdefault(other_person, {})[runde] = val

        if len(popularity_map) == 0:
            continue

        plt.figure(figsize=(10, 6))

        for other_person, round_dict in popularity_map.items():
            runden = sorted(round_dict.keys())
            values = [round_dict[r] for r in runden]
            plt.plot(runden, values, label=other_person, marker='o')

        plt.title(f"Kognitive Algebra aus Sicht von {agent_name}\nSimulation: {simulation_name}")
        plt.xlabel("Runde")
        plt.ylabel("Beliebtheits-Wert")
        plt.legend()
        plt.grid(True)

        out_filename = f"{simulation_name}-{agent_name}-cognitive_algebra.png"
        out_path = os.path.join(vis_dir, out_filename)
        plt.savefig(out_path, dpi=200, bbox_inches="tight")
        plt.close()


# -------------------------------------------------------------------
# (1) Beiträge vs. Durchschnitt, aber mit verbundenen Punkten
# -------------------------------------------------------------------
def plot_contribution_vs_average_with_lines(df_all, simulation_name, vis_dir):
    """
    Modifizierter Plot:
    X-Achse: Durchschnittlicher Beitrag aller Agenten (pro Runde)
    Y-Achse: Individueller Beitrag
    ABER: Die Punkte werden pro Agent nach Runde sortiert und verbunden.
    """
    # Durchschnitt pro Runde
    round_avg = df_all.groupby("Runde")["Contribution"].mean().reset_index()
    round_avg.rename(columns={"Contribution": "avg_contribution"}, inplace=True)

    # Mergen
    merged = pd.merge(df_all, round_avg, on="Runde", how="left")
    merged = merged.sort_values(by=["agent_name", "Runde"])

    plt.figure(figsize=(10, 6))

    for agent_name, subdf in merged.groupby("agent_name"):
        # Sortieren nach Runde
        subdf = subdf.sort_values(by="Runde")
        plt.plot(
            subdf["avg_contribution"],
            subdf["Contribution"],
            marker='o',
            label=agent_name
        )

    plt.title(f"Contribution vs. durchschnittlicher Beitrag (verbunden)\nSimulation: {simulation_name}")
    plt.xlabel("Durchschnitt (alle Agenten, pro Runde)")
    plt.ylabel("Individueller Beitrag")
    plt.legend()
    plt.grid(True)

    out_filename = f"{simulation_name}-all_agents-contribution_vs_average_lines.png"
    out_path = os.path.join(vis_dir, out_filename)
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


# -------------------------------------------------------------------
# (2) „Ähnliche Verläufe“ zusammenfassen (z. B. K-Means-Clustering)
# -------------------------------------------------------------------
def plot_clustered_contributions(df_all, simulation_name, vis_dir, n_clusters=3):
    """
    Beispielhafter Ansatz: Wir betrachten die Zeitreihen der Agents
    (Contribution pro Runde) und fassen ähnliche Verläufe zusammen.
    Für jeden Cluster wird eine durchschnittliche Linie gezeichnet.
    """
    # 1) Wir brauchen eine "Pivot-Tabelle": Zeilen = Agent, Spalten = Runde, Wert = Average Contribution
    #    Falls es mehrere CSVs pro Agent gibt, haben wir sie ja schon in df_all,
    #    aber wir nehmen an, pro (Agent, Runde) gibt es einen eindeutigen Contribution-Wert.

    pivot = df_all.pivot_table(
        index="agent_name",
        columns="Runde",
        values="Contribution",
        aggfunc="mean"  # falls es doch mehrere Zeilen pro (agent, runde)
    ).fillna(method='ffill', axis=1).fillna(method='bfill', axis=1)
    # .fillna: Auffüllen, falls mal Lücken sind; man könnte auch 0 oder Mittelwert nehmen

    # 2) Clustering
    #    pivot.values ist ein 2D-Array mit shape (Anzahl_Agents, Anzahl_Runden)
    X = pivot.values  # shape: (n_agents, n_rounds)

    if X.shape[0] < n_clusters:
        # Wenn weniger Agenten als Cluster, reduzieren wir die Cluster-Anzahl
        n_clusters = X.shape[0]

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(X)  # Cluster-Label pro Agent

    # 3) Mittelwerte pro Cluster berechnen
    cluster_means = []
    for c in range(n_clusters):
        # Mittelwert aller Zeitreihen, die dem Cluster c angehören
        members = (labels == c)
        if np.sum(members) == 0:
            continue
        mean_vals = X[members].mean(axis=0)  # Durchschnitt über Zeilen
        cluster_means.append((c, mean_vals))

    # 4) Plot
    rounds = pivot.columns  # Spalten sind die Runden
    plt.figure(figsize=(10, 6))

    for c, mean_vals in cluster_means:
        plt.plot(rounds, mean_vals, marker='o', label=f"Cluster {c}")

    plt.title(f"Clustering der Contributions (K={n_clusters})\nSimulation: {simulation_name}")
    plt.xlabel("Runde")
    plt.ylabel("Durchschnittliche Contribution pro Cluster")
    plt.legend()
    plt.grid(True)

    out_filename = f"{simulation_name}-all_agents-clustered_contributions.png"
    out_path = os.path.join(vis_dir, out_filename)
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


# -------------------------------------------------------------------
# (3) Sinnvolle Visualisierung: Boxplot pro Agent
# -------------------------------------------------------------------
def plot_boxplot_contributions(df_all, simulation_name, vis_dir):
    """
    Boxplot (oder alternativ Violinplot) pro Agent, um die Verteilung
    der Contributions zu sehen.
    """
    plt.figure(figsize=(10, 6))

    # Sortiere Agenten nach Alphabet oder nach Auftreten
    agents_sorted = sorted(df_all["agent_name"].unique())
    data_to_plot = []

    for agent_name in agents_sorted:
        subdf = df_all[df_all["agent_name"] == agent_name]
        data_to_plot.append(subdf["Contribution"].dropna().values)

    plt.boxplot(data_to_plot, labels=agents_sorted)
    plt.title(f"Boxplot der Beiträge pro Agent\nSimulation: {simulation_name}")
    plt.xlabel("Agent")
    plt.ylabel("Contribution")
    plt.grid(True)

    out_filename = f"{simulation_name}-all_agents-boxplot_contributions.png"
    out_path = os.path.join(vis_dir, out_filename)
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


# -------------------------------------------------------------------
# (4) Normalisierte Grafik:
#     Durchschnitt als fette Linie, Einzellinien in weniger dominanter Farbe
# -------------------------------------------------------------------
def plot_normalized_contributions(df_all, simulation_name, vis_dir):
    """
    Zeigt den Verlauf der Contributions in einer Grafik:
      - Eine (fett) gezeichnete Linie: Durchschnitt aller Agenten pro Runde
      - Alle Agenten-Linien in heller Farbe dahinter
    """
    # 1) Runden-Durchschnitt berechnen
    df_round = df_all.groupby("Runde")["Contribution"].mean().reset_index()
    df_round.rename(columns={"Contribution": "avg_contribution"}, inplace=True)

    # 2) Alle Agenten-Linien (Contribution vs. Runde) in heller Farbe
    plt.figure(figsize=(10, 6))

    for agent_name, subdf in df_all.groupby("agent_name"):
        subdf = subdf.sort_values(by="Runde")
        plt.plot(subdf["Runde"], subdf["Contribution"], color='gray', alpha=0.3)

    # 3) Durchschnitt in fetter, dunkler Farbe
    df_round = df_round.sort_values(by="Runde")
    plt.plot(
        df_round["Runde"],
        df_round["avg_contribution"],
        color='red',
        linewidth=2.5,
        label='Durchschnitt'
    )

    plt.title(f"Normalisierte Ansicht: Durchschnitt vs. Einzellinien\nSimulation: {simulation_name}")
    plt.xlabel("Runde")
    plt.ylabel("Contribution")
    plt.legend()
    plt.grid(True)

    out_filename = f"{simulation_name}-all_agents-normalized_contributions.png"
    out_path = os.path.join(vis_dir, out_filename)
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()

# Test multiple agent in the same round based environment
end_after_rounds = 20
data_directory = os.getcwd() + os.sep + "iteration2" + os.sep + "data"
data_visual_directory = os.getcwd() + os.sep + "iteration2" + os.sep + "datavisuals"

experiment_name = data_directory + os.sep + "Bigger Population"
simulation = ClassicPublicGoodsGame((0, 2), end_after_rounds, experiment_name)
simulation.run_simulation()

for filename in os.listdir(data_directory):
    if filename.endswith(".csv") and "configuration" in filename:
        # Beispiel: "meinesimulation-configuration.csv"

        # Simulation-Name extrahieren (alles vor '-configuration')
        simulation_name = filename.split('-configuration')[0]

        # Pfad zur Config-Datei
        config_path = os.path.join(data_directory, filename)

        # Config-Datei einlesen
        config_df = pd.read_csv(config_path)

        # Dictionary Agent -> Agent Name
        agent_to_agentname = dict(zip(config_df['agent'], config_df['agent_name']))

        # ---------------------------------------
        # Ordner für die Agentenplots dieser Simulation anlegen
        # ---------------------------------------
        agent_vis_dir = os.path.join(data_visual_directory, simulation_name)
        os.makedirs(agent_vis_dir, exist_ok=True)

        # ---------------------------------------
        # CSVs für diese Simulation sammeln
        # ---------------------------------------
        all_agent_data = []

        for agent, agent_name in agent_to_agentname.items():
            # Such-Präfix: "{simulation_name}-{agent_name}-..."
            search_prefix = f"{simulation_name}-{agent_name}-"

            # Alle CSVs dazu im data_directory
            for f in os.listdir(data_directory):
                if f.startswith(search_prefix) and f.endswith(".csv"):
                    # Wert hinter dem letzten '-' extrahieren (Agreeableness)
                    parts = f.split('-')
                    last_part = parts[-1]  # z.B. "0.27.csv"
                    agreeableness = last_part.replace(".csv", "")

                    # CSV einlesen
                    data_path = os.path.join(data_directory, f)
                    df = pd.read_csv(data_path)

                    # --- Einzelplot: Fortune & Contribution ---
                    plt.figure(figsize=(8, 5))
                    plt.plot(df["Runde"], df["Fortune"], label="Fortune", marker='o')
                    plt.plot(df["Runde"], df["Contribution"], label="Contribution", marker='x')

                    plt.title(f"Simulation: {simulation_name}\nAgent: {agent_name}, "
                              f"Agreeableness: {agreeableness}")
                    plt.xlabel("Runde")
                    plt.ylabel("Wert")
                    plt.legend()
                    plt.grid(True)

                    # Speichern
                    out_filename = f"{simulation_name}-{agent_name}-{agreeableness}.png"
                    out_path = os.path.join(agent_vis_dir, out_filename)
                    plt.savefig(out_path, dpi=200, bbox_inches="tight")
                    plt.close()

                    # Daten sammeln für die globalen Plots
                    df["agent"] = agent
                    df["agent_name"] = agent_name
                    df["agreeableness"] = agreeableness

                    all_agent_data.append(df)

        if len(all_agent_data) == 0:
            continue

        # Großen DataFrame erstellen
        all_data_df = pd.concat(all_agent_data, ignore_index=True)

        # --- Bestehende (alte) Übersichtsgrafiken ---
        plot_all_agents_contribution_over_time(
            all_data_df, simulation_name, data_visual_directory
        )
        plot_cognitive_algebra(
            all_data_df, simulation_name, data_visual_directory
        )

        # --- Neue / Erweiterte Übersichtsgrafiken ---
        plot_contribution_vs_average_with_lines(
            all_data_df, simulation_name, data_visual_directory
        )
        plot_clustered_contributions(
            all_data_df, simulation_name, data_visual_directory
        )
        plot_boxplot_contributions(
            all_data_df, simulation_name, data_visual_directory
        )
        plot_normalized_contributions(
            all_data_df, simulation_name, data_visual_directory
        )
