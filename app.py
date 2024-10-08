import streamlit as st
from fpdf import FPDF
from datetime import datetime
import pandas as pd

# Caminho fixo do arquivo Excel
CAMINHO_ARQUIVO = "teste_produtos.xlsx"  # Substitua pelo caminho do seu arquivo

# Função para carregar a base de produtos do arquivo Excel
@st.cache_data
def carregar_produtos_excel(caminho_arquivo):
    return pd.read_excel("teste_produtos.xlsx")

# Função para gerar o PDF com todos os produtos
def gerar_pdf(produtos):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Relatório de Validade de Produto", ln=True, align="C")
    pdf.ln(10)

    # Adicionar data e hora de geração
    data_hora_geracao = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    pdf.cell(200, 10, txt=f"Data e Hora de Geração: {data_hora_geracao}", ln=True)
    pdf.ln(10)

    for produto in produtos:
        pdf.cell(200, 10, txt=f"Código do Produto: {produto['codigo']}", ln=True)
        pdf.cell(200, 10, txt=f"Descrição: {produto['descricao']}", ln=True)  # Adicionado descrição
        pdf.cell(200, 10, txt=f"Data de Validade: {produto['validade'].strftime('%d/%m/%Y')}", ln=True)
        pdf.cell(200, 10, txt=f"Quantidade: {produto['quantidade']}", ln=True)
        pdf.cell(200, 10, txt=f"Promoção: {produto['promocao']}", ln=True)
        pdf.ln(10)

    pdf_output_path = "relatorio_validade.pdf"
    pdf.output(pdf_output_path)

    return pdf_output_path

# Interface do Streamlit
def app():
    st.title("Cadastro de Validade de Produtos")

    # Carregar o arquivo Excel automaticamente
    df_produtos = carregar_produtos_excel(CAMINHO_ARQUIVO)

    # Recuperar lista de produtos da sessão ou inicializar se não existir
    if "produtos" not in st.session_state:
        st.session_state.produtos = []
    
    # Recuperar produtos informados do estado da sessão
    if "produtos_inicializados" not in st.session_state:
        st.session_state.produtos = []  # Inicializar a lista de produtos
        st.session_state.produtos_inicializados = True  # Indicar que os produtos foram inicializados

    # Inicializar campos se não estiverem definidos
    if "codigo_barras_produto" not in st.session_state:
        st.session_state.codigo_barras_produto = ""
    if "descricao_produto" not in st.session_state:
        st.session_state.descricao_produto = ""
    if "quantidade" not in st.session_state:
        st.session_state.quantidade = 1
    if "promocao" not in st.session_state:
        st.session_state.promocao = "Não"
    if "validade_input" not in st.session_state:
        st.session_state.validade_input = datetime.today()

    # Entrada de texto para código de barras ou descrição
    pesquisa_produto = st.text_input("Pesquisar produto por código de barras ou descrição")

    # Verificar se a busca corresponde a um código de barras ou descrição
    if pesquisa_produto:
        produto_encontrado = df_produtos[
            (df_produtos["codigo_barras"].astype(str).str.contains(pesquisa_produto)) |
            (df_produtos["descricao"].str.contains(pesquisa_produto, case=False))
        ]

        if not produto_encontrado.empty:
            descricao_produto = produto_encontrado.iloc[0]["descricao"]
            codigo_barras_produto = produto_encontrado.iloc[0]["codigo_barras"]
            st.write(f"Produto encontrado: **{descricao_produto}** (Código: {codigo_barras_produto})")
            # Atualizar os campos com os dados do produto encontrado
            st.session_state.codigo_barras_produto = codigo_barras_produto
            st.session_state.descricao_produto = descricao_produto
            st.session_state.validade_input = datetime.today()
        else:
            descricao_produto = ""
            codigo_barras_produto = ""
            st.write("Produto não encontrado. Insira os dados manualmente.")
    else:
        descricao_produto = ""
        codigo_barras_produto = ""

    # Exibir campos de entrada
    st.session_state.codigo_barras_produto = st.text_input("Código de Barras", value=st.session_state.codigo_barras_produto)
    st.session_state.descricao_produto = st.text_input("Descrição do Produto", value=st.session_state.descricao_produto)
    st.session_state.quantidade = st.number_input("Quantidade do Produto", min_value=1, value=st.session_state.quantidade)
    st.session_state.promocao = st.radio("Foi feita promoção com este produto?", ("Sim", "Não"), index=1 if st.session_state.promocao == "Não" else 0)
    st.session_state.validade_input = st.date_input("Data de Validade", min_value=datetime.today(), value=st.session_state.validade_input)

    # Exibir lista de produtos cadastrados em forma de DataFrame
    if len(st.session_state.produtos) > 0:
        st.subheader("Produtos Informados:")
        
        # Criar DataFrame a partir da lista de produtos
        df_produtos_cadastrados = pd.DataFrame(st.session_state.produtos)

        # Ordenar o DataFrame pela coluna 'validade' em ordem decrescente
        df_produtos_cadastrados.sort_values(by='validade', ascending=False, inplace=True)

        # Exibir DataFrame como uma tabela interativa
        st.dataframe(df_produtos_cadastrados)

    # Botão para adicionar o produto à lista
    if st.button("Adicionar Produto"):
        if st.session_state.codigo_barras_produto and st.session_state.descricao_produto and st.session_state.validade_input:
            produto = {
                "codigo": st.session_state.codigo_barras_produto,
                "descricao": st.session_state.descricao_produto,  # Adicionando descrição
                "validade": datetime.strptime(str(st.session_state.validade_input), '%Y-%m-%d'),
                "quantidade": st.session_state.quantidade,
                "promocao": st.session_state.promocao,
            }
            st.session_state.produtos.append(produto)
            st.success(f"Produto {st.session_state.codigo_barras_produto} adicionado com sucesso!")

            # Limpar campos após adicionar
            st.session_state.codigo_barras_produto = ""
            st.session_state.descricao_produto = ""
            st.session_state.quantidade = 1
            st.session_state.promocao = "Não"
            st.session_state.validade_input = datetime.today()
        else:
            st.error("Por favor, preencha os campos obrigatórios.")

    # Botão para gerar o PDF com todos os produtos
    if st.button("Gerar PDF"):
        if len(st.session_state.produtos) > 0:
            pdf_path = gerar_pdf(st.session_state.produtos)
            st.success("PDF gerado com sucesso!")

            # Link para download do PDF
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="Baixar PDF",
                    data=f,
                    file_name=pdf_path,
                    mime="application/pdf"
                )
        else:
            st.error("Nenhum produto cadastrado para gerar o PDF.")

    # Botão para limpar campos
    if st.button("Limpar Campos"):
        st.session_state.codigo_barras_produto = ""
        st.session_state.descricao_produto = ""
        st.session_state.quantidade = 1
        st.session_state.promocao = "Não"
        st.session_state.validade_input = datetime.today()
        st.success("Campos limpos com sucesso!")

if __name__ == "__main__":
    app()
