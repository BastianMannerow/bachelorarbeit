import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# MAIN visualize method
def visualize_everything():
    # Ordner
    data_directory = os.path.join(os.getcwd(), "iteration2", "data")
    data_visual_directory = os.path.join(os.getcwd(), "iteration2", "datavisuals")

    # Dictionary für globale Plots
    # Speichert pro Simulation (Key) den DataFrame (Werte aller Agents).
    all_simulation_dfs = {}

    # Durchlaufe alle Konfigurationsdateien
    for filename in os.listdir(data_directory):
        if filename.endswith(".csv") and "configuration" in filename:
            simulation_name = filename.split('-configuration')[0]
            config_path = os.path.join(data_directory, filename)
            config_df = pd.read_csv(config_path)

            # Agent -> Agent Name
            agent_to_agentname = dict(zip(config_df['agent'], config_df['agent_name']))

            # Übergeordneter Ordner für diese Simulation
            sim_vis_dir = os.path.join(data_visual_directory, simulation_name)
            os.makedirs(sim_vis_dir, exist_ok=True)

            # Einzelagenten-Unterordner
            singleagents_vis_dir = os.path.join(sim_vis_dir, "singleagents")
            os.makedirs(singleagents_vis_dir, exist_ok=True)

            all_agent_data = []

            # CSVs zuordnen
            for agent, agent_name in agent_to_agentname.items():
                search_prefix = f"{simulation_name}-{agent_name}-"
                for f in os.listdir(data_directory):
                    if f.startswith(search_prefix) and f.endswith(".csv"):
                        data_path = os.path.join(data_directory, f)
                        df = pd.read_csv(data_path)

                        # Runden evtl. als "Runde 0" etc.
                        df["Runde"] = df["Runde"].astype(str).apply(
                            lambda x: int(x.replace("Runde", "").strip()) if x.startswith("Runde") else int(x)
                        )

                        # Extrahiere die Agreeableness aus dem Dateinamen
                        splitted = f.split('-')  # [simulation, agentName, '0.27.csv']
                        agreeableness_str = splitted[-1].replace(".csv", "")
                        try:
                            agreeableness_val = float(agreeableness_str)
                        except ValueError:
                            agreeableness_val = np.nan

                        # 1) Plot mit zwei Y-Achsen (Fortune vs. Contribution) + Punishment
                        plot_single_agent_fortune_vs_contribution(
                            df_agent=df,
                            agent_name=agent_name,
                            simulation_name=simulation_name,
                            vis_dir_single=singleagents_vis_dir
                        )

                        # 2) Plot: Cognitive Algebra + Distortion => singleagents
                        plot_cognitive_algebra_and_distortion_for_agent(
                            df_agent=df,
                            agent_name=agent_name,
                            simulation_name=simulation_name,
                            vis_dir_single=singleagents_vis_dir
                        )

                        # 3) Neuer Plot: Einzel-Agent-Kurven (Contribution und Fortune), Punishment markiert
                        plot_single_agent_only_contribution_and_fortune(
                            df_agent=df,
                            agent_name=agent_name,
                            simulation_name=simulation_name,
                            vis_dir_single=singleagents_vis_dir
                        )

                        # Füge Agent-Metadaten hinzu
                        df["agent"] = agent
                        df["agent_name"] = agent_name
                        df["agreeableness"] = agreeableness_val

                        all_agent_data.append(df)

            # Falls keine Agentendaten gefunden, continue
            if len(all_agent_data) == 0:
                continue

            # Kombiniere alle DataFrames zu einer Simulation
            all_data_df = pd.concat(all_agent_data, ignore_index=True)

            # a) Lokale (simulation-spezifische) Plots
            # ----------------------------------------
            plot_all_agents_contribution_over_time(all_data_df, simulation_name, sim_vis_dir)
            plot_boxplot_contributions(all_data_df, simulation_name, sim_vis_dir)
            plot_clustered_contributions(all_data_df, simulation_name, sim_vis_dir)
            plot_normalized_contributions(all_data_df, simulation_name, sim_vis_dir)
            plot_clustered_normalized_view(all_data_df, simulation_name, sim_vis_dir)
            plot_average_reputation_vs_contribution(all_data_df, simulation_name, sim_vis_dir)
            plot_avg_contribution_and_total_wealth(all_data_df, simulation_name, sim_vis_dir)
            plot_wealth_slope_vs_contribution(all_data_df, simulation_name, sim_vis_dir)

            # b) Kognitive Algebra (pro Agent) => singleagents
            plot_cognitive_algebra(all_data_df, simulation_name, singleagents_vis_dir)

            # c) Reputation & Contribution (pro Agent) => singleagents
            all_agent_names = all_data_df["agent_name"].unique()
            for agent_name in all_agent_names:
                plot_agent_reputation_and_contribution_for_agent(
                    df_all=all_data_df,
                    agent_name=agent_name,
                    all_agents=all_agent_names,
                    simulation_name=simulation_name,
                    vis_dir_single=singleagents_vis_dir
                )

            # d) Beitrag aller bestraften Agenten => global pro Simulation
            plot_contribution_of_all_punished_agents(
                df_all=all_data_df,
                simulation_name=simulation_name,
                vis_dir=sim_vis_dir
            )

            # Speichere (für globale Vergleiche)
            all_simulation_dfs[simulation_name] = all_data_df

    # ----------------------------------------------------------------------------
    # NACHDEM ALLE SIMULATIONEN GELESEN SIND: GLOBALE PLOTS (ALLE SIMS VERGLEICHEN)
    # ----------------------------------------------------------------------------
    if len(all_simulation_dfs) > 1:
        # global_vis_dir = der Ordner "iteration2/datavisuals"
        global_vis_dir = data_visual_directory
        os.makedirs(global_vis_dir, exist_ok=True)

        # a) Vergleich: Ø Contribution über Zeit
        plot_compare_all_simulations_avg_contribution(all_simulation_dfs, global_vis_dir)

        # b) Cluster vs Population (alle Simulationen)
        plot_clusters_vs_population_all_simulations(all_simulation_dfs, global_vis_dir)

    print("Fertig!")


