from datetime import date
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Co-digestão Anaeróbia", layout="wide")

# Estilização CSS Dark Theme
st.markdown(
    """
<style>
    .stApp { background-color: #121214; color: #E4E4E7; }
    .badge-status-green {
        background-color: #14532D; color: #4ADE80;
        padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: bold;
    }
    .badge-status-yellow {
        background-color: #713F12; color: #FACC15;
        padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: bold;
    }
    .pill-tag {
        background-color: #2E3856; color: #818CF8;
        padding: 4px 12px; border-radius: 16px; font-size: 12px; font-weight: bold;
        display: inline-block; margin-bottom: 8px; margin-top: 4px;
    }
    div[data-testid="stExpander"] {
        background-color: #18181B;
        border: 1px solid #27272A;
        border-radius: 8px;
        margin-bottom: 12px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Controle de Exibição Única de Modal
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
# MODAL 1: DIMENSIONAMENTO DO ENSAIO
# ---------------------------------------------------------
@st.dialog("Dimensionamento do Ensaio", width="small")
def modal_calcular_volume():
    if st.session_state.etapa_modal_vol == 1:
        st.markdown("### 1. Caracterização")

        for i, comp in enumerate(st.session_state.compostos):
            with st.container(border=True):
                st.markdown(f"**Composto {i+1}**")

                novo_nome = st.text_input(
                    f"Nome do composto {i+1}",
                    value=comp["nome"],
                    key=f"nome_comp_{i}",
                    label_visibility="collapsed",
                    placeholder="Nome do composto",
                )
                st.session_state.compostos[i]["nome"] = novo_nome

                c_val, c_unit = st.columns([3, 1])
                novo_val = c_val.number_input(
                    f"Valor {i+1}",
                    value=comp["valor"],
                    key=f"val_comp_{i}",
                    label_visibility="collapsed",
                )
                nova_unit = c_unit.selectbox(
                    f"Unidade {i+1}",
                    ["g/mL", "g/g"],
                    index=0 if comp["unidade"] == "g/mL" else 1,
                    key=f"unit_comp_{i}",
                    label_visibility="collapsed",
                )

                st.session_state.compostos[i]["valor"] = novo_val
                st.session_state.compostos[i]["unidade"] = nova_unit

        if st.button("➕ Adicionar composto", key="add_comp"):
            st.session_state.compostos.append(
                {
                    "nome": f"Composto {len(st.session_state.compostos) + 1}",
                    "valor": 0.0,
                    "unidade": "g/mL",
                }
            )
            st.rerun()

        st.write("---")

        _, col_space, col_next = st.columns([2, 1, 2])
        with col_next:
            if st.button(
                "Próximo ➔", key="btn_vol_next1", use_container_width=True
            ):
                st.session_state.etapa_modal_vol = 2
                st.rerun()

    elif st.session_state.etapa_modal_vol == 2:
        st.markdown("### 2. Condições dos reatores")

        for i, cond in enumerate(st.session_state.condicoes):
            with st.container(border=True):
                st.markdown("**Headspace desejado (%)**")
                hs = st.number_input(
                    f"Headspace {i}",
                    value=cond["headspace"],
                    step=5.0,
                    key=f"hs_{i}",
                    label_visibility="collapsed",
                )

                st.markdown(f"**Composição {i+1} (I:S)**")
                comp = st.text_input(
                    f"Composição {i}",
                    value=cond["composicao"],
                    key=f"comp_{i}",
                    label_visibility="collapsed",
                )

                st.markdown("**Número de réplicas**")
                rep = st.number_input(
                    f"Réplicas {i}",
                    value=cond["replicas"],
                    step=1,
                    key=f"rep_{i}",
                    label_visibility="collapsed",
                )

                st.session_state.condicoes[i] = {
                    "headspace": hs,
                    "composicao": comp,
                    "replicas": rep,
                }

        if st.button("➕ Adicionar condição", key="add_cond"):
            st.session_state.condicoes.append(
                {"headspace": 30.0, "composicao": "1:1", "replicas": 3}
            )
            st.rerun()

        st.write("---")

        col_back, col_space, col_next = st.columns([2, 1, 2])
        with col_back:
            if st.button(
                "⬅ Voltar", key="btn_vol_back1", use_container_width=True
            ):
                st.session_state.etapa_modal_vol = 1
                st.rerun()

        with col_next:
            if st.button(
                "Próximo ➔", key="btn_vol_next2", use_container_width=True
            ):
                st.session_state.etapa_modal_vol = 3
                st.rerun()

    elif st.session_state.etapa_modal_vol == 3:
        st.markdown("### 3. Identificação e Período")

        nome_lancamento = st.text_input(
            "Nome do Lançamento",
            value=f"Lançamento {date.today().strftime('%d/%m/%Y')}",
            key="input_nome_lancamento",
        )

        st.write("")
        corrigir_ph = st.checkbox("Será feita a correção de pH", value=False)

        st.write("---")
        st.markdown("**Período de Digestão**")
        d_col1, d_col2 = st.columns(2)
        d_inicio = d_col1.date_input(
            "Data Inicial", value=date.today(), key="dt_inicio_e3"
        )
        d_fim = d_col2.date_input(
            "Data Final", value=date.today(), key="dt_fim_e3"
        )

        dias = max(0, (d_fim - d_inicio).days)
        st.caption(f"⏱️ **{dias} dias de digestão**")

        st.write("---")

        col_back, col_space, col_finish = st.columns([2, 1, 3])
        with col_back:
            if st.button(
                "⬅ Voltar", key="btn_vol_back2", use_container_width=True
            ):
                st.session_state.etapa_modal_vol = 2
                st.rerun()

        with col_finish:
            if st.button(
                "🚀 Finalizar e Calcular",
                type="primary",
                key="btn_vol_finish",
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

                composicoes_estudadas = []
                for cond in st.session_state.condicoes:
                    reagentes_cond = [
                        {"nome": comp["nome"], "qtd": comp["qtd"]}
                        for comp in compostos_calculados
                    ]
                    composicoes_estudadas.append(
                        {
                            "proporcao": cond["composicao"],
                            "carga": f"{carga_composicao:.3f} g SV/mL",
                            "massa_sv_val": massa_sv_total,
                            "reagentes": reagentes_cond,
                        }
                    )

                novo_id = f"lanc_{len(st.session_state.lista_lancamentos) + 1}"
                novo_item = {
                    "id": novo_id,
                    "titulo": nome_lancamento,
                    "status": "Em andamento",
                    "data_str": f"{d_inicio.strftime('%d/%m/%Y')} • {dias} dias de digestão",
                    "tem_grafico": False,
                    "massa_sv_total_val": massa_sv_total,
                    "massa_sv_total": f"{massa_sv_total:.2f} g SV",
                    "carga_volumetrica": f"{carga_composicao:.3f} g SV/mL",
                    "compostos": compostos_calculados,
                    "composicoes_estudadas": composicoes_estudadas,
                    "dados_rendimento": None,
                }

                st.session_state.lista_lancamentos.insert(0, novo_item)

                st.session_state.toast_msg = "✅ Lançamento preparado com sucesso!"
                st.session_state.scroll_to_novo = True

                st.session_state.etapa_modal_vol = 1
                st.session_state.modal_ativo = None
                st.rerun()


# ---------------------------------------------------------
# MODAL 2: RENDIMENTO POR RÉPLICAS
# ---------------------------------------------------------
@st.dialog("Cálculo de Rendimento por Réplicas", width="medium")
def modal_calcular_rendimento():
    if not st.session_state.lista_lancamentos:
        st.warning("Nenhum lançamento registrado até o momento.")
        return

    if st.session_state.etapa_modal_rend == 1:
        titulos_lancamentos = [
            item["titulo"] for item in st.session_state.lista_lancamentos
        ]
        escolha_titulo = st.selectbox(
            "Selecione o Lançamento para carregar as composições:",
            titulos_lancamentos,
            key="select_lanc_rend",
        )

        lanc_selecionado = next(
            item
            for item in st.session_state.lista_lancamentos
            if item["titulo"] == escolha_titulo
        )

        st.write("---")
        st.markdown("**Insira os dados medidos de cada réplica:**")

        composicoes = lanc_selecionado.get("composicoes_estudadas", [])
        num_replicas = (
            st.session_state.condicoes[0]["replicas"]
            if st.session_state.condicoes
            else 3
        )

        dados_replicas_temp = []

        for idx_comp, comp in enumerate(composicoes):
            prop = comp["proporcao"]
            massa_sv = comp.get("massa_sv_val", 1.0)

            with st.container(border=True):
                st.markdown(
                    f"### 🧪 Composição `{prop}` ({num_replicas} réplicas)"
                )

                replicas_comp = []
                for rep in range(1, num_replicas + 1):
                    st.markdown(f"**Réplica {rep}**")
                    col1, col2 = st.columns(2)

                    metano_pct = col1.number_input(
                        f"Metano (% CH₄) - R{rep}",
                        min_value=0.0,
                        max_value=100.0,
                        value=60.0,
                        step=0.5,
                        key=f"rep_pct_{escolha_titulo}_{idx_comp}_{rep}",
                    )
                    vol_biogas = col2.number_input(
                        f"Biogás Total (mL) - R{rep}",
                        min_value=0.0,
                        value=350.0,
                        step=5.0,
                        key=f"rep_vol_{escolha_titulo}_{idx_comp}_{rep}",
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

        st.write("---")

        _, col_space, col_next = st.columns([1, 1, 3])
        with col_next:
            if st.button(
                "Próximo ➔ (Calcular Médias)",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.temp_rend_data = {
                    "titulo": escolha_titulo,
                    "composicoes": dados_replicas_temp,
                }
                st.session_state.etapa_modal_rend = 2
                st.rerun()

    elif st.session_state.etapa_modal_rend == 2:
        st.markdown("### 📊 Resultado das Médias Calculadas")

        temp_data = st.session_state.get("temp_rend_data", {})
        resultados_finais = []

        for comp in temp_data.get("composicoes", []):
            prop = comp["proporcao"]
            reps = comp["replicas"]

            media_metano = sum(r["metano_pct"] for r in reps) / len(reps)
            media_vol_biogas = sum(r["vol_biogas"] for r in reps) / len(reps)
            media_vol_ch4 = sum(r["vol_ch4"] for r in reps) / len(reps)
            media_rendimento = sum(r["rendimento"] for r in reps) / len(reps)

            with st.container(border=True):
                st.markdown(f"**Composição (I:S): `{prop}`**")
                col_m1, col_m2, col_m3 = st.columns(3)

                col_m1.metric("Média % CH₄", f"{media_metano:.1f}%")
                col_m2.metric("Média Vol. Biogás", f"{media_vol_biogas:.1f} mL")
                col_m3.metric(
                    "Média Rendimento", f"{media_rendimento:.2f} mL/g SV"
                )

            resultados_finais.append(
                {
                    "composicao": prop,
                    "fracao_metano": media_metano,
                    "vol_biogas": media_vol_biogas,
                    "vol_ch4": media_vol_ch4,
                    "rendimento": media_rendimento,
                }
            )

        st.write("---")

        col_back, col_space, col_save = st.columns([2, 1, 3])
        with col_back:
            if st.button("⬅ Voltar", use_container_width=True):
                st.session_state.etapa_modal_rend = 1
                st.rerun()

        with col_save:
            if st.button(
                "💾 Confirmar e Gerar Gráfico",
                type="primary",
                use_container_width=True,
            ):
                lanc_target = next(
                    item
                    for item in st.session_state.lista_lancamentos
                    if item["titulo"] == temp_data["titulo"]
                )
                lanc_target["tem_grafico"] = True
                lanc_target["status"] = "Finalizado"
                lanc_target["dados_rendimento"] = resultados_finais

                st.toast("Médias salvas e gráfico gerado com sucesso!", icon="🎉")
                st.session_state.etapa_modal_rend = 1
                st.session_state.modal_ativo = None
                st.rerun()


# ---------------------------------------------------------
# MODAL 3: ESTIMAR MELHOR COMPOSIÇÃO
# ---------------------------------------------------------
@st.dialog("🎯 Estimativa Estatística da Melhor Composição", width="medium")
def modal_estimar_composicao():
    st.markdown("### Análise de Regressão e Otimização")

    historico_dados = []
    for lanc in st.session_state.lista_lancamentos:
        if lanc["status"] == "Finalizado" and lanc.get("dados_rendimento"):
            for d in lanc["dados_rendimento"]:
                try:
                    partes = [
                        float(p) for p in d["composicao"].split(":") if p.strip()
                    ]
                    if len(partes) >= 2:
                        tot = sum(partes)
                        prop_inoculo = partes[0] / tot
                        prop_substrato = partes[1] / tot
                        historico_dados.append(
                            {
                                "Inóculo": prop_inoculo,
                                "Substrato": prop_substrato,
                                "Rendimento": d["rendimento"],
                                "Metano_pct": d["fracao_metano"],
                            }
                        )
                except Exception:
                    continue

    if len(historico_dados) < 3:
        st.warning(
            "⚠️ São necessários dados de pelo menos 3 composições finalizadas para realizar a análise estatística com precisão."
        )
        return

    df = pd.DataFrame(historico_dados)

    X = np.column_stack(
        [
            np.ones(len(df)),
            df["Inóculo"],
            df["Substrato"],
            df["Inóculo"] * df["Substrato"],
        ]
    )
    y = df["Rendimento"].values

    coef, residuals, rank, s = np.linalg.lstsq(X, y, rcond=None)

    grid_inoculo = np.linspace(0.1, 0.9, 100)
    melhor_rend = -1
    melhor_prop = (0.5, 0.5)

    curva_x = []
    curva_y = []

    for inoc in grid_inoculo:
        subst = 1.0 - inoc
        x_row = np.array([1.0, inoc, subst, inoc * subst])
        rend_pred = np.dot(x_row, coef)

        curva_x.append(inoc)
        curva_y.append(rend_pred)

        if rend_pred > melhor_rend:
            melhor_rend = rend_pred
            melhor_prop = (inoc, subst)

    y_pred = X @ coef
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    ss_res = np.sum((y - y_pred) ** 2)
    r2_score = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    st.success("✨ **Composição Ideal Estimada:**")

    prop_inoc_pct = int(round(melhor_prop[0] * 100))
    prop_sub_pct = int(round(melhor_prop[1] * 100))

    col_res1, col_res2, col_res3 = st.columns(3)
    col_res1.metric("Prop. Inóculo", f"{prop_inoc_pct}%")
    col_res2.metric("Prop. Substrato", f"{prop_sub_pct}%")
    col_res3.metric("Rendimento Estimado", f"{melhor_rend:.1f} mL/g SV")

    st.caption(f"📈 Nível de Precisão do Modelo ($R^2$): **{r2_score*100:.1f}%**")

    st.write("---")
    st.markdown("**Curva Estatística de Otimização (Superfície de Resposta)**")

    fig, ax = plt.subplots(figsize=(6, 3))
    fig.patch.set_facecolor("#18181B")
    ax.set_facecolor("#18181B")

    ax.plot(
        curva_x,
        curva_y,
        color="#818CF8",
        linewidth=2.5,
        label="Modelo Preditivo",
    )
    ax.scatter(
        df["Inóculo"],
        df["Rendimento"],
        color="#FACC15",
        s=50,
        zorder=5,
        label="Pontos Experimentais",
    )

    ax.axvline(
        x=melhor_prop[0],
        color="#4ADE80",
        linestyle="--",
        label=f"Ponto Ótimo ({prop_inoc_pct}:{prop_sub_pct})",
    )

    ax.set_xlabel("Fração de Inóculo", color="#A1A1AA", fontsize=9)
    ax.set_ylabel("Rendimento (mL CH4/g SV)", color="#A1A1AA", fontsize=9)
    ax.tick_params(colors="#A1A1AA", labelsize=8)
    ax.legend(
        facecolor="#27272A", edgecolor="none", labelcolor="#E4E4E7", fontsize=8
    )

    for spine in ax.spines.values():
        spine.set_color("#27272A")

    st.pyplot(fig)


# ---------------------------------------------------------
# INTERFACE PRINCIPAL (DASHBOARD)
# ---------------------------------------------------------
st.title("👋 Olá, [nome]!")

if "toast_msg" in st.session_state and st.session_state.toast_msg:
    st.toast(st.session_state.toast_msg, icon="🎉")
    del st.session_state["toast_msg"]

col_b1, col_b2, col_b3 = st.columns(3)
with col_b1:
    if st.button("➤ Quero calcular o volume", use_container_width=True):
        st.session_state.etapa_modal_vol = 1
        st.session_state.modal_ativo = "volume"

with col_b2:
    if st.button("➤ Quero calcular o rendimento", use_container_width=True):
        st.session_state.etapa_modal_rend = 1
        st.session_state.modal_ativo = "rendimento"

with col_b3:
    if st.button("➤ Quero estimar a melhor composição", use_container_width=True):
        st.session_state.modal_ativo = "otimizacao"

# Renderização do Modal Ativo (Garante apenas um por execução)
if st.session_state.modal_ativo == "volume":
    modal_calcular_volume()
elif st.session_state.modal_ativo == "rendimento":
    modal_calcular_rendimento()
elif st.session_state.modal_ativo == "otimizacao":
    modal_estimar_composicao()

st.write("---")
st.subheader("Meus lançamentos")

for idx, item in enumerate(st.session_state.lista_lancamentos):
    if idx == 0:
        st.markdown(
            '<div id="novo-lancamento-anchor"></div>', unsafe_allow_html=True
        )

    with st.expander(item["titulo"], expanded=(idx == 0)):
        if item["status"] == "Finalizado":
            st.markdown(
                '<span class="badge-status-green">Finalizado</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="badge-status-yellow">Em andamento</span>',
                unsafe_allow_html=True,
            )

        st.caption(item["data_str"])
        st.write("")

        tab1, tab2, tab3 = st.tabs(
            [
                "🧪 1. Caracterização",
                "📊 2. Composições e Carga",
                "📈 3. Rendimento",
            ]
        )

        with tab1:
            st.markdown("**Compostos Registrados**")
            for comp in item["compostos"]:
                st.markdown(
                    f'<span class="pill-tag">{comp["nome"]}</span>',
                    unsafe_allow_html=True,
                )
                st.caption(
                    f"Concentração de sólidos voláteis: **{comp['conc']}**"
                )
                qtd_tot = comp.get("qtd_total", "N/A")
                st.caption(
                    f"📦 Volume/Massa total utilizada no ensaio: **{qtd_tot}**"
                )

        with tab2:
            st.markdown("**Detalhes das Composições e Reagentes**")
            composicoes = item.get("composicoes_estudadas", [])

            if composicoes:
                for comp_est in composicoes:
                    with st.container(border=True):
                        st.markdown(
                            f"**Composição (I:S):** `{comp_est['proporcao']}`"
                        )
                        st.caption(
                            f"🧪 **Carga Orgânica:** `{comp_est['carga']}`"
                        )
                        st.markdown("**Reagentes Utilizados por Reator:**")
                        for r in comp_est["reagentes"]:
                            st.caption(
                                f"• **{r['nome']}**: `Quantidade inserida: {r['qtd']}`"
                            )

        with tab3:
            st.markdown("**Rendimento Médio e Qualidade do Biogás**")
            dados_r = item.get("dados_rendimento")

            if item["tem_grafico"] and dados_r:
                comp_labels = [d["composicao"] for d in dados_r]
                rendimentos = [d["rendimento"] for d in dados_r]
                fracoes_ch4 = [d["fracao_metano"] for d in dados_r]

                fig, ax1 = plt.subplots(figsize=(6, 3))
                fig.patch.set_facecolor("#18181B")
                ax1.set_facecolor("#18181B")

                bars = ax1.bar(
                    comp_labels,
                    rendimentos,
                    color="#818CF8",
                    width=0.35,
                    label="Rendimento (mL CH4/g SV)",
                )
                ax1.set_xlabel(
                    "Composições (I:S)", color="#A1A1AA", fontsize=9
                )
                ax1.set_ylabel(
                    "Rendimento (mL CH4/g SV)", color="#818CF8", fontsize=8
                )
                ax1.tick_params(colors="#A1A1AA", labelsize=8)

                ax2 = ax1.twinx()
                ax2.plot(
                    comp_labels,
                    fracoes_ch4,
                    color="#FACC15",
                    marker="o",
                    linewidth=2,
                    label="% CH4",
                )
                ax2.set_ylabel("% CH4 Biometano", color="#FACC15", fontsize=8)
                ax2.tick_params(colors="#A1A1AA", labelsize=8)
                ax2.set_ylim(0, 100)

                for spine in ax1.spines.values():
                    spine.set_color("#27272A")
                for spine in ax2.spines.values():
                    spine.set_color("#27272A")

                st.pyplot(fig)
            else:
                st.info(
                    "Gráfico ainda não gerado. Calcule o rendimento clicando no botão no topo da página."
                )

if st.session_state.scroll_to_novo:
    st.session_state.scroll_to_novo = False
    components.html(
        """
        <script>
            setTimeout(function() {
                var element = window.parent.document.getElementById('novo-lancamento-anchor');
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }, 300);
        </script>
        """,
        height=0,
    )
