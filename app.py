from datetime import date
import io
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Importações para a geração de PDF (ReportLab)
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

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
# FUNÇÕES AUXILIARES DE GERAÇÃO DE PDF
# ---------------------------------------------------------
def gerar_pdf_popup_calculos(dados_popup):
    """Gera o PDF com o resumo dos cálculos iniciais no pop-up."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor('#4F46E5'))
    sub_style = ParagraphStyle('Sub', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor('#27272A'))
    body_bold = ParagraphStyle('BodyB', parent=styles['Normal'], fontSize=9, leading=12, fontName='Helvetica-Bold')
    body_style = ParagraphStyle('BodyN', parent=styles['Normal'], fontSize=9, leading=12)

    # Título do Relatório
    story.append(Paragraph(f"<b>Relatório de Lançamento: {dados_popup.get('titulo', '')}</b>", title_style))
    story.append(Paragraph(f"Período: {dados_popup.get('data_str', '')}", body_style))
    story.append(Spacer(1, 15))

    # Tabela 1: Totais Gerais por Composto
    story.append(Paragraph("<b>1. Volume / Massa Total dos Compostos (Todas Réplicas)</b>", sub_style))
    story.append(Spacer(1, 6))
    
    data_totais = [["Composto", "Concentração SV", "Total Necessário (Ensaio)"]]
    for t in dados_popup.get("totais_compostos", []):
        data_totais.append([t.get("nome", ""), t.get("conc", ""), t.get("total_formatado", "")])
    
    t_totais = Table(data_totais, colWidths=[200, 150, 180])
    t_totais.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0E7FF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#3730A3')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    story.append(t_totais)
    story.append(Spacer(1, 15))

    # Tabela 2: Condições dos Reatores
    story.append(Paragraph("<b>2. Detalhamento por Condição (Quantidades e Correção de pH)</b>", sub_style))
    story.append(Spacer(1, 6))

    data_cond = [["Razão (I:S)", "Headspace", "Vol. Útil", "Réplicas", "Reagentes / Reator", "pH Médio", "NaHCO3 Médio"]]
    for c in dados_popup.get("detalhes_condicoes", []):
        reag_str = "\n".join([f"• {r.get('nome')}: {r.get('qtd')}" for r in c.get("reagentes", [])])
        bic_g = c.get("nahco3_medio_g", 0.0)
        bic_str = f"{bic_g*1000:.1f} mg" if bic_g > 0 else "0.0 mg"

        data_cond.append([
            c.get("proporcao", ""),
            f"{c.get('headspace')}%",
            f"{c.get('vol_util_ml')} mL",
            str(c.get("replicas")),
            Paragraph(reag_str.replace("\n", "<br/>"), body_style),
            f"{c.get('ph_medio', 0.0):.2f}",
            bic_str
        ])

    t_cond = Table(data_cond, colWidths=[65, 60, 60, 50, 160, 60, 75])
    t_cond.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    story.append(t_cond)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def gerar_pdf_relatorio_finalizado(item):
    """Gera o PDF completo de um lançamento finalizado com resultados de rendimento."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor('#1E1B4B'))
    sub_style = ParagraphStyle('Sub', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor('#334155'))
    body_style = ParagraphStyle('BodyN', parent=styles['Normal'], fontSize=9, leading=12)

    # Título
    story.append(Paragraph(f"<b>Relatório Final do Ensaio: {item.get('titulo', '')}</b>", title_style))
    story.append(Paragraph(f"Data/Duração: {item.get('data_str', '')} | Status: <b>{item.get('status', '')}</b>", body_style))
    story.append(Spacer(1, 15))

    # Tabela Compostos
    story.append(Paragraph("<b>1. Caracterização dos Compostos Utilizados</b>", sub_style))
    story.append(Spacer(1, 6))
    data_comp = [["Composto", "Concentração SV", "Total Consumido no Ensaio"]]
    for c in item.get("compostos", []):
        data_comp.append([c.get("nome", ""), c.get("conc", ""), c.get("qtd_total", "")])
    
    t_comp = Table(data_comp, colWidths=[200, 150, 180])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0E7FF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#3730A3')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 15))

    # Tabela Rendimento Final
    story.append(Paragraph("<b>2. Resultados de Rendimento e Produção de Biogás</b>", sub_style))
    story.append(Spacer(1, 6))
    
    data_rend = [["Razão (I:S)", "% CH4 no Biogás", "Volume Biogás (mL)", "Volume CH4 (mL)", "Rendimento (mL CH4 / g SV)"]]
    for r in item.get("dados_rendimento", []):
        data_rend.append([
            r.get("composicao", ""),
            f"{r.get('fracao_metano', 0.0):.1f}%",
            f"{r.get('vol_biogas', 0.0):.1f}",
            f"{r.get('vol_ch4', 0.0):.1f}",
            f"{r.get('rendimento', 0.0):.1f}"
        ])

    t_rend = Table(data_rend, colWidths=[80, 100, 110, 100, 140])
    t_rend.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FEF3C7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#92400E')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_rend)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# ---------------------------------------------------------
