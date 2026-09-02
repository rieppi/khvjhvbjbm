import streamlit as st
import matplotlib.pyplot as plt

# Configuração da página e tema escuro
st.set_page_config(page_title="Co-digestão Anaeróbia", layout="wide")

# Estilização CSS para reproduzir a UI do layout enviado
st.markdown("""
<style>
    .stApp { background-color: #121214; color: #E4E4E7; }
    div[data-testid="stMetricValue"] { color: #818CF8; }
    .card {
        background-color: #18181B;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #27272A;
        margin-bottom: 20px;
    }
    .badge-status {
        background-color: #14532D;
        color: #4ADE80;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 1. Saudação
st.title("👋 Olá, Pesquisador!")

# 2. Botões de Ação
col_b1, col_b2, col_b3 = st.columns(3)
with col_b1:
    st.button("➤ Quero calcular o volume", use_container_width=True)
with col_b2:
    st.button("➤ Quero calcular o rendimento", use_container_width=True)
with col_b3:
    st.button("➤ Quero estimar a melhor composição", use_container_width=True)

st.write("---")
st.subheader("Meus lançamentos")

# Cabeçalho do Lançamento
col_hdr1, col_hdr2 = st.columns([3, 1])
with col_hdr1:
    st.markdown("### ▼ Lançamento Atual")
with col_hdr2:
    st.markdown('<span class="badge-status">Em andamento</span>', unsafe_allow_html=True)

st.caption("31 dias de digestão anaeróbia")

# Layout de duas colunas (Gráfico à esquerda | Inputs e Resultados à direita)
col_grafico, col_inputs = st.columns(2)

with col_inputs:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Caracterização")
    
    # Entradas do usuário
    vol_total = st.number_input("Volume Total do Reator (mL)", value=500.0, step=50.0)
    headspace = st.slider("Porcentagem de Headspace (%)", min_value=10.0, max_value=80.0, value=30.0)
    
    st.markdown("**Inóculo 1**")
    sv_inoculo = st.number_input("Concentração de SV do Inóculo (g/L)", value=15.0, step=1.0)
    
    st.markdown("**Substrato 1**")
    sv_substrato = st.number_input("Concentração de SV do Substrato (g/L)", value=40.0, step=1.0)
    
    razao_is = st.number_input("Razão Inóculo/Substrato (I/S em SV)", value=2.0, step=0.5)
    
    # Cálculos automatizados
    vol_headspace = vol_total * (headspace / 100.0)
    vol_util = vol_total - vol_headspace
    vol_util_l = vol_util / 1000.0
    
    fator = (razao_is * sv_substrato) / sv_inoculo
    vol_sub_l = vol_util_l / (1 + fator)
    vol_inoc_l = vol_util_l - vol_sub_l
    
    st.markdown("---")
    st.markdown("**Resultados Calculados:**")
    res_c1, res_c2 = st.columns(2)
    res_c1.metric("Vol. Inóculo", f"{round(vol_inoc_l * 1000, 1)} mL")
    res_c2.metric("Vol. Substrato", f"{round(vol_sub_l * 1000, 1)} mL")
    
    res_c3, res_c4 = st.columns(2)
    res_c3.metric("Vol. Útil", f"{round(vol_util, 1)} mL")
    res_c4.metric("Vol. Headspace", f"{round(vol_headspace, 1)} mL")
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_grafico:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Rendimento Estimado de Biometano**")
    
    # Gráfico Matplotlib estilizado para Dark Mode
    fig, ax = plt.subplots(figsize=(5, 4))
    fig.patch.set_facecolor('#18181B')
    ax.set_facecolor('#18181B')
    
    ratios = ["1:2", "2:1", "1:3", "1:1"]
    valores = [380, 240, 310, 290]
    
    ax.bar(ratios, valores, color="#818CF8", width=0.5)
    ax.tick_params(colors="#A1A1AA", labelsize=9)
    ax.set_ylabel("mL CH4 / g SV", color="#A1A1AA", fontsize=9)
    
    for spine in ax.spines.values():
        spine.set_color('#27272A')
        
    st.pyplot(fig)
    st.markdown('</div>', unsafe_allow_html=True)
