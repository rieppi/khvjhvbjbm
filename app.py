import streamlit as st
import matplotlib.pyplot as plt
from datetime import date

st.set_page_config(page_title="Co-digestão Anaeróbia", layout="wide")

# Estilização CSS para recriar o tema escuro idêntico ao Figma
st.markdown("""
<style>
    .stApp { background-color: #121214; color: #E4E4E7; }
    .card {
        background-color: #18181B;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #27272A;
        margin-bottom: 20px;
    }
    .badge-status-green {
        background-color: #14532D; color: #4ADE80;
        padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold;
    }
    .badge-status-yellow {
        background-color: #713F12; color: #FACC15;
        padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold;
    }
    .pill-tag {
        background-color: #2E3856; color: #818CF8;
        padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;
        display: inline-block; margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# COMPONENTE 2: DIÁLOG/MODAL DE CONFIGURAÇÃO DO REATOR
# ---------------------------------------------------------
@st.dialog("Configuração do Reator", width="large")
def modal_calcular_volume():
    col1, col2 = st.columns(2)
    
    # --- Painel Esquerdo: Caracterização ---
    with col1:
        st.markdown("### Caracterização")
        
        # Inóculo 1
        st.markdown('<span class="pill-tag">Inóculo 1</span>', unsafe_allow_html=True)
        st.caption("Concentração de sólidos voláteis (g/g ou g/mL)")
        c_in_val, c_in_unit = st.columns([2, 1])
        sv_inoculo = c_in_val.number_input("Inóculo SV", value=15.0, label_visibility="collapsed")
        unidade_inoculo = c_in_unit.selectbox("Unidade Inóculo", ["g/mL", "g/g"], label_visibility="collapsed")
        
        # Substrato 1
        st.markdown('<span class="pill-tag">Substrato 1</span>', unsafe_allow_html=True)
        st.caption("Concentração de sólidos voláteis (g/g ou g/mL)")
        c_sub_val, c_sub_unit = st.columns([2, 1])
        sv_substrato = c_sub_val.number_input("Substrato SV", value=40.0, label_visibility="collapsed")
        unidade_substrato = c_sub_unit.selectbox("Unidade Substrato", ["g/g", "g/mL"], label_visibility="collapsed")
        
        st.button("➕ Adicionar composto", key="add_composto")
        st.write("⚪ ⚫")

    # --- Painel Direito: Condições dos reatores ---
    with col2:
        st.markdown("### Condições dos reatores")
        
        st.caption("Período de Digestão")
        d_col1, d_col2 = st.columns(2)
        dt_inicio = d_col1.date_input("Data Inicial", value=date.today())
        dt_fim = d_col2.date_input("Data Final", value=date.today())
        dias_digestao = (dt_fim - dt_inicio).days
        st.caption(f"⏱️ {max(0, dias_digestao)} dias de digestão")
        
        headspace = st.number_input("Headspace desejado (%)", value=30.0, step=5.0)
        composicao_is = st.text_input("Composição 1 (I:S)", value="2:1")
        replicas = st.number_input("Número de réplicas", value=3, step=1)
        
        st.button("➕ Adicionar condição", key="add_condicao")
        st.write("⚫ ⚪")

    st.write("---")
    if st.button("🚀 Confirmar e Calcular", use_container_width=True, type="primary"):
        st.success("Dados salvos e cálculo efetuado com sucesso!")
        st.rerun()

# ---------------------------------------------------------
# INTERFACE PRINCIPAL (DASHBOARD)
# ---------------------------------------------------------
st.title("👋 Olá, [nome]!")

# Botões de Ação Superiores
col_b1, col_b2, col_b3 = st.columns(3)
with col_b1:
    if st.button("➤ Quero calcular o volume", use_container_width=True):
        modal_calcular_volume()
with col_b2:
    st.button("➤ Quero calcular o rendimento", use_container_width=True)
with col_b3:
    st.button("➤ Quero estimar a melhor composição", use_container_width=True)

st.write("---")
st.subheader("Meus lançamentos")

# --- Lançamento 1 (Finalizado) ---
col_h1, col_h2 = st.columns([4, 1])
col_h1.markdown("**▼ Lançamento 09/06/2023**")
col_h2.markdown('<span class="badge-status-green">Finalizado</span>', unsafe_allow_html=True)

g_col1, g_col2 = st.columns(2)
with g_col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.caption("09/06/2023 • 31 dias de digestão")
    fig, ax = plt.subplots(figsize=(4, 2.2))
    fig.patch.set_facecolor('#18181B')
    ax.set_facecolor('#18181B')
    ax.bar(["1:2", "2:1", "1:3", "1:1"], [380, 240, 310, 290], color="#818CF8", width=0.45)
    ax.tick_params(colors="#A1A1AA", labelsize=8)
    ax.set_ylabel("Rendimento (mL CH4/g SV)", color="#A1A1AA", fontsize=7)
    for spine in ax.spines.values(): spine.set_color('#27272A')
    st.pyplot(fig)
    st.markdown('</div>', unsafe_allow_html=True)

with g_col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Caracterização**")
    st.markdown('<span class="pill-tag">Inóculo 1</span>', unsafe_allow_html=True)
    st.caption("Concentração de sólidos voláteis: 15.0 g/mL")
    st.markdown('<span class="pill-tag">Substrato 1</span>', unsafe_allow_html=True)
    st.caption("Concentração de sólidos voláteis: 40.0 g/g")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Lançamento 2 (Em andamento) ---
col_h3, col_h4 = st.columns([4, 1])
col_h3.markdown("**▼ Lançamento 16/06/2023**")
col_h4.markdown('<span class="badge-status-yellow">Em andamento</span>', unsafe_allow_html=True)

g_col3, g_col4 = st.columns(2)
with g_col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.caption("09/06/2023 • 31 dias de digestão")
    st.info("Gráfico Indisponível")
    st.markdown('</div>', unsafe_allow_html=True)

with g_col4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Caracterização**")
    st.markdown('<span class="pill-tag">Inóculo 1</span>', unsafe_allow_html=True)
    st.caption("Concentração de sólidos voláteis: 12.0 g/mL")
    st.markdown('</div>', unsafe_allow_html=True)