# CÁLCULOS E GRÁFICOS
# ---------------------------------------------------------
def calcular_bicarbonato(ph_atual, ph_alvo, vol_util_ml):
    if ph_atual >= ph_alvo or ph_atual <= 0:
        return 0.0

    delta_ph = ph_alvo - ph_atual
    beta = 0.02  # mol H+ / L / unidade de pH
    vol_litros = vol_util_ml / 1000.0

    moles_nahco3 = beta * delta_ph * vol_litros
    massa_g = moles_nahco3 * 84.007
    return round(massa_g, 4)


@st.cache_resource(show_spinner=False)
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

    return fig


@st.cache_resource(show_spinner=False)
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

    return fig


def gerar_excel_quantidades(condicoes, compostos):
    rows = []
    vol_frasco = 250.0
    qtd_compostos = len(compostos) if compostos else 1

    for idx, cond in enumerate(condicoes):
        hs = float(cond.get("headspace", 30.0))
        vol_util = vol_frasco * (1 - (hs / 100.0))
        replicas = int(cond.get("replicas", 3))

        for c in compostos:
            unidade = c.get("unidade", "g/mL")
            val_conc = c.get("valor", 0.0)

            if unidade == "g/mL":
                qtd_reator = round(vol_util / max(1, qtd_compostos), 1)
                unit_str = "mL"
            else:
                qtd_reator = round((vol_util / max(1, qtd_compostos)) * 0.5, 1)
                unit_str = "g"

            qtd_total_ensaio = round(qtd_reator * replicas, 1)

            rows.append(
                {
                    "Condição": f"Condição #{idx+1}",
                    "Razão (I:S)": cond.get("composicao", "1:1"),
                    "Headspace (%)": hs,
                    "Volume Útil/Reator (mL)": vol_util,
                    "Réplicas": replicas,
                    "Composto": c.get("nome", ""),
                    "Concentração SV": f"{val_conc} {unidade}",
                    "Qtd / Reator": f"{qtd_reator} {unit_str}",
                    "Qtd Total Condição": f"{qtd_total_ensaio} {unit_str}",
                }
            )

    df = pd.DataFrame(rows)
    return df.to_csv(index=False, sep=";").encode("utf-8-sig")


# Inicialização de Estado
if "modal_ativo" not in st.session_state:
    st.session_state.modal_ativo = None
if "etapa_modal_vol" not in st.session_state:
    st.session_state.etapa_modal_vol = 1
if "etapa_modal_rend" not in st.session_state:
    st.session_state.etapa_modal_rend = 1
if "scroll_to_novo" not in st.session_state:
    st.session_state.scroll_to_novo = False
if "resumo_calculo_popup" not in st.session_state:
    st.session_state.resumo_calculo_popup = None

if "compostos" not in st.session_state:
    st.session_state.compostos = [
        {"nome": "Inóculo 1", "valor": 15.0, "unidade": "g/mL"},
        {"nome": "Substrato 1", "valor": 40.0, "unidade": "g/g"},
    ]

if "condicoes" not in st.session_state:
    st.session_state.condicoes = [
        {"headspace": 30.0, "composicao": "2:1", "replicas": 3, "ph_replicas": [6.5, 6.6, 6.5]},
        {"headspace": 30.0, "composicao": "1:1", "replicas": 3, "ph_replicas": [6.8, 6.7, 6.8]},
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
                    "qtd_total": "622.5 mL",
                },
                {
                    "nome": "Substrato 1",
                    "conc": "40.0 g/g",
                    "qtd_total": "382.5 g",
                },
            ],
            "composicoes_estudadas": [
                {
                    "proporcao": "2:1",
                    "carga": "0.082 g SV/mL",
                    "headspace": 30.0,
                    "replicas": 3,
                    "ph_medio": 6.53,
                    "nahco3_medio_g": 0.105,
                    "massa_sv_val": 14.40,
                    "reagentes": [
                        {"nome": "Inóculo 1", "qtd": "120.0 mL"},
                        {"nome": "Substrato 1", "qtd": "40.0 g"},
                    ],
                },
                {
                    "proporcao": "1:1",
                    "carga": "0.082 g SV/mL",
                    "headspace": 30.0,
                    "replicas": 3,
                    "ph_medio": 6.77,
                    "nahco3_medio_g": 0.049,
                    "massa_sv_val": 14.40,
                    "reagentes": [
                        {"nome": "Inóculo 1", "qtd": "87.5 mL"},
                        {"nome": "Substrato 1", "qtd": "87.5 g"},
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
            ],
        }
    ]


