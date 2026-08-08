from collections import defaultdict
from collections.abc import Iterable, Sequence

from gestion_depenses_pro.modeles import (
    BilanMensuel,
    Configuration,
    ConversionIndisponible,
    ConversionReussie,
    Depense,
    DepenseIndexee,
    DepenseRejetee,
    TauxChange,
)


def appartient_a_periode(
    depense: Depense,
    periode: str,
) -> bool:
    periode_depense = depense.date.strftime("%Y-%m")
    return periode_depense == periode


def calculer_total(
    depenses: Iterable[Depense],
) -> float:
    return sum(depense.montant for depense in depenses)


def calculer_totaux_par_categorie(
    depenses: Iterable[Depense],
) -> dict[str, float]:
    totaux: defaultdict[str, float] = defaultdict(float)

    for depense in depenses:
        totaux[depense.categorie] += depense.montant

    return dict(totaux)


def calculer_budget_restant(
    plafond: float,
    total: float,
) -> float:
    return round(plafond - total, 2)


def calculer_pourcentage_utilise(
    total: float,
    plafond: float,
) -> float:
    return round(
        total / plafond * 100,
        2,
    )


def convertir_montant(
    montant: float,
    taux: float,
) -> float:
    return round(
        montant * taux,
        2,
    )


def separer_depenses_de_la_periode(
    depenses_indexees: Iterable[DepenseIndexee],
    periode: str,
) -> tuple[
    list[Depense],
    list[DepenseRejetee],
]:
    depenses_retenues: list[Depense] = []
    depenses_rejetees: list[DepenseRejetee] = []

    for index, depense in depenses_indexees:
        if appartient_a_periode(
            depense,
            periode,
        ):
            depenses_retenues.append(depense)
        else:
            depenses_rejetees.append(
                DepenseRejetee(
                    index=index,
                    erreurs=[
                        (
                            f"date : {depense.date} "
                            f"n’appartient pas à "
                            f"la période {periode}"
                        )
                    ],
                )
            )

    return depenses_retenues, depenses_rejetees


def creer_conversions(
    total: float,
    taux_changes: Iterable[TauxChange],
) -> list[ConversionReussie]:
    conversions: list[ConversionReussie] = []

    for taux_change in taux_changes:
        conversions.append(
            ConversionReussie(
                devise=taux_change.quote,
                taux=taux_change.rate,
                montant_converti=convertir_montant(
                    total,
                    taux_change.rate,
                ),
            )
        )

    return conversions


def construire_bilan(
    configuration: Configuration,
    depenses: Sequence[Depense],
    depenses_rejetees: Sequence[DepenseRejetee],
    conversions: Sequence[ConversionReussie] = (),
    conversions_indisponibles: Sequence[ConversionIndisponible] = (),
) -> BilanMensuel:
    total = calculer_total(depenses)
    plafond = configuration.plafond_xaf

    return BilanMensuel(
        periode=configuration.periode,
        devise_source=configuration.devise_source,
        plafond=plafond,
        depenses=list(depenses),
        depenses_rejetees=list(depenses_rejetees),
        nombre_depenses_valides=len(depenses),
        nombre_depenses_rejetees=len(depenses_rejetees),
        total=total,
        totaux_par_categorie=(calculer_totaux_par_categorie(depenses)),
        budget_restant=calculer_budget_restant(
            plafond,
            total,
        ),
        pourcentage_utilise=(
            calculer_pourcentage_utilise(
                total,
                plafond,
            )
        ),
        plafond_depasse=total > plafond,
        conversions=list(conversions),
        conversions_indisponibles=list(conversions_indisponibles),
    )
