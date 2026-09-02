from datetime import date
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Co-digestão Anaeróbia", layout="wide")

# Estilização CSS Dark Theme Limpa
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

# Inicialização de estados do modal e formulário
if "abrir_modal_vol" not in st.session_state:
    st.session_state.abrir_modal_vol = False
if "abrir_modal_rend" not in st.session_state:
    st.session_state.abrir_modal_rend = False

if "etapa_modal_vol" not in st.session_state:
    st.session_state.etapa_modal_vol = 1
if "etapa_modal_rend" not in st.session_state:
    st.session_state.etapa_modal_rend = 1

if "compostos" not in st.session_state:
    st.session_state.compostos = [
        {"nome": "Inóculo 1", "valor": 15.0, "unidade": "g/mL"},
        {"nome": "Substrato 1", "valor": 40.0, "unidade": "g/g"},
    ]

if "condicoes" not in st.session_state:
    st.session_state.condicoes = [
        {"headspace": 30.0, "composicao": "2:1", "replicas": 3}
    ]

if "lista_lancamentos" not in st.session_state:
    st.session_state.lista_lancamentos = [
        {
            "titulo": "Lançamento 09/06/2023",
            "status": "Finalizado",
            "data_str": "09/06/2023 • 31 dias de digestão",
            "tem_grafico": True,
            "compostos": [
                {
                    "nome": "Inóculo 1",
                    "conc": "15.0 g/mL",
                    "qtd": "150.0 mL",
                },
                {"nome": "Substrato 1", "conc": "40.0 g/g", "qtd": "50.0 g"},
            ],
        },
        {
            "titulo": "Lançamento 16/06/2023",
            "status": "Em andamento",
            "data_str": "16/06/2023 • 31 dias de digestão",
            "tem_grafico": False,
            "compostos": [
                {
                    "nome": "Inóculo 1",
                    "conc": "12.0 g/mL",
                    "qtd": "120.0 mL",
                }
            ],
        },
    ]