###############################################################################
# NEUE FUNKTIONEN FÜR PUNISHMENT-PLOTS UND SINGLE-AGENT-FORTUNEvsCONTRIBUTION
###############################################################################
def plot_contribution_of_all_punished_agents(df_all, simulation_name, vis_dir):
    """
    Zeigt nur die Agenten, die jemals eine Bestrafung ("Punished"==True) erhalten haben.
    Deren Contribution-Kurve wird geplottet. Runde(n), in denen Punishment stattfand,
    werden rot markiert.
    """
    if "Punished" not in df_all.columns:
        # Keine Punished-Spalte, also nichts zu tun
        return

    # Liste aller Agenten, die mind. einmal bestraft wurden
    punished_agents = df_all.groupby("agent_name")["Punished"].apply(lambda x: any(x == True))
    punished_agents = punished_agents[punished_agents == True].index.tolist()

    if len(punished_agents) == 0:
        # Kein Agent wurde je bestraft
        return

    plt.figure(figsize=(10, 6))
    for agent_name in punished_agents:
        subdf = df_all[df_all["agent_name"] == agent_name].sort_values(by="Runde")
        plt.plot(
            subdf["Runde"],
            subdf["Contribution"],
            label=agent_name,
            marker='o',
            alpha=0.7
        )
        # Runde(n) hervorheben, in denen "Punished" == True
        pun_rounds = subdf[subdf["Punished"] == True]
        if not pun_rounds.empty:
            plt.scatter(pun_rounds["Runde"], pun_rounds["Contribution"], color='red', s=60, zorder=3)

    plt.title(f"Contribution-Kurve aller bestraften Agenten\nSimulation: {simulation_name}")
    plt.xlabel("Runde")
    plt.ylabel("Contribution")
    plt.grid(True)
    plt.legend()
    out_filename = f"{simulation_name}-punished_agents_contribution.png"
    out_path = os.path.join(vis_dir, out_filename)
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


