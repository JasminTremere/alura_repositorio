import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Dashboard Anchieta", 
    page_icon="📊",
    layout="wide"
)

API_URL = "https://app.anchieta.br/Relatorio_Anchieta/python/banco.php"

def load_data():
    try:
        resp = requests.get(API_URL, timeout=30)
        resp.raise_for_status()
        dados_json = resp.json()
        if isinstance(dados_json, dict) and 'data' in dados_json:
            return pd.DataFrame(dados_json['data'])
        return pd.DataFrame(dados_json)
    except Exception as e:
        st.error(f"Erro ao conectar com a API: {e}")
        return pd.DataFrame()

# 1. Carregar e Limpar os dados
df_raw = load_data()

if not df_raw.empty:
    for col in df_raw.columns:
        if df_raw[col].dtype == 'object':
            df_raw[col] = df_raw[col].str.replace('**', '', regex=False).str.strip()

    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.header("🔍 Filtros")
    categorias_disponiveis = sorted(df_raw['CATEGORIA'].unique())
    categorias_selecionadas = st.sidebar.multiselect("Filtrar por Categoria", categorias_disponiveis)
    nomes_disponiveis = sorted(df_raw['NOME'].unique())
    nomes_selecionados = st.sidebar.multiselect("Filtrar por Nome", nomes_disponiveis)
    telefones_disponiveis = sorted(df_raw['TELEFONE'].unique())
    telefones_selecionados = st.sidebar.multiselect("Filtrar por Telefone", telefones_disponiveis)

    # --- APLICAR FILTROS ---
    df_filtrado = df_raw.copy()
    if categorias_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['CATEGORIA'].isin(categorias_selecionadas)]
    if nomes_selecionados:
        df_filtrado = df_filtrado[df_filtrado['NOME'].isin(nomes_selecionados)]
    if telefones_selecionados:
        df_filtrado = df_filtrado[df_filtrado['TELEFONE'].isin(telefones_selecionados)]

    # --- INTERFACE PRINCIPAL ---
    st.title("📊 Dashboard de Análise Anchieta")

    # --- MÉTRICAS ---
    st.subheader("Métricas Principais")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total de registros", len(df_filtrado))
    c2.metric("Categorias Únicas", df_filtrado['CATEGORIA'].nunique())
    c3.metric("Contatos Únicos", df_filtrado['TELEFONE'].nunique())
    st.markdown("---")

    if not df_filtrado.empty:
        # --- PRIMEIRA LINHA DE GRÁFICOS ---
        st.subheader("Análise de Categorias e Assuntos")
        col_graf1, col_graf2 = st.columns(2)

        with col_graf1:
            grafico_categoria = df_filtrado.groupby('CATEGORIA').size().nlargest(10).reset_index(name='Quantidade')
            fig_cat = px.bar(grafico_categoria, x='CATEGORIA', y='Quantidade', title="Top 10 Categorias", text_auto=True)
            st.plotly_chart(fig_cat, use_container_width=True)

        with col_graf2:
            grafico_assunto = df_filtrado['CATEGORIA'].value_counts().reset_index()
            grafico_assunto.columns = ['CATEGORIA', 'Quantidade']
            fig_assunto = px.pie(grafico_assunto, values='Quantidade', names='CATEGORIA', title="Distribuição de Assuntos", hole=0.5)
            fig_assunto.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_assunto, use_container_width=True)

        st.markdown("---")
        st.subheader("🔍 Detalhamento Adicional")
        
        # --- SEGUNDA LINHA: GRÁFICOS DE OUTROS E SUPORTE ---
        col_graf3, col_graf4 = st.columns(2)

        df_outros = df_filtrado[df_filtrado['CATEGORIA'] == 'Outros']
        df_sup = df_filtrado[df_filtrado['CATEGORIA'] == 'Suporte']

        with col_graf3:
            if not df_outros.empty:
                data_outros = df_outros.groupby('SUBCATEGORIA').size().nlargest(10).reset_index(name='Quantidade')
                fig_outros = px.bar(data_outros, x='SUBCATEGORIA', y='Quantidade', title="Subcategorias: Outros", text_auto=True)
                st.plotly_chart(fig_outros, use_container_width=True)
            else:
                st.info("Nenhum dado em 'Outros'.")

        with col_graf4:
            if not df_sup.empty:
                data_sup = df_sup.groupby('SUBCATEGORIA').size().nlargest(10).reset_index(name='Quantidade')
                fig_sup = px.bar(data_sup, x='SUBCATEGORIA', y='Quantidade', title="Subcategorias: Suporte", text_auto=True, color_discrete_sequence=['#2ca02c'])
                st.plotly_chart(fig_sup, use_container_width=True)
            else:
                st.info("Nenhum dado em 'Suporte'.")

        # --- TERCEIRA LINHA: TABELAS (ALINHADAS COM OS GRÁFICOS ACIMA) ---
        col_graf5, col_graf6 = st.columns(2)

        with col_graf5:
            if not df_outros.empty:
                st.write("**Tabela: Detalhes de Outros**")
                # Mostramos a contagem para a tabela ser igual ao gráfico
                tab_outros = df_outros.groupby('SUBCATEGORIA').size().reset_index(name='Quantidade').sort_values('Quantidade', ascending=False)
                st.dataframe(tab_outros, use_container_width=True, hide_index=True)

        with col_graf6:
            if not df_sup.empty:
                st.write("**Tabela: Detalhes de Suporte**")
                tab_sup = df_sup.groupby('SUBCATEGORIA').size().reset_index(name='Quantidade').sort_values('Quantidade', ascending=False)
                st.dataframe(tab_sup, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("📋 Dados Detalhados")
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    else:
        st.warning("Nenhum dado disponível para os filtros selecionados.")
else:
    st.error("O banco de dados está vazio ou a API não respondeu.")
