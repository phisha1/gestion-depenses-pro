from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from gestion_depenses_pro.modeles import BilanMensuel


def formater_montant(
    montant: float,
    devise: str,
) -> str:
    valeur = f"{montant:,.2f}".replace(",", " ")
    return f"{valeur} {devise}"


def afficher_resume(
    bilan: BilanMensuel,
    console: Console,
) -> None:
    if bilan.plafond_depasse:
        statut = "[bold red]Plafond dépassé[/bold red]"
    else:
        statut = "[bold green]Budget respecté[/bold green]"

    contenu = "\n".join(
        [
            (
                "[bold]Total :[/bold] "
                f"{
                    formater_montant(
                        bilan.total,
                        bilan.devise_source,
                    )
                }"
            ),
            (
                "[bold]Plafond :[/bold] "
                f"{
                    formater_montant(
                        bilan.plafond,
                        bilan.devise_source,
                    )
                }"
            ),
            (
                "[bold]Budget restant :[/bold] "
                f"{
                    formater_montant(
                        bilan.budget_restant,
                        bilan.devise_source,
                    )
                }"
            ),
            (f"[bold]Budget utilisé :[/bold] {bilan.pourcentage_utilise:.2f} %"),
            f"[bold]État :[/bold] {statut}",
        ]
    )

    console.print(
        Panel(
            contenu,
            title="Résumé",
            border_style="cyan",
        )
    )


def afficher_depenses(
    bilan: BilanMensuel,
    console: Console,
) -> None:
    table = Table(
        title="Dépenses retenues",
        header_style="bold cyan",
    )
    table.add_column("Date")
    table.add_column("Catégorie")
    table.add_column("Description")
    table.add_column(
        "Montant",
        justify="right",
    )

    for depense in bilan.depenses:
        table.add_row(
            depense.date.isoformat(),
            escape(depense.categorie),
            escape(depense.description or "—"),
            formater_montant(
                depense.montant,
                bilan.devise_source,
            ),
        )

    console.print(table)


def afficher_categories(
    bilan: BilanMensuel,
    console: Console,
) -> None:
    table = Table(
        title="Totaux par catégorie",
        header_style="bold magenta",
    )
    table.add_column("Catégorie")
    table.add_column(
        "Total",
        justify="right",
    )

    for categorie, total in bilan.totaux_par_categorie.items():
        table.add_row(
            escape(categorie),
            formater_montant(
                total,
                bilan.devise_source,
            ),
        )

    console.print(table)


def afficher_conversions(
    bilan: BilanMensuel,
    console: Console,
) -> None:
    table = Table(
        title="Conversions",
        header_style="bold green",
    )
    table.add_column("Devise")
    table.add_column(
        "Taux",
        justify="right",
    )
    table.add_column(
        "Montant converti",
        justify="right",
    )
    table.add_column("État")

    for conversion_reussie in bilan.conversions:
        table.add_row(
            conversion_reussie.devise,
            f"{conversion_reussie.taux:.6f}",
            formater_montant(
                conversion_reussie.montant_converti,
                conversion_reussie.devise,
            ),
            "[green]Disponible[/green]",
        )

    for conversion_indisponible in bilan.conversions_indisponibles:
        table.add_row(
            conversion_indisponible.devise,
            "—",
            "—",
            (f"[red]{escape(conversion_indisponible.raison)}[/red]"),
        )

    console.print(table)


def afficher_rejets(
    bilan: BilanMensuel,
    console: Console,
) -> None:
    if not bilan.depenses_rejetees:
        return

    table = Table(
        title="Dépenses rejetées",
        header_style="bold red",
    )
    table.add_column(
        "Index",
        justify="right",
    )
    table.add_column("Erreurs")

    for rejet in bilan.depenses_rejetees:
        table.add_row(
            str(rejet.index),
            escape("\n".join(rejet.erreurs)),
        )

    console.print(table)


def afficher_bilan(
    bilan: BilanMensuel,
    console: Console,
) -> None:
    console.rule(f"[bold cyan]Bilan {escape(bilan.periode)}")

    afficher_resume(bilan, console)

    if bilan.depenses:
        afficher_depenses(bilan, console)
        afficher_categories(bilan, console)
    else:
        console.print("[yellow]Aucune dépense valide.[/yellow]")

    if bilan.conversions or bilan.conversions_indisponibles:
        afficher_conversions(bilan, console)

    afficher_rejets(bilan, console)