def plot_single_agent_fortune_vs_contribution(df_agent, agent_name, simulation_name, vis_dir_single):
    """
    Zeichnet Fortune vs. Contribution mit zwei Y-Achsen.
    Markiert rote Punkte in jenen Runden, in denen Punishment == True war.
    """
    # Sortieren nach Runde
    df_agent = df_agent.sort_values(by="Runde")

    fig, ax1 = plt.subplots(figsize=(8, 5))

    # Linke Y-Achse (Fortune)
    color_fortune = 'tab:blue'
    ax1.set_xlabel("Runde")
    ax1.set_ylabel("Fortune", color=color_fortune)
    l1 = ax1.plot(df_agent["Runde"], df_agent["Fortune"], marker='o', color=color_fortune, label="Fortune")
    ax1.tick_params(axis='y', labelcolor=color_fortune)
    ax1.grid(True)

    # Rechte Y-Achse (Contribution)
    ax2 = ax1.twinx()
    color_contribution = 'tab:red'
    ax2.set_ylabel("Contribution", color=color_contribution)
    l2 = ax2.plot(df_agent["Runde"], df_agent["Contribution"], marker='x', color=color_contribution, label="Contribution")
    ax2.tick_params(axis='y', labelcolor=color_contribution)

    # Punishment markieren (sofern Spalte vorhanden)
    if "Punished" in df_agent.columns:
        pun_rounds = df_agent[df_agent["Punished"] == True]
        if not pun_rounds.empty:
            ax2.scatter(
                pun_rounds["Runde"],
                pun_rounds["Contribution"],
                color='red',
                s=60,
                zorder=3,
                label='Punished'
            )

    # Gemeinsame Legende
    lines = l1 + l2
    labels = [l.get_label() for l in lines]
    # Falls Punished-Punkte dabei sind, erweitern
    if "Punished" in df_agent.columns and not df_agent[df_agent["Punished"] == True].empty:
        labels.append("Punished")
        lines.append(ax2.scatter([], [], color='red', s=60))  # Dummy-Eintrag für Legende

    ax1.legend(lines, labels, loc=0)

    plt.title(f"Simulation: {simulation_name}\nAgent: {agent_name} – Fortune vs. Contribution")
    fig.tight_layout()

    out_filename = f"{simulation_name}-{agent_name}-fortune_vs_contribution.png"
    out_path = os.path.join(vis_dir_single, out_filename)
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


def plot_single_agent_only_contribution_and_fortune(df_agent, agent_name, simulation_name, vis_dir_single):
    """
    Neuer dritter Plottyp für Single-Agents:
    Zeigt zwei Kurven: Contribution und Fortune.
    Markiert in Contribution jene Runden, wo Punished == True.
    """
    df_agent = df_agent.sort_values(by="Runde")

    plt.figure(figsize=(8, 5))
    plt.plot(df_agent["Runde"], df_agent["Contribution"], label="Contribution", marker='o', color='blue')
    plt.plot(df_agent["Runde"], df_agent["Fortune"], label="Fortune", marker='x', color='green')

    if "Punished" in df_agent.columns:
        pun_rounds = df_agent[df_agent["Punished"] == True]
        if not pun_rounds.empty:
            # Markiere Punished-Runden in Contribution
            plt.scatter(pun_rounds["Runde"], pun_rounds["Contribution"], color='red', s=70, zorder=3, label='Punished')

    plt.title(f"Agent: {agent_name}\nSingle-Agent Kurven (Contribution & Fortune)\nSimulation: {simulation_name}")
    plt.xlabel("Runde")
    plt.ylabel("Wert")
    plt.grid(True)
    plt.legend(loc="best")

    out_filename = f"{simulation_name}-{agent_name}-only_contribution_and_fortune.png"
    out_path = os.path.join(vis_dir_single, out_filename)
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


