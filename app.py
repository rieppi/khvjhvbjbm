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
    /* Estilo exclusivo para os botões de bolinha de paginação */
    div[data-testid="column"]:has(button[key^="dot_"]) button {
        border-radius: 50% !important;
        width: 18px !important;
        height: 18px !important;
        min-height: 18px !important;
        padding: 0px !important;
        font-size: 10px !important;
        line-height: 1 !important;
        border: none !important;
        background-color: transparent !important;
        box-shadow: none !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Inicialização de estados
if "etapa_modal_vol" not in st.session_state:
    st.session_state.etapa_modal_vol = 1
if "etapa_modal_rend" not in st.session_state:
    st.session_state.etapa_modal_rend = 1


# ---------------------------------------------------------
# MODAL 1: DIMENSIONAMENTO DO ENSAIO
# ---------------------------------------------------------
@st.dialog("Dimensionamento do Ensaio", width="small")
def modal_calcular_volume():
    if st.session_state.etapa_modal_vol == 1:
        st.markdown("### Caracterização")
        st.markdown(
            '<span class="pill-tag">Inóculo 1</span>', unsafe_allow_html=True
        )

        c_in_val, c_in_unit = st.columns([3, 1])
        c_in_val.number_input(
            "Inóculo SV", value=15.0, label_visibility="collapsed"
        )
        c_in_unit.selectbox(
            "Unidade Inóculo", ["g/mL", "g/g"], label_visibility="collapsed"
        )

        st.markdown(
            '<span class="pill-tag">Substrato 1</span>', unsafe_allow_html=True
        )

        c_sub_val, c_sub_unit = st.columns([3, 1])
        c_sub_val.number_input(
            "Substrato SV", value=40.0, label_visibility="collapsed"
        )
        c_sub_unit.selectbox(
            "Unidade Substrato", ["g/g", "g/mL"], label_visibility="collapsed"
        )

        st.button("➕ Adicionar composto", key="add_comp")
        st.write("---")

        c_l, c_dot1, c_dot2, c_r = st.columns([6, 1, 1, 6])
        with c_dot1:
            st.button("⚪", key="dot_v1_active", disabled=True)
        with c_dot2:
            if st.button("⚫", key="dot_v1_to_2"):
                st.session_state.etapa_modal_vol = 2
                st.rerun()

    elif st.session_state.etapa_modal_vol == 2:
        st.markdown("### Condições dos reatores")
        d_col1, d_col2 = st.columns(2)
        d_col1.date_input("Data Inicial", value=date.today())
        d_col2.date_input("Data Final", value=date.today())

        st.number_input("Headspace desejado (%)", value=30.0, step=5.0)
        st.text_input("Composição 1 (I:S)", value="2:1")
        st.number_input("Número de réplicas", value=3, step=1)

        st.button("➕ Adicionar condição", key="add_cond")

        if st.button(
            "🚀 Finalizar e Calcular", use_container_width=True, type="primary"
        ):
            st.success("Cálculo realizado!")
            st.session_state.etapa_modal_vol = 1
            st.rerun()

        st.write("---")

        c_l, c_dot1, c_dot2, c_r = st.columns([6, 1, 1, 6])
        with c_dot1:
            if st.button("⚫", key="dot_v2_to_1"):
                st.session_state.etapa_modal_vol = 1
                st.rerun()
        with c_dot2:
            st.button("⚪", key="dot_v2_active", disabled=True)


# ---------------------------------------------------------
# MODAL 2: RENDIMENTO
# ---------------------------------------------------------
@st.dialog("Rendimento", width="small")
def modal_calcular_rendimento():
    if st.session_state.etapa_modal_rend == 1:
        st.selectbox(
            "Selecione o lançamento",
            ["Lançamento 09/06/2023", "Lançamento 16/06/2023"],
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

        c_l, c_dot1, c_dot2, c_r = st.columns([6, 1, 1, 6])
        with c_dot1:
            st.button("⚪", key="dot_r1_active", disabled=True)
        with c_dot2:
            if st.button("⚫", key="dot_r1_to_2"):
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
            st.rerun()

        st.write("---")

        c_l, c_dot1, c_dot2, c_r = st.columns([6, 1, 1, 6])
        with c_dot1:
            if st.button("⚫", key="dot_r2_to_1"):
                st.session_state.etapa_modal_rend = 1
                st.rerun()
        with c_dot2:
            st.button("⚪", key="dot_r2_active", disabled=True)


# ---------------------------------------------------------
# INTERFACE PRINCIPAL (DASHBOARD)
# ---------------------------------------------------------
st.title("👋 Olá, [nome]!")

col_b1, col_b2, col_b3 = st.columns(3)
with col_b1:
    if st.button("➤ Quero calcular o volume", use_container_width=True):
        st.session_state.etapa_modal_vol = 1
        modal_calcular_volume()

with col_b2:
    if st.button("➤ Quero calcular o rendimento", use_container_width=True):
        st.session_state.etapa_modal_rend = 1
        modal_calcular_rendimento()

with col_b3:
    st.button("➤ Quero estimar a melhor composição", use_container_width=True)

st.write("---")
st.subheader("Meus lançamentos")

# Lançamento 1
with st.expander("Lançamento 09/06/2023", expanded=True):
    st.markdown(
        '<span class="badge-status-green">Finalizado</span>',
        unsafe_allow_html=True,
    )
    st.write("")

    g_col1, g_col2 = st.columns(2)
    with g_col1:
        st.caption("09/06/2023 • 31 dias de digestão")

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
        ax.set_ylabel("Rendimento (mL CH4/g SV)", color="#A1A1AA", fontsize=7)
        for spine in ax.spines.values():
            spine.set_color("#27272A")
        st.pyplot(fig)

    with g_col2:
        st.markdown("**Caracterização**")
        st.markdown(
            '<span class="pill-tag">Inóculo 1</span>', unsafe_allow_html=True
        )
        st.caption("Concentração de sólidos voláteis: 15.0 g/mL")
        st.markdown(
            '<span class="pill-tag">Substrato 1</span>', unsafe_allow_html=True
        )
        st.caption("Concentração de sólidos voláteis: 40.0 g/g")

# Lançamento 2
with st.expander("Lançamento 16/06/2023", expanded=False):
    st.markdown(
        '<span class="badge-status-yellow">Em andamento</span>',
        unsafe_allow_html=True,
    )
    st.write("")

    g_col3, g_col4 = st.columns(2)
    with g_col3:
        st.caption("16/06/2023 • 31 dias de digestão")
        st.info("Gráfico Indisponível")

    with g_col4:
        st.markdown("**Caracterização**")
        st.markdown(
            '<span class="pill-tag">Inóculo 1</span>', unsafe_allow_html=True
        )
        st.caption("Concentração de sólidos voláteis: 12.0 g/mL")
