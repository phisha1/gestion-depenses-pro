import asyncio
import json
from datetime import date
from pathlib import Path

import httpx
import pytest
from pytest_mock import MockerFixture

from gestion_depenses_pro.exceptions import (
    ErreurConfiguration,
    ErreurFichierDepenses,
)
from gestion_depenses_pro.infrastructure import (
    URL_TAUX,
    charger_configuration,
    charger_depenses,
    exporter_bilan,
    recuperer_taux,
    recuperer_un_taux,
)
from gestion_depenses_pro.modeles import (
    BilanMensuel,
    Configuration,
    ConversionIndisponible,
    Depense,
    TauxChange,
)
from gestion_depenses_pro.services import (
    construire_bilan,
)


def test_charger_configuration(
    tmp_path: Path,
) -> None:
    chemin = tmp_path / "configuration.json"
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

    configuration = charger_configuration(chemin)

    assert configuration.periode == "2026-08"
    assert configuration.plafond_xaf == 250_000
    assert configuration.devises_cibles == [
        "EUR",
        "USD",
    ]


def test_charger_configuration_absente(
    tmp_path: Path,
) -> None:
    chemin = tmp_path / "absente.json"

    with pytest.raises(
        ErreurConfiguration,
        match="Impossible de lire",
    ):
        charger_configuration(chemin)


def test_charger_depenses_separe_les_rejets(
    tmp_path: Path,
) -> None:
    chemin = tmp_path / "depenses.json"
    chemin.write_text(
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

    valides, rejetees = charger_depenses(chemin)

    assert len(valides) == 1
    assert valides[0][0] == 0
    assert valides[0][1].montant == 8000
    assert len(rejetees) == 1
    assert rejetees[0].index == 1


def test_charger_depenses_refuse_un_objet_racine(
    tmp_path: Path,
) -> None:
    chemin = tmp_path / "depenses.json"
    chemin.write_text(
        json.dumps(
            {
                "montant": 8000,
                "categorie": "Alimentation",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ErreurFichierDepenses,
        match="Fichier de dépenses invalide",
    ):
        charger_depenses(chemin)


def test_exporter_bilan(
    tmp_path: Path,
    configuration: Configuration,
    depenses: list[Depense],
) -> None:
    chemin = tmp_path / "resultats" / "bilan.json"
    bilan = construire_bilan(
        configuration=configuration,
        depenses=depenses,
        depenses_rejetees=[],
    )

    exporter_bilan(chemin, bilan)

    texte = chemin.read_text(encoding="utf-8")
    bilan_recharge = BilanMensuel.model_validate_json(texte)

    assert chemin.exists()
    assert bilan_recharge.total == 38_500
    assert bilan_recharge.periode == "2026-08"


def test_recuperer_un_taux_reussit(
    mocker: MockerFixture,
) -> None:
    requete = httpx.Request("GET", URL_TAUX)
    reponse = httpx.Response(
        status_code=200,
        json=[
            {
                "date": "2026-08-08",
                "base": "XAF",
                "quote": "EUR",
                "rate": 0.00152,
            }
        ],
        request=requete,
    )

    client: httpx.AsyncClient = mocker.create_autospec(
        httpx.AsyncClient,
        instance=True,
    )
    mocker.patch.object(
        client,
        "get",
        new=mocker.AsyncMock(return_value=reponse),
    )

    resultat = asyncio.run(
        recuperer_un_taux(
            client,
            "XAF",
            "EUR",
        )
    )

    assert isinstance(resultat, TauxChange)
    assert resultat.quote == "EUR"
    assert resultat.rate == 0.00152


def test_recuperer_un_taux_gere_erreur_http(
    mocker: MockerFixture,
) -> None:
    requete = httpx.Request("GET", URL_TAUX)
    reponse = httpx.Response(
        status_code=503,
        request=requete,
    )

    client: httpx.AsyncClient = mocker.create_autospec(
        httpx.AsyncClient,
        instance=True,
    )
    mocker.patch.object(
        client,
        "get",
        new=mocker.AsyncMock(return_value=reponse),
    )

    resultat = asyncio.run(
        recuperer_un_taux(
            client,
            "XAF",
            "EUR",
        )
    )

    assert isinstance(
        resultat,
        ConversionIndisponible,
    )
    assert resultat.devise == "EUR"
    assert resultat.raison == "erreur HTTP 503"


def test_recuperer_un_taux_gere_reponse_invalide(
    mocker: MockerFixture,
) -> None:
    requete = httpx.Request("GET", URL_TAUX)
    reponse = httpx.Response(
        status_code=200,
        json=[
            {
                "date": "date-invalide",
                "base": "XAF",
                "quote": "EUR",
                "rate": -1,
            }
        ],
        request=requete,
    )

    client: httpx.AsyncClient = mocker.create_autospec(
        httpx.AsyncClient,
        instance=True,
    )
    mocker.patch.object(
        client,
        "get",
        new=mocker.AsyncMock(return_value=reponse),
    )

    resultat = asyncio.run(
        recuperer_un_taux(
            client,
            "XAF",
            "EUR",
        )
    )

    assert isinstance(
        resultat,
        ConversionIndisponible,
    )
    assert resultat.raison == ("réponse du service invalide")


def test_recuperer_un_taux_gere_taux_absent(
    mocker: MockerFixture,
) -> None:
    requete = httpx.Request("GET", URL_TAUX)
    reponse = httpx.Response(
        status_code=200,
        json=[
            {
                "date": "2026-08-08",
                "base": "XAF",
                "quote": "GBP",
                "rate": 0.00131,
            }
        ],
        request=requete,
    )

    client: httpx.AsyncClient = mocker.create_autospec(
        httpx.AsyncClient,
        instance=True,
    )
    mocker.patch.object(
        client,
        "get",
        new=mocker.AsyncMock(return_value=reponse),
    )

    resultat = asyncio.run(
        recuperer_un_taux(
            client,
            "XAF",
            "EUR",
        )
    )

    assert isinstance(
        resultat,
        ConversionIndisponible,
    )
    assert resultat.raison == ("taux demandé absent de la réponse")


def test_recuperer_taux_classe_les_resultats(
    mocker: MockerFixture,
) -> None:
    taux_eur = TauxChange(
        date=date(2026, 8, 8),
        base="XAF",
        quote="EUR",
        rate=0.00152,
    )
    echec_usd = ConversionIndisponible(
        devise="USD",
        raison="service indisponible",
    )

    client: httpx.AsyncClient = mocker.create_autospec(
        httpx.AsyncClient,
        instance=True,
    )

    classe_client = mocker.patch(
        "gestion_depenses_pro.infrastructure.httpx.AsyncClient"
    )
    classe_client.return_value.__aenter__.return_value = client

    recuperation_simulee = mocker.patch(
        "gestion_depenses_pro.infrastructure.recuperer_un_taux",
        new=mocker.AsyncMock(side_effect=[taux_eur, echec_usd]),
    )

    taux, indisponibles = asyncio.run(
        recuperer_taux(
            "XAF",
            ["EUR", "USD"],
        )
    )

    assert taux == [taux_eur]
    assert indisponibles == [echec_usd]
    assert recuperation_simulee.await_count == 2