###############################################################################
# HILFSFUNKTIONEN FÜR EINZEL-AGENTEN-PLOTS (bestehend)
###############################################################################
def plot_agent_reputation_and_contribution_for_agent(
        df_all,
        agent_name,
        all_agents,
        simulation_name,
        vis_dir_single
):
    """
    Zeige die Reputation von `agent_name`, so wie sie
    von den anderen Agenten wahrgenommen wird.
    """
    if "Cognitive Algebra" not in df_all.columns:
        return

    # 1) Welche Runden gibt es überhaupt?
    rounds_sorted = sorted(df_all["Runde"].unique())

    # 2) Contribution des Agenten selbst (um sie später als Balken zu plotten)
    df_self = df_all[df_all["agent_name"] == agent_name].copy()
    contrib_map = dict(zip(df_self["Runde"], df_self["Contribution"]))

    # 3) Für alle anderen Agents: "last-known" = 5.0
    other_agents = [a for a in all_agents if a != agent_name]
    vantage_by_other = {other: 5.0 for other in other_agents}

    rep_per_round = []

    for r in rounds_sorted:
        # Zeilen dieser Runde (sämtliche vantage-Agents, die in Runde r etwas notiert haben)
        df_round = df_all[df_all["Runde"] == r]

        if not df_round.empty:
            # Wir schauen uns jede Zeile an => dort steht in "Cognitive Algebra" ein String
            for idx, row in df_round.iterrows():
                vantage_agent = row["agent_name"]  # der, der bewertet
                if vantage_agent == agent_name:
                    continue

                # Parsen des Strings
                raw_cog = row.get("Cognitive Algebra", "")
                if pd.notna(raw_cog) and str(raw_cog).strip() != "":
                    parts = [p.strip() for p in raw_cog.split("|") if ":" in p]
                    for p in parts:
                        splitted = p.split(":")
                        if len(splitted) == 2:
                            target_of_view = splitted[0].strip()
                            val_str = splitted[1].strip()
                            if target_of_view == agent_name:
                                try:
                                    val = float(val_str)
                                except ValueError:
                                    val = 5.0
                                vantage_by_other[vantage_agent] = val

        # Runde abgeschlossen: bestimme den Durchschnittswert
        mean_val = np.mean(list(vantage_by_other.values()))
        rep_per_round.append((r, mean_val))

    # 4) Plotten
    runden = [t[0] for t in rep_per_round]
    rep_values = [t[1] for t in rep_per_round]

    contrib_values = [contrib_map.get(r, 0.0) for r in runden]

    plt.figure(figsize=(10, 6))
    # Balken = Contribution
    plt.bar(runden, contrib_values, color='gray', alpha=0.3, label='Contribution')
    # Linie = Reputation (aus Sicht anderer)
    plt.plot(runden, rep_values, marker='o', color='blue', label='Reputation')

    plt.title(
        f"Reputation & Contribution – {agent_name}\n(Sicht der Anderen auf {agent_name})\n"
        f"Simulation: {simulation_name}"
    )
    plt.xlabel("Runde")
    plt.ylabel("Wert")
    plt.grid(True)
    plt.legend()

    out_filename = f"{simulation_name}-{agent_name}-reputation_and_contribution.png"
    out_path = os.path.join(vis_dir_single, out_filename)
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


###############################################################################
# HILFSFUNKTIONEN FÜR LOKALE (SIMULATIONSSPEZIFISCHE) PLOTS
###############################################################################
def plot_all_agents_contribution_over_time(df_all, simulation_name, vis_dir):
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


def plot_cognitive_algebra(df_all, simulation_name, vis_dir_single):
    if "Cognitive Algebra" not in df_all.columns:
        print("Spalte 'Cognitive Algebra' fehlt – überspringe diesen Plot.")
        return

    for agent_name, subdf in df_all.groupby("agent_name"):
        subdf = subdf.sort_values(by="Runde").reset_index(drop=True)

        popularity_map = {}
        last_known = {}

        for _, row in subdf.iterrows():
            runde = row["Runde"]
            raw_cog = row["Cognitive Algebra"]

            if pd.isna(raw_cog) or str(raw_cog).strip() == "":
                # Falls kein Eintrag -> verwende last_known
                for other_person, val in last_known.items():
                    popularity_map.setdefault(other_person, {})[runde] = val
            else:
                entries = [x.strip() for x in raw_cog.split("|")]
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
        out_path = os.path.join(vis_dir_single, out_filename)
        plt.savefig(out_path, dpi=200, bbox_inches="tight")
        plt.close()


