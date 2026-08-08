import asyncio
from collections.abc import Sequence
from pathlib import Path

import httpx
from pydantic import (
    TypeAdapter,
    ValidationError,
)

from gestion_depenses_pro.exceptions import (
    ErreurConfiguration,
    ErreurExport,
    ErreurFichierDepenses,
)
from gestion_depenses_pro.modeles import (
    BilanMensuel,
    Configuration,
    ConversionIndisponible,
    Depense,
    DepenseIndexee,
    DepenseRejetee,
    TauxChange,
)

adaptateur_depenses_brutes = TypeAdapter(list[dict[str, object]])
URL_TAUX = "https://api.frankfurter.dev/v2/rates"
DELAI_HTTP = 10.0

adaptateur_taux = TypeAdapter(list[TauxChange])


def formater_erreurs(
    erreur: ValidationError,
) -> list[str]:
    erreurs_formatees: list[str] = []

    for detail in erreur.errors():
        emplacement = ".".join(str(partie) for partie in detail["loc"])
        message = detail["msg"]

        erreurs_formatees.append(f"{emplacement} : {message}")

    return erreurs_formatees


def charger_configuration(
    chemin: Path,
) -> Configuration:
    try:
        texte = chemin.read_text(encoding="utf-8")
    except OSError as erreur:
        raise ErreurConfiguration(
            f"Impossible de lire la configuration : {chemin}"
        ) from erreur

    try:
        return Configuration.model_validate_json(texte)
    except ValidationError as erreur:
        details = "; ".join(formater_erreurs(erreur))
        raise ErreurConfiguration(f"Configuration invalide : {details}") from erreur


def charger_depenses(
    chemin: Path,
) -> tuple[
    list[DepenseIndexee],
    list[DepenseRejetee],
]:
    try:
        texte = chemin.read_text(encoding="utf-8")
    except OSError as erreur:
        raise ErreurFichierDepenses(
            f"Impossible de lire les dépenses : {chemin}"
        ) from erreur

    try:
        donnees = adaptateur_depenses_brutes.validate_json(texte)
    except ValidationError as erreur:
        details = "; ".join(formater_erreurs(erreur))
        raise ErreurFichierDepenses(
            f"Fichier de dépenses invalide : {details}"
        ) from erreur

    depenses_valides: list[DepenseIndexee] = []
    depenses_rejetees: list[DepenseRejetee] = []

    for index, donnee in enumerate(donnees):
        try:
            depense = Depense.model_validate(donnee)
        except ValidationError as erreur:
            depenses_rejetees.append(
                DepenseRejetee(
                    index=index,
                    erreurs=formater_erreurs(erreur),
                )
            )
        else:
            depenses_valides.append((index, depense))

    return depenses_valides, depenses_rejetees


async def recuperer_un_taux(
    client: httpx.AsyncClient,
    devise_source: str,
    devise_cible: str,
) -> TauxChange | ConversionIndisponible:
    try:
        reponse = await client.get(
            URL_TAUX,
            params={
                "base": devise_source,
                "quotes": devise_cible,
            },
        )
        reponse.raise_for_status()

        taux_retournes = adaptateur_taux.validate_json(reponse.content)
    except httpx.HTTPStatusError as erreur:
        return ConversionIndisponible(
            devise=devise_cible,
            raison=(f"erreur HTTP {erreur.response.status_code}"),
        )
    except httpx.RequestError:
        return ConversionIndisponible(
            devise=devise_cible,
            raison="service de change inaccessible",
        )
    except ValidationError:
        return ConversionIndisponible(
            devise=devise_cible,
            raison="réponse du service invalide",
        )

    for taux in taux_retournes:
        if taux.base == devise_source and taux.quote == devise_cible:
            return taux

    return ConversionIndisponible(
        devise=devise_cible,
        raison="taux demandé absent de la réponse",
    )


async def recuperer_taux(
    devise_source: str,
    devises_cibles: Sequence[str],
) -> tuple[
    list[TauxChange],
    list[ConversionIndisponible],
]:
    if not devises_cibles:
        return [], []

    async with httpx.AsyncClient(timeout=DELAI_HTTP) as client:
        resultats = await asyncio.gather(
            *(
                recuperer_un_taux(
                    client,
                    devise_source,
                    devise_cible,
                )
                for devise_cible in devises_cibles
            )
        )

    taux_valides: list[TauxChange] = []
    conversions_indisponibles: list[ConversionIndisponible] = []

    for resultat in resultats:
        if isinstance(resultat, TauxChange):
            taux_valides.append(resultat)
        else:
            conversions_indisponibles.append(resultat)

    return (
        taux_valides,
        conversions_indisponibles,
    )


def exporter_bilan(
    chemin: Path,
    bilan: BilanMensuel,
) -> None:
    try:
        chemin.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        chemin.write_text(
            bilan.model_dump_json(indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as erreur:
        raise ErreurExport(f"Impossible d’exporter le bilan : {chemin}") from erreur
