import pytest
from pydantic import ValidationError

from gestion_depenses_pro.modeles import (
    Configuration,
    Depense,
)


def test_depense_normalise_les_textes() -> None:
    depense = Depense.model_validate(
        {
            "date": "2026-08-01",
            "montant": 8000,
            "categorie": "  alimentation  ",
            "description": "  Courses  ",
        }
    )

    assert depense.categorie == "Alimentation"
    assert depense.description == "Courses"


def test_depense_refuse_un_montant_textuel() -> None:
    with pytest.raises(ValidationError) as capture:
        Depense.model_validate(
            {
                "date": "2026-08-01",
                "montant": "8000",
                "categorie": "Alimentation",
            }
        )

    erreur = capture.value.errors()[0]

    assert erreur["loc"] == ("montant",)
    assert erreur["type"] == "number_type"


def test_depense_refuse_un_montant_negatif() -> None:
    with pytest.raises(ValidationError) as capture:
        Depense.model_validate(
            {
                "date": "2026-08-01",
                "montant": -5000,
                "categorie": "Alimentation",
            }
        )

    assert capture.value.errors()[0]["type"] == ("greater_than")


def test_depense_refuse_un_champ_inconnu() -> None:
    with pytest.raises(ValidationError) as capture:
        Depense.model_validate(
            {
                "date": "2026-08-01",
                "montant": 8000,
                "categorie": "Alimentation",
                "champ_inconnu": True,
            }
        )

    assert capture.value.errors()[0]["type"] == ("extra_forbidden")


def test_configuration_refuse_les_doublons() -> None:
    with pytest.raises(
        ValidationError,
        match="ne doivent pas contenir de doublon",
    ):
        Configuration(
            periode="2026-08",
            plafond_xaf=250_000,
            devise_source="XAF",
            devises_cibles=["EUR", "EUR"],
        )


def test_configuration_refuse_la_source_comme_cible() -> None:
    with pytest.raises(
        ValidationError,
        match="ne peut pas être une devise cible",
    ):
        Configuration(
            periode="2026-08",
            plafond_xaf=250_000,
            devise_source="XAF",
            devises_cibles=["EUR", "XAF"],
        )


def test_depense_refuse_une_categorie_non_textuelle() -> None:
    with pytest.raises(ValidationError) as capture:
        Depense.model_validate(
            {
                "date": "2026-08-01",
                "montant": 8000,
                "categorie": 123,
            }
        )

    assert capture.value.errors()[0]["loc"] == ("categorie",)
    assert capture.value.errors()[0]["type"] == ("string_type")
