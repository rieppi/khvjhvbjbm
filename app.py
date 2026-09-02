from datetime import date
import matplotlib.pyplot as plt
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

# Inicialização de estados
if "abrir_modal_vol" not in st.session_state:
    st.session_state.abrir_modal_vol = False
if "abrir_modal_rend" not in st.session_state:
    st.session_state.abrir_modal_rend = False

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
            "status": "Em andamento",
            "data_str": "16/06/2023 • 31 dias de digestão",
            "tem_grafico": False,
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
            ],
            "dados_rendimento": None,
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

        col_back, col_space, col_next = st.columns([2, 3, 2])
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

        col_back, col_finish = st.columns([1, 1])
        if col_back.button("⬅ Voltar", key="btn_vol_back2"):
            st.session_state.etapa_modal_vol = 2
            st.rerun()

        if col_finish.button(
            "🚀 Finalizar e Calcular", type="primary", key="btn_vol_finish"
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
            st.session_state.abrir_modal_vol = False
            st.rerun()


# ---------------------------------------------------------
# MODAL 2: RENDIMENTO (PUXANDO DADOS DAS COMPOSIÇÕES)
# ---------------------------------------------------------
@st.dialog("Cálculo de Rendimento do Ensaio", width="medium")
def modal_calcular_rendimento():
    if not st.session_state.lista_lancamentos:
        st.warning("Nenhum lançamento registrado até o momento.")
        return

    titulos_lancamentos = [
        item["titulo"] for item in st.session_state.lista_lancamentos
    ]
    escolha_titulo = st.selectbox(
        "Selecione o Lançamento para puxar os dados:", titulos_lancamentos
    )

    # Seleção do item escolhido
    lanc_selecionado = next(
        item
        for item in st.session_state.lista_lancamentos
        if item["titulo"] == escolha_titulo
    )

    st.write("---")
    st.markdown("**Insira os dados medidos para cada composição:**")

    composicoes = lanc_selecionado.get("composicoes_estudadas", [])
    resultados_rendimento = []

    for idx, comp in enumerate(composicoes):
        prop = comp["proporcao"]
        massa_sv = comp.get("massa_sv_val", 1.0)
        carga = comp.get("carga", "N/A")

        with st.container(border=True):
            st.markdown(
                f"### 🧪 Composição `{prop}` (Carga: `{carga}`, SV: `{massa_sv:.2f} g`)"
            )

            col1, col2 = st.columns(2)
            metano_pct = col1.number_input(
                f"Fração de Metano (% CH₄) - Composição {prop}",
                min_value=0.0,
                max_value=100.0,
                value=60.0,
                step=1.0,
                key=f"rend_pct_{escolha_titulo}_{idx}",
            )
            vol_biogas = col2.number_input(
                f"Volume de Biogás Total (mL) - Composição {prop}",
                min_value=0.0,
                value=350.0,
                step=10.0,
                key=f"rend_vol_{escolha_titulo}_{idx}",
            )

            # Cálculo individual
            vol_ch4 = vol_biogas * (metano_pct / 100.0)
            rendimento_esp = vol_ch4 / massa_sv if massa_sv > 0 else 0.0

            st.caption(
                f"💡 **Volume CH₄ Puro:** `{vol_ch4:.1f} mL` | **Rendimento Calculado:** `{rendimento_esp:.2f} mL CH₄/g SV`"
            )

            resultados_rendimento.append(
                {
                    "composicao": prop,
                    "fracao_metano": metano_pct,
                    "vol_biogas": vol_biogas,
                    "vol_ch4": vol_ch4,
                    "rendimento": rendimento_esp,
                }
            )

    st.write("---")

    if st.button(
        "📊 Gerar Gráfico e Salvar Rendimento",
        type="primary",
        use_container_width=True,
    ):
        # Atualização do lançamento com os resultados finais
        lanc_selecionado["tem_grafico"] = True
        lanc_selecionado["status"] = "Finalizado"
        lanc_selecionado["dados_rendimento"] = resultados_rendimento

        st.toast(
            "Gráfico gerado e rendimento registrado com sucesso!", icon="🎉"
        )
        st.session_state.abrir_modal_rend = False
        st.rerun()


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
        st.session_state.abrir_modal_vol = True

with col_b2:
    if st.button("➤ Quero calcular o rendimento", use_container_width=True):
        st.session_state.abrir_modal_rend = True

with col_b3:
    st.button("➤ Quero estimar a melhor composição", use_container_width=True)

if st.session_state.abrir_modal_vol:
    modal_calcular_volume()

if st.session_state.abrir_modal_rend:
    modal_calcular_rendimento()

st.write("---")
st.subheader("Meus lançamentos")

# Renderização dos Lançamentos em Carrossel/Abas
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

        # Estrutura do Carrossel por Abas
        tab1, tab2, tab3 = st.tabs(
            [
                "🧪 1. Caracterização",
                "📊 2. Composições e Carga",
                "📈 3. Rendimento",
            ]
        )

        # ABA 1: CARACTERIZAÇÃO
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

        # ABA 2: COMPOSIÇÕES ESTUDADAS E CARGA
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

        # ABA 3: GRÁFICO DE RENDIMENTO COM DUPLO EIXO Y
        with tab3:
            st.markdown("**Rendimento e Qualidade do Biogás**")
            dados_r = item.get("dados_rendimento")

            if item["tem_grafico"] and dados_r:
                comp_labels = [d["composicao"] for d in dados_r]
                rendimentos = [d["rendimento"] for d in dados_r]
                fracoes_ch4 = [d["fracao_metano"] for d in dados_r]

                # Construção do gráfico de barras com duplo eixo Y
                fig, ax1 = plt.subplots(figsize=(6, 3))
                fig.patch.set_facecolor("#18181B")
                ax1.set_facecolor("#18181B")

                # Eixo Y1 (Esquerdo) - Rendimento
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

                # Eixo Y2 (Direito) - Fração de Metano
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
