import os
import numpy as np
from datetime import datetime
from tinydb import TinyDB, Query
from structure import Structure

class StructureManager():
    """
    Speichert und lädt Struktur-Objekte. 
    Informationen werden in TinyDB im JSON-Format gespeichert, Daten im binären Format in .npz  
    """

    def __init__(self, path="structure_storage.json", data_dir="structure_data"):
        #Database initialisieren, Tabelle "Structures" laden
        self.db = TinyDB(path)                  
        self.table = self.db.table("structures")

        self.data_dir = data_dir
        #Ordner für Structure-Daten erstellen
        os.makedirs(self.data_dir, exist_ok=True)

    def save(self, name, structure: Structure):
            
        #Nodes und Edges laden, relevante Attribute speichern
        
        #Node-Informationen in Arrays speichern
        node_ids = []
        pos = []
        fixed = []
        forces = []

        #Daten auslesen, an Array anhängen
        for id, data in structure.graph.nodes(data=True):
            node = data["node_ref"]
            
            node_ids.append(id),
            pos.append(node.pos),
            fixed.append(node.fixed),
            forces.append(node.F)

        #Listen in Arrays konvertieren, Daten sollen explizit als Array gespeichert werden,
        #sonst später Unstimmigkeiten bei Abfrage
        node_ids = np.array(node_ids)
        pos = np.array(pos)
        fixed = np.array(fixed)
        forces = np.array(forces)

        #Spring-Informationen in Arrays speichern
        con_nodes = []
        x_vals = []

        for i_id, j_id, data in structure.graph.edges(data=True):
            spring = data["spring"]

            con_nodes.append([i_id, j_id])
            x_vals.append(spring.x)
        
        con_nodes = np.array(con_nodes)
        x_vals = np.array(x_vals)

        #Daten in NPZ speichern
        file_name = f"{name}.npz"
        #Pfad festlegen, join mit Name
        file_path = os.path.join(self.data_dir, file_name)

        np.savez_compressed(file_path,
            node_ids=node_ids, pos=pos, fixed=fixed, forces=forces,
            con_nodes=con_nodes, x=x_vals)

        #Eintrag erstellen, Dictionary
        entry = {
            "name": name,
            "file": file_name,
            "EA": structure.EA,
            "dim": structure.dim,
            "n_nodes": len(node_ids),
            "n_edges": len(con_nodes),
            "date": datetime.now().isoformat()
        }

        #Datenabfrage
        Struct = Query()
        #Wenn Name bereits existiert: Ersetzen, sonst neu speichern
        self.table.upsert(entry, Struct.name == name)
        print(f"Struktur erfolgreich gespeichert.")


    def load(self, name):

        #Referenzdatei aus TinyDB laden
        Struct = Query()
        entry = self.table.get(Struct.name == name)

        #NPZ File laden
        file_path = os.path.join(self.data_dir, entry["file"])
        data = np.load(file_path)

        #Struktur neu aufbauen
        structure = Structure.build_from_data(data, entry["EA"], entry["dim"])

        print(f"Struktur {name} erfolgreich geladen.")
        return structure
