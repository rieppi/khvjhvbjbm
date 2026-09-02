# Inicialização do estado dos compostos (caso não exista)
if "compostos" not in st.session_state:
    st.session_state.compostos = [
        {"nome": "Inóculo 1", "valor": 15.0, "unidade": "g/mL"},
        {"nome": "Substrato 1", "valor": 40.0, "unidade": "g/g"},
    ]


@st.dialog("Dimensionamento do Ensaio", width="small")
def modal_calcular_volume():
    if st.session_state.etapa_modal_vol == 1:
        st.markdown("### Caracterização")

        # Renderização dinâmica dos compostos
        for i, comp in enumerate(st.session_state.compostos):
            # Nome do composto editável
            novo_nome = st.text_input(
                f"Nome do composto {i+1}",
                value=comp["nome"],
                key=f"nome_comp_{i}",
                label_visibility="collapsed",
            )
            st.session_state.compostos[i]["nome"] = novo_nome

            # Inputs de Valor e Unidade
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

        # Botão para adicionar novo composto dinâmico
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

        # Navegação no canto inferior direito
        _, col_next = st.columns([3, 1])
        if col_next.button("Próximo ➔", key="btn_vol_next"):
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

        col_back, _ = st.columns([1, 3])
        if col_back.button("⬅ Voltar", key="btn_vol_back"):
            st.session_state.etapa_modal_vol = 1
            st.rerun()