# ---------------------------------------------------------
# MODAIS
# ---------------------------------------------------------
@st.dialog("📋 Resumo do Lançamento e Correção de pH", width="medium")
def modal_resumo_popup():
    dados = st.session_state.resumo_calculo_popup
    if not dados:
        st.write("Sem dados para exibir.")
        return

    st.subheader(f"🧪 {dados.get('titulo', 'Lançamento')}")
    st.caption(f"Período: {dados.get('data_str', '')}")
    st.divider()

    st.markdown("### 📦 Total de Compostos Necessários (Todas as Condições & Réplicas)")
    totais_comp = dados.get("totais_compostos", [])
    if totais_comp:
        cols = st.columns(len(totais_comp))
        for idx, t_comp in enumerate(totais_comp):
            cols[idx % len(cols)].metric(t_comp["nome"], t_comp["total_formatado"], help=f"Concentração: {t_comp['conc']}")

    st.divider()
    st.markdown("### Quantidades por Reator e Parâmetros Médios")
    for cond in dados.get("detalhes_condicoes", []):
        with st.container(border=True):
            st.markdown(f"**Razão (I:S): `{cond.get('proporcao', '1:1')}`** | Headspace: **{cond.get('headspace', 30.0)}%** | Vol. Útil: **{cond.get('vol_util_ml', 175.0)} mL** | Réplicas: **{cond.get('replicas', 3)}**")
            
            c_comp, c_ph = st.columns([1.2, 1])
            with c_comp:
                st.markdown("**Substratos/Inóculo por Reator:**")
                for r in cond.get("reagentes", []):
                    st.write(f"• **{r.get('nome', '')}**: {r.get('qtd', '')}")

            with c_ph:
                st.markdown("**Parâmetros Médios:**")
                ph_medio_val = cond.get("ph_medio", 7.0)
                st.write(f"• **pH Médio Inicial:** `{ph_medio_val:.2f}`")
                
                bic_m_g = cond.get("nahco3_medio_g", 0.0)
                if bic_m_g > 0:
                    st.write(f"• **NaHCO₃ Médio:** `{bic_m_g*1000:.1f} mg` ({bic_m_g:.3f} g)")
                else:
                    st.write("• **NaHCO₃ Médio:** `0.0 mg` *(pH ≥ 7.00)*")

    st.divider()
    
    # Gerar e permitir o download do PDF dos cálculos iniciais
    pdf_bytes = gerar_pdf_popup_calculos(dados)
    
    col_pdf, col_sair = st.columns([1, 1])
    with col_pdf:
        st.download_button(
            label="📄 Baixar PDF do Lançamento",
            data=pdf_bytes,
            file_name=f"calculos_{dados.get('titulo', 'lancamento').lower().replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        
    with col_sair:
        if st.button("👍 Entendido / Sair", type="primary", use_container_width=True):
            st.session_state.modal_ativo = None
            st.session_state.resumo_calculo_popup = None
            st.rerun()


@st.dialog("➕ Registrar Novo Lançamento", width="small")
def modal_calcular_volume():
    if st.session_state.etapa_modal_vol == 1:
        st.subheader("1. Identificação e Período")

        nome_lancamento = st.text_input(
            "Nome do Lançamento",
            value=f"Lançamento {date.today().strftime('%d/%m/%Y')}",
            key="input_nome_lancamento",
        )

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
        st.subheader("2. Caracterização dos Compostos")

        for i, comp in enumerate(st.session_state.compostos):
            with st.container(border=True):
                st.markdown(f"**Composto #{i+1}**")
                novo_nome = st.text_input(
                    "Nome", value=comp["nome"], key=f"nome_comp_{i}"
                )

                c_val, c_unit = st.columns([2, 1])
                novo_val = c_val.number_input(
                    "Concentração SV",
                    value=float(comp["valor"]),
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
        st.subheader("3. Condições dos Reatores")

        st.checkbox(
            "Fazer correção de pH no meio",
            value=True,
            key="cb_corrigir_ph",
        )

        usar_mesmo_hs = st.checkbox(
            "Usar o mesmo Headspace para todas as condições",
            value=True,
            key="cb_mesmo_headspace",
        )

        first_hs = float(st.session_state.condicoes[0]["headspace"])

        for i, cond in enumerate(st.session_state.condicoes):
            with st.container(border=True):
                st.markdown(f"**Condição #{i+1}**")
                c1, c2, c3 = st.columns(3)

                disable_hs = usar_mesmo_hs and i > 0
                val_hs = first_hs if disable_hs else float(cond["headspace"])

                hs = c1.number_input(
                    "Headspace (%)",
                    value=val_hs,
                    step=5.0,
                    disabled=disable_hs,
                    key=f"hs_{i}",
                )

                if i == 0 and usar_mesmo_hs:
                    first_hs = hs

                comp = c2.text_input(
                    "Razão (I:S)", value=cond["composicao"], key=f"comp_{i}"
                )
                rep = c3.number_input(
                    "Réplicas", value=int(cond.get("replicas", 3)), min_value=1, step=1, key=f"rep_{i}"
                )

                ph_list = cond.get("ph_replicas", [6.8] * int(rep))
                if len(ph_list) != int(rep):
                    ph_list = [6.8] * int(rep)

                st.session_state.condicoes[i] = {
                    "headspace": hs,
                    "composicao": comp,
                    "replicas": rep,
                    "ph_replicas": ph_list,
                }

        if usar_mesmo_hs:
            for cond in st.session_state.condicoes:
                cond["headspace"] = first_hs

        if st.button("➕ Adicionar Condição", key="add_cond"):
            padrao_hs = first_hs if usar_mesmo_hs else 30.0
            st.session_state.condicoes.append(
                {"headspace": padrao_hs, "composicao": "1:1", "replicas": 3, "ph_replicas": [6.8, 6.8, 6.8]}
            )
            st.rerun()

        excel_bytes = gerar_excel_quantidades(
            st.session_state.condicoes, st.session_state.compostos
        )
        st.download_button(
            label="📥 Baixar Cálculo de Quantidades (.csv)",
            data=excel_bytes,
            file_name="calculo_quantidades_reatores.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.divider()

        col_back, col_next = st.columns(2)
        with col_back:
            if st.button("⬅ Voltar", use_container_width=True):
                st.session_state.etapa_modal_vol = 2
                st.rerun()

        with col_next:
            if st.button("Próximo ➔", use_container_width=True, type="primary"):
                st.session_state.etapa_modal_vol = 4
                st.rerun()

    elif st.session_state.etapa_modal_vol == 4:
        st.subheader("4. pH Inicial das Réplicas")
        st.caption("Insira o pH inicial individual das réplicas para calcular as médias de pH e Bicarbonato de Sódio (NaHCO₃):")

        vol_frasco = 250.0

        for i, cond in enumerate(st.session_state.condicoes):
            num_rep = int(cond.get("replicas", 3))
            lista_ph = cond.get("ph_replicas", [6.8] * num_rep)
            if len(lista_ph) != num_rep:
                lista_ph = [6.8] * num_rep

            vol_util = vol_frasco * (1.0 - (float(cond["headspace"]) / 100.0))

            with st.container(border=True):
                st.markdown(f"**Condição #{i+1}** - Razão (I:S): `{cond['composicao']}` | Vol. Útil: **{vol_util:.1f} mL**")
                
                novos_phs = []
                cols = st.columns(min(num_rep, 4))
                for r in range(num_rep):
                    col_idx = r % 4
                    val_ph = cols[col_idx].number_input(
                        f"Réplica {r+1}",
                        min_value=0.0,
                        max_value=14.0,
                        value=float(lista_ph[r]),
                        step=0.1,
                        key=f"ph_cond_{i}_rep_{r}",
                    )
                    novos_phs.append(val_ph)

                st.session_state.condicoes[i]["ph_replicas"] = novos_phs

                ph_medio_cond = float(np.mean(novos_phs))
                bicarb_por_rep = [calcular_bicarbonato(p, 7.00, vol_util) for p in novos_phs]
                bicarb_medio_cond = float(np.mean(bicarb_por_rep))

                if bicarb_medio_cond > 0:
                    st.caption(f"💡 **Média do pH:** `{ph_medio_cond:.2f}` | **Média de NaHCO₃:** `{bicarb_medio_cond*1000:.1f} mg` ({bicarb_medio_cond:.3f} g)")
                else:
                    st.caption(f"💡 **Média do pH:** `{ph_medio_cond:.2f}` | ✅ pH adequado (≥ 7.00). Nenhum bicarbonato necessário.")

        st.divider()

        col_back, col_finish = st.columns(2)
        with col_back:
            if st.button("⬅ Voltar", use_container_width=True):
                st.session_state.etapa_modal_vol = 3
                st.rerun()

        with col_finish:
            if st.button(
                "🚀 Finalizar e Calcular",
                type="primary",
                use_container_width=True,
            ):
                vol_frasco = 250.0
                qtd_compostos = len(st.session_state.compostos)
                
                massa_sv_total_geral = 0.0
                composicoes_estudadas = []
                detalhes_popup_condicoes = []

                totais_por_composto = {c["nome"]: {"qtd": 0.0, "unidade": c["unidade"], "valor_conc": c["valor"]} for c in st.session_state.compostos}

                for cond in st.session_state.condicoes:
                    hs = float(cond["headspace"])
                    vol_util = vol_frasco * (1.0 - (hs / 100.0))
                    num_rep = int(cond["replicas"])
                    phs = cond.get("ph_replicas", [7.0] * num_rep)

                    reagentes_cond = []
                    massa_sv_cond = 0.0

                    for c in st.session_state.compostos:
                        unidade = c["unidade"]
                        val_conc = c["valor"] if c["valor"] > 0 else 1.0

                        if unidade == "g/mL":
                            qtd_por_reator = round(vol_util / max(1, qtd_compostos), 1)
                            qtd_str = f"{qtd_por_reator} mL"
                            massa_sv = qtd_por_reator * (val_conc / 100.0)
                        else:
                            qtd_por_reator = round((vol_util / max(1, qtd_compostos)) * 0.5, 1)
                            qtd_str = f"{qtd_por_reator} g"
                            massa_sv = qtd_por_reator * (val_conc / 100.0)

                        massa_sv_cond += massa_sv
                        reagentes_cond.append({
                            "nome": c["nome"],
                            "qtd": qtd_str,
                        })

                        totais_por_composto[c["nome"]]["qtd"] += (qtd_por_reator * num_rep)

                    massa_sv_total_geral += (massa_sv_cond * num_rep)
                    carga_comp = massa_sv_cond / vol_util if vol_util > 0 else 0.0

                    ph_medio = float(np.mean(phs))
                    bicarb_reps = [calcular_bicarbonato(p, 7.00, vol_util) for p in phs]
                    bicarb_medio_g = float(np.mean(bicarb_reps))

                    composicoes_estudadas.append({
                        "proporcao": cond["composicao"],
                        "carga": f"{carga_comp:.3f} g SV/mL",
                        "headspace": hs,
                        "replicas": num_rep,
                        "ph_medio": ph_medio,
                        "nahco3_medio_g": bicarb_medio_g,
                        "massa_sv_val": massa_sv_cond,
                        "reagentes": reagentes_cond,
                    })

                    detalhes_popup_condicoes.append({
                        "proporcao": cond["composicao"],
                        "headspace": hs,
                        "vol_util_ml": vol_util,
                        "replicas": num_rep,
                        "reagentes": reagentes_cond,
                        "ph_medio": ph_medio,
                        "nahco3_medio_g": bicarb_medio_g,
                    })

                compostos_calculados_geral = []
                totais_popup = []
                for name, data in totais_por_composto.items():
                    unit_str = "mL" if data["unidade"] == "g/mL" else "g"
                    total_fmt = f"{data['qtd']:.1f} {unit_str}"
                    
                    compostos_calculados_geral.append({
                        "nome": name,
                        "conc": f"{data['valor_conc']} {data['unidade']}",
                        "qtd_total": total_fmt,
                    })
                    
                    totais_popup.append({
                        "nome": name,
                        "conc": f"{data['valor_conc']} {data['unidade']}",
                        "total_formatado": total_fmt
                    })

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
                    "massa_sv_total_val": massa_sv_total_geral,
                    "massa_sv_total": f"{massa_sv_total_geral:.2f} g SV",
                    "carga_volumetrica": f"{composicoes_estudadas[0]['carga']}",
                    "compostos": compostos_calculados_geral,
                    "composicoes_estudadas": composicoes_estudadas,
                    "dados_rendimento": None,
                }

                st.session_state.lista_lancamentos.insert(0, novo_item)
                
                st.session_state.resumo_calculo_popup = {
                    "titulo": nome_lan,
                    "data_str": f"{dt_ini.strftime('%d/%m/%Y')} • {dias_lan} dias de digestão",
                    "totais_compostos": totais_popup,
                    "detalhes_condicoes": detalhes_popup_condicoes,
                }

                st.session_state.toast_msg = "✅ Lançamento e cálculos concluídos!"
                st.session_state.scroll_to_novo = True
                st.session_state.etapa_modal_vol = 1
                st.session_state.modal_ativo = "popup_resumo"
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
        dados_replicas_temp = []

        for idx_comp, comp in enumerate(lanc.get("composicoes_estudadas", [])):
            prop = comp["proporcao"]
            massa_sv = comp.get("massa_sv_val", 1.0)
            num_replicas = int(comp.get("replicas", 3))

            with st.container(border=True):
                st.markdown(f"### 🧪 Razão `(I:S) {prop}`")
                st.caption(
                    f"Headspace: {comp.get('headspace', 30.0)}% | Réplicas: {num_replicas}"
                )
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
# DASHBOARD PRINCIPAL
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
        "Registre e calcule automaticamente o volume ou massa dos compostos e o bicarbonato"
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
elif st.session_state.modal_ativo == "popup_resumo":
    modal_resumo_popup()

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
            st.markdown("**Compostos Envolvidos e Quantidades Totais Necessárias:**")
            for comp in item["compostos"]:
                with st.container(border=True):
                    c_n, c_c, c_t = st.columns(3)
                    c_n.markdown(f'<span class="pill-tag">{comp["nome"]}</span>', unsafe_allow_html=True)
                    c_c.caption(f"Concentração: **{comp['conc']}**")
                    c_t.markdown(f"**Total / Ensaio:** `{comp.get('qtd_total', 'N/A')}`")

        with tab2:
            st.markdown("**Composições e Parâmetros Médios:**")
            for comp_est in item.get("composicoes_estudadas", []):
                with st.container(border=True):
                    c_prop, c_carga, c_hs, c_rep = st.columns(4)
                    c_prop.markdown(f"**Razão (I:S):** `{comp_est['proporcao']}`")
                    c_carga.markdown(f"**Carga Orgânica:** `{comp_est['carga']}`")
                    c_hs.markdown(f"**Headspace:** `{comp_est.get('headspace', 'N/A')}%`")
                    c_rep.markdown(f"**Réplicas:** `{comp_est.get('replicas', 'N/A')}`")

                    ph_m = comp_est.get("ph_medio", "N/A")
                    bic_m = comp_est.get("nahco3_medio_g", 0.0)

                    st.markdown("**Médias da Condição:**")
                    st.caption(f"• **pH Inicial Médio:** `{ph_m if isinstance(ph_m, str) else f'{ph_m:.2f}'}`")
                    st.caption(f"• **Média de NaHCO₃ Necessário:** `{bic_m*1000:.1f} mg` ({bic_m:.3f} g)")

                    st.caption("**Quantidades por Reator:**")
                    for r in comp_est.get("reagentes", []):
                        st.caption(f"• **{r.get('nome', '')}**: {r.get('qtd', '')}")

        with tab3:
            dados_r = item.get("dados_rendimento")
            if item["tem_grafico"] and dados_r:
                labels = tuple([d["composicao"] for d in dados_r])
                rend = tuple([d["rendimento"] for d in dados_r])
                ch4 = tuple([d["fracao_metano"] for d in dados_r])

                fig = gerar_grafico_rendimento(labels, rend, ch4)
                st.pyplot(fig)
                
                st.divider()
                # Botão para baixar o PDF completo do Lançamento Finalizado
                pdf_finalizado_bytes = gerar_pdf_relatorio_finalizado(item)
                st.download_button(
                    label="📄 Baixar PDF do Relatório Completo",
                    data=pdf_finalizado_bytes,
                    file_name=f"relatorio_final_{item['titulo'].lower().replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            else:
                st.info(
                    "ℹ️ Medições não adicionadas. Clique em **'📊 Calcular rendimento'** no topo para registrar as réplicas."
                )

# Autoscroll
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
