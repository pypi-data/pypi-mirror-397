@dataclass
class MpdxNode:
    id: str
    type: str            # "table", "title", "t", "v"
    parents: list[str]
    text: str | None = None
    meta: dict = field(default_factory=dict)

@dataclass
class MpdxDocument:
    nodes: dict[str, MpdxNode]
    root_id: str

    def add_node(self, node: MpdxNode) -> None: ...
    def get_node(self, node_id: str) -> MpdxNode: ...
