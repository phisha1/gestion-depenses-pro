from pytest import MonkeyPatch

from gestion_depenses_pro.parametres import charger_parametres


def test_charger_parametres_lit_les_variables(
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "APPLICATION_ENV",
        "test",
    )
    monkeypatch.setenv(
        "TAUX_API_URL",
        "https://example.com/rates",
    )
    monkeypatch.setenv(
        "JETON_DEMONSTRATION",
        "jeton-factice",
    )

    parametres = charger_parametres()

    assert parametres.application_env == "test"
    assert str(parametres.taux_api_url) == "https://example.com/rates"
    assert parametres.jeton_demonstration.get_secret_value() == "jeton-factice"
