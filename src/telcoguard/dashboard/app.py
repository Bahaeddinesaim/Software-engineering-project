"""French Streamlit demonstration platform with real-data exploration and inference."""

import base64
import html
import json
import re
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from telcoguard.api.schemas import Customer
from telcoguard.config import Settings
from telcoguard.dashboard.data import contract_rates, load_dataset, load_predictor, read_report

ROOT = Path(__file__).resolve().parents[3]
NAVIGATION = ["Vue d’ensemble", "Simulateur", "Explorer les données", "Le modèle"]
INK = "#203b59"
CORAL = "#e58c65"
TEAL = "#639c97"
CONTRACTS = {"Month-to-month": "Mensuel", "One year": "Un an", "Two year": "Deux ans"}
LABELS = {
    "Yes": "Oui",
    "No": "Non",
    "Female": "Femme",
    "Male": "Homme",
    "Month-to-month": "Mensuel",
    "One year": "Un an",
    "Two year": "Deux ans",
    "Fiber optic": "Fibre optique",
    "No internet service": "Sans Internet",
    "No phone service": "Sans téléphone",
    "Electronic check": "Chèque électronique",
    "Mailed check": "Chèque postal",
    "Bank transfer (automatic)": "Virement automatique",
    "Credit card (automatic)": "Carte bancaire automatique",
}


def icon(name: str) -> str:
    """Render a small consistent inline SVG icon family."""
    paths = {
        "shield": '<path d="M12 3 21 7v6c0 5-9 9-9 9s-9-4-9-9V7Z"/><path d="m8 12 3 3 5-6"/>',
        "people": '<circle cx="9" cy="8" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3M17 5a3 '
        '3 0 0 1 0 6M21 21v-3a6 6 0 0 0-3-5"/>',
        "chart": '<path d="M4 3v17h18M8 15v-4M13 15V7M18 15V4"/>',
        "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/>'
        '<circle cx="12" cy="12" r="1"/>',
        "pulse": '<path d="M2 12h5l3-8 4 16 3-8h5"/>',
    }
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        + paths[name]
        + "</svg>"
    )


def markup(content: str) -> None:
    """Render controlled application HTML."""

    def encode_svg(match: re.Match) -> str:
        svg = match.group().replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
        data = base64.b64encode(svg.encode()).decode()
        return f'<img src="data:image/svg+xml;base64,{data}" alt="">'

    content = re.sub(r"<svg\b.*?</svg>", encode_svg, content, flags=re.DOTALL)
    st.html(content)


def metric(label: str, value: str, note: str, symbol: str) -> None:
    """Display a concise, consistently styled statistic."""
    markup(
        f'<div class="metric-card"><div class="metric-top">{label}'
        f'<div class="metric-icon">{icon(symbol)}</div></div>'
        f'<div class="metric-value">{value}</div><div class="metric-foot">{note}</div></div>'
    )


def section(title: str, note: str = "") -> None:
    """Render a panel heading with supplementary context."""
    markup(f'<div class="section-head"><h3>{title}</h3><span>{note}</span></div>')


