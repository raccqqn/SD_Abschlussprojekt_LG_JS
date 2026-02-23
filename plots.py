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
    def beam_undeformed(self, beam, show_nodes=True, node_size=4, linewidth=1, supports=None,
                        display=True, placeholder=None, color_bins=20):
        """
        Zeichnet die (undeformed) 2D-Struktur.
        - returns fig (and optionally calls placeholder.plotly_chart)
        - supports: dict of { (x,y): {...}} optional, drawn as red markers
        """
        # build single-line arrays
        x_lines, y_lines, _ = self._edges_to_lines_2d(beam)

        fig = go.Figure()
        fig.add_trace(go.Scattergl(
            x=x_lines, y=y_lines, mode="lines",
            line=dict(width=linewidth, color="#444444"),
            hoverinfo="skip"
        ))

        if show_nodes:
            x_nodes, y_nodes = [], []
            for _, ndata in beam.graph.nodes(data=True):
                node = ndata["node_ref"]
                x_nodes.append(node.pos[0])
                y_nodes.append(node.pos[1])
            fig.add_trace(go.Scattergl(
                x=x_nodes, y=y_nodes, mode="markers",
                marker=dict(size=node_size, color="#1f77b4"),
                hoverinfo="skip"
            ))

        if supports:
            xs, ys = [], []
            for pos, _ in (supports.items() if isinstance(supports, dict) else []):
                xs.append(pos[0]); ys.append(pos[1])
            if xs:
                fig.add_trace(go.Scattergl(
                    x=xs, y=ys, mode="markers",
                    marker=dict(size=8, color="red"),
                    hoverinfo="skip"
                ))

        fig.update_layout(
            showlegend=False,
            xaxis=dict(scaleanchor="y"),
            yaxis=dict(autorange="reversed"),
            margin=dict(l=0, r=0, t=20, b=0)
        )

        if display:
            if placeholder is None:
                st.plotly_chart(fig, use_container_width=True)
            else:
                placeholder.plotly_chart(fig, use_container_width=True)
        return fig

    def body_undeformed(self, body, show_nodes=True, node_size=3, linewidth=2,
                        display=True, placeholder=None):
        x_lines, y_lines, z_lines, _ = self._edges_to_lines_3d(body)

        fig = go.Figure()
        fig.add_trace(go.Scatter3d(
            x=x_lines, y=y_lines, z=z_lines, mode="lines",
            line=dict(width=linewidth, color="#444444"),
            hoverinfo="skip"
        ))
        fig.update_scenes(aspectmode="data")

        if show_nodes:
            x_nodes, y_nodes, z_nodes = [], [], []
            for _, ndata in body.graph.nodes(data=True):
                node = ndata["node_ref"]
                x_nodes.append(node.pos[0]); y_nodes.append(node.pos[1]); z_nodes.append(node.pos[2])
            fig.add_trace(go.Scatter3d(
                x=x_nodes, y=y_nodes, z=z_nodes, mode="markers",
                marker=dict(size=node_size, color="#1f77b4"),
                hoverinfo="skip"
            ))

        fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=20, b=0))
        if display:
            if placeholder is None:
                st.plotly_chart(fig, use_container_width=True)
            else:
                placeholder.plotly_chart(fig, use_container_width=True)
        return fig

    # ---------------------------
    # SIMP: Farbliche Darstellung nach x_vals
    # - wir gruppieren Edges in 'bins' um nicht 5000 traces zu erzeugen
    # ---------------------------
    def simp_figure_2d(self, structure, x_vals, bins=20, node_markers=True, node_size=3, scale=1.0):
        """
        Erzeugt eine Figure, die Kanten nach x_vals einfärbt.
        x_vals must be an iterable of length == number of edges (ordered the same way edges are enumerated).
        We render 'bins' traces (one per color bucket) for performance.
        """
        # collect edge endpoints and x per edge in deterministic order
        edges = []
        for idx, (i_id, j_id, data) in enumerate(structure.graph.edges(data=True)):
            spring = data["spring"]
            xi, yi = spring.i.pos[0], spring.i.pos[1]
            xj, yj = spring.j.pos[0], spring.j.pos[1]
            xval = float(x_vals[idx]) if idx < len(x_vals) else 0.0
            edges.append((idx, xi, yi, xj, yj, xval))

        # bin edges by xval
        xs_bins = [[] for _ in range(bins)]
        ys_bins = [[] for _ in range(bins)]
        xvals_array = np.array([e[5] for e in edges])
        if xvals_array.max() == xvals_array.min():
            # avoid zero-range
            edges_bins_edges = np.zeros_like(xvals_array, dtype=int)
        else:
            range_val = np.ptp(xvals_array)
            if range_val == 0:
                edges_bins_edges = np.zeros_like(xvals_array, dtype=int)
            else:
                edges_bins_edges = np.floor(
                    (xvals_array - xvals_array.min()) /
                    (range_val / bins)
                ).astype(int)

            edges_bins_edges = np.clip(edges_bins_edges, 0, bins - 1)

        for e, bin_idx in zip(edges, edges_bins_edges):
            _, xi, yi, xj, yj, _ = e
            xs_bins[bin_idx] += [xi, xj, None]
            ys_bins[bin_idx] += [yi, yj, None]

        # choose colors from palette (sample evenly)
        palette = self.palette
        # ensure we have at least 'bins' colors
        if len(palette) < bins:
            # repeat palette
            palette = (palette * (bins // len(palette) + 1))[:bins]
        else:
            # sample evenly
            stride = max(1, len(palette) // bins)
            palette = [palette[i * stride] for i in range(bins)]

        fig = go.Figure()
        for k in range(bins):
            if not xs_bins[k]:
                continue
            fig.add_trace(go.Scattergl(
                x=xs_bins[k], y=ys_bins[k], mode="lines",
                line=dict(width=1.5, color=palette[k]),
                hoverinfo="skip",
                name=f"bin_{k}"
            ))

        # nodes on top
        if node_markers:
            x_nodes, y_nodes = [], []
            for _, ndata in structure.graph.nodes(data=True):
                node = ndata["node_ref"]
                x_nodes.append(node.pos[0]); y_nodes.append(node.pos[1])
            fig.add_trace(go.Scattergl(
                x=x_nodes, y=y_nodes, mode="markers",
                marker=dict(size=node_size, color="#1f77b4"),
                hoverinfo="skip", name="nodes"
            ))

        fig.update_layout(
            showlegend=False,
            xaxis=dict(scaleanchor="y"),
            yaxis=dict(autorange="reversed"),
            margin=dict(l=0, r=0, t=20, b=0),
            title="SIMP progress (binned coloring)"
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