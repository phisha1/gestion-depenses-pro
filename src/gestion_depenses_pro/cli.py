import asyncio
from pathlib import Path

from rich.console import Console
from rich.markup import escape

from gestion_depenses_pro.exceptions import (
    ErreurConfiguration,
    ErreurExport,
    ErreurFichierDepenses,
)
from gestion_depenses_pro.infrastructure import (
    charger_configuration,
    charger_depenses,
    exporter_bilan,
    recuperer_taux,
)
from gestion_depenses_pro.modeles import (
    ConversionIndisponible,
    ConversionReussie,
)
from gestion_depenses_pro.presentation import (
    afficher_bilan,
)
from gestion_depenses_pro.services import (
    calculer_total,
    construire_bilan,
    creer_conversions,
    separer_depenses_de_la_periode,
)

CHEMIN_CONFIGURATION = Path("data/configuration.json")
CHEMIN_DEPENSES = Path("data/depenses.json")
CHEMIN_BILAN = Path("data/bilan.json")


async def executer(
    console: Console,
    chemin_configuration: Path = CHEMIN_CONFIGURATION,
    chemin_depenses: Path = CHEMIN_DEPENSES,
    chemin_bilan: Path = CHEMIN_BILAN,
) -> int:
    try:
        configuration = charger_configuration(chemin_configuration)
        candidates, rejets_validation = charger_depenses(chemin_depenses)
    except (
        ErreurConfiguration,
        ErreurFichierDepenses,
    ) as erreur:
        console.print(f"[bold red]Erreur :[/bold red] {escape(str(erreur))}")
        return 1

    depenses, rejets_periode = separer_depenses_de_la_periode(
        candidates,
        configuration.periode,
    )

    depenses_rejetees = rejets_validation + rejets_periode

    conversions: list[ConversionReussie] = []
    conversions_indisponibles: list[ConversionIndisponible] = []

    if depenses:
        total = calculer_total(depenses)

        taux, conversions_indisponibles = await recuperer_taux(
            configuration.devise_source,
            configuration.devises_cibles,
        )

        conversions = creer_conversions(
            total,
            taux,
        )

    bilan = construire_bilan(
        configuration=configuration,
        depenses=depenses,
        depenses_rejetees=depenses_rejetees,
        conversions=conversions,
        conversions_indisponibles=(conversions_indisponibles),
    )

    afficher_bilan(bilan, console)

    try:
        exporter_bilan(
            chemin_bilan,
            bilan,
        )
    except ErreurExport as erreur:
        console.print(f"[bold red]Export impossible :[/bold red] {escape(str(erreur))}")
        return 1

    console.print(
        f"\n[bold green]Bilan enregistré dans {escape(str(chemin_bilan))}[/bold green]"
    )

    return 0


def main() -> int:
    console = Console()
    return asyncio.run(executer(console))


if __name__ == "__main__":
    raise SystemExit(main())