def plot_cognitive_algebra_and_distortion_for_agent(df_agent, agent_name, simulation_name, vis_dir_single):
    if "Cognitive Algebra" not in df_agent.columns:
        return

    popularity_map = {}
    distortion_map = {}

    for _, row in df_agent.iterrows():
        runde = row["Runde"]
        # Cognitive Algebra
        raw_cog = row.get("Cognitive Algebra", "")
        if pd.notna(raw_cog) and str(raw_cog).strip() != "":
            entries = [x.strip() for x in raw_cog.split("|")]
            for e in entries:
                parts = e.split(":")
                if len(parts) == 2:
                    other_person = parts[0].strip()
                    popularity = float(parts[1].strip())
                    popularity_map.setdefault(other_person, {})[runde] = popularity

        # Cognitive Distortion
        raw_dist = row.get("Cognitive Distortion", "")
        if pd.notna(raw_dist) and str(raw_dist).strip() != "":
            dist_entries = [x.strip() for x in raw_dist.split("|")]
            for dist_e in dist_entries:
                parts_dist = dist_e.split(":")
                if len(parts_dist) == 2:
                    other_person_dist = parts_dist[0].strip()
                    dist_label = parts_dist[1].strip().lower()
                    distortion_map.setdefault(other_person_dist, {})[runde] = dist_label

    if len(popularity_map) == 0:
        return

    plt.figure(figsize=(10, 6))
    for other_person, round_dict in popularity_map.items():
        runden = sorted(round_dict.keys())
        values = [round_dict[r] for r in runden]
        plt.plot(runden, values, color='gray', alpha=0.5, linewidth=1)

        for i, r in enumerate(runden):
            val = values[i]
            if other_person in distortion_map and r in distortion_map[other_person]:
                if distortion_map[other_person][r] == "positive":
                    plt.plot(r, val, marker='o', color='green')
                elif distortion_map[other_person][r] == "negative":
                    plt.plot(r, val, marker='o', color='red')
                else:
                    plt.plot(r, val, marker='o', color='gray')
            else:
                plt.plot(r, val, marker='o', color='blue')

    plt.title(f"Cognitive Algebra + Distortion aus Sicht von {agent_name}\nSimulation: {simulation_name}")
    plt.xlabel("Runde")
    plt.ylabel("Reputation (Cognitive Algebra)")
    plt.grid(True)
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='gray', lw=1, label='Reputation'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=6, label='Positive Distortion'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=6, label='Negative Distortion'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=5, label='No Distortion')
    ]
    plt.legend(handles=legend_elements, loc='best')

    out_filename = f"{simulation_name}-{agent_name}-cognitive_algebra_distortion.png"
    out_path = os.path.join(vis_dir_single, out_filename)
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


def plot_boxplot_contributions(df_all, simulation_name, vis_dir):
    if "agreeableness" not in df_all.columns:
        print("Spalte 'agreeableness' fehlt – Boxplot wird übersprungen.")
        return

    df_filtered = df_all.dropna(subset=["agreeableness"]).copy()
    df_filtered = df_filtered.sort_values("agreeableness")

    min_a = df_filtered["agreeableness"].min()
    max_a = df_filtered["agreeableness"].max()
    if pd.isna(min_a) or pd.isna(max_a):
        print("Keine validen 'agreeableness'-Werte, Boxplot übersprungen.")
        return

    bin_edges = np.linspace(min_a, max_a, 6)
    df_filtered["agree_bin"] = pd.cut(df_filtered["agreeableness"], bins=bin_edges,
                                      include_lowest=True, labels=False)

    box_data = []
    x_labels = []
    for bin_id in range(5):
        sub = df_filtered[df_filtered["agree_bin"] == bin_id]
        c_vals = sub["Contribution"].dropna().values
        box_data.append(c_vals)

        left = bin_edges[bin_id]
        right = bin_edges[bin_id+1]
        x_labels.append(f"{round(left,2)} - {round(right,2)}")

    plt.figure(figsize=(10, 6))
    plt.boxplot(box_data, labels=x_labels)
    plt.title(f"Beitragsverhalten nach Social Agreeableness – {simulation_name}")
    plt.xlabel("Agreeableness-Bins")
    plt.ylabel("Contribution")
    plt.grid(True)
    plt.xticks(ticks=range(1,6), labels=x_labels)

    out_filename = f"{simulation_name}-all_agents-boxplot_contributions.png"
    out_path = os.path.join(vis_dir, out_filename)
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


def plot_normalized_contributions(df_all, simulation_name, vis_dir):
    df_round = df_all.groupby("Runde")["Contribution"].mean().reset_index()
    df_round.rename(columns={"Contribution": "avg_contribution"}, inplace=True)

    plt.figure(figsize=(10, 6))
    for agent_name, subdf in df_all.groupby("agent_name"):
        subdf = subdf.sort_values(by="Runde")
        plt.plot(subdf["Runde"], subdf["Contribution"], color='gray', alpha=0.3)

    df_round = df_round.sort_values(by="Runde")
    plt.plot(df_round["Runde"], df_round["avg_contribution"],
             linestyle='-', color='red', linewidth=2.5, label='Durchschnitt')

    plt.title(f"Normalisierte Ansicht (alle Agenten) – {simulation_name}")
    plt.xlabel("Runde")
    plt.ylabel("Contribution")
    plt.legend()
    plt.grid(True)

    out_filename = f"{simulation_name}-all_agents-normalized_contributions.png"
    out_path = os.path.join(vis_dir, out_filename)
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


