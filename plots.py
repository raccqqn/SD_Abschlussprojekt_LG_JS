import streamlit as st
import matplotlib.pyplot as plt

class Plotter:
    """
    Plotter, der einfach das plotten auslagert
    """

    def __init__(self, invert_y: bool = True):
        self.invert_y = invert_y

    def beam_undeformed(self, beam, show_nodes: bool = True, node_size: float = 1.0, linewidth: float = 1.0, supports = False):
        fig, ax = plt.subplots()                                

        for _,_, edge in beam.graph.edges(data = True):             #Federninfo aus Kanten abrufen
            spring = edge["spring"]
            xi, yi = spring.i.pos                                   #Ausgangspositionen auslesen
            xj, yj = spring.j.pos
            ax.plot([xi, xj], [yi, yj], "b-", linewidth = 1)        #Plotten der Feder als einzelne Linien
        
        for _, node in beam.graph.nodes(data = True):               #Massenpunkte abrufen, speichern und plotten
            mass = node["node_ref"]
            x,y = mass.pos
            ax.plot(x,y, "bo", markersize = 1)

        if supports:
            for pos, s in supports.items():
                xs, ys = pos
                ax.plot(xs, ys, "ro", markersize=6)  # rot
                # optional: Beschriftung
                # ax.text(xs+0.2, ys+0.2, str(s["mask"]), color="red", fontsize=8)
        
        ax.set_aspect("equal")              
        ax.invert_yaxis()
        st.pyplot(fig)

    def beam_deformed(structure, u, scale=0.2, show_nodes=True):
        fig, ax = plt.subplots()

        for _, _, edge in structure.graph.edges(data=True):
            spring = edge["spring"]
            xi, yi = spring.i.pos
            xj, yj = spring.j.pos
            ax.plot([xi, xj], [yi, yj], color="0.7", linewidth=1, zorder=1)       #Normale Darstellung Balken

        for _, _, edge in structure.graph.edges(data=True):
            spring = edge["spring"]
            xi, yi = spring.i.pos
            xj, yj = spring.j.pos
            ui = u[spring.i.dof_indices]                                #Verschiebungen
            uj = u[spring.j.dof_indices]
            ax.plot([xi + scale*ui[0], xj + scale*uj[0]],               #verschobene Darstellung
                    [yi + scale*ui[1], yj + scale*uj[1]], color="b", linewidth=1, zorder=2)

        if show_nodes:                                                              #Massenpunkte
            for _, ndata in structure.graph.nodes(data=True):
                node = ndata["node_ref"]
                x, y = node.pos
                ux, uy = u[node.dof_indices] 
                ax.plot(x, y, "o", markersize=1, color="0.7", zorder=1)             #Normale Darstellung
                ax.plot(x + scale*ux, y + scale*uy, "bo", markersize=1, zorder=2)   #Verschobener Plot

        ax.set_aspect("equal")
        ax.invert_yaxis()
        st.pyplot(fig)

    def body_undeformed(self, body, show_nodes: bool = True, linewidth: float = 1.0):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection = "3d")                    #3D Plot generieren                                
        for _,_, edge in body.graph.edges(data = True):                 #Federninfo aus Kanten abrufen
            spring = edge["spring"]
            xi, yi, zi = spring.i.pos                                   #Ausgangspositionen auslesen
            xj, yj, zj = spring.j.pos
            ax.plot([xi, xj], [yi, yj], [zi, zj], "b-", linewidth = 1)  #Plotten der Feder als einzelne Linien

        for _, nodes in body.graph.nodes(data = True):               #Massenpunkte abrufen, speichern und plotten
            mass = nodes["node_ref"]
            x,y,z = mass.pos
            ax.scatter(x,y,z, color="b")

        ax.set_aspect("equal")
        st.pyplot(fig)

    def body_deformed(structure, u, scale=0.2, show_nodes=True):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")

        for _, _, edge in structure.graph.edges(data=True):
            spring = edge["spring"]
            xi, yi, zi = spring.i.pos
            xj, yj, zj = spring.j.pos
            ax.plot([xi, xj], [yi, yj], [zi, zj], color="0.7", linewidth=1, zorder=1)       #Normale Darstellung Balken

        for _, _, edge in structure.graph.edges(data=True):
            spring = edge["spring"]
            xi, yi, zi = spring.i.pos
            xj, yj, zj = spring.j.pos
            ui = u[spring.i.dof_indices]                                #Verschiebungen
            uj = u[spring.j.dof_indices]
            ax.plot([xi + scale*ui[0], xj + scale*uj[0]],                #verschobene Darstellung
                    [yi + scale*ui[1], yj + scale*uj[1]],
                    [zi + scale*ui[2], zj + scale*uj[2]], color="b", linewidth=1, zorder=2)

        if show_nodes:                                                              #Massenpunkte
            for _, ndata in structure.graph.nodes(data=True):
                node = ndata["node_ref"]
                x, y, z = node.pos
                ux, uy, uz = u[node.dof_indices] 
                ax.scatter(x,y,z)             #Normale Darstellung
                ax.scatter(x + scale*ux, y + scale*uy, z+scale*uz)   #Verschobener Plot

        ax.set_aspect("equal")
        ax.invert_yaxis()
        st.pyplot(fig)

    def plot_optimization_result(structure, u, scale_factor=0.1):
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Alle Edges (Stäbe) durchlaufen
        for i, j, data in structure.graph.edges(data=True):
            spring = data["spring"]
            x_val = spring.x
            
            # Original-Positionen
            pos_i = np.array(spring.i.pos)
            pos_j = np.array(spring.j.pos)
            
            # Verschiebungen extrahieren (u hat das Format [u1x, u1y, u2x, u2y, ...])
            u_i = u[spring.i.dof_indices]
            u_j = u[spring.j.dof_indices]
            
            # Deformierte Positionen berechnen
            pos_i_def = pos_i + scale_factor * u_i
            pos_j_def = pos_j + scale_factor * u_j

            # 1. OPTIMIERTE STRUKTUR (Grau/Schwarz)
            if x_val > 0.01:
                ax.plot(
                    [pos_i[0], pos_j[0]], [pos_i[1], pos_j[1]],
                    color=plt.cm.Greys(x_val),
                    linewidth=5 * x_val,
                    alpha=0.3, # Etwas transparenter, damit rot besser wirkt
                    zorder=1
                )
            
            # 2. VERSCHOBENE STRUKTUR (Rot)
            # Wir plotten die verschobene Struktur dünner, um die Tendenz zu zeigen
            if x_val > 0.1: # Nur relevante Stäbe verschoben zeigen
                ax.plot(
                    [pos_i_def[0], pos_j_def[0]], [pos_i_def[1], pos_j_def[1]],
                    color='red',
                    linestyle='--',
                    linewidth=1,
                    alpha=0.6,
                    zorder=2
                )
            
            ax.set_aspect("equal")
            ax.set_title(f"Optimierung & Verformung (Skalierung: {scale_factor}x)")
            ax.axis('off')
            ax.invert_yaxis()
            plt.show()

    def plot_nodes(opt_beam, u, deformed = False):
        scale = 0.1                                         #Skalierung, sonst sieht man nichts

        for _, data in opt_beam.graph.nodes(data=True):
            node = data["node_ref"]
            x, y = node.pos

            ux, uy = u[node.dof_indices]

            if deformed == False:
                plt.plot(x, y, "ko")                            #ursprüngliche Lage    
            else:                    
                plt.plot(x + scale*ux, y + scale*uy, "ro")      #verformte Lage

        plt.gca().invert_yaxis()
        plt.gca().set_aspect("equal")
        plt.show()