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

                        # Runden evtl. als "Runde 0" etc. -> in int konvertieren
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

            # NEU: Zusätzliche Plots:
            plot_punisher_deviation_distribution(
                df_all=all_data_df,
                simulation_name=simulation_name,
                vis_dir=sim_vis_dir
            )
            plot_contribution_vs_others_clusters(
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
# NEUE FUNKTION 1 (pun.png) – mit umgekehrter Differenz
###############################################################################
def plot_punisher_deviation_distribution(df_all, simulation_name, vis_dir):
    """
    Erstellt ein Balkendiagramm mit den Abweichungen (Differenzen) zwischen
    (target_agent Beitrag in r-1) und (vantage_agent Beitrag in r-1), sofern:
      - vantage_agent hat target_agent in Runde r mit Reputation < 4
      - vantage_agent hat eine Negative Distortion auf target_agent in Runde r

    Binning der Differenzen in folgende Intervalle (X-Achse):
       [-20,-14] , [-14,-8] , [-8,-2] , [-2,2] , [2,8] , [8,14] , [14,20]

    Y-Achse: Anzahl der "Bestrafungs-Ereignisse" (d. h. Summe aller Agents,
             die in diese Kategorie fallen).

    Achtung: "diff = target_contribution - vantage_contribution".
    => Wenn der gepunishte Agent weniger beigetragen hat, ist diff negativ.
    """
    if "Cognitive Algebra" not in df_all.columns or "Cognitive Distortion" not in df_all.columns:
        # Wenn diese Spalten fehlen, brechen wir ab
        return

    # Sortieren nach Agent und Runde
    df_sorted = df_all.sort_values(by=["agent_name", "Runde"]).reset_index(drop=True)

    # Bins:
    bin_edges = [-20, -14, -8, -2, 2, 8, 14, 20]
    bin_labels = [
        "[-20,-14]", "[-14,-8]", "[-8,-2]", "[-2,2]", "[2,8]", "[8,14]", "[14,20]"
    ]
    bin_counts = {label: 0 for label in bin_labels}

    # Lookup: (agent_name, runde) -> Contribution
    contr_lookup = {}
    for idx, row in df_sorted.iterrows():
        contr_lookup[(row["agent_name"], row["Runde"])] = row["Contribution"]

    def parse_cognitive_string(raw_str):
        """Dictionary { 'AgentName': (float oder str) }. """
        result = {}
        if pd.isna(raw_str) or str(raw_str).strip() == "":
            return result
        entries = [x.strip() for x in raw_str.split("|")]
        for e in entries:
            parts = e.split(":")
            if len(parts) == 2:
                target = parts[0].strip()
                val_str = parts[1].strip()
                result[target] = val_str
        return result

    # Über alle vantage_agent-Runden
    for idx, row in df_sorted.iterrows():
        vantage_agent = row["agent_name"]
        r = row["Runde"]
        cog_alg_str = row.get("Cognitive Algebra", "")
        cog_dis_str = row.get("Cognitive Distortion", "")

        rep_dict = parse_cognitive_string(cog_alg_str)
        dist_dict = parse_cognitive_string(cog_dis_str)

        for target_agent, rep_val_str in rep_dict.items():
            try:
                rep_val = float(rep_val_str)
            except:
                continue

            dist_label = dist_dict.get(target_agent, None)
            if dist_label and dist_label.lower().startswith("neg"):
                if rep_val < 4:
                    # Schaue auf Contribution in r-1
                    if (vantage_agent, r-1) in contr_lookup and (target_agent, r-1) in contr_lookup:
                        vantage_contr_prev = contr_lookup[(vantage_agent, r-1)]
                        target_contr_prev = contr_lookup[(target_agent, r-1)]
                        # diff = target - vantage
                        diff = target_contr_prev - vantage_contr_prev

                        idx_bin = None
                        for i in range(len(bin_edges) - 1):
                            left = bin_edges[i]
                            right = bin_edges[i+1]
                            if diff >= left and diff < right:
                                idx_bin = i
                                break
                        if idx_bin is not None:
                            bin_counts[bin_labels[idx_bin]] += 1

    # Plot
    x_positions = range(len(bin_labels))
    y_values = [bin_counts[l] for l in bin_labels]

    plt.figure(figsize=(8, 5))
    plt.bar(x_positions, y_values, color='orange', alpha=0.7)
    plt.xticks(x_positions, bin_labels, rotation=30)
    plt.xlabel("Abweichung (target_agent - punisher) in Runde (r-1)")
    plt.ylabel("Anzahl negativer Distortion-Ereignisse\n(Reputation<4 & Distortion=negative)")

    out_filename = f"{simulation_name}-pun.png"
    out_path = os.path.join(vis_dir, out_filename)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


###############################################################################
# NEUE FUNKTION 2 (con.png) – mit durchgehenden Linien und Diagonale (0,0)-(20,20)
###############################################################################
def plot_contribution_vs_others_clusters(df_all, simulation_name, vis_dir):
    """
    Erstellt den Plot {simulation_name}-con.png:
      - X-Achse: durchschnittliche Beiträge der anderen Gruppenmitglieder (in 2er-Bins von 0..20)
      - Y-Achse: eigener Beitrag
      - Darstellung: 3 Cluster-Linien (K=3 per Agent über alle Runden)
        => Pro Cluster werden die (x,y)-Punkte aller Agents dieses Clusters zusammengefasst.
           (x,y) in Runde r:  x = Mittelwert(Contribution aller anderen Agents in r)
                               y = Contribution(des eigenen Agents in r)
        => Dann in Bins: [0,2), [2,4), ..., [18,20] => Mittelwert von y pro Bin
      - Die Linien werden nicht unterbrochen, d. h. Bins ohne Datenpunkte werden übersprungen.
      - Zusätzliche diagonale graue Linie von (0,0) bis (20,20).
    """
    # 1) Clustering
    pivot = df_all.pivot_table(
        index="agent_name",
        columns="Runde",
        values="Contribution",
        aggfunc="mean"
    )
    pivot = pivot.fillna(method='ffill', axis=1).fillna(method='bfill', axis=1)

    if pivot.shape[0] < 3:
        # Zu wenige Agenten für K=3
        return

    kmeans = KMeans(n_clusters=3, random_state=42)
    labels = kmeans.fit_predict(pivot.values)
    agent_cluster_map = dict(zip(pivot.index, labels))

    # 2) Alle (avgOthers, ownContribution)-Punkte sammeln
    cluster_points = {0: [], 1: [], 2: []}
    all_agents = df_all["agent_name"].unique()
    rounds_sorted = sorted(df_all["Runde"].unique())

    # Lookup: (Runde) -> (agent -> Contribution)
    round_agent_contribution = {}
    for r in rounds_sorted:
        subdf_r = df_all[df_all["Runde"] == r]
        contr_map = dict(zip(subdf_r["agent_name"], subdf_r["Contribution"]))
        round_agent_contribution[r] = contr_map

    for r in rounds_sorted:
        contr_map = round_agent_contribution[r]
        if len(contr_map) <= 1:
            continue
        total_sum = sum(contr_map.values())
        total_n = len(contr_map)

        for agent_name in all_agents:
            if agent_name not in contr_map:
                continue
            own_contribution = contr_map[agent_name]
            others_sum = total_sum - own_contribution
            others_n = total_n - 1
            if others_n <= 0:
                continue
            avg_others = others_sum / others_n
            y = own_contribution
            c_label = agent_cluster_map.get(agent_name, None)
            if c_label is not None:
                cluster_points[c_label].append((avg_others, y))

    # 3) Bins
    bin_edges = np.arange(0, 22, 2)  # 0,2,4,...,20
    # Keine globale Liste von x-Achsenlabels nötig, wir erzeugen sie dynamisch pro Bin.

    # 4) Aggregation pro Cluster & Bin
    cluster_binned_means = {}
    for c_label, pointlist in cluster_points.items():
        if len(pointlist) == 0:
            cluster_binned_means[c_label] = ([], [])
            continue

        arr = np.array(pointlist)
        X_others = arr[:, 0]
        Y_own = arr[:, 1]

        # bin_index -> Liste von Y-Werten
        bin_dict = {i: [] for i in range(len(bin_edges) - 1)}
        for i in range(len(X_others)):
            x_val = X_others[i]
            y_val = Y_own[i]
            # Passende bin suchen
            idx_bin = None
            for b_i in range(len(bin_edges) - 1):
                left = bin_edges[b_i]
                right = bin_edges[b_i+1]
                # Falls x_val == 20, stecken wir es in den letzten Bin
                if b_i == len(bin_edges)-2 and x_val == 20:
                    idx_bin = b_i
                    break
                if x_val >= left and x_val < right:
                    idx_bin = b_i
                    break
            if idx_bin is not None:
                bin_dict[idx_bin].append(y_val)

        # Nun Mittelwerte pro Bin – überspringe leere Bins
        x_mids = []
        mean_ys = []
        for b_i in range(len(bin_edges) - 1):
            in_bin_yvals = bin_dict[b_i]
            if len(in_bin_yvals) == 0:
                # Kein Eintrag -> diesen Bin ganz weglassen => führt zu durchgehenden Linien
                continue
            left = bin_edges[b_i]
            right = bin_edges[b_i+1]
            mean_y = np.mean(in_bin_yvals)
            x_mid = (left + right)/2.0
            x_mids.append(x_mid)
            mean_ys.append(mean_y)

        cluster_binned_means[c_label] = (x_mids, mean_ys)

    # 5) Plotten
    plt.figure(figsize=(8, 5))

    # Diagonale Linie (grau) von (0,0) bis (20,20)
    plt.plot([0, 20], [0, 20], color='gray', linestyle='--', label='Gleicher Beitrag')

    color_list = ["#1f77b4", "#2ca02c", "#d62728"]
    for c_label in sorted(cluster_binned_means.keys()):
        x_vals, y_vals = cluster_binned_means[c_label]
        # Jetzt plotten wir nur die nicht-leeren Bins als durchgehende Linie
        plt.plot(
            x_vals, y_vals,
            marker='o', linestyle='-',
            color=color_list[c_label % len(color_list)],
            label=f"Cluster {c_label}"
        )

    plt.xlabel("Durchschnittlicher Beitrag anderer Teilnehmer")
    plt.ylabel("Eigener Beitrag")
    plt.grid(True)
    plt.legend()

    out_filename = f"{simulation_name}-con.png"
    out_path = os.path.join(vis_dir, out_filename)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


###############################################################################
# PLOTS BEREITS VORHANDEN
###############################################################################
def plot_contribution_of_all_punished_agents(df_all, simulation_name, vis_dir):
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

    # Punishment markieren
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

    lines = l1 + l2
    labels = [l.get_label() for l in lines]
    if "Punished" in df_agent.columns and not df_agent[df_agent["Punished"] == True].empty:
        labels.append("Punished")
        lines.append(ax2.scatter([], [], color='red', s=60))  # Dummy für Legende

    ax1.legend(lines, labels, loc=0)
    plt.title(f"Simulation: {simulation_name}\nAgent: {agent_name} – Fortune vs. Contribution")
    fig.tight_layout()

    out_filename = f"{simulation_name}-{agent_name}-fortune_vs_contribution.png"
    out_path = os.path.join(vis_dir_single, out_filename)
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


def plot_single_agent_only_contribution_and_fortune(df_agent, agent_name, simulation_name, vis_dir_single):
    df_agent = df_agent.sort_values(by="Runde")

    plt.figure(figsize=(8, 5))
    plt.plot(df_agent["Runde"], df_agent["Contribution"], label="Contribution", marker='o', color='blue')
    plt.plot(df_agent["Runde"], df_agent["Fortune"], label="Fortune", marker='x', color='green')

    if "Punished" in df_agent.columns:
        pun_rounds = df_agent[df_agent["Punished"] == True]
        if not pun_rounds.empty:
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


def plot_agent_reputation_and_contribution_for_agent(
        df_all,
        agent_name,
        all_agents,
        simulation_name,
        vis_dir_single
):
    if "Cognitive Algebra" not in df_all.columns:
        return

    rounds_sorted = sorted(df_all["Runde"].unique())

    df_self = df_all[df_all["agent_name"] == agent_name].copy()
    contrib_map = dict(zip(df_self["Runde"], df_self["Contribution"]))

    other_agents = [a for a in all_agents if a != agent_name]
    vantage_by_other = {other: 5.0 for other in other_agents}

    rep_per_round = []

    for r in rounds_sorted:
        df_round = df_all[df_all["Runde"] == r]
        if not df_round.empty:
            for idx, row in df_round.iterrows():
                vantage_agent = row["agent_name"]
                if vantage_agent == agent_name:
                    continue

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

        mean_val = np.mean(list(vantage_by_other.values()))
        rep_per_round.append((r, mean_val))

    runden = [t[0] for t in rep_per_round]
    rep_values = [t[1] for t in rep_per_round]
    contrib_values = [contrib_map.get(r, 0.0) for r in runden]

    plt.figure(figsize=(10, 6))
    # Balken = Contribution
    plt.bar(runden, contrib_values, color='gray', alpha=0.3, label='Contribution')
    # Linie = Reputation
    plt.plot(runden, rep_values, marker='o', color='blue', label='Reputation')

    plt.title(
        f"Reputation & Contribution – {agent_name}\n(Sicht der Anderen)\n"
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


def plot_all_agents_contribution_over_time(df_all, simulation_name, vis_dir):
    plt.figure(figsize=(10, 6))
    for agent_name, subdf in df_all.groupby("agent_name"):
        plt.plot(subdf["Runde"], subdf["Contribution"], label=agent_name, marker='o')

    plt.title(f"Zeitverlauf der Beiträge aller Agenten\nSimulation: {simulation_name}")
    plt.xlabel("Runde")
    plt.ylabel("Beitrag")
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
        raw_cog = row.get("Cognitive Algebra", "")
        if pd.notna(raw_cog) and str(raw_cog).strip() != "":
            entries = [x.strip() for x in raw_cog.split("|")]
            for e in entries:
                parts = e.split(":")
                if len(parts) == 2:
                    other_person = parts[0].strip()
                    popularity = float(parts[1].strip())
                    popularity_map.setdefault(other_person, {})[runde] = popularity

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
    plt.xlabel("Agreeableness")
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

    plt.xlabel("Runde")
    plt.ylabel("Beitrag")
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
    plt.title(f"Beitragsentwicklung nach Cluster (K=3) – {simulation_name}")
    plt.xlabel("Runde")
    plt.ylabel("Beitrag")
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
    plt.xlabel("Runde")
    plt.ylabel("Durchschnittlicher Beitrag pro Cluster")
    plt.legend()
    plt.grid(True)

    out_filename = f"{simulation_name}-all_agents-clustered_contributions.png"
    out_path = os.path.join(vis_dir, out_filename)
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


###############################################################################
# GLOBALE PLOTS (über alle Simulationen)
###############################################################################
def plot_compare_all_simulations_avg_contribution(all_simulation_dfs, global_vis_dir):
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
    K = 3
    color_list = ["#1f77b4", "#2ca02c", "#d62728", "#9467bd",
                  "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
    line_styles = ["-", "--", ":", "-."]

    plt.figure(figsize=(8, 8))
    # Graue Diagonale (0,0) bis (20,20)
    plt.plot([0, 20], [0, 20], color='gray', linewidth=1, linestyle='--')
    # Achsenlimits
    plt.xlim(0, 20)
    plt.ylim(0, 20)

    for idx, (sim_name, df) in enumerate(all_simulation_dfs.items()):
        pop_mean_original = df.groupby("Runde")["Contribution"].mean()
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

            cluster_df.dropna(subset=["pop_mean"], inplace=True)

            color = color_list[idx % len(color_list)]
            style = line_styles[c % len(line_styles)]
            label_str = f"{sim_name} – Cluster {c}"

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


# Ende