def plot_clustered_normalized_view(df_all, simulation_name, vis_dir):
    pivot = df_all.pivot_table(
        index="agent_name",
        columns="Runde",
        values="Contribution",
        aggfunc="mean"
    ).fillna(method='ffill', axis=1).fillna(method='bfill', axis=1)

    X = pivot.values
    if X.shape[0] < 3:
        print("Zu wenige Agenten für K=3.")
        return

    kmeans = KMeans(n_clusters=3, random_state=42)
    labels = kmeans.fit_predict(X)

    rounds = pivot.columns
    cluster_means = []
    for c in range(3):
        members = (labels == c)
        if np.sum(members) == 0:
            continue
        mean_vals = X[members].mean(axis=0)
        cluster_means.append((c, mean_vals))

    overall_mean = X.mean(axis=0)

    color_list = ["#1f77b4", "#2ca02c", "#d62728"]
    plt.figure(figsize=(10, 6))

    for c, mean_vals in cluster_means:
        plt.plot(rounds, mean_vals, linestyle='--',
                 color=color_list[c % len(color_list)],
                 alpha=0.5, linewidth=2, marker='o', label=f"Cluster {c}")

    plt.plot(rounds, overall_mean, linestyle='-', color='red', linewidth=3, marker='x',
             label="Gesamt-Durchschnitt")

    plt.xticks(rounds, [str(r) for r in rounds])
    plt.title(f"Clustered Normalized View (K=3) – {simulation_name}")
    plt.xlabel("Runde")
    plt.ylabel("Contribution")
    plt.legend()
    plt.grid(True)

    out_filename = f"{simulation_name}-all_clusters-normalized_view.png"
    out_path = os.path.join(vis_dir, out_filename)
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


def plot_wealth_slope_vs_contribution(df_all, simulation_name, vis_dir):
    df_sorted = df_all.sort_values(by=["agent_name", "Runde"])
    df_sorted['Delta_Fortune'] = df_sorted.groupby('agent_name')['Fortune'].diff()

    fortune_slope = df_sorted.groupby('agent_name')['Delta_Fortune'].mean().reset_index()
    fortune_slope.rename(columns={'Delta_Fortune': 'Avg_Delta_Fortune'}, inplace=True)

    contribution_avg = df_all.groupby('agent_name')['Contribution'].mean().reset_index()
    contribution_avg.rename(columns={'Contribution': 'Avg_Contribution'}, inplace=True)

    merged = pd.merge(fortune_slope, contribution_avg, on='agent_name', how='inner').fillna(0)
    merged = merged.sort_values("agent_name")

    corr = merged['Avg_Delta_Fortune'].corr(merged['Avg_Contribution'])

    plt.figure(figsize=(10, 6))
    plt.scatter(merged['Avg_Contribution'], merged['Avg_Delta_Fortune'],
                color='blue', alpha=0.7)
    if len(merged) > 1:
        m, b = np.polyfit(merged['Avg_Contribution'], merged['Avg_Delta_Fortune'], 1)
        plt.plot(merged['Avg_Contribution'], m*merged['Avg_Contribution'] + b,
                 linestyle='--', color='orange', label="Trend")

    plt.title(f"Wealth-Slope vs. Contribution\nSim: {simulation_name} | r={corr:.2f}")
    plt.xlabel("Avg. Contribution")
    plt.ylabel("Avg. Delta Fortune")
    plt.grid(True)
    plt.legend()

    out_filename = f"{simulation_name}-wealth_slope_vs_contribution.png"
    out_path = os.path.join(vis_dir, out_filename)
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


