from datetime import date

import pytest

from gestion_depenses_pro.modeles import (
    Configuration,
    Depense,
)


@pytest.fixture
def configuration() -> Configuration:
    return Configuration(
        periode="2026-08",
        plafond_xaf=250_000,
        devise_source="XAF",
        devises_cibles=["EUR", "USD"],
    )


@pytest.fixture
def depenses() -> list[Depense]:
    return [
        Depense(
            date=date(2026, 8, 1),
            montant=8_000,
            categorie="Alimentation",
            description="Courses",
        ),
        Depense(
            date=date(2026, 8, 2),
            montant=3_500,
            categorie="Transport",
            description="Taxi",
        ),
        Depense(
            date=date(2026, 8, 3),
            montant=15_000,
            categorie="Internet",
            description="Forfait mensuel",
        ),
        Depense(
            date=date(2026, 8, 4),
            montant=12_000,
            categorie="Alimentation",
            description="Supermarché",
        ),
    ]
