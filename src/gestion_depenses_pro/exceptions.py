class ErreurApplication(Exception):
    """Erreur contrôlée provenant de l’application."""


class ErreurConfiguration(ErreurApplication):
    """La configuration ne peut pas être utilisée."""


class ErreurFichierDepenses(ErreurApplication):
    """Le fichier des dépenses ne peut pas être utilisé."""


class ErreurExport(ErreurApplication):
    """Le bilan ne peut pas être exporté."""
