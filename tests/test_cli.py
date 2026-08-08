import asyncio
import json
from datetime import date
from io import StringIO
from pathlib import Path

from pytest_mock import MockerFixture
from rich.console import Console

from gestion_depenses_pro.cli import executer
from gestion_depenses_pro.modeles import Configuration, Depense, TauxChange
from gestion_depenses_pro.presentation import (
    afficher_bilan,
)
from gestion_depenses_pro.services import (
    construire_bilan,
)


def creer_console() -> tuple[Console, StringIO]:
    sortie = StringIO()
    console = Console(
        file=sortie,
        force_terminal=False,
        color_system=None,
        width=120,
    )
    return console, sortie


def ecrire_configuration(chemin: Path) -> None:
    chemin.write_text(
        json.dumps(
            {
                "periode": "2026-08",
                "plafond_xaf": 250_000,
                "devise_source": "XAF",
                "devises_cibles": ["EUR", "USD"],
            }
        ),
        encoding="utf-8",
    )


def test_executer_produit_et_exporte_le_bilan(
    tmp_path: Path,
    mocker: MockerFixture,
) -> None:
    chemin_configuration = tmp_path / "configuration.json"
    chemin_depenses = tmp_path / "depenses.json"
    chemin_bilan = tmp_path / "bilan.json"

    ecrire_configuration(chemin_configuration)
    chemin_depenses.write_text(
        json.dumps(
            [
                {
                    "date": "2026-08-01",
                    "montant": 8000,
                    "categorie": "Alimentation",
                },
                {
                    "date": "2026-08-02",
                    "montant": -5000,
                    "categorie": "Erreur",
                },
            ]
        ),
        encoding="utf-8",
    )

    taux_eur = TauxChange(
        date=date(2026, 8, 8),
        base="XAF",
        quote="EUR",
        rate=0.00152,
    )
    taux_usd = TauxChange(
        date=date(2026, 8, 8),
        base="XAF",
        quote="USD",
        rate=0.00176,
    )

    mocker.patch(
        "gestion_depenses_pro.cli.recuperer_taux",
        new=mocker.AsyncMock(
            return_value=(
                [taux_eur, taux_usd],
                [],
            )
        ),
    )

    console, sortie = creer_console()

    code = asyncio.run(
        executer(
            console=console,
            chemin_configuration=(chemin_configuration),
            chemin_depenses=chemin_depenses,
            chemin_bilan=chemin_bilan,
        )
    )

    texte = sortie.getvalue()

    assert code == 0
    assert chemin_bilan.exists()
    assert "Bilan 2026-08" in texte
    assert "Alimentation" in texte
    assert "Dépenses rejetées" in texte
    assert "EUR" in texte
    assert "USD" in texte


def test_executer_echoue_si_configuration_absente(
    tmp_path: Path,
    mocker: MockerFixture,
) -> None:
    recuperation_simulee = mocker.patch(
        "gestion_depenses_pro.cli.recuperer_taux",
        new=mocker.AsyncMock(),
    )
    console, sortie = creer_console()

    code = asyncio.run(
        executer(
            console=console,
            chemin_configuration=(tmp_path / "absente.json"),
            chemin_depenses=(tmp_path / "depenses.json"),
            chemin_bilan=tmp_path / "bilan.json",
        )
    )

    assert code == 1
    assert "Erreur" in sortie.getvalue()
    recuperation_simulee.assert_not_awaited()


def test_executer_ne_contacte_pas_api_si_aucune_depense_valide(
    tmp_path: Path,
    mocker: MockerFixture,
) -> None:
    chemin_configuration = tmp_path / "configuration.json"
    chemin_depenses = tmp_path / "depenses.json"

    ecrire_configuration(chemin_configuration)
    chemin_depenses.write_text(
        json.dumps(
            [
                {
                    "date": "2026-08-01",
                    "montant": -5000,
                    "categorie": "Erreur",
                }
            ]
        ),
        encoding="utf-8",
    )

    recuperation_simulee = mocker.patch(
        "gestion_depenses_pro.cli.recuperer_taux",
        new=mocker.AsyncMock(),
    )
    console, sortie = creer_console()

    code = asyncio.run(
        executer(
            console=console,
            chemin_configuration=(chemin_configuration),
            chemin_depenses=chemin_depenses,
            chemin_bilan=tmp_path / "bilan.json",
        )
    )

    assert code == 0
    assert "Aucune dépense valide" in (sortie.getvalue())
    recuperation_simulee.assert_not_awaited()


def test_executer_signale_un_export_impossible(
    tmp_path: Path,
    mocker: MockerFixture,
) -> None:
    chemin_configuration = tmp_path / "configuration.json"
    chemin_depenses = tmp_path / "depenses.json"

    ecrire_configuration(chemin_configuration)
    chemin_depenses.write_text(
        "[]",
        encoding="utf-8",
    )

    mocker.patch(
        "gestion_depenses_pro.cli.recuperer_taux",
        new=mocker.AsyncMock(),
    )
    console, sortie = creer_console()

    code = asyncio.run(
        executer(
            console=console,
            chemin_configuration=(chemin_configuration),
            chemin_depenses=chemin_depenses,
            chemin_bilan=tmp_path,
        )
    )

    assert code == 1
    assert "Export impossible" in sortie.getvalue()


def test_afficher_bilan_signale_plafond_depasse(
    depenses: list[Depense],
) -> None:
    configuration = Configuration(
        periode="2026-08",
        plafond_xaf=10_000,
        devise_source="XAF",
        devises_cibles=["EUR"],
    )
    bilan = construire_bilan(
        configuration=configuration,
        depenses=depenses,
        depenses_rejetees=[],
    )
    console, sortie = creer_console()

    afficher_bilan(bilan, console)

    assert bilan.plafond_depasse is True
    assert "Plafond dépassé" in sortie.getvalue()
