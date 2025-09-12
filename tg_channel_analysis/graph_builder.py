import os
import webbrowser

import networkx as nx
from pyvis.network import Network

NODE_COLORS = {
    "channel": "lightblue",
    "user": "lightgreen",
    "reposted_channel": "coral",
    "private_channel": "grey"
}


class GraphBuilder:
    def __init__(self, output_filename="graph.html"):
        self.graph = nx.Graph()
        self.output_filename = output_filename

    def add_channel_node(self, channel_id, title, username, members_count, is_repost=False):
        node_title = (
            f"Информация о '{title}':\n"
            f"Username: @{username or 'N/A'}\n"
            f"ID: {channel_id}\n"
            f"Участники: {members_count or 'N/A'}"
        )
        if self.graph.has_node(channel_id) and not is_repost:
            self.graph.nodes[channel_id]['color'] = NODE_COLORS["channel"]
            return

        if not self.graph.has_node(channel_id):
            color = NODE_COLORS["reposted_channel"] if is_repost else NODE_COLORS["channel"]
            self.graph.add_node(
                channel_id, label=title, title=node_title, color=color, size=15
            )

    def add_user_node(self, user_id, name, username):
        if not self.graph.has_node(user_id):
            self.graph.add_node(
                user_id,
                label=name,
                title=f"ID: {user_id}, Username: @{username}",
                color=NODE_COLORS["user"],
                size=10
            )

    def add_private_channel_node(self, channel_id, title="Приватный канал"):
        if not self.graph.has_node(channel_id):
            self.graph.add_node(
                channel_id,
                label=f"{title} (Приватный)",
                title=f"ID: {channel_id}\n(Приватный канал, нет доступа)",
                color=NODE_COLORS["private_channel"],
                size=12
            )

    def add_edge(self, source_id, target_id):
        if not self.graph.has_edge(source_id, target_id):
            self.graph.add_edge(source_id, target_id)

    def save_graph(self):
        if self.graph.number_of_nodes() == 0:
            print("\n[INFO] Граф пуст. Сохранение отменено.")
            return

        print("\n[INFO] Сохранение графа в HTML...")
        try:
            net = Network(
                height="800px",
                width="100%",
                cdn_resources='in_line',
                directed=True,
            )
            net.from_nx(self.graph)
            net.show_buttons(filter_=['physics'])
            net.set_options("""
            {
              "configure": {},
              "physics": {
                "barnesHut": { "gravitationalConstant": -3000, "centralGravity": 0.15, "springLength": 150, "springConstant": 0.02, "damping": 0.1, "avoidOverlap": 0.15 },
                "minVelocity": 0.75,
                "solver": "barnesHut"
              }
            }
            """)

            html_content = net.generate_html()
            html_content = html_content.replace("drawGraph();", "window.onload = drawGraph;")

            with open(self.output_filename, "w", encoding="utf-8") as f:
                f.write(html_content)

            print(f"[SUCCESS] Граф успешно сохранен в файл '{self.output_filename}'.")

            try:
                webbrowser.open(f"file://{os.path.abspath(self.output_filename)}")
            except Exception as e:
                print(f"[WARNING] Не удалось автоматически открыть файл в браузере: {e}")

        except Exception as e:
            print(f"[ERROR] Не удалось сохранить граф: {e}")