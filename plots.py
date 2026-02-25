# plots.py
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

class Plotter:
    """
    Plotter: Plotly / WebGL-based, Streamlit-friendly.
    - kompatible Signaturen zu deiner bisherigen API
    - effizientes Rendering für 2D/3D Strukturen
    - SIMP: färbt Stäbe nach x-Faktor (Binning für Performance)
    - ESO: filtert Knoten & Kanten nach node_mask
    """

    def __init__(self, color_scale="Viridis"):
        # Farbpalette für SIMP-Binning
        self.palette = getattr(px.colors.sequential, color_scale, px.colors.sequential.Viridis)

    # ---------------------------
    # Helpers
    # ---------------------------
    def _edges_to_lines_2d(self, structure, edge_indices=None, include_node_mask=None):
        """
        Liefert x_lines,y_lines und für jedes Edge den zugehörigen Node-Paar (i,j).
        edge_indices: optional list/iterable von edge indices (int) die verwendet werden.
        include_node_mask: dict mapping node_id -> bool (True=keep). Falls gesetzt, Edges die gelöschte Knoten verbinden werden weggelassen.
        """
        x_lines, y_lines = [], []
        edge_to_nodes = []  # list of (i_id, j_id)
        # enumerate edges to get deterministic index mapping
        for idx, (i_id, j_id, data) in enumerate(structure.graph.edges(data=True)):
            if (edge_indices is not None) and (idx not in edge_indices):
                continue
            if include_node_mask is not None:
                if (not include_node_mask.get(i_id, True)) or (not include_node_mask.get(j_id, True)):
                    continue
            spring = data["spring"]
            xi, yi = spring.i.pos[0], spring.i.pos[1]
            xj, yj = spring.j.pos[0], spring.j.pos[1]
            x_lines += [xi, xj, None]
            y_lines += [yi, yj, None]
            edge_to_nodes.append((i_id, j_id))
        return x_lines, y_lines, edge_to_nodes

    def _edges_to_lines_3d(self, structure, edge_indices=None, include_node_mask=None):
        x_lines, y_lines, z_lines = [], [], []
        edge_to_nodes = []
        for idx, (i_id, j_id, data) in enumerate(structure.graph.edges(data=True)):
            if (edge_indices is not None) and (idx not in edge_indices):
                continue
            if include_node_mask is not None:
                if (not include_node_mask.get(i_id, True)) or (not include_node_mask.get(j_id, True)):
                    continue
            spring = data["spring"]
            xi, yi, zi = spring.i.pos[0], spring.i.pos[1], spring.i.pos[2]
            xj, yj, zj = spring.j.pos[0], spring.j.pos[1], spring.j.pos[2]
            x_lines += [xi, xj, None]
            y_lines += [yi, yj, None]
            z_lines += [zi, zj, None]
            edge_to_nodes.append((i_id, j_id))
        return x_lines, y_lines, z_lines, edge_to_nodes

    # ---------------------------
    # Backwards-compatible 2D / 3D "undeformed" display
    # signature kept similar to old API
    # ---------------------------
    def beam_undeformed(self, beam, show_nodes=True, node_size=4, linewidth=1, 
                        display=True, placeholder=None):
        
        x_lines, y_lines, _ = self._edges_to_lines_2d(beam)
        fig = go.Figure()

        # Struktur-Linien
        fig.add_trace(go.Scattergl(
            x=x_lines, y=y_lines, mode="lines",
            line=dict(width=linewidth, color="#444444"),
            hoverinfo="skip",
            showlegend=False
        ))

        if show_nodes:
            #Dictionary für die verschiedenen Kategorien mit Klarnamen für die Legende
            node_groups = {
                "Knoten":        {"x": [], "y": [], "color": "#1f77b4", "symbol": "circle", "size": node_size},
                "Kraftangriff":  {"x": [], "y": [], "color": "red",     "symbol": "circle", "size": node_size + 3},
                "Festlager (XY)":{"x": [], "y": [], "color": "green", "symbol": "square", "size": node_size + 6},
                "Loslager (X)":  {"x": [], "y": [], "color": "green", "symbol": "triangle-up", "size": node_size + 9},
                "Loslager (Y)":  {"x": [], "y": [], "color": "green", "symbol": "triangle-down", "size": node_size + 9},
            }

            for _, ndata in beam.graph.nodes(data=True):
                node = ndata["node_ref"]
                x, y = node.pos[0], node.pos[1]
                f = node.fixed # [bool, bool]
                
                if f[0] and f[1]:
                    key = "Festlager (XY)"
                elif f[0]:
                    key = "Loslager (X)"
                elif f[1]:
                    key = "Loslager (Y)"
                elif np.any(node.F != 0):
                    key = "Kraftangriff"
                else:
                    key = "Knoten"
                
                node_groups[key]["x"].append(x)
                node_groups[key]["y"].append(y)

            for name, data in node_groups.items():
                if data["x"]:
                    is_standard_node = (name == "Knoten")

                    fig.add_trace(go.Scattergl(
                        x=data["x"], y=data["y"], mode="markers",
                        marker=dict(size=data["size"], color=data["color"], symbol=data["symbol"]),
                        name=name,
                        showlegend=not is_standard_node
                    ))

        fig.update_layout(
            legend=dict(orientation="h", yanchor="top", y=0.98, xanchor="left", x=0.01),
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis=dict(scaleanchor="y", showgrid=False, zeroline=False),
            yaxis=dict(autorange="reversed", showgrid=False, zeroline=False),
            plot_bgcolor="rgba(0,0,0,0)"
        )

        if display:
            target = placeholder if placeholder else st
            target.plotly_chart(fig, use_container_width=True)
            
        return fig

    def body_undeformed(self, body, show_nodes=True, node_size=3, linewidth=2,
                        display=True, placeholder=None):
        """ Zeichnet die 3D-Struktur mit farbigen Markern für Lager (Grün) und Kräfte (Rot). """
        
        x_lines, y_lines, z_lines, _ = self._edges_to_lines_3d(body)
        fig = go.Figure()

        # Struktur-Linien (Gittermodell)
        fig.add_trace(go.Scatter3d(
            x=x_lines, y=y_lines, z=z_lines, mode="lines",
            line=dict(width=linewidth, color="#444444"),
            hoverinfo="skip", showlegend=False
        ))

        if show_nodes:
            # Gruppen-Definition (Name: [Farbe, Größe, Legende_Anzeigen])
            groups = {
                "Knoten":        {"pos": [], "color": "#1f77b4", "size": node_size,     "show": False},
                "Kraftangriff":  {"pos": [], "color": "red",     "size": node_size + 2, "show": True},
                "Festlager (XYZ)":{"pos": [], "color": "green", "size": node_size + 4, "show": True},
                "Loslager":{"pos": [], "color": "yellow", "size": node_size + 3, "show": True},
            }

            for _, ndata in body.graph.nodes(data=True):
                node = ndata["node_ref"]
                f = node.fixed # Erwartet [bool, bool, bool]
                
                # Kategorisierung für 3D
                if all(f[:3]):
                    key = "Festlager (XYZ)"
                elif any(f[:3]):
                    key = "Loslager"
                elif np.any(node.F != 0):
                    key = "Kraftangriff"
                else:
                    key = "Knoten"
                
                groups[key]["pos"].append(node.pos)

            # Traces hinzufügen
            for name, data in groups.items():
                if data["pos"]:
                    pts = np.array(data["pos"])
                    fig.add_trace(go.Scatter3d(
                        x=pts[:,0], y=pts[:,1], z=pts[:,2], mode="markers",
                        marker=dict(size=data["size"], color=data["color"], opacity=0.9),
                        name=name, showlegend=data["show"]
                    ))

        camera = dict(
            eye=dict(x=-1.5, y=-1.5, z=1.5),  # Position der Kamera
            center=dict(x=0, y=0, z=0),       # Worauf die Kamera schaut
            up=dict(x=0, y=0, z=1)            # Welche Achse "oben" ist
        )

        fig.update_scenes(aspectmode="data")
        fig.update_layout(
            scene_camera=camera,
            legend=dict(orientation="h", yanchor="top", y=0.98, xanchor="left", x=0.01),
            margin=dict(l=0, r=0, t=30, b=0)
        )

        if display:
            target = placeholder if placeholder else st
            target.plotly_chart(fig, use_container_width=True)
            
        return fig

    # ---------------------------
    # SIMP: Farbliche Darstellung nach x_vals
    # - wir gruppieren Edges in 'bins' um nicht 5000 traces zu erzeugen
    # ---------------------------
    def simp_figure_2d(self, structure, x_vals, bins=15, node_markers=True, node_size=2):
        """
        SIMP Visualisierung: 
        - Nur Federn mit x >= 0.01 werden gezeichnet.
        - Nur Knoten, die noch aktive Federn haben, werden gezeichnet.
        - Blau-Weiß Skala (Blau = massiv, Weiß/Hellblau = dünn).
        """
        import plotly.express as px
        
        # Farbskala: Von Hellblau (niedrig) zu Dunkelblau (hoch)
        colors = px.colors.sample_colorscale("Blues", [i/(bins-1) for i in range(bins)])
        
        xs_bins = [[] for _ in range(bins)]
        ys_bins = [[] for _ in range(bins)]
        active_node_ids = set() # Zum Tracking der Knoten mit "Material"
        
        # 1. Federn filtern und binnig
        for idx, (i_id, j_id, data) in enumerate(structure.graph.edges(data=True)):
            x_val = float(x_vals[idx]) if idx < len(x_vals) else 0.0
            
            if x_val < 0.01:
                continue
                
            b_idx = int(min(x_val * bins, bins - 1))
            node_i, node_j = data["spring"].i, data["spring"].j
            
            # Koordinaten für Linien
            xs_bins[b_idx] += [node_i.pos[0], node_j.pos[0], None]
            ys_bins[b_idx] += [node_i.pos[1], node_j.pos[1], None]
            
            # Knoten als "aktiv" markieren
            active_node_ids.add(i_id)
            active_node_ids.add(j_id)

        fig = go.Figure()

        # 2. Aktive Federn plotten
        for k in range(bins):
            if xs_bins[k]:
                fig.add_trace(go.Scattergl(
                    x=xs_bins[k], y=ys_bins[k], mode="lines",
                    line=dict(width=1.8, color=colors[k]),
                    hoverinfo="skip", showlegend=False
                ))

        # 3. Nur aktive Knoten plotten
        if node_markers:
            x_n, y_n = [], []
            for n_id, ndata in structure.graph.nodes(data=True):
                if n_id in active_node_ids:
                    node = ndata["node_ref"]
                    x_n.append(node.pos[0]); y_n.append(node.pos[1])
                
            fig.add_trace(go.Scattergl(
                x=x_n, y=y_n, mode="markers",
                marker=dict(size=node_size, color="#555555", opacity=0.5),
                hoverinfo="skip", showlegend=False
            ))

        fig.update_layout(
            xaxis=dict(scaleanchor="y", showgrid=False, zeroline=False, visible=False),
            yaxis=dict(autorange="reversed", showgrid=False, zeroline=False, visible=False),
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        
        return fig

    # ---------------------------
    # ESO: Entferne Knoten (node_mask: numpy boolean array aligned with initial_node_ids)
    # ---------------------------
    def eso_figure_2d(self, structure, node_mask, initial_node_ids, node_size=3):
        """
        Zeichnet die Struktur, filtert Knoten und Kanten die nicht mehr existieren.
        - node_mask: boolean array, matching order of initial_node_ids (True => node exists)
        - initial_node_ids: list/array of node ids in the original indexing order used by ESO
        """
        # build mapping node_id -> bool
        node_alive = {nid: bool(node_mask[i]) for i, nid in enumerate(initial_node_ids)}

        # edges only if both nodes alive
        x_lines, y_lines, _ = self._edges_to_lines_2d(structure, include_node_mask=node_alive)

        fig = go.Figure()
        fig.add_trace(go.Scattergl(x=x_lines, y=y_lines, mode="lines",
                                   line=dict(width=1.2, color="#444444"),
                                   hoverinfo="skip"))

        # nodes
        x_nodes, y_nodes = [], []
        for nid, ndata in structure.graph.nodes(data=True):
            node = ndata["node_ref"]
            if node_alive.get(nid, True):
                x_nodes.append(node.pos[0]); y_nodes.append(node.pos[1])
        fig.add_trace(go.Scattergl(x=x_nodes, y=y_nodes, mode="markers",
                                   marker=dict(size=node_size, color="#1f77b4"),
                                   hoverinfo="skip"))

        fig.update_layout(
            showlegend=False,
            xaxis=dict(scaleanchor="y"),
            yaxis=dict(autorange="reversed"),
            margin=dict(l=0, r=0, t=20, b=0),
            title="ESO progress (removed nodes filtered out)"
        )
        return fig

    def simp_figure_3d(self, structure, x_vals, node_markers=False):
        # 1. Daten vorbereiten
        edges = list(structure.graph.edges())
        
        x_lines = []
        y_lines = []
        z_lines = []
        color_values = []

        for i, (u_id, v_id) in enumerate(edges):
            density = x_vals[i]
            
            # Performance-Filter: Sehr dünne Stäbe gar nicht erst senden
            if density < 0.1:
                continue
                
            pos_u = structure.graph.nodes[u_id]["node_ref"].pos
            pos_v = structure.graph.nodes[v_id]["node_ref"].pos

            # Liniensegmente mit None-Trenner hinzufügen
            x_lines.extend([pos_u[0], pos_v[0], None])
            y_lines.extend([pos_u[1], pos_v[1], None])
            z_lines.extend([pos_u[2], pos_v[2], None])
            
            # Wir weisen jedem Punkt der Linie die Dichte als Farbwert zu
            color_values.extend([density, density, density])

        fig = go.Figure()

        # 2. ALLES in einen einzigen Trace packen
        fig.add_trace(go.Scatter3d(
            x=x_lines,
            y=y_lines,
            z=z_lines,
            mode="lines",
            line=dict(
                width=5,
                color=color_values, # Plotly mappt die Dichte-Werte auf die Farbskala
                colorscale='Blues', # Oder 'Viridis', 'Greys' etc.
                showscale=True
            ),
            hoverinfo="skip"
        ))

        # Layout stabilisieren
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                aspectmode="data"
            )
        )
        return fig

    def eso_figure_3d(self, structure, node_mask, initial_node_ids):
        node_alive = {nid: bool(node_mask[i]) for i, nid in enumerate(initial_node_ids)}
        x_lines, y_lines, z_lines, _ = self._edges_to_lines_3d(structure, include_node_mask=node_alive)
        fig = go.Figure()
        fig.add_trace(go.Scatter3d(x=x_lines, y=y_lines, z=z_lines, mode="lines",
                                   line=dict(width=2, color="#444444"), hoverinfo="skip"))
        x_nodes,y_nodes,z_nodes = [],[],[]
        for nid, ndata in structure.graph.nodes(data=True):
            node = ndata["node_ref"]
            if node_alive.get(nid, True):
                x_nodes.append(node.pos[0]); y_nodes.append(node.pos[1]); z_nodes.append(node.pos[2])
        fig.add_trace(go.Scatter3d(x=x_nodes, y=y_nodes, z=z_nodes, mode="markers",
                                   marker=dict(size=3, color="#1f77b4"), hoverinfo="skip"))
        fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=20, b=0))
        fig.update_scenes(aspectmode="data")
        return fig
    
    #Dimension der Struktur bestimmen
    def eso_figure(self, structure, node_mask, initial_node_ids):
        if structure.dim == 3:
            return self.eso_figure_3d(structure, node_mask, initial_node_ids)
        else:
            return self.eso_figure_2d(structure, node_mask, initial_node_ids)
        
    def simp_figure(self, structure, x_vals):
        if structure.dim == 3:
            return self.simp_figure_3d(structure, x_vals)
        else:
            return self.simp_figure_2d(structure, x_vals)