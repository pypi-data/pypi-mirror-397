class CtLtoMpdxConverter:
    def convert(self, ctl: CanonicalTableLayout) -> MpdxDocument:
        """
        Convert a CanonicalTableLayout into an MPDX document.
        Each original cell becomes a semantic text node (`t`).
        Layout information is stored in node.meta.
        """
        pass


    class MpdxToCtlConverter:
    def convert(self, doc: MpdxDocument) -> CanonicalTableLayout:
        """
        Reconstruct CanonicalTableLayout from MPDX layout metadata.
        Requires layout-preserving MPDX (v0).
        """
