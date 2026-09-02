# Adicione este trecho ao seu CSS inicial no app.py para alinhar e estilizar os dots de paginação
st.markdown(
    """
<style>
    /* Estilização para alinhar inputs e seletores na mesma linha */
    div[data-testid="column"] {
        display: flex;
        align-items: center;
    }
    /* Centralizador dos botões de paginação */
    .pagination-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 8px;
        margin-top: 15px;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# MODAL RENDIMENTO (CORRIGIDO)
# ---------------------------------------------------------
@st.dialog("Rendimento", width="small")
def modal_calcular_rendimento():

    # --- ETAPA 1 ---
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

        # Campo 1: Fração de Metano
        st.markdown("**Fração de Metano (%)**")
        col_m1, col_m2 = st.columns([4, 1])
        with col_m1:
            f_metano = st.number_input(
                "Fração de Metano",
                value=60.0,
                step=1.0,
                label_visibility="collapsed",
            )
        with col_m2:
            st.markdown("<p style='padding-top:8px;'>%</p>", unsafe_allow_html=True)

        # Campo 2: Volume de Biogás
        st.markdown("**Volume de Biogás (mL)**")
        col_v1, col_v2 = st.columns([4, 1])
        with col_v1:
            v_biogas = st.number_input(
                "Volume de Biogás",
                value=350.0,
                step=10.0,
                label_visibility="collapsed",
            )
        with col_v2:
            st.markdown("<p style='padding-top:8px;'>mL</p>", unsafe_allow_html=True)

        st.write("---")

        # Paginação Centralizada (Etapa 1: Ativa⚪ | Inativa⚫)
        c_left, c_dot1, c_dot2, c_right = st.columns([3, 1, 1, 3])
        with c_dot1:
            # Pág 1 Ativa
            st.button("⚪", key="dot_r1_active", disabled=True)
        with c_dot2:
            # Clique na pág 2 Inativa -> Avança
            if st.button("⚫", key="dot_r1_to_2"):
                st.session_state.fracao_metano = f_metano
                st.session_state.vol_biogas = v_biogas
                st.session_state.etapa_modal_rend = 2
                st.rerun()

    # --- ETAPA 2 ---
    elif st.session_state.etapa_modal_rend == 2:
        st.markdown("### Resultado do Rendimento")

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

        # Paginação Centralizada (Etapa 2: Inativa⚫ | Ativa⚪)
        c_left, c_dot1, c_dot2, c_right = st.columns([3, 1, 1, 3])
        with c_dot1:
            # Clique na pág 1 Inativa -> Volta
            if st.button("⚫", key="dot_r2_to_1"):
                st.session_state.etapa_modal_rend = 1
                st.rerun()
        with c_dot2:
            # Pág 2 Ativa
            st.button("⚪", key="dot_r2_active", disabled=True)
