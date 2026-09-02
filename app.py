from datetime import date
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Configuração inicial
st.set_page_config(
    page_title="Co-digestão Anaeróbia", page_icon="🧪", layout="wide"
)

# Style CSS Otimizado
st.markdown(
    """
<style>
    .stApp { background-color: #0F0F11; color: #E4E4E7; }
    .badge-status-green {
        background-color: rgba(34, 197, 94, 0.15); color: #4ADE80;
        border: 1px solid rgba(74, 222, 128, 0.3);
        padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; display: inline-block;
    }
    .badge-status-yellow {
        background-color: rgba(234, 179, 8, 0.15); color: #FACC15;
        border: 1px solid rgba(250, 204, 21, 0.3);
        padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; display: inline-block;
    }
    .pill-tag {
        background-color: #1E1E24; color: #818CF8; border: 1px solid rgba(129, 140, 248, 0.2);
        padding: 4px 12px; border-radius: 12px; font-size: 13px; font-weight: 600; display: inline-block; margin-bottom: 6px;
    }
    div[data-testid="stExpander"] {
        background-color: #18181C !important; border: 1px solid #27272A !important;
        border-radius: 12px !important; margin-bottom: 16px !important;
    }
    button[kind="primary"] {
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important; border: none !important; font-weight: 600 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# FUNÇÕES COM CACHE DE ALTA PERFORMANCE
# ---------------------------------------------------------
@st.cache_data(show_spinner=False)
def gerar_grafico_rendimento(labels, rend, ch4):
    fig, ax1 = plt.subplots(figsize=(6, 2.8))
    fig.patch.set_facecolor("#18181C")
    ax1.set_facecolor("#18181C")

    ax1.bar(
        labels,
        rend,
        color="#6366F1",
        width=0.35,
        alpha=0.85,
        label="Rendimento",
    )
    ax1.set_ylabel(
        "mL CH₄ / g SV", color="#818CF8", fontsize=9, fontweight="bold"
    )
    ax1.tick_params(colors="#A1A1AA", labelsize=8)

    ax2 = ax1.twinx()
    ax2.plot(
        labels, ch4, color="#FACC15", marker="o", linewidth=2, label="% CH₄"
    )
    ax2.set_ylabel(
        "% CH₄ no Biogás", color="#FACC15", fontsize=9, fontweight="bold"
    )
    ax2.tick_params(colors="#A1A1AA", labelsize=8)
    ax2.set_ylim(0, 100)

    for spine in ax1.spines.values():
        spine.set_color("#27272A")
    for spine in ax2.spines.values():
        spine.set_color("#27272A")

    plt.close(fig)
    return fig


@st.cache_data(show_spinner=False)
def gerar_grafico_otimizacao(curva_x, curva_y, df_inoc, df_rend, p_otima, p1, p2):
    fig, ax = plt.subplots(figsize=(6, 3))
    fig.patch.set_facecolor("#18181C")
    ax.set_facecolor("#18181C")

    ax.plot(
        curva_x, curva_y, color="#818CF8", linewidth=2.5, label="Modelo Smooth"
    )
    ax.scatter(
        df_inoc,
        df_rend,
        color="#FACC15",
        s=40,
        zorder=5,
        label="Histórico",
    )
    ax.axvline(
        x=p_otima,
        color="#4ADE80",
        linestyle="--",
        label=f"Ótimo ({p1}:{p2})",
    )

    ax.set_xlabel("Proporção de Inóculo", color="#A1A1AA", fontsize=9)
    ax.set_ylabel("Rendimento (mL CH4/g SV)", color="#A1A1AA", fontsize=9)
    ax.tick_params(colors="#A1A1AA", labelsize=8)
    ax.grid(True, linestyle=":", alpha=0.15)
    ax.legend(
        facecolor="#27272A", edgecolor="none", labelcolor="#E4E4E7", fontsize=8
    )

    for spine in ax.spines.values():
        spine.set_color("#27272A")

    plt.close(fig)
    return fig


# Inicialização de Estado
if "modal_ativo" not in st.session_state:
    st.session_state.modal_ativo = None
if "etapa_modal_vol" not in st.session_state:
    st.session_state.etapa_modal_vol = 1
if "etapa_modal_rend" not in st.session_state:
    st.session_state.etapa_modal_rend = 1
if "scroll_to_novo" not in st.session_state:
    st.session_state.scroll_to_novo = False

if "compostos" not in st.session_state:
    st.session_state.compostos = [
        {"nome": "Inóculo 1", "valor": 15.0, "unidade": "g/mL"},
        {"nome": "Substrato 1", "valor": 40.0, "unidade": "g/g"},
    ]

if "condicoes" not in st.session_state:
    st.session_state.condicoes = [
        {"headspace": 30.0, "composicao": "2:1", "replicas": 3},
        {"headspace": 30.0, "composicao": "1:1", "replicas": 3},
    ]

if "lista_lancamentos" not in st.session_state:
    st.session_state.lista_lancamentos = [
        {
            "id": "l_1",
            "titulo": "Lançamento 16/06/2023",
            "status": "Finalizado",
            "data_str": "16/06/2023 • 31 dias de digestão",
            "tem_grafico": True,
            "massa_sv_total_val": 14.40,
            "massa_sv_total": "14.40 g SV",
            "carga_volumetrica": "0.082 g SV/mL",
            "compostos": [
                {
                    "nome": "Inóculo 1",
                    "conc": "12.0 g/mL",
                    "qtd_total": "360.0 mL",
                },
                {
                    "nome": "Substrato 1",
                    "conc": "40.0 g/g",
                    "qtd_total": "120.0 g",
                },
            ],
            "composicoes_estudadas": [
                {
                    "proporcao": "2:1",
                    "carga": "0.082 g SV/mL",
                    "massa_sv_val": 14.40,
                    "reagentes": [
                        {"nome": "Inóculo 1", "qtd": "120.0 mL"},
                        {"nome": "Substrato 1", "qtd": "40.0 g"},
                    ],
                },
                {
                    "proporcao": "1:1",
                    "carga": "0.082 g SV/mL",
                    "massa_sv_val": 14.40,
                    "reagentes": [
                        {"nome": "Inóculo 1", "qtd": "87.5 mL"},
                        {"nome": "Substrato 1", "qtd": "87.5 g"},
                    ],
                },
                {
                    "proporcao": "1:2",
                    "carga": "0.082 g SV/mL",
                    "massa_sv_val": 14.40,
                    "reagentes": [
                        {"nome": "Inóculo 1", "qtd": "60.0 mL"},
                        {"nome": "Substrato 1", "qtd": "120.0 g"},
                    ],
                },
            ],
            "dados_rendimento": [
                {
                    "composicao": "2:1",
                    "fracao_metano": 55.0,
                    "vol_biogas": 310.0,
                    "vol_ch4": 170.5,
                    "rendimento": 220.5,
                },
                {
                    "composicao": "1:1",
                    "fracao_metano": 68.0,
                    "vol_biogas": 450.0,
                    "vol_ch4": 306.0,
                    "rendimento": 380.0,
                },
                {
                    "composicao": "1:2",
                    "fracao_metano": 62.0,
                    "vol_biogas": 390.0,
                    "vol_ch4": 241.8,
                    "rendimento": 295.0,
                },
            ],
        }
    ]


# ---------------------------------------------------------
# MODAIS
# ---------------------------------------------------------
@st.dialog("➕ Registrar Novo Lançamento", width="small")
def modal_calcular_volume():
    if st.session_state.etapa_modal_vol == 1:
        st.subheader("1. Identificação e Período")

        nome_lancamento = st.text_input(
            "Nome do Lançamento",
            value=f"Lançamento {date.today().strftime('%d/%m/%Y')}",
            key="input_nome_lancamento",
        )

        st.checkbox("Fazer correção de pH no meio", value=False)
        st.divider()

        st.markdown("**Período de Digestão Estimado**")
        d_col1, d_col2 = st.columns(2)
        d_inicio = d_col1.date_input("Data Inicial", value=date.today())
        d_fim = d_col2.date_input("Data Final", value=date.today())

        dias = max(0, (d_fim - d_inicio).days)
        st.info(f"⏱️ Tempo total previsto: **{dias} dias**")
        st.divider()

        _, col_next = st.columns([1, 1])
        with col_next:
            if st.button("Próximo ➔", use_container_width=True, type="primary"):
                st.session_state.temp_dt_inicio = d_inicio
                st.session_state.temp_dias = dias
                st.session_state.temp_nome_lancamento = nome_lancamento
                st.session_state.etapa_modal_vol = 2
                st.rerun()

    elif st.session_state.etapa_modal_vol == 2:
        st.subheader("2. Condições dos Reatores")

        for i, cond in enumerate(st.session_state.condicoes):
            with st.container(border=True):
                st.markdown(f"**Condição #{i+1}**")
                c1, c2, c3 = st.columns(3)
                hs = c1.number_input(
                    "Headspace (%)",
                    value=cond["headspace"],
                    step=5.0,
                    key=f"hs_{i}",
                )
                comp = c2.text_input(
                    "Razão (I:S)", value=cond["composicao"], key=f"comp_{i}"
                )
                rep = c3.number_input(
                    "Réplicas", value=cond["replicas"], step=1, key=f"rep_{i}"
                )

                st.session_state.condicoes[i] = {
                    "headspace": hs,
                    "composicao": comp,
                    "replicas": rep,
                }

        if st.button("➕ Adicionar Condição", key="add_cond"):
            st.session_state.condicoes.append(
                {"headspace": 30.0, "composicao": "1:1", "replicas": 3}
            )
            st.rerun()

        st.divider()

        col_back, col_next = st.columns(2)
        with col_back:
            if st.button("⬅ Voltar", use_container_width=True):
                st.session_state.etapa_modal_vol = 1
                st.rerun()
        with col_next:
            if st.button("Próximo ➔", use_container_width=True, type="primary"):
                st.session_state.etapa_modal_vol = 3
                st.rerun()

    elif st.session_state.etapa_modal_vol == 3:
        st.subheader("3. Caracterização dos Compostos")

        for i, comp in enumerate(st.session_state.compostos):
            with st.container(border=True):
                st.markdown(f"**Composto #{i+1}**")
                novo_nome = st.text_input(
                    "Nome", value=comp["nome"], key=f"nome_comp_{i}"
                )

                c_val, c_unit = st.columns([2, 1])
                novo_val = c_val.number_input(
                    "Concentração SV",
                    value=comp["valor"],
                    key=f"val_comp_{i}",
                )
                nova_unit = c_unit.selectbox(
                    "Unidade",
                    ["g/mL", "g/g"],
                    index=0 if comp["unidade"] == "g/mL" else 1,
                    key=f"unit_comp_{i}",
                )

                st.session_state.compostos[i] = {
                    "nome": novo_nome,
                    "valor": novo_val,
                    "unidade": nova_unit,
                }

        if st.button("➕ Adicionar Composto", key="add_comp"):
            st.session_state.compostos.append(
                {
                    "nome": f"Composto {len(st.session_state.compostos) + 1}",
                    "valor": 0.0,
                    "unidade": "g/mL",
                }
            )
            st.rerun()

        st.divider()

        col_back, col_finish = st.columns(2)
        with col_back:
            if st.button("⬅ Voltar", use_container_width=True):
                st.session_state.etapa_modal_vol = 2
                st.rerun()

        with col_finish:
            if st.button(
                "🚀 Finalizar e Calcular",
                type="primary",
                use_container_width=True,
            ):
                vol_frasco = 250.0
                hs_medio = (
                    st.session_state.condicoes[0]["headspace"]
                    if st.session_state.condicoes
                    else 30.0
                )
                vol_util = vol_frasco * (1 - (hs_medio / 100.0))

                compostos_calculados = []
                qtd_compostos = len(st.session_state.compostos)
                massa_sv_total = 0.0
                total_replicas = sum(
                    c["replicas"] for c in st.session_state.condicoes
                )

                for c in st.session_state.compostos:
                    unidade = c["unidade"]
                    val_conc = c["valor"] if c["valor"] > 0 else 1.0

                    if unidade == "g/mL":
                        qtd_por_reator = round(
                            (vol_util / max(1, qtd_compostos)), 1
                        )
                        qtd_total_ensaio = round(
                            qtd_por_reator * max(1, total_replicas), 1
                        )
                        qtd_str = f"{qtd_por_reator} mL"
                        qtd_total_str = f"{qtd_total_ensaio} mL"
                        massa_sv = qtd_por_reator * (val_conc / 100.0)
                    else:
                        qtd_por_reator = round(
                            (vol_util / max(1, qtd_compostos)) * 0.5, 1
                        )
                        qtd_total_ensaio = round(
                            qtd_por_reator * max(1, total_replicas), 1
                        )
                        qtd_str = f"{qtd_por_reator} g"
                        qtd_total_str = f"{qtd_total_ensaio} g"
                        massa_sv = qtd_por_reator * (val_conc / 100.0)

                    massa_sv_total += massa_sv
                    compostos_calculados.append(
                        {
                            "nome": c["nome"],
                            "conc": f"{c['valor']} {unidade}",
                            "qtd": qtd_str,
                            "qtd_total": qtd_total_str,
                        }
                    )

                carga_composicao = (
                    massa_sv_total / vol_util if vol_util > 0 else 0.0
                )
                composicoes_estudadas = [
                    {
                        "proporcao": cond["composicao"],
                        "carga": f"{carga_composicao:.3f} g SV/mL",
                        "massa_sv_val": massa_sv_total,
                        "reagentes": [
                            {"nome": comp["nome"], "qtd": comp["qtd"]}
                            for comp in compostos_calculados
                        ],
                    }
                    for cond in st.session_state.condicoes
                ]

                nome_lan = st.session_state.get(
                    "temp_nome_lancamento",
                    f"Lançamento {date.today().strftime('%d/%m/%Y')}",
                )
                dt_ini = st.session_state.get("temp_dt_inicio", date.today())
                dias_lan = st.session_state.get("temp_dias", 0)

                novo_item = {
                    "id": f"lanc_{len(st.session_state.lista_lancamentos) + 1}",
                    "titulo": nome_lan,
                    "status": "Em andamento",
                    "data_str": f"{dt_ini.strftime('%d/%m/%Y')} • {dias_lan} dias de digestão",
                    "tem_grafico": False,
                    "massa_sv_total_val": massa_sv_total,
                    "massa_sv_total": f"{massa_sv_total:.2f} g SV",
                    "carga_volumetrica": f"{carga_composicao:.3f} g SV/mL",
                    "compostos": compostos_calculados,
                    "composicoes_estudadas": composicoes_estudadas,
                    "dados_rendimento": None,
                }

                st.session_state.lista_lancamentos.insert(0, novo_item)
                st.session_state.toast_msg = "✅ Lançamento criado com sucesso!"
                st.session_state.scroll_to_novo = True
                st.session_state.etapa_modal_vol = 1
                st.session_state.modal_ativo = None
                st.rerun()


@st.dialog("📊 Cálculo de Rendimento", width="medium")
def modal_calcular_rendimento():
    if not st.session_state.lista_lancamentos:
        st.warning("Nenhum lançamento encontrado.")
        return

    if st.session_state.etapa_modal_rend == 1:
        titulos = [
            item["titulo"] for item in st.session_state.lista_lancamentos
        ]
        escolha = st.selectbox("Selecione o Lançamento:", titulos)
        lanc = next(
            i for i in st.session_state.lista_lancamentos if i["titulo"] == escolha
        )

        st.divider()
        num_replicas = (
            st.session_state.condicoes[0]["replicas"]
            if st.session_state.condicoes
            else 3
        )
        dados_replicas_temp = []

        for idx_comp, comp in enumerate(lanc.get("composicoes_estudadas", [])):
            prop = comp["proporcao"]
            massa_sv = comp.get("massa_sv_val", 1.0)

            with st.container(border=True):
                st.markdown(f"### 🧪 Razão `(I:S) {prop}`")
                replicas_comp = []

                for rep in range(1, num_replicas + 1):
                    st.caption(f"**Réplica {rep}**")
                    c1, c2 = st.columns(2)
                    metano_pct = c1.number_input(
                        "Metano (% CH₄)",
                        0.0,
                        100.0,
                        60.0,
                        step=0.5,
                        key=f"rep_pct_{escolha}_{idx_comp}_{rep}",
                    )
                    vol_biogas = c2.number_input(
                        "Biogás Total (mL)",
                        0.0,
                        value=350.0,
                        step=10.0,
                        key=f"rep_vol_{escolha}_{idx_comp}_{rep}",
                    )

                    vol_ch4 = vol_biogas * (metano_pct / 100.0)
                    rend_esp = vol_ch4 / massa_sv if massa_sv > 0 else 0.0
                    replicas_comp.append(
                        {
                            "replica": rep,
                            "metano_pct": metano_pct,
                            "vol_biogas": vol_biogas,
                            "vol_ch4": vol_ch4,
                            "rendimento": rend_esp,
                        }
                    )

                dados_replicas_temp.append(
                    {
                        "proporcao": prop,
                        "massa_sv": massa_sv,
                        "replicas": replicas_comp,
                    }
                )

        st.divider()
        if st.button(
            "Calcular Médias ➔", type="primary", use_container_width=True
        ):
            st.session_state.temp_rend_data = {
                "titulo": escolha,
                "composicoes": dados_replicas_temp,
            }
            st.session_state.etapa_modal_rend = 2
            st.rerun()

    elif st.session_state.etapa_modal_rend == 2:
        st.subheader("📊 Resumo das Médias Obtidas")
        temp_data = st.session_state.get("temp_rend_data", {})
        resultados_finais = []

        for comp in temp_data.get("composicoes", []):
            reps = comp["replicas"]
            media_metano = np.mean([r["metano_pct"] for r in reps])
            media_vol_biogas = np.mean([r["vol_biogas"] for r in reps])
            media_rendimento = np.mean([r["rendimento"] for r in reps])

            with st.container(border=True):
                st.markdown(f"**Razão (I:S): `{comp['proporcao']}`**")
                m1, m2, m3 = st.columns(3)
                m1.metric("Média % CH₄", f"{media_metano:.1f}%")
                m2.metric("Média Biogás", f"{media_vol_biogas:.1f} mL")
                m3.metric("Rendimento", f"{media_rendimento:.1f} mL/g SV")

            resultados_finais.append(
                {
                    "composicao": comp["proporcao"],
                    "fracao_metano": media_metano,
                    "vol_biogas": media_vol_biogas,
                    "vol_ch4": media_vol_biogas * (media_metano / 100.0),
                    "rendimento": media_rendimento,
                }
            )

        st.divider()
        c_back, c_save = st.columns(2)
        with c_back:
            if st.button("⬅ Voltar", use_container_width=True):
                st.session_state.etapa_modal_rend = 1
                st.rerun()
        with c_save:
            if st.button(
                "💾 Salvar e Atualizar",
                type="primary",
                use_container_width=True,
            ):
                target = next(
                    i
                    for i in st.session_state.lista_lancamentos
                    if i["titulo"] == temp_data["titulo"]
                )
                target["tem_grafico"] = True
                target["status"] = "Finalizado"
                target["dados_rendimento"] = resultados_finais

                gerar_grafico_rendimento.clear()

                st.session_state.toast_msg = "🎉 Dados gravados!"
                st.session_state.etapa_modal_rend = 1
                st.session_state.modal_ativo = None
                st.rerun()


@st.dialog("🎯 Otimização Estatística", width="medium")
def modal_estimar_composicao():
    historico = []
    for l in st.session_state.lista_lancamentos:
        if l["status"] == "Finalizado" and l.get("dados_rendimento"):
            for d in l["dados_rendimento"]:
                try:
                    p = [
                        float(x)
                        for x in d["composicao"].split(":")
                        if x.strip()
                    ]
                    if len(p) >= 2:
                        tot = sum(p)
                        historico.append(
                            {
                                "Inoculo": p[0] / tot,
                                "Substrato": p[1] / tot,
                                "Rendimento": d["rendimento"],
                            }
                        )
                except Exception:
                    continue

    if len(historico) < 3:
        st.info(
            "ℹ️ Finalize pelo menos 3 medições de composições para realizar a otimização."
        )
        return

    df = pd.DataFrame(historico)
    X = np.column_stack(
        [
            np.ones(len(df)),
            df["Inoculo"],
            df["Substrato"],
            df["Inoculo"] * df["Substrato"],
        ]
    )
    y = df["Rendimento"].values
    coef, _, _, _ = np.linalg.lstsq(X, y, rcond=None)

    grid = np.linspace(0.1, 0.9, 100)
    best_rend, best_prop = -1, (0.5, 0.5)
    cx, cy = [], []

    for inoc in grid:
        subst = 1.0 - inoc
        pred = np.dot([1.0, inoc, subst, inoc * subst], coef)
        cx.append(inoc)
        cy.append(pred)
        if pred > best_rend:
            best_rend = pred
            best_prop = (inoc, subst)

    st.success("✨ **Composição Ideal Encontrada**")
    p1, p2 = int(round(best_prop[0] * 100)), int(round(best_prop[1] * 100))

    c1, c2, c3 = st.columns(3)
    c1.metric("Inóculo", f"{p1}%")
    c2.metric("Substrato", f"{p2}%")
    c3.metric("Rendimento Est.", f"{best_rend:.1f} mL/g SV")

    fig = gerar_grafico_otimizacao(
        cx, cy, df["Inoculo"], df["Rendimento"], best_prop[0], p1, p2
    )
    st.pyplot(fig)


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------
st.title("👋 Olá, Pesquisador!")
st.caption("Acompanhamento e otimização dos processos de co-digestão")

if "toast_msg" in st.session_state and st.session_state.toast_msg:
    st.toast(st.session_state.toast_msg, icon="🎉")
    del st.session_state["toast_msg"]

st.write("")
col_b1, col_b2, col_b3 = st.columns(3)

with col_b1:
    if st.button(
        "➕ Registrar lançamento", type="primary", use_container_width=True
    ):
        st.session_state.etapa_modal_vol = 1
        st.session_state.modal_ativo = "volume"
    st.caption(
        "Registre e calcule automaticamente o volume ou massa dos compostos a serem utilizados"
    )

with col_b2:
    if st.button("📊 Calcular rendimento", use_container_width=True):
        st.session_state.etapa_modal_rend = 1
        st.session_state.modal_ativo = "rendimento"
    st.caption(
        "Insira os dados medidos nas réplicas para obter médias e gráficos de rendimento"
    )

with col_b3:
    if st.button("🎯 Estimar melhor composição", use_container_width=True):
        st.session_state.modal_ativo = "otimizacao"
    st.caption(
        "Analise o histórico e encontre a proporção ideal entre os compostos"
    )

# Controle de Exibição dos Modais
if st.session_state.modal_ativo == "volume":
    modal_calcular_volume()
elif st.session_state.modal_ativo == "rendimento":
    modal_calcular_rendimento()
elif st.session_state.modal_ativo == "otimizacao":
    modal_estimar_composicao()

st.divider()
st.subheader("📁 Meus Lançamentos")

for idx, item in enumerate(st.session_state.lista_lancamentos):
    if idx == 0:
        st.markdown(
            '<div id="novo-lancamento-anchor"></div>', unsafe_allow_html=True
        )

    with st.expander(f"{item['titulo']}", expanded=(idx == 0)):
        badge = (
            '<span class="badge-status-green">Finalizado</span>'
            if item["status"] == "Finalizado"
            else '<span class="badge-status-yellow">Em andamento</span>'
        )

        c_head1, c_head2 = st.columns([3, 1])
        c_head1.caption(f"📅 {item['data_str']}")
        c_head2.markdown(
            f"<div style='text-align:right;'>{badge}</div>",
            unsafe_allow_html=True,
        )

        st.write("")
        tab1, tab2, tab3 = st.tabs(
            [
                "🧪 1. Caracterização",
                "📊 2. Composições e Carga",
                "📈 3. Rendimento",
            ]
        )

        with tab1:
            st.markdown("**Compostos Envolvidos:**")
            for comp in item["compostos"]:
                st.markdown(
                    f'<span class="pill-tag">{comp["nome"]}</span>',
                    unsafe_allow_html=True,
                )
                st.caption(
                    f"Concentração: **{comp['conc']}** | Total utilizado: **{comp.get('qtd_total', 'N/A')}**"
                )

        with tab2:
            st.markdown("**Composições e Reagentes por Reator:**")
            for comp_est in item.get("composicoes_estudadas", []):
                with st.container(border=True):
                    c_prop, c_carga = st.columns(2)
                    c_prop.markdown(
                        f"**Proporção (I:S):** `{comp_est['proporcao']}`"
                    )
                    c_carga.markdown(f"**Carga Orgânica:** `{comp_est['carga']}`")

                    st.caption("**Quantidades por Reator:**")
                    for r in comp_est["reagentes"]:
                        st.caption(f"• **{r['nome']}**: {r['qtd']}")

        with tab3:
            dados_r = item.get("dados_rendimento")
            if item["tem_grafico"] and dados_r:
                labels = tuple([d["composicao"] for d in dados_r])
                rend = tuple([d["rendimento"] for d in dados_r])
                ch4 = tuple([d["fracao_metano"] for d in dados_r])

                fig = gerar_grafico_rendimento(labels, rend, ch4)
                st.pyplot(fig)
            else:
                st.info(
                    "ℹ️ Medições não adicionadas. Clique em **'📊 Calcular rendimento'** no topo para registrar as réplicas."
                )

# Autoscroll inteligente
if st.session_state.scroll_to_novo:
    st.session_state.scroll_to_novo = False
    components.html(
        """
        <script>
            setTimeout(function() {
                var el = window.parent.document.getElementById('novo-lancamento-anchor');
                if (el) { el.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
            }, 200);
        </script>
        """,
        height=0,
    )