# ---------------------------------------------------------
# MODAL 1: DIMENSIONAMENTO DO ENSAIO (3 ETAPAS)
# ---------------------------------------------------------
@st.dialog("Dimensionamento do Ensaio", width="small")
def modal_calcular_volume():
    # ETAPA 1: Caracterização dos Compostos
    if st.session_state.etapa_modal_vol == 1:
        st.markdown("### 1. Caracterização")

        for i, comp in enumerate(st.session_state.compostos):
            novo_nome = st.text_input(
                f"Nome do composto {i+1}",
                value=comp["nome"],
                key=f"nome_comp_{i}",
                label_visibility="collapsed",
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

        _, col_next = st.columns([3, 1])
        if col_next.button("Próximo ➔", key="btn_vol_next1"):
            st.session_state.etapa_modal_vol = 2
            st.rerun()

    # ETAPA 2: Condições dos Reatores
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

        col_back, col_next = st.columns([1, 1])
        if col_back.button("⬅ Voltar", key="btn_vol_back1"):
            st.session_state.etapa_modal_vol = 1
            st.rerun()

        if col_next.button("Próximo ➔", key="btn_vol_next2"):
            st.session_state.etapa_modal_vol = 3
            st.rerun()

    # ETAPA 3: Identificação, Correção de pH e Período de Digestão
    elif st.session_state.etapa_modal_vol == 3:
        st.markdown("### 3. Identificação e Período")

        st.markdown("**Nome do Lançamento**")
        nome_lancamento = st.text_input(
            "Nome do Lançamento",
            value=f"Lançamento {date.today().strftime('%d/%m/%Y')}",
            key="input_nome_lancamento",
            label_visibility="collapsed",
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

        col_back, col_finish = st.columns([1, 1])
        if col_back.button("⬅ Voltar", key="btn_vol_back2"):
            st.session_state.etapa_modal_vol = 2
            st.rerun()

        if col_finish.button(
            "🚀 Finalizar e Calcular", type="primary", key="btn_vol_finish"
        ):
            # Adiciona o novo lançamento na lista do dashboard
            novo_item = {
                "titulo": nome_lancamento,
                "status": "Em andamento",
                "data_str": f"{d_inicio.strftime('%d/%m/%Y')} • {dias} dias de digestão",
                "tem_grafico": False,
                "compostos": [
                    {
                        "nome": c["nome"],
                        "conc": f"{c['valor']} {c['unidade']}",
                        "qtd": "0.0 mL",
                    }
                    for c in st.session_state.compostos
                ],
            }

            st.session_state.lista_lancamentos.insert(0, novo_item)

            st.success("Lançamento adicionado com sucesso!")
            st.session_state.etapa_modal_vol = 1
            st.session_state.abrir_modal_vol = False
            st.rerun()


# ---------------------------------------------------------
# MODAL 2: RENDIMENTO
# ---------------------------------------------------------
@st.dialog("Rendimento", width="small")
def modal_calcular_rendimento():
    if st.session_state.etapa_modal_rend == 1:
        opcoes_lancamentos = [
            item["titulo"] for item in st.session_state.lista_lancamentos
        ]
        st.selectbox(
            "Selecione o lançamento",
            opcoes_lancamentos,
            label_visibility="collapsed",
        )

        st.markdown(
            '<span class="pill-tag">Composição 1:2</span>',
            unsafe_allow_html=True,
        )

        col_m1, col_m2 = st.columns([3, 1])
        f_metano = col_m1.number_input(
            "Fração de Metano",
            value=60.0,
            step=1.0,
            label_visibility="collapsed",
        )
        col_m2.text_input(
            "Unidade Metano",
            value="%",
            disabled=True,
            label_visibility="collapsed",
        )

        col_v1, col_v2 = st.columns([3, 1])
        v_biogas = col_v1.number_input(
            "Volume de Biogás",
            value=350.0,
            step=10.0,
            label_visibility="collapsed",
        )
        col_v2.text_input(
            "Unidade Biogás",
            value="mL",
            disabled=True,
            label_visibility="collapsed",
        )

        st.write("---")

        _, col_next = st.columns([3, 1])
        if col_next.button("Próximo ➔", key="btn_rend_next"):
            st.session_state.fracao_metano = f_metano
            st.session_state.vol_biogas = v_biogas
            st.session_state.etapa_modal_rend = 2
            st.rerun()

    elif st.session_state.etapa_modal_rend == 2:
        st.markdown("### Resultado Estimado")

        f_metano = st.session_state.get("fracao_metano", 60.0)
        v_biogas = st.session_state.get("vol_biogas", 350.0)
        v_ch4 = v_biogas * (f_metano / 100.0)

        st.metric("Volume de Metano Puro", f"{v_ch4:.1f} mL CH₄")

        if st.button(
            "💾 Salvar Rendimento", use_container_width=True, type="primary"
        ):
            st.success("Rendimento salvo!")
            st.session_state.etapa_modal_rend = 1
            st.session_state.abrir_modal_rend = False
            st.rerun()

        st.write("---")

        col_back, _ = st.columns([1, 3])
        if col_back.button("⬅ Voltar", key="btn_rend_back"):
            st.session_state.etapa_modal_rend = 1
            st.rerun()


# ---------------------------------------------------------
# INTERFACE PRINCIPAL (DASHBOARD)
# ---------------------------------------------------------
st.title("👋 Olá, [nome]!")

col_b1, col_b2, col_b3 = st.columns(3)
with col_b1:
    if st.button("➤ Quero calcular o volume", use_container_width=True):
        st.session_state.etapa_modal_vol = 1
        st.session_state.abrir_modal_vol = True

with col_b2:
    if st.button("➤ Quero calcular o rendimento", use_container_width=True):
        st.session_state.etapa_modal_rend = 1
        st.session_state.abrir_modal_rend = True

with col_b3:
    st.button("➤ Quero estimar a melhor composição", use_container_width=True)

if st.session_state.abrir_modal_vol:
    modal_calcular_volume()

if st.session_state.abrir_modal_rend:
    modal_calcular_rendimento()

st.write("---")
st.subheader("Meus lançamentos")

# Renderização dinâmica dos Lançamentos da Lista
for idx, item in enumerate(st.session_state.lista_lancamentos):
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

        st.write("")
        g_col1, g_col2 = st.columns(2)

        with g_col1:
            st.caption(item["data_str"])
            if item["tem_grafico"]:
                fig, ax = plt.subplots(figsize=(4, 2.2))
                fig.patch.set_facecolor("#18181B")
                ax.set_facecolor("#18181B")
                ax.bar(
                    ["1:2", "2:1", "1:3", "1:1"],
                    [380, 240, 310, 290],
                    color="#818CF8",
                    width=0.45,
                )
                ax.tick_params(colors="#A1A1AA", labelsize=8)
                ax.set_ylabel(
                    "Rendimento (mL CH4/g SV)", color="#A1A1AA", fontsize=7
                )
                for spine in ax.spines.values():
                    spine.set_color("#27272A")
                st.pyplot(fig)
            else:
                st.info("Gráfico Indisponível")

        with g_col2:
            st.markdown("**Caracterização**")
            for comp in item["compostos"]:
                st.markdown(
                    f'<span class="pill-tag">{comp["nome"]}</span>',
                    unsafe_allow_html=True,
                )
                st.caption(
                    f"Concentração de sólidos voláteis: {comp['conc']}"
                )
                st.caption(f"Quantidade inserida: {comp['qtd']}")
