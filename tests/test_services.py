from datetime import date

import pytest

from gestion_depenses_pro.modeles import (
    Configuration,
    Depense,
    TauxChange,
)
from gestion_depenses_pro.services import (
    calculer_budget_restant,
    calculer_pourcentage_utilise,
    calculer_total,
    calculer_totaux_par_categorie,
    construire_bilan,
    creer_conversions,
    separer_depenses_de_la_periode,
)


def test_calculer_total(
    depenses: list[Depense],
) -> None:
    assert calculer_total(depenses) == 38_500


def test_calculer_totaux_par_categorie(
    depenses: list[Depense],
) -> None:
    assert calculer_totaux_par_categorie(depenses) == {
        "Alimentation": 20_000,
        "Transport": 3_500,
        "Internet": 15_000,
    }


@pytest.mark.parametrize(
    ("plafond", "total", "resultat_attendu"),
    [
        (250_000, 38_500, 211_500),
        (100_000, 100_000, 0),
        (100_000, 120_000, -20_000),
    ],
)
def test_calculer_budget_restant(
    plafond: float,
    total: float,
    resultat_attendu: float,
) -> None:
    assert (
        calculer_budget_restant(
            plafond,
            total,
        )
        == resultat_attendu
    )


def test_calculer_pourcentage_utilise() -> None:
    resultat = calculer_pourcentage_utilise(
        total=38_500,
        plafond=250_000,
    )

    assert resultat == 15.4


def test_separer_depenses_de_la_periode(
    depenses: list[Depense],
) -> None:
    depense_hors_periode = Depense(
        date=date(2026, 9, 1),
        montant=5_000,
        categorie="Loisirs",
    )

    candidates = [
        *enumerate(depenses),
        (10, depense_hors_periode),
    ]

    retenues, rejetees = separer_depenses_de_la_periode(
        candidates,
        "2026-08",
    )

    assert retenues == depenses
    assert len(rejetees) == 1
    assert rejetees[0].index == 10
    assert "2026-09-01" in rejetees[0].erreurs[0]


def test_creer_conversions() -> None:
    taux = [
        TauxChange(
            date=date(2026, 8, 8),
            base="XAF",
            quote="EUR",
            rate=0.00152,
        ),
        TauxChange(
            date=date(2026, 8, 8),
            base="XAF",
            quote="USD",
            rate=0.00176,
        ),
    ]

    conversions = creer_conversions(
        38_500,
        taux,
    )

    assert len(conversions) == 2
    assert conversions[0].devise == "EUR"
    assert conversions[0].montant_converti == 58.52
    assert conversions[1].devise == "USD"
    assert conversions[1].montant_converti == 67.76


def test_construire_bilan(
    configuration: Configuration,
    depenses: list[Depense],
) -> None:
    bilan = construire_bilan(
        configuration=configuration,
        depenses=depenses,
        depenses_rejetees=[],
    )

    assert bilan.total == 38_500
    assert bilan.budget_restant == 211_500
    assert bilan.pourcentage_utilise == 15.4
    assert bilan.plafond_depasse is False
    assert bilan.nombre_depenses_valides == 4
    assert bilan.nombre_depenses_rejetees == 0