def plot_average_reputation_vs_contribution(df_all, simulation_name, vis_dir):
    if "Cognitive Algebra" not in df_all.columns:
        print("Keine Spalte 'Cognitive Algebra' – überspringe diesen Plot.")
        return

    def _mean_of_cog_algebra(series):
        vals = []
        for entry in series.dropna():
            parts = [p.strip() for p in entry.split("|") if ":" in p]
            for part in parts:
                try:
                    val = float(part.split(":")[1].strip())
                    vals.append(val)
                except:
                    pass
        return np.mean(vals) if len(vals) > 0 else np.nan

    df_reputation = df_all.groupby("Runde")["Cognitive Algebra"].apply(_mean_of_cog_algebra)
    df_reputation = df_reputation.reset_index(name="avg_reputation")

    df_contribution = df_all.groupby("Runde")["Contribution"].mean().reset_index(name="avg_contribution")

    df_merged = pd.merge(df_reputation, df_contribution, on="Runde", how="inner").sort_values("Runde")

    plt.figure(figsize=(10, 6))
    plt.plot(df_merged["Runde"], df_merged["avg_reputation"], linestyle='--',
             color='blue', linewidth=2, label='Durchschnittl. Reputation')
    plt.plot(df_merged["Runde"], df_merged["avg_contribution"], linestyle='-',
             color='green', linewidth=2, label='Durchschnittl. Contribution')

    plt.title(f"Durchschnittliche Reputation vs Contribution – {simulation_name}")
    plt.xlabel("Runde")
    plt.ylabel("Wert")
    plt.legend()
    plt.grid(True)

    out_filename = f"{simulation_name}-average_reputation_vs_contribution.png"
    out_path = os.path.join(vis_dir, out_filename)
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


def plot_avg_contribution_and_total_wealth(df_all, simulation_name, vis_dir):
    df_avg_contribution = df_all.groupby("Runde")["Contribution"].mean().reset_index(name="avg_contribution")
    df_total_wealth = df_all.groupby("Runde")["Fortune"].sum().reset_index(name="total_wealth")

    df_merged = pd.merge(df_avg_contribution, df_total_wealth, on="Runde", how="inner").sort_values("Runde")

    rounds = df_merged["Runde"].values
    avg_contrib = df_merged["avg_contribution"].values
    total_w = df_merged["total_wealth"].values

    fig, ax1 = plt.subplots(figsize=(10,6))
    color1 = 'tab:red'
    color2 = 'tab:blue'

    ax1.set_xlabel("Runde")
    ax1.set_ylabel("Ø Contribution", color=color1)
    l1 = ax1.plot(rounds, avg_contrib, color=color1, marker='o', label="Avg. Contribution")
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True)

    ax2 = ax1.twinx()
    ax2.set_ylabel("Total Wealth", color=color2)
    l2 = ax2.plot(rounds, total_w, color=color2, marker='x', label="Total Wealth")
    ax2.tick_params(axis='y', labelcolor=color2)

    lines = l1 + l2
    labels = [l.get_label() for l in lines]
    plt.title(f"Avg. Contribution & Total Wealth – {simulation_name}")
    plt.legend(lines, labels, loc=0)

    out_filename = f"{simulation_name}-avg_contribution_and_total_wealth.png"
    out_path = os.path.join(vis_dir, out_filename)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


def plot_clustered_contributions(df_all, simulation_name, vis_dir):
    pivot = df_all.pivot_table(
        index="agent_name",
        columns="Runde",
        values="Contribution",
        aggfunc="mean"
    ).fillna(method='ffill', axis=1).fillna(method='bfill', axis=1)

    X = pivot.values
    if X.shape[0] < 3:
        print("Zu wenige Agenten für K=3-Clustering.")
        return

    kmeans = KMeans(n_clusters=3, random_state=42)
    labels = kmeans.fit_predict(X)

    rounds = pivot.columns
    cluster_means = []
    for c in range(3):
        members = (labels == c)
        if np.sum(members) == 0:
            continue
        mean_vals = X[members].mean(axis=0)
        cluster_means.append((c, mean_vals))

    color_list = ["#1f77b4", "#2ca02c", "#d62728"]
    plt.figure(figsize=(10, 6))
    for c, mean_vals in cluster_means:
        plt.plot(rounds, mean_vals,
                 linestyle='-', color=color_list[c % len(color_list)],
                 alpha=0.8, linewidth=2, marker='o',
                 label=f"Cluster {c}")

    plt.xticks(rounds, [str(r) for r in rounds])
    plt.title(f"Clustering der Contributions (K=3) – {simulation_name}")
    plt.xlabel("Runde")
    plt.ylabel("Durchschnittliche Contribution pro Cluster")
    plt.legend()
    plt.grid(True)

    out_filename = f"{simulation_name}-all_agents-clustered_contributions.png"
    out_path = os.path.join(vis_dir, out_filename)
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


