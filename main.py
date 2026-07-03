import flet as ft
import json
import os

FICHIER_SAUVEGARDE = "data_backtest.json"

def charger_donnees():
    if os.path.exists(FICHIER_SAUVEGARDE):
        try:
            with open(FICHIER_SAUVEGARDE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"stats": {"total": 0, "gagnes": 0}, "trades": []}

def sauvegarder_donnees(donnees):
    with open(FICHIER_SAUVEGARDE, "w", encoding="utf-8") as f:
        json.dump(donnees, f, indent=4, ensure_ascii=False)

def main(page: ft.Page):
    page.title = "Journal de Trading APK"
    page.scroll = "adaptive"

    donnees_locales = charger_donnees()
    stats = donnees_locales["stats"]

    # --- TABLEAU DE BORD ---
    txt_total = ft.Text("Trades : 0", weight=ft.FontWeight.BOLD, size=14)
    txt_winrate = ft.Text("Win Rate : 0%", weight=ft.FontWeight.BOLD, size=14, color="blue")
    txt_balance = ft.Text("Balance : 0$", weight=ft.FontWeight.BOLD, size=14, color="green")

    tableau_stats = ft.Container(
        content=ft.Row([txt_total, txt_winrate, txt_balance]),
        padding=12,
        bgcolor="#e3f2fd",
        border_radius=10,
        width=400
    )

    # --- ENCADRÉ NOIR POUR LA COURBE AUTOMATIQUE MOBILE ---
    conteneur_graphique = ft.Container(
        width=400,
        height=180,
        bgcolor="#1e1e1e",
        border_radius=10,
        padding=15
    )

    # --- FORMULAIRE ---
    actif_input = ft.TextField(label="Actif (ex: BTCUSDT, GOLD)", width=400)
    
    direction_input = ft.Dropdown(
        label="Direction",
        width=400,
        options=[ft.dropdown.Option("ACHAT (Bullish)"), ft.dropdown.Option("VENTE (Bearish)")]
    )
    
    statut_input = ft.Dropdown(
        label="Résultat (Ratio 1:2)",
        width=400,
        options=[ft.dropdown.Option("TP Touché (Gagné)"), ft.dropdown.Option("SL Touché (Perdu)")]
    )

    message_confirmation = ft.Text("", size=14, weight=ft.FontWeight.BOLD)
    liste_affichage = ft.Column(spacing=10)

    def rafraichir_interface():
        total = stats["total"]
        gagnes = stats["gagnes"]
        perdus = total - gagnes
        argent_total = (gagnes * 8) - (perdus * 4)
        win_rate = round((gagnes / total) * 100) if total > 0 else 0

        txt_total.value = f"Trades : {total}"
        txt_winrate.value = f"Win Rate : {win_rate}%"
        txt_balance.value = f"Balance : {argent_total}$"
        txt_balance.color = "green" if argent_total >= 0 else "red"

        # --- GESTION DE LA COURBE POUR LE TÉLÉPHONE ---
        try:
            trades_chronologiques = list(reversed(donnees_locales["trades"]))
            solde = 0
            nouveaux_points = [ft.LineChartDataPoint(0, 0)]
            
            for index, t in enumerate(trades_chronologiques):
                solde += 8 if "Gagné" in t["resultat"] else -4
                nouveaux_points.append(ft.LineChartDataPoint(index + 1, solde))
            
            chart_data = ft.LineChartData(
                data_points=nouveaux_points,
                stroke_width=3,
                color="green" if solde >= 0 else "red",
                curved=True
            )
            
            conteneur_graphique.content = ft.LineChart(
                datasets=[chart_data],
                border=ft.border.all(1, "grey"),
                width=380,
                height=150
            )
        except:
            conteneur_graphique.content = ft.Text(
                f"Mode APK Activé 📱\nCourbe de suivi prête pour ton téléphone !\nBalance actuelle : {argent_total}$",
                color="white",
                weight=ft.FontWeight.BOLD,
                size=13
            )

        # --- HISTORIQUE ---
        liste_affichage.controls.clear()
        for t in donnees_locales["trades"]:
            couleur = "green" if "Gagné" in t["resultat"] else "red"
            ligne = ft.Container(
                content=ft.Row(
                    [
                        ft.Text(f"#{t['id']} {t['actif']}", weight=ft.FontWeight.BOLD),
                        ft.Text(f"{t['direction']}", color="grey"),
                        ft.Text(t["resultat"], color=couleur, weight=ft.FontWeight.BOLD)
                    ]
                ),
                padding=10,
                bgcolor="#f5f5f5",
                border_radius=5,
                width=400
            )
            liste_affichage.controls.append(ligne)

    def cliquer_sauvegarder(e):
        if not actif_input.value or not direction_input.value or not statut_input.value:
            message_confirmation.value = "Erreur : Remplis toutes les cases !"
            message_confirmation.color = "red"
            page.update()
            return

        stats["total"] += 1
        est_gagne = "Gagné" in statut_input.value
        texte_res = "Gagné (+8$)" if est_gagne else "Perdu (-4$)"
        if est_gagne: stats["gagnes"] += 1

        nouveau_trade = {
            "id": stats["total"],
            "actif": actif_input.value.upper(),
            "direction": direction_input.value.split()[0],
            "resultat": texte_res
        }
        
        donnees_locales["trades"].insert(0, nouveau_trade)
        sauvegarder_donnees(donnees_locales)
        rafraichir_interface()

        message_confirmation.value = f"Trade #{stats['total']} enregistré !"
        message_confirmation.color = "green"
        
        actif_input.value = ""
        direction_input.value = None
        statut_input.value = None
        page.update()

    def cliquer_reinitialiser(e):
        nonlocal donnees_locales, stats
        donnees_locales = {"stats": {"total": 0, "gagnes": 0}, "trades": []}
        stats = donnees_locales["stats"]
        sauvegarder_donnees(donnees_locales)
        rafraichir_interface()
        message_confirmation.value = "Historique vidé !"
        message_confirmation.color = "orange"
        page.update()

    btn_sauvegarder = ft.ElevatedButton(
        content=ft.Text("Sauvegarder le Trade", color="white", weight=ft.FontWeight.BOLD),
        bgcolor="blue", width=400, on_click=cliquer_sauvegarder
    )

    btn_reinitialiser = ft.TextButton(
        content=ft.Text("Effacer tout l'historique", color="red", weight=ft.FontWeight.BOLD),
        on_click=cliquer_reinitialiser
    )

    rafraichir_interface()

    page.add(
        ft.Column(
            [
                ft.Text("Tableau de Bord", size=16, weight=ft.FontWeight.BOLD),
                tableau_stats,
                ft.Text("Visualisation Graphique", size=14, weight=ft.FontWeight.BOLD),
                conteneur_graphique,
                ft.Divider(height=15),
                ft.Text("Enregistrer un Trade", size=18, weight=ft.FontWeight.BOLD),
                actif_input,
                direction_input,
                statut_input,
                btn_sauvegarder,
                message_confirmation,
                ft.Divider(height=15),
                ft.Text("Historique des Trades", size=16, weight=ft.FontWeight.BOLD),
                liste_affichage,
                ft.Divider(height=20),
                btn_reinitialiser
            ]
        )
    )

ft.app(target=main)
