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

# Função para aplicar o estilo CSS no campo de pesquisa
def aplicar_estilo_css():
    st.markdown(
        """
        <style>
        .stTextInput > div > input {
            background-color: #f0f0f0;
            border: 2px solid #00ccff;
            padding: 10px;
            font-size: 16px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Função para gerar o PDF
def gerar_pdf(produtos):
    # Criação do objeto PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()

    # Definindo fonte para o PDF
    pdf.set_font("Arial", size=10)

    # Título do documento
    pdf.cell(200, 10, txt="Relatório de Validade de Produtos", ln=True, align="C")
    pdf.ln(5)  # Espaçamento

    # Adicionando informações ao PDF
    data_atual = datetime.now().strftime('%d/%m/%Y %H:%M')
    pdf.cell(200, 10, txt=f"Relatório gerado em: {data_atual}", ln=True)
    pdf.ln(5)

    for produto in produtos:
        pdf.cell(200, 10, txt=f"Código: {produto['codigo']}", ln=True)
        pdf.cell(200, 10, txt=f"Descrição: {produto['descricao']}", ln=True)
        pdf.cell(200, 10, txt=f"Validade: {produto['validade'].strftime('%d/%m/%Y')}", ln=True)
        pdf.cell(200, 10, txt=f"Quantidade: {produto['quantidade']}", ln=True)

        # Calcular dias para validade
        dias_faltando = (produto['validade'] - datetime.now()).days

        # Verificar se a validade é menor que 15 dias (vermelho)
        if dias_faltando < 15:
            pdf.set_text_color(255, 0, 0)  # Vermelho
            pdf.cell(200, 10, txt=f"Dias para validade: {dias_faltando} dias", ln=True)

        # Verificar se a validade está entre 16 e 30 dias (amarelo)
        elif 16 <= dias_faltando <= 30:
            pdf.set_text_color(255, 165, 0)  # Amarelo
            pdf.cell(200, 10, txt=f"Dias para validade: {dias_faltando} dias", ln=True)

        # Validade acima de 30 dias (normal)
        else:
            pdf.set_text_color(0, 0, 0)  # Preto
            pdf.cell(200, 10, txt=f"Dias para validade: {dias_faltando} dias", ln=True)

        pdf.ln(5)

    # Salvando o PDF em um arquivo
    pdf_output_path = "relatorio_validade.pdf"
    pdf.output(pdf_output_path)

    return pdf_output_path

# Interface do Streamlit
def app():
    st.title("Cadastro de Validade de Produtos")

    # Carregar o arquivo Excel automaticamente
    df_produtos = carregar_produtos_excel(CAMINHO_ARQUIVO)

    # Aplicar o estilo CSS ao campo de pesquisa
    aplicar_estilo_css()

    # Recuperar lista de produtos da sessão ou inicializar se não existir
    if "produtos" not in st.session_state:
        st.session_state.produtos = []

    # Inicializar campos se não estiverem definidos
    if "codigo_barras_produto" not in st.session_state:
        st.session_state.codigo_barras_produto = ""
    if "descricao_produto" not in st.session_state:
        st.session_state.descricao_produto = ""
    if "quantidade" not in st.session_state:
        st.session_state.quantidade = 1
    if "validade_input" not in st.session_state:
        st.session_state.validade_input = datetime.today()

    # Entrada de texto para código de barras ou descrição com novo estilo
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
    st.session_state.validade_input = st.date_input("Data de Validade", min_value=datetime.today(), value=st.session_state.validade_input)

    # Exibir lista de produtos cadastrados em forma de DataFrame
    if len(st.session_state.produtos) > 0:
        st.subheader("Produtos Informados:")
        
        # Criar DataFrame a partir da lista de produtos
        df_produtos_cadastrados = pd.DataFrame(st.session_state.produtos)

        # Ordenar o DataFrame pela coluna 'validade' em ordem decrescente
        df_produtos_cadastrados['dias_para_validade'] = df_produtos_cadastrados['validade'].apply(lambda x: (x - datetime.now()).days)
        df_produtos_cadastrados.sort_values(by='validade', ascending=False, inplace=True)

        # Exibir DataFrame como uma tabela interativa
        st.dataframe(df_produtos_cadastrados)

    # Botão para adicionar o produto à lista
    if st.button("Adicionar Produto"):
        # Verificar se o produto já foi adicionado
        produto_existe = any(produto['codigo'] == st.session_state.codigo_barras_produto for produto in st.session_state.produtos)
        
        if produto_existe:
            st.error(f"O produto com o código {st.session_state.codigo_barras_produto} já foi adicionado.")
        else:
            if st.session_state.codigo_barras_produto and st.session_state.descricao_produto and st.session_state.validade_input:
                produto = {
                    "codigo": st.session_state.codigo_barras_produto,
                    "descricao": st.session_state.descricao_produto,  # Adicionando descrição
                    "validade": datetime.strptime(str(st.session_state.validade_input), '%Y-%m-%d'),
                    "quantidade": st.session_state.quantidade,
                }
                st.session_state.produtos.append(produto)
                st.success(f"Produto {st.session_state.codigo_barras_produto} adicionado com sucesso!")

                # Limpar campos após adicionar
                st.session_state.codigo_barras_produto = ""
                st.session_state.descricao_produto = ""
                st.session_state.quantidade = 1
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
            st.error("Nenhum produto informado para gerar o PDF.")

if __name__ == "__main__":
    app()