def polish(figure: go.Figure, height: int = 285) -> go.Figure:
    """Apply shared chart typography, spacing and accessible hover labels."""
    figure.update_layout(
        height=height,
        margin=dict(l=10, r=12, t=12, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, Arial", color="#748194", size=12),
        showlegend=False,
        hoverlabel=dict(bgcolor="white", font_color=INK),
    )
    figure.update_xaxes(showgrid=False, zeroline=False, fixedrange=True)
    figure.update_yaxes(gridcolor="#edf0f5", zeroline=False, fixedrange=True)
    return figure


def chart(figure: go.Figure, key: str) -> None:
    """Render a responsive chart without an unnecessary editing toolbar."""
    st.plotly_chart(figure, width="stretch", config={"displayModeBar": False}, key=key)


def go_simulator() -> None:
    """Switch navigation before the next widget run."""
    st.session_state["navigation"] = "Simulateur"


def overview(frame: pd.DataFrame | None, metadata: dict, ready: bool) -> None:
    """Present observed cohort statistics and a direct entry to simulation."""
    with st.container(key="overview-hero"):
        left, right = st.columns([1.7, 1], gap="large")
        with left:
            markup(
                '<div role="heading" aria-level="1" class="hero-title">Anticipez les départs.<br>'
                '<span class="hero-accent">Préservez la relation.</span></div>'
                '<p class="hero-copy">Comprendre les signaux de churn, explorer votre '
                "clientèle et transformer une estimation en point de départ pour agir.</p>"
            )
            st.button("Simuler un profil client  →", type="primary", on_click=go_simulator)
        with right:
            markup(
                '<div class="signal-art"><div class="label">TELCOGUARD INTELLIGENCE</div>'
                '<div class="art-title">Chaque signal compte.<br>Chaque relation aussi.</div>'
                '<svg viewBox="0 0 360 80" aria-hidden="true">'
                '<path d="M0 60 C40 60 45 35 80 40 S120 75 160 35 S200 65 240 20 '
                'S300 40 360 4" fill="none" stroke="#efad8e" stroke-width="2.5"/>'
                '<path d="M0 72 C50 75 65 60 100 64 S180 45 225 55 S300 20 360 28" '
                'fill="none" stroke="#647f98" stroke-width="1.5"/>'
                '<circle cx="240" cy="20" r="5" fill="#efad8e"/></svg>'
                '<div class="art-foot"><span>Customer retention, éclairée par la data.</span>'
                "<span>Illustration</span></div></div>"
            )
    if frame is None:
        st.info(
            "Téléchargez les données IBM pour afficher le tableau de bord : "
            "poetry run telcoguard download"
        )
        return
    counts = frame.Churn.value_counts()
    churn = frame.Churn.eq("Yes").mean()
    cards = st.columns(4)
    values = [
        (
            "Clients dans le dataset",
            f"{len(frame):,}".replace(",", " "),
            "Source · IBM Telco",
            "people",
        ),
        (
            "Churn observé",
            f"{churn * 100:.1f} %",
            f"{counts.get('Yes', 0):,} départs observés".replace(",", " "),
            "pulse",
        ),
        (
            "Ancienneté moyenne",
            f"{frame.tenure.mean():.1f} mois",
            "Sur l’ensemble du dataset",
            "chart",
        ),
        (
            "ROC-AUC du modèle",
            f"{metadata['metrics']['roc_auc']:.3f}" if metadata else "—",
            "Évaluation sur le test tenu à l’écart",
            "target",
        ),
    ]
    for column, values_ in zip(cards, values, strict=True):
        with column:
            metric(*values_)
    st.write("")
    left, right = st.columns([1.55, 1], gap="medium")
    with left, st.container(key="panel-contract"):
        section("Le contrat fait la différence", "Taux de churn observé")
        rates = contract_rates(frame)
        rates["rank"] = rates.Contract.map({"Month-to-month": 0, "One year": 1, "Two year": 2})
        rates = rates.sort_values("rank")
        figure = go.Figure(
            go.Bar(
                x=rates.Contract.map(CONTRACTS),
                y=rates.taux * 100,
                marker_color=[CORAL, INK, TEAL],
                width=0.42,
                text=[f"{value:.1f} %" for value in rates.taux * 100],
                textposition="outside",
                textfont=dict(color=INK, size=13),
                customdata=rates.clients,
                hovertemplate="%{x}<br>Churn : %{y:.1f} %<br>%{customdata} clients<extra></extra>",
            )
        )
        figure.update_yaxes(range=[0, max(rates.taux * 100) * 1.25], ticksuffix=" %")
        chart(polish(figure, 260), "contract-overview")
    with right, st.container(key="panel-distribution"):
        section("Une clientèle à comprendre", "Distribution réelle")
        figure = go.Figure(
            go.Pie(
                labels=["Restent", "Churn"],
                values=[counts.get("No", 0), counts.get("Yes", 0)],
                hole=0.78,
                marker=dict(colors=[INK, CORAL], line=dict(color="white", width=4)),
                textinfo="none",
                sort=False,
                hovertemplate="%{label} : %{value} (%{percent})<extra></extra>",
            )
        )
        figure.add_annotation(
            text=f"<b>{100 * (1 - churn):.1f} %</b><br>restent",
            showarrow=False,
            font=dict(size=24, color=INK),
        )
        chart(polish(figure, 225), "distribution-overview")
        markup(
            f'<div class="mini-legend"><span>● Restent <b>{counts.get("No", 0):,}</b></span>'
            f'<span style="color:#bd6a45">● Churn <b>{counts.get("Yes", 0):,}</b></span></div>'
        )
    markup(
        '<div class="insight"><b>Le bon réflexe : regarder au-delà de l’accuracy.</b>'
        "Le dataset contient une majorité de clients qui restent. Precision, recall et "
        "ROC-AUC complètent la lecture du modèle. "
        "Les relations observées ne sont pas causales.</div>"
    )


def preset(name: str) -> dict:
    """Return explicitly hypothetical, coherent customer scenarios."""
    record = {
        "gender": "Female",
        "SeniorCitizen": 0,
        "Partner": "Yes",
        "Dependents": "No",
        "tenure": 12,
        "PhoneService": "Yes",
        "MultipleLines": "No",
        "InternetService": "Fiber optic",
        "OnlineSecurity": "No",
        "OnlineBackup": "No",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "Yes",
        "StreamingMovies": "Yes",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 85.0,
        "TotalCharges": 1020.0,
    }
    if name == "Client fidèle":
        record.update(
            tenure=60,
            Contract="Two year",
            OnlineSecurity="Yes",
            TechSupport="Yes",
            PaymentMethod="Bank transfer (automatic)",
            MonthlyCharges=65.0,
            TotalCharges=3900.0,
            InternetService="DSL",
            Dependents="Yes",
        )
    elif name == "Nouveau client":
        record.update(
            tenure=1,
            MonthlyCharges=29.85,
            TotalCharges=29.85,
            PhoneService="No",
            MultipleLines="No phone service",
            InternetService="DSL",
            OnlineBackup="Yes",
            StreamingTV="No",
            StreamingMovies="No",
        )
    return record


def reset_scenario() -> None:
    """Populate the form and invalidate the result when switching scenarios."""
    for name, value in preset(st.session_state["scenario"]).items():
        st.session_state[f"customer_{name}"] = value
    st.session_state.pop("prediction_result", None)


def select(label: str, feature: str, options: list) -> object:
    """Select a training category with a French display label."""
    return st.selectbox(
        label,
        options,
        format_func=lambda value: LABELS.get(value, str(value)),
        key=f"customer_{feature}",
    )


def simulator(predictor) -> None:
    """Edit a complete customer record and request a real model prediction."""
    markup(
        '<h1 class="page-title">Une relation. Plusieurs signaux.</h1>'
        '<p class="page-desc">Composez un profil et estimez son risque de churn. '
        "Une démonstration concrète, alimentée par le modèle entraîné.</p>"
    )
    if predictor is None:
        st.warning(
            "Le modèle est indisponible. Lancez poetry run telcoguard train, puis rechargez."
        )
        return
    st.selectbox(
        "Charger un scénario de démonstration",
        ["Profil à explorer", "Client fidèle", "Nouveau client"],
        key="scenario",
        on_change=reset_scenario,
    )
    if "customer_tenure" not in st.session_state:
        reset_scenario()
    st.caption("Profils hypothétiques et modifiables · aucune identité client · inférence locale")
    left, right = st.columns([1.55, 1], gap="large")
    with left, st.container(key="panel-simulator-form"), st.form("customer_form"):
        markup(
            '<div class="form-step"><span class="step-number">01</span> Contrat & facturation</div>'
        )
        a, b = st.columns(2)
        with a:
            contract = select("Type de contrat", "Contract", list(CONTRACTS))
            tenure = st.number_input(
                "Ancienneté (mois)", min_value=0, max_value=1200, step=1, key="customer_tenure"
            )
            monthly = st.number_input(
                "Facturation mensuelle",
                min_value=0.0,
                max_value=100000.0,
                step=5.0,
                key="customer_MonthlyCharges",
            )
        with b:
            payment = select(
                "Mode de paiement",
                "PaymentMethod",
                [
                    "Electronic check",
                    "Mailed check",
                    "Bank transfer (automatic)",
                    "Credit card (automatic)",
                ],
            )
            paperless = select("Facture dématérialisée", "PaperlessBilling", ["Yes", "No"])
            total = st.number_input(
                "Montant total facturé",
                min_value=0.0,
                max_value=100000000.0,
                step=10.0,
                key="customer_TotalCharges",
            )
        st.caption("Montants dans l’unité monétaire du dataset IBM ; aucune conversion en euros.")
        markup('<div class="form-step"><span class="step-number">02</span> Services & profil</div>')
        a, b = st.columns(2)
        with a:
            internet = select("Accès Internet", "InternetService", ["DSL", "Fiber optic", "No"])
        with b:
            phone = select("Ligne téléphonique", "PhoneService", ["Yes", "No"])
        additional = {}
        with st.expander("Personnaliser les services et la démographie", expanded=False):
            a, b = st.columns(2)
            with a:
                additional["gender"] = select("Genre", "gender", ["Female", "Male"])
                additional["SeniorCitizen"] = select(
                    "Senior (indicateur IBM)", "SeniorCitizen", [0, 1]
                )
                additional["Partner"] = select("En couple", "Partner", ["Yes", "No"])
                additional["Dependents"] = select("Personnes à charge", "Dependents", ["Yes", "No"])
                additional["MultipleLines"] = select(
                    "Lignes multiples", "MultipleLines", ["Yes", "No", "No phone service"]
                )
            with b:
                for feature, label in [
                    ("OnlineSecurity", "Sécurité en ligne"),
                    ("OnlineBackup", "Sauvegarde en ligne"),
                    ("DeviceProtection", "Protection des appareils"),
                    ("TechSupport", "Assistance technique"),
                    ("StreamingTV", "Streaming TV"),
                    ("StreamingMovies", "Streaming cinéma"),
                ]:
                    additional[feature] = select(
                        label, feature, ["Yes", "No", "No internet service"]
                    )
        submitted = st.form_submit_button(
            "Analyser le risque de churn  →", width="stretch", type="primary"
        )
        if submitted:
            record = additional | {
                "Contract": contract,
                "tenure": tenure,
                "MonthlyCharges": monthly,
                "TotalCharges": total,
                "PaymentMethod": payment,
                "PaperlessBilling": paperless,
                "InternetService": internet,
                "PhoneService": phone,
            }
            if phone == "No":
                record["MultipleLines"] = "No phone service"
            elif record["MultipleLines"] == "No phone service":
                record["MultipleLines"] = "No"
            for feature in [
                "OnlineSecurity",
                "OnlineBackup",
                "DeviceProtection",
                "TechSupport",
                "StreamingTV",
                "StreamingMovies",
            ]:
                if internet == "No":
                    record[feature] = "No internet service"
                elif record[feature] == "No internet service":
                    record[feature] = "No"
            try:
                validated = Customer.model_validate(record)
                with st.spinner("Analyse des signaux du profil…"):
                    result = predictor.predict(validated.model_dump())
                st.session_state["prediction_result"] = {"result": result, "record": record}
            except Exception:
                st.session_state.pop("prediction_result", None)
                st.error("L’analyse n’a pas abouti. Vérifiez les valeurs et le modèle local.")
    with right, st.container(key="panel-prediction"):
        result_state = st.session_state.get("prediction_result")
        if not result_state:
            markup(
                '<div class="empty-result"><div class="empty-icon">' + icon("target") + "</div>"
                "<h3>Le prochain signal<br>commence ici.</h3>"
                "<p>Ajustez le profil, puis lancez l’analyse.<br>"
                "Votre estimation apparaîtra dans cet espace.</p></div>"
            )
        else:
            result = result_state["result"]
            probability = result["churn_probability"]
            risk = result["risk_level"]
            names = {"low": "Risque faible", "medium": "Risque modéré", "high": "Risque élevé"}
            markup(
                '<div class="result-label">PROBABILITÉ ESTIMÉE DE CHURN</div>'
                f'<div class="result-value">{probability * 100:.1f}'
                '<span class="result-unit"> %</span></div>'
                f'<div class="risk-badge risk-{risk}">{names[risk]}</div>'
            )
            figure = go.Figure(
                go.Indicator(
                    mode="gauge",
                    value=probability * 100,
                    gauge=dict(
                        axis=dict(range=[0, 100], tickvals=[0, 30, 70, 100], ticksuffix="%"),
                        bar=dict(color=INK, thickness=0.3),
                        bgcolor="white",
                        borderwidth=0,
                        steps=[
                            dict(range=[0, 30], color="#deeee5"),
                            dict(range=[30, 70], color="#f6e7ca"),
                            dict(range=[70, 100], color="#f1d1c2"),
                        ],
                    ),
                )
            )
            figure = polish(figure, 180)
            figure.update_layout(margin=dict(l=28, r=28, t=10, b=20))
            chart(figure, "risk-gauge")
            st.write("**Départ prédit**" if result["prediction"] else "**Maintien prédit**")
            st.caption("Décision au seuil de 50 % · modèle " + result["model_version"])
            markup(
                '<p class="result-note">Une estimation statistique pour orienter la réflexion, '
                "pas une certitude sur ce client. Probabilités non recalibrées.</p>"
            )
            st.download_button(
                "Télécharger cette analyse",
                json.dumps(result_state, indent=2, ensure_ascii=False),
                "analyse_telcoguard.json",
                "application/json",
                width="stretch",
            )
            with st.expander("Voir le profil effectivement analysé"):
                st.json(result_state["record"])
        st.divider()
        markup(
            '<p class="result-note"><b>Comment lire le score ?</b><br>'
            "Faible : moins de 30 %<br>Modéré : de 30 % à moins de 70 %<br>"
            "Élevé : à partir de 70 %<br><br>Ces seuils sont des conventions pédagogiques.</p>"
        )


def explorer(frame: pd.DataFrame | None) -> None:
    """Explore actual dataset cohorts without exposing identifiers."""
    markup(
        '<h1 class="page-title">Derrière les chiffres, des comportements.</h1>'
        '<p class="page-desc">Explorez le dataset IBM, isolez une population et '
        "observez les signaux associés au churn.</p>"
    )
    if frame is None:
        st.info("Données indisponibles. Lancez poetry run telcoguard download.")
        return
    with st.container(key="panel-filters"):
        a, b, c = st.columns(3)
        contracts = a.multiselect(
            "Contrat", list(CONTRACTS), default=list(CONTRACTS), format_func=CONTRACTS.get
        )
        internet = b.multiselect(
            "Internet",
            ["DSL", "Fiber optic", "No"],
            default=["DSL", "Fiber optic", "No"],
            format_func=lambda value: LABELS.get(value, value),
        )
        tenure = c.slider(
            "Ancienneté (mois)", 0, int(frame.tenure.max()), (0, int(frame.tenure.max()))
        )
    cohort = frame[
        frame.Contract.isin(contracts)
        & frame.InternetService.isin(internet)
        & frame.tenure.between(*tenure)
    ]
    if cohort.empty:
        st.info("Aucun profil dans cette sélection. Élargissez les filtres pour poursuivre.")
        return
    st.write("")
    columns = st.columns(3)
    with columns[0]:
        metric(
            "Profils sélectionnés",
            f"{len(cohort):,}".replace(",", " "),
            "Cohorte filtrée",
            "people",
        )
    with columns[1]:
        metric(
            "Churn de la cohorte",
            f"{cohort.Churn.eq('Yes').mean() * 100:.1f} %",
            "Observation, pas prédiction",
            "pulse",
        )
    with columns[2]:
        metric(
            "Facture mensuelle moyenne",
            f"{cohort.MonthlyCharges.mean():.2f}",
            "Unité monétaire du dataset",
            "chart",
        )
    st.write("")
    a, b = st.columns(2)
    with a, st.container(key="panel-tenure"):
        section("L’ancienneté, en perspective")
        figure = go.Figure()
        for target, label, color in [("No", "Restent", INK), ("Yes", "Churn", CORAL)]:
            figure.add_trace(
                go.Histogram(
                    x=cohort.loc[cohort.Churn.eq(target), "tenure"],
                    name=label,
                    marker_color=color,
                    xbins=dict(start=0, end=75, size=6),
                    opacity=0.85,
                )
            )
        figure.update_layout(barmode="group", bargap=0.15)
        figure.update_xaxes(title="Ancienneté (mois)")
        figure.update_yaxes(title="Clients")
        figure = polish(figure)
        figure.update_layout(showlegend=True, legend=dict(orientation="h", y=1.18))
        chart(figure, "cohort-tenure")
    with b, st.container(key="panel-service"):
        section("Churn par accès Internet")
        rates = cohort.assign(churn=cohort.Churn.eq("Yes")).groupby("InternetService").churn.mean()
        figure = go.Figure(
            go.Bar(
                x=[LABELS.get(name, name) for name in rates.index],
                y=rates * 100,
                marker_color=[INK, CORAL, TEAL],
                width=0.5,
            )
        )
        figure.update_yaxes(ticksuffix=" %", range=[0, 100])
        chart(polish(figure), "cohort-internet")
    with st.expander("Consulter les données de la sélection (identifiants exclus)"):
        markup(
            '<div class="table-wrap">'
            + cohort.head(100).to_html(index=False, classes="cohort-table", escape=True, border=0)
            + "</div>"
        )
        st.caption(
            "Aperçu limité aux 100 premières lignes de la sélection ; graphiques calculés "
            "sur toute la cohorte."
        )
        st.caption(
            "Données pédagogiques IBM. Les droits de redistribution du CSV restent à clarifier."
        )


def model_page(metadata: dict) -> None:
    """Explain the measured model, baseline comparison and reproducibility."""
    markup(
        '<h1 class="page-title">Un modèle simple. Des preuves concrètes.</h1>'
        '<p class="page-desc">Régression logistique, prétraitement intégré et évaluation '
        "sur des observations tenues à l’écart de l’apprentissage.</p>"
    )
    if not metadata:
        st.info("Aucun rapport d’évaluation disponible. Entraînez le modèle pour commencer.")
        return
    metrics = metadata["metrics"]
    for column, (name, label) in zip(
        st.columns(4),
        [
            ("accuracy", "Accuracy"),
            ("precision", "Precision"),
            ("recall", "Recall"),
            ("f1", "F1-score"),
        ],
        strict=True,
    ):
        with column:
            metric(label, f"{metrics[name] * 100:.1f} %", "Test · seuil de décision 0,5", "target")
    st.write("")
    a, b = st.columns([1.2, 1])
    with a, st.container(key="panel-comparison"):
        section("La baseline à l’épreuve", f"{metadata['test_rows']:,} observations de test")
        labels = ["Accuracy", "Precision", "Recall", "F1", "ROC-AUC"]
        keys = ["accuracy", "precision", "recall", "f1", "roc_auc"]
        figure = go.Figure()
        for source, label, color in [
            ("metrics", "LogisticRegression", INK),
            ("dummy_metrics", "DummyClassifier", CORAL),
        ]:
            figure.add_trace(
                go.Bar(
                    name=label, x=labels, y=[metadata[source][k] for k in keys], marker_color=color
                )
            )
        figure.update_yaxes(range=[0, 1], tickformat=".0%")
        figure = polish(figure)
        figure.update_layout(barmode="group", showlegend=True, legend=dict(orientation="h", y=1.18))
        chart(figure, "model-comparison")
    with b, st.container(key="panel-confusion"):
        section("Ce que le modèle détecte", "Matrice de confusion")
        matrix = metrics["confusion_matrix"]
        figure = go.Figure(
            go.Heatmap(
                z=matrix,
                x=["Prédit : reste", "Prédit : churn"],
                y=["Réel : reste", "Réel : churn"],
                colorscale=[[0, "#f4e9df"], [1, INK]],
                text=matrix,
                texttemplate="%{text}",
                textfont=dict(size=22),
                showscale=False,
                xgap=5,
                ygap=5,
                hovertemplate="%{y}<br>%{x}<br>%{z} observations<extra></extra>",
            )
        )
        figure.update_yaxes(autorange="reversed")
        chart(polish(figure), "model-confusion")
    markup(
        '<div class="pipeline"><div><small>01 / ACQUÉRIR</small><b>Les données IBM</b>'
        "<p>Schéma contrôlé, données manquantes identifiées, identifiants exclus.</p></div>"
        "<div><small>02 / SÉPARER</small><b>80 % train · 20 % test</b>"
        "<p>Split stratifié, graine 42. Aucun ajustement sur le test.</p></div>"
        "<div><small>03 / APPRENDRE</small><b>Une Pipeline complète</b>"
        "<p>Imputation, encodage, normalisation et régression logistique.</p></div>"
        "<div><small>04 / ÉVALUER</small><b>Mesurer, puis servir</b>"
        "<p>Métriques sur le test. Pipeline persistée et API authentifiée.</p></div></div>"
    )
    with st.expander("Fiche technique et limites"):
        st.write(
            f"Version **{metadata['model_version']}** · scikit-learn "
            f"**{metadata['sklearn_version']}** · entraînement **{metadata['trained_at'][:10]}**"
        )
        st.code(metadata["dataset_sha256"], language=None)
        st.write(
            "Données pédagogiques historiques ; calibration dédiée, validation temporelle et "
            "audit d’équité non réalisés. Une association n’est pas une causalité. "
            "La licence spécifique du CSV doit être clarifiée avant redistribution."
        )
        st.download_button(
            "Exporter le rapport d’évaluation",
            json.dumps(metadata, indent=2),
            "evaluation_telcoguard.json",
            "application/json",
        )


def main() -> None:
    """Load trusted local resources and render the selected demonstration page."""
    st.set_page_config(
        page_title="TelcoGuard AI · Intelligence de fidélisation",
        page_icon="◈",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    markup(
        "<style>" + Path(__file__).with_name("style.css").read_text(encoding="utf-8") + "</style>"
    )
    settings = Settings()
    model_path = settings.model_path
    if not model_path.is_absolute():
        model_path = ROOT / model_path
    predictor = None
    model_error = None
    if model_path.exists():
        try:
            predictor = load_predictor(str(model_path), model_path.stat().st_mtime)
        except Exception:
            model_error = (
                "Le modèle local n’a pas pu être chargé. Réentraînez-le pour rétablir l’analyse."
            )
    frame = None
    data_path = ROOT / "data/raw/telco.csv"
    data_error = None
    if data_path.exists():
        try:
            frame = load_dataset(str(data_path), data_path.stat().st_mtime)
        except Exception:
            data_error = (
                "Le CSV local ne respecte pas le schéma attendu. Relancez le téléchargement."
            )
    metadata = predictor.metadata if predictor else read_report(ROOT / "reports/evaluation.json")
    with st.sidebar:
        markup(
            '<div class="brand"><div class="brand-mark">' + icon("shield") + "</div>"
            '<div><div class="brand-name">TelcoGuard<span>.</span></div>'
            '<div class="brand-tag">CUSTOMER INTELLIGENCE</div></div></div>'
            '<div class="nav-label">ESPACE D’ANALYSE</div>'
        )
        page = st.radio("Navigation", NAVIGATION, key="navigation", label_visibility="collapsed")
        markup(
            '<div class="sidebar-note"><b>La data au service du lien.</b>'
            "<p>Une plateforme pour explorer, comprendre et démontrer la prédiction du churn.</p>"
            '</div><div class="sidebar-footer">PROJET ACADÉMIQUE · EPITA<br>'
            "<b>SAIM Bahaeddine<br>Hazem OUNI</b><br>SOENFO · 2026–2027</div>"
        )
    status = "Modèle prêt" if predictor else "Modèle indisponible"
    markup(
        '<div class="topline"><span>Workspace <span style="color:#c1c9d3"> / </span>'
        f' <strong>{html.escape(page)}</strong></span><span class="status '
        f'{"" if predictor else "offline"}"><span class="status-dot"></span>{status}'
        " · inférence locale</span></div>"
    )
    if model_error:
        st.warning(model_error)
    if data_error:
        st.warning(data_error)
    if page == NAVIGATION[0]:
        overview(frame, metadata, predictor is not None)
    elif page == NAVIGATION[1]:
        simulator(predictor)
    elif page == NAVIGATION[2]:
        explorer(frame)
    else:
        model_page(metadata)
    markup(
        '<div class="footnote"><span>TelcoGuard AI · Démonstration académique · '
        "Données IBM Telco</span><span>Estimer le risque. Éclairer la décision.</span></div>"
    )