###############################################################################
# NEUE GLOBALE PLOTS (alle Simulationen zusammen)
###############################################################################
def plot_compare_all_simulations_avg_contribution(all_simulation_dfs, global_vis_dir):
    """
    Zeigt pro Simulation eine Linie der durchschnittlichen Contribution pro Runde.
    all_simulation_dfs: dict { simulation_name: df_all }
    """
    plt.figure(figsize=(10, 6))

    for idx, (sim_name, df) in enumerate(all_simulation_dfs.items()):
        df_round = df.groupby("Runde")["Contribution"].mean().reset_index()
        df_round = df_round.sort_values("Runde")
        plt.plot(df_round["Runde"], df_round["Contribution"],
                 marker='o', label=f"{sim_name}")

    plt.title("Vergleich: Ø Contribution pro Runde (über alle Simulationen)")
    plt.xlabel("Runde")
    plt.ylabel("Avg. Contribution")
    plt.legend()
    plt.grid(True)

    out_path = os.path.join(global_vis_dir, "all_simulations_avg_contribution_over_time.png")
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


def plot_clusters_vs_population_all_simulations(all_simulation_dfs, global_vis_dir):
    """
    Zeichnet für jede Simulation die Cluster (K=3).
    X-Achse = Populations-Durchschnitt, Y-Achse = Cluster-Durchschnitt.
    """
    K = 3
    color_list = ["#1f77b4", "#2ca02c", "#d62728", "#9467bd",
                  "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
    line_styles = ["-", "--", ":", "-."]

    plt.figure(figsize=(8, 8))
    # Graue Diagonale (0,0) bis (20,20)
    plt.plot([0, 20], [0, 20], color='gray', linewidth=1, linestyle='--')
    # Fixe Achsenlimits
    plt.xlim(0, 20)
    plt.ylim(0, 20)

    for idx, (sim_name, df) in enumerate(all_simulation_dfs.items()):
        # 1) Populations-Durchschnitt pro Runde
        pop_mean_original = df.groupby("Runde")["Contribution"].mean()

        # 2) K-Means Clustering
        pivot = df.pivot_table(index="agent_name", columns="Runde",
                               values="Contribution", aggfunc="mean")
        pivot = pivot.fillna(method='ffill', axis=1).fillna(method='bfill', axis=1)

        X = pivot.values
        if X.shape[0] < K:
            print(f"Simulation '{sim_name}': Zu wenige Agents für K={K}. Überspringe Plot.")
            continue

        kmeans = KMeans(n_clusters=K, random_state=42)
        labels = kmeans.fit_predict(X)
        rounds_sorted = pivot.columns

        # => reindex pop_mean_original nach rounds_sorted
        pop_mean = pop_mean_original.reindex(index=rounds_sorted).sort_index()

        for c in range(K):
            cluster_members = (labels == c)
            if np.sum(cluster_members) == 0:
                continue

            cluster_mean_vals = X[cluster_members].mean(axis=0)

            cluster_df = pd.DataFrame({
                "Runde": rounds_sorted,
                "pop_mean": pop_mean.values,
                "cluster_mean": cluster_mean_vals
            }).sort_values("Runde")

            # NaNs entfernen
            cluster_df.dropna(subset=["pop_mean"], inplace=True)

            color = color_list[idx % len(color_list)]
            style = line_styles[c % len(line_styles)]
            label_str = f"{sim_name} – Cluster {c}"

            # Pfad von Runde zu Runde in (pop_mean, cluster_mean)-Koordinaten
            plt.plot(cluster_df["pop_mean"], cluster_df["cluster_mean"],
                     linestyle=style, color=color, marker='o', alpha=0.8,
                     label=label_str)

    plt.title("Cluster vs. Population (alle Simulationen)")
    plt.xlabel("Population Avg. Contribution (0-20)")
    plt.ylabel("Cluster Avg. Contribution (0-20)")
    plt.grid(True)
    plt.legend(loc="best")

    out_path = os.path.join(global_vis_dir, "all_simulations_clusters_vs_population.png")
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()
