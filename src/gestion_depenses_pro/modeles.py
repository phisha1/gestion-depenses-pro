from __future__ import annotations

from datetime import date
from typing import Annotated, Self

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)
from pydantic_core import PydanticCustomError


def verifier_nombre(valeur: object) -> object:
    if isinstance(valeur, bool) or not isinstance(
        valeur,
        (int, float),
    ):
        raise PydanticCustomError(
            "number_type",
            "la valeur doit être un nombre",
        )

    return valeur


MontantPositif = Annotated[
    float,
    BeforeValidator(verifier_nombre),
    Field(gt=0),
]

MontantNonNegatif = Annotated[
    float,
    BeforeValidator(verifier_nombre),
    Field(ge=0),
]

CodeDevise = Annotated[
    str,
    Field(strict=True),
    StringConstraints(pattern=r"^[A-Z]{3}$"),
]

Periode = Annotated[
    str,
    Field(strict=True),
    StringConstraints(
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
    ),
]


class ModeleBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Configuration(ModeleBase):
    periode: Periode
    plafond_xaf: MontantPositif
    devise_source: CodeDevise
    devises_cibles: list[CodeDevise] = Field(
        min_length=1,
    )

    @model_validator(mode="after")
    def verifier_devises(self) -> Self:
        if len(self.devises_cibles) != len(set(self.devises_cibles)):
            raise ValueError("les devises cibles ne doivent pas contenir de doublon")

        if self.devise_source in self.devises_cibles:
            raise ValueError("la devise source ne peut pas être une devise cible")

        return self


class Depense(ModeleBase):
    date: date
    montant: MontantPositif
    categorie: str = Field(
        min_length=3,
        max_length=50,
        strict=True,
    )
    description: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        strict=True,
    )

    @field_validator(
        "categorie",
        "description",
        mode="before",
    )
    @classmethod
    def supprimer_espaces(
        cls,
        valeur: object,
    ) -> object:
        if isinstance(valeur, str):
            return valeur.strip()

        return valeur

    @field_validator("categorie")
    @classmethod
    def normaliser_categorie(
        cls,
        valeur: str,
    ) -> str:
        return valeur.title()


type DepenseIndexee = tuple[int, Depense]


class DepenseRejetee(ModeleBase):
    index: int = Field(ge=0, strict=True)
    erreurs: list[str] = Field(min_length=1)


class TauxChange(ModeleBase):
    date: date
    base: CodeDevise
    quote: CodeDevise
    rate: MontantPositif


class ConversionReussie(ModeleBase):
    devise: CodeDevise
    taux: MontantPositif
    montant_converti: MontantNonNegatif


class ConversionIndisponible(ModeleBase):
    devise: CodeDevise
    raison: str = Field(
        min_length=1,
        max_length=200,
        strict=True,
    )


class BilanMensuel(ModeleBase):
    periode: Periode
    devise_source: CodeDevise
    plafond: MontantPositif
    depenses: list[Depense]
    depenses_rejetees: list[DepenseRejetee]
    nombre_depenses_valides: int = Field(
        ge=0,
        strict=True,
    )
    nombre_depenses_rejetees: int = Field(
        ge=0,
        strict=True,
    )
    total: MontantNonNegatif
    totaux_par_categorie: dict[str, float]
    budget_restant: float
    pourcentage_utilise: MontantNonNegatif
    plafond_depasse: bool = Field(strict=True)
    conversions: list[ConversionReussie]
    conversions_indisponibles: list[ConversionIndisponible]
