import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
st.set_page_config(
    page_title="Dashboard de Análise Ancheita!", 
    page_icon="📊",
    layout="wide"
)

st.title("👾Dashboard de Análise Ancheita!👾")
st.markdown("Análise de assuntos extraídos em CSV do Blip.")

# --------------------------------------------------------------------------------------------------------------------------------

try: 
    # DataFrame EAD
    df_ead_raw = pd.read_csv(
        'https://raw.githubusercontent.com/JasminTremere/alura_repositorio/main/dados_ead.csv', 
        sep=';', 
        encoding='latin1', 
        header=None,
        names=['Acoes_Total_Raw', 'Extra1', 'Extra2', 'Extra3', 'Extra4', 'Extra5'], 
        on_bad_lines='skip' 
    )
    df_ead = df_ead_raw.iloc[1:].copy() 
    df_ead.columns = ['Ações,%,Total', 'Extra1', 'Extra2', 'Extra3', 'Extra4', 'Extra5']
    
    # DataFrame PRESENCIAL/SEMI
    df_pres_semi_raw = pd.read_csv(
        'https://raw.githubusercontent.com/JasminTremere/alura_repositorio/main/dados_pres_semi.csv', 
        sep=';', 
        encoding='latin1', 
        header=None, 
        names=['Acoes_Total_Raw', 'Extra1', 'Extra2', 'Extra3', 'Extra4', 'Extra5'],
        on_bad_lines='skip'
    )
    df_pres_semi = df_pres_semi_raw.iloc[1:].copy()
    df_pres_semi.columns = ['Ações,%,Total', 'Extra1', 'Extra2', 'Extra3', 'Extra4', 'Extra5']

    # DataFrame SUPORTE EAD
    df_sup_ead_raw = pd.read_csv(
        'https://raw.githubusercontent.com/JasminTremere/alura_repositorio/main/sup_ead.csv', 
        sep=';', 
        encoding='latin1', 
        header=None, 
        names=['Acoes_Total_Raw', 'Extra1', 'Extra2', 'Extra3', 'Extra4', 'Extra5'],
        on_bad_lines='skip'
    )
    df_sup_ead = df_sup_ead_raw.iloc[1:].copy()
    df_sup_ead.columns = ['Ações,%,Total', 'Extra1', 'Extra2', 'Extra3', 'Extra4', 'Extra5']

    # DataFrame SUPORTE PRESENCIAL/SEMI
    df_sup_pres_semi_raw = pd.read_csv(
        'https://raw.githubusercontent.com/JasminTremere/alura_repositorio/main/sup_pres_semi.csv', 
        sep=';', 
        encoding='latin1', 
        header=None, 
        names=['Acoes_Total_Raw', 'Extra1', 'Extra2', 'Extra3', 'Extra4', 'Extra5'],
        on_bad_lines='skip'
    )
    df_sup_pres_semi = df_sup_pres_semi_raw.iloc[1:].copy()
    df_sup_pres_semi.columns = ['Ações,%,Total', 'Extra1', 'Extra2', 'Extra3', 'Extra4', 'Extra5']


except pd.errors.ParserError as e:
    st.error(f"Erro ao tentar ler um dos arquivos CSV! Detalhes do erro: {e}")
    st.stop()
except Exception as e:
    st.error(f"Erro ao carregar dados: Verifique se os arquivos existem no GitHub. Detalhes: {e}")
    st.stop()

# --------------------------------------------------------------------------------------------------------------------------------
## Processamento DataFrames (Ead)

df_colunas = df_ead['Ações,%,Total'].str.split('|', expand=True).iloc[:, :3]
df_colunas.columns = ['Nome', 'Telefone', 'Assunto']

df_colunas['Nome'] = df_colunas['Nome'].str.replace('Nome:', '', regex=False).str.strip()
df_colunas['Telefone'] = df_colunas['Telefone'].str.replace('Telefone:', '', regex=False).str.strip()
df_colunas['Assunto'] = df_colunas['Assunto'].str.replace('Assunto:', '', regex=False).str.strip()

df_ead_limpo = df_colunas.copy()
df_ead_limpo['Tipo'] = 'Outros EAD' 


category_patterns = {
    # Categoria Atendimento
    'Atendimento Humano': ['falar com atendente','atendente','consultor','quero falar com alguém','quero falar com uma pessoa'],
    # Categoria Colação de grau/Conclusão de Curso
    'Colação de grau/Conclusão de Curso': ['Conclusão','conclusão','Colação de grau','colação de grau','Terminar','Formatura','Colação','Colacao','colacao','colação','formatura'],
    # Categoria de Ativdades Complementares
    'Atividades Complementares':['Hora','hora','Horas','horas','atividade complementar',' Atividade complementar','Hora complementar','Atividades complementares','atividades complementares'],
    # Categoria De Perguntas sobre o Curso
    'Sobre Curso': ['Meu curso','meu curso','Cursos','data de finalização','ao curso','Durabilidade do curso', 'finalizo o curso?','finalizar curso', 'sobre o curso','do curso',' coordenação do meu curso','Curso'],
    # Categoria De Certificados e Diploma
    'Certificado/Diploma': ['Certificado','certificado', 'diploma','Diploma'],
    # Categoria de Tranferencia
    'Transferência': ['transferir','mudar','Sobre mudar de curso','Transferência'],
    # Categoria Sobre Históricos
    'Histórico': ['Historico','Historico escolar', 'Histórico escolar','Histórico'],
    # Categoria sobre Estágio
    'Estágio': ['estágio', 'estágio remunerado','Estágio','Estagio','Estágio não obrigatorio','Estágio obrigatorio','Estágio não obrigatório','Estágio obrigatório','Carreiras','carreiras','estágio obrigatório','estagio obrigatorio','estágio não obrigatório','estagio não obrigatorio'],
    # Categoria Documento
    'Documentos': ['Documento','documento','Documentos','documentos','Documentações','documentações', 'Documentação','documentação','Comprovante','comprovante','atestado médico','atestado de frequência','cnpj','atestado de matrícula'],
    # Categoria Dados para serem modificados
    'Dados Cadastrais': ['Dados cadastrais','dados pessoais','Mudança','Atualizar','alteração do meu nome','Data de nascimento','data de nascimento','Alteração de nome','Queria atualizar','Atualizar e-mail'],
    # Categoria Dispensas
    'Dispensas': ['eliminar matérias', 'dispensas','Dispensa','dispensa','Dispensas'],
    # Categoria Dúvidas
    'Dúvidas': ['tirar dúvidas', 'dúvidas','dúvida','Dúvida','Dúvidas','duvidas','duvida','Duvida'],
    # Categoria Matrículas
    'Matrícula': ['graduações','Graduação','Estudo','Matrícula', 'Matrículas', 'matricula','matriculas','Matricula','Matriculas','fazer algum curso','Estudar','minha vaga'],
    # Categoria sobre as Carteirinhas
    'Carteirinha': ['passe escolar','emtu escolar','carteira','Carteira', 'Carteirinha', 'carteirinha','Cartão','cartão', 'Bilhete escolar','bilhete escolar','bilhete unico','bilhete único','Bilhete único','carteira de meia passagem','Cartão de meia passagem','Carteira de meia passagem','cartão de meia passagem'],
    # Categoria sobre as Provas e as Notas
    'Avaliação/Notas': ['Média','Media','media','média','notas','Notas','nota','Nota','Notas abaixo da média','médias','Avaliação on-line', 'Pontuação','provas','prova','Prova','Provas','recuperação','Recuperação'],
    # Categoria sobre Aulas e Hórarios
    'Aulas/Horários': ['Aula','Aula inaugural','Aulas','aulas','aula online','férias','Férias','início das aulas','aulas pendentes','começa as aulas'],
    # Categoria Financeiro/Acordos
    'Financeiro': ['parcelas','Parcelas','parcela','Parcela','cobrança','Cobrança','pendências','Acordo','acordo','Acordos','acordos','quitação','data de vencimento','pagamento','pagamentos','Pagamento','Pagamentos','Boleto','Boletos','boletos','boleto','financeiro','Financeiro','Mensalidade','mensalidade','Contrato','Fatura','fatura','Valores','valores','Consulta de Valores','valores de cursos'],
    # Categoria Biblioteca
    'Minha Biblioteca': ['Biblioteca','biblioteca'],
    # Categoria dos Polos
    'Polos': ['Polo','polo','Polos','polos'],
    # Categoria Secretária Geral: Prouni
    'Secretária Geral': ['Prouni','prouni','ProUni','Secretaria','secretaria','Secretária','secretária'],
    # Acesso E-mails
    'Acesso Emais': ['e-mail institucional','email institucional','recebemos esse e-mail','email estranho','E-mail','sobre esses e-mails'],
    # Pacote Office para os alunos
    'Pacote Office': ['Microsoft','pacote office','usar o Word','Pacote','Word'],
    # Categoria Disciplinas e Turmas
    'Disciplinas/Turmas': ['Disciplinas','Disciplina','disciplinas','disciplina','Enturmações','Enturmação','enturmação','enturmações','grade curricular','grade','Grade','Grade curricular','Turma','turma','Turmas','turmas'],
    # Categoria Site
    'Site': ['Site','site'],
    # Categoria Análise
    'Análise': ['Análise','retorno da analise','analises','Retorno análise','Análises','analise'],
    # Categoria Suporte
    'Suporte ao Aluno': ['Suporte e Inf. Gerais','Suporte','suporte'],
    # Categoria Bolsas
    'Bolsa': ['analise da bolsa','bolsa','Bolsa'],
    # Categoria Retorno ao Curso
    'Retorno ao Curso': ['Atualização do meu R A','ativar RA','Atualização do meu RA','Retorno a graduação hibrida','quero saber se posso voltar','Teria como iniciar novamente o curso','Refazer o curso','Recomeçar estudos','Reiniciar o curso do início','retorno ao curso'],
    # Categoria Ouvidoria
    'Ouvidoria': ['Ouvidoria','ouvidoria'],
    # Bagagens
    'Bagagem': ['bagagem','Bagagem','bagagens'],
    # Jornada Acadêmica
    'Jornada acadêmica': ['Jornada acadêmica','jornada acadêmica','jornada academica','Jornada Academica','Jornada academica','Jornada Acadêmica'],
    # Requerimento
    'Requerimento': ['requerimento','Requerimento'],
    # Imagem/Video/Audio
    'img/video': ['{type":"v', '{type":"i','{type":"a'],
    # Categoria Trancar matrícula (Refinado)
    'Trancar matrícula': ['Trancar matrícula', 'Trancar o curso', 'Trancar curso', 'Trancar a faculdade', 'trancar', 'Trancamento','trancamento','Encerrar inscrição','Trancar','parar de estudar','tranquei','cancelament','Trancamento de curso','outra instituição','troca','trocar','Trocar','Troca',' Tranquei','trancamento do curso','encerrar o curso','cancelamento','Cancelar matricula','cancelar','Cancelamento de matrícula'],
    # Categoria DP/ADAP (Refinado)
    'DP/ADAP': ['DP', 'ADAP', 'dp', 'adap', 'dependência', 'dependencia'],
    # Categoria Acesso Ava/Aluno online (Refinado)
    'Acesso Ava/Aluno online': ['não consigo logar','não estou conseguindo logar','logar na minha conta','Aluno online','aluno online','acadêmico','Acadêmico','academico','Academico','ambientação','Meu login','meu acesso','Ambientação Virtual de Aprendizagem','ambientação','Ambientação','acessar','plataforma','Portal','Senha','Acesso','canva','portal do aluno','acesso','Canvas','login na plataforma','senha do AVA','Ava','ava','AVA', 'acessar o ava', 'acesso', 'acessa','RA','senha do curso', 'aplicativo','Aplicativo','App','app','Senha no aplicativo'],
    # Categoria Material/Conteúdo (Refinado)
    'Material/Conteúdo': ['Tarefa','tarefa','Tarefas','tarefas','Prazo','Prazos','prazo','prazos','Atividade','atividades','Atividades','Matérias do curso', 'Matérias', 'materia', 'atividade','Matéria','Envio de trabalho','Exercício','Exercícios','exercício','exercicios','exercicio','exercício','conteúdo','Conteúdo'],
    # Categoria Prática
    'Prática Extensionista': ['prática','Prática','praticas','PRÁTICA EXTENSIONISTA','práticas extensionistas','Pratica','pratica','Prática Extensionista'],
    # Categoria Relatório
    'Relatório': ['Máscara de relatório e liberação da pasta star'],
    }

# Função para categorizar
def categorize_assunto(assunto):
    if not isinstance(assunto, str):
        return 'Outros'
    assunto_lower = assunto.lower()
    for category, patterns in category_patterns.items():
        for pattern in patterns:
            if pattern.lower() in assunto_lower:
                return category
    return 'Outros'

df_ead_limpo['Categoria'] = df_ead_limpo['Assunto'].apply(categorize_assunto)

# --------------------------------------------------------------------------------------------------------------------------------
## Processamento DataFrames (Presencial e Semipresencial)

df_colunas2 = df_pres_semi['Ações,%,Total'].str.split('|', expand=True).iloc[:, :3]
df_colunas2.columns = ['Nome', 'Telefone', 'Assunto']

df_colunas2['Nome'] = df_colunas2['Nome'].str.replace('Nome:', '', regex=False).str.strip()
df_colunas2['Telefone'] = df_colunas2['Telefone'].str.replace('Telefone:', '', regex=False).str.strip()
df_colunas2['Assunto'] = df_colunas2['Assunto'].str.replace('Assunto:', '', regex=False).str.strip()

df_pres_semi_limpo = df_colunas2.copy()
df_pres_semi_limpo['Tipo'] = 'Outros Presencial/Semi'

category_patterns2 = {
    # Categoria Atendimento
    'Atendimento Humano': ['falar com atendente','atendente','consultor','quero falar com alguém','quero falar com uma pessoa'],
    # Categoria Colação de grau/Conclusão de Curso
    'Colação de grau/Conclusão de Curso': ['Conclusão','conclusão','Colação de grau','colação de grau','Terminar','Formatura','Colação','Colacao','colacao','colação','formatura'],
    # Categoria de Ativdades Complementares
    'Atividades Complementares':['Hora','hora','Horas','horas','atividade complementar',' Atividade complementar','Hora complementar','Atividades complementares','atividades complementares'],
    # Categoria De Perguntas sobre o Curso
    'Sobre Curso': ['Meu curso','meu curso','Cursos','data de finalização','ao curso','Durabilidade do curso', 'finalizo o curso?','finalizar curso', 'sobre o curso','do curso',' coordenação do meu curso','Curso'],
    # Categoria De Certificados e Diploma
    'Certificado/Diploma': ['Certificado','certificado', 'diploma','Diploma'],
    # Categoria de Tranferencia
    'Transferência': ['transferir','mudar','Sobre mudar de curso','Transferência','Sair do curso','Trocar faculdade presencial para ead'],
    # Categoria Sobre Históricos
    'Histórico/Declarações': ['Historico','Historico escolar', 'Histórico escolar','Histórico','declaração de estudante','Declaração de matrícula'],
    # Categoria sobre Estágio
    'Estágio': ['Horas de estagio','estágio', 'estágio remunerado','Estágio','Estagio','Estágio não obrigatorio','Estágio obrigatorio','Estágio não obrigatório','Estágio obrigatório','Carreiras','carreiras','estágio obrigatório','estagio obrigatorio','estágio não obrigatório','estagio não obrigatorio'],
    # Categoria Documento
    'Documentos': ['Documento','documento','Documentos','documentos','Documentações','documentações', 'Documentação','documentação','Comprovante','comprovante','atestado médico','atestado de frequência','cnpj','anexo','assinatura','atestado de matrícula'],
    # Categoria Dados para serem modificados
    'Dados Cadastrais': ['Dados cadastrais','dados pessoais','Mudança','Atualizar','alteração do meu nome','Data de nascimento','data de nascimento','Alteração de nome','Queria atualizar','Atualizar e-mail'],
    # Categoria Dispensas
    'Dispensas': ['eliminar matérias', 'dispensas','Dispensa','dispensa','Dispensas','eliminar materia'],
    # Categoria Dúvidas
    'Dúvidas': ['tirar dúvidas', 'dúvidas','dúvida','Dúvida','Dúvidas','duvidas','duvida','Duvida'],
    # Categoria Matrículas
    'Matrícula': ['graduações','Graduação','Estudo','Matrícula', 'Matrículas','Matricula','Matriculas','fazer algum curso','Estudar','cursar'],
    # Categoria sobre as Carteirinhas
    'Carteirinha': ['carteira','Carteira', 'Carteirinha', 'carteirinha'],
    # Categoria sobre as Provas e as Notas
    'Avaliação/Notas': ['Média','Media','media','média','notas','Notas','nota','Nota','Notas abaixo da média','médias','Avaliação on-line', 'Pontuação','provas','prova','Prova','Provas','recuperação','Recuperação'],
    # Categoria sobre Aulas e Hórarios
    'Aulas/Horários': ['Aula','Aula inaugural','Aulas','aulas','aula online','férias','Férias','início das aulas','aulas pendentes','começa as aulas'],
    # Categoria Financeiro/Acordos
    'Financeiro': ['parcelas','Parcelas','parcela','Parcela','cobrança','Cobrança','pendências','Acordo','acordo','Acordos','acordos','quitação','data de vencimento','pagamento','pagamentos','Pagamento','Pagamentos','Boleto','Boletos','boletos','boleto','financeiro','Financeiro','Mensalidade','mensalidade','Contrato','Fatura','fatura','Valores','valores','Consulta de Valores','valores de cursos'],
    # Categoria Biblioteca
    'Minha Biblioteca': ['Biblioteca','biblioteca'],
    # Categoria dos Polos
    'Polos': ['Polo','polo','Polos','polos'],
    # Categoria Secretária Geral: Prouni
    'Secretária Geral': ['Prouni','prouni','ProUni','Secretaria','secretaria','Secretária','secretária'],
    # Acesso E-mails
    'Acesso Emais': ['e-mail institucional','email institucional','recebemos esse e-mail','email estranho','E-mail','sobre esses e-mails','Senha do email'],
    # Pacote Office para os alunos
    'Pacote Office': ['Microsoft','pacote office','usar o Word','Pacote','Word'],
    # Categoria Disciplinas e Turmas
    'Disciplinas/Turmas': ['Disciplinas','Disciplina','disciplinas','disciplina','Enturmações','Enturmação','enturmação','enturmações','grade curricular','grade','Grade','Grade curricular','Turma','turma','Turmas','turmas'],
    # Categoria Site
    'Site': ['Site','site'],
    # Categoria Análise
    'Análise': ['Análise','retorno da analise','analises','Retorno análise','Análises','analise'],
    # Categoria Suporte
    'Suporte ao Aluno': ['Suporte e Inf. Gerais','Suporte','suporte'],
    # Categoria Bolsas
    'Bolsa': ['analise da bolsa','bolsa','Bolsa'],
    # Categoria Retorno ao Curso
    'Retorno ao Curso': ['Atualização do meu R A','ativar RA','Atualização do meu RA','Retorno a graduação hibrida','quero saber se posso voltar','Teria como iniciar novamente o curso','Refazer o curso','Recomeçar estudos','Reiniciar o curso do início','retorno ao curso'],
    # Categoria Ouvidoria
    'Ouvidoria': ['Ouvidoria','ouvidoria'],
    # Bagagens
    'Bagagem': ['bagagem','Bagagem','bagagens'],
    # Jornada Acadêmica
    'Jornada acadêmica': ['Jornada acadêmica','jornada acadêmica','jornada academica','Jornada Academica','Jornada academica','Jornada Acadêmica'],
    # Requerimento
    'Requerimento': ['requerimento','Requerimento'],
    # Imagem/Video/Audio
    'img/video': ['{type":"image/jpeg",', '{type":"i','{type":"a'],
    # Categoria Trancar matrícula (Refinado)
    'Trancar matrícula': ['Trancar matrícula','Trancar matricula','Trancar matrícula', 'Trancar o curso', 'Trancar curso', 'Trancar a faculdade', 'trancar', 'Trancamento','trancamento','Encerrar inscrição','Trancar','parar de estudar','tranquei','cancelament','Trancamento de curso','outra instituição','troca','trocar','Trocar','Troca',' Tranquei','trancamento do curso','encerrar o curso','cancelamento','Cancelar matricula','cancelar','Cancelamento de matrícula'],
    # Categoria DP/ADAP (Refinado)
    'DP/ADAP': ['DP', 'ADAP', 'dp', 'adap', 'dependência', 'dependencia',],
    # Categoria Acesso Ava/Aluno online (Refinado)
    'Acesso Ava/Aluno online': ['não consigo logar','não estou conseguindo logar','logar na minha conta','Aluno online','aluno online','acadêmico','Acadêmico','academico','Academico','ambientação','Meu login','meu acesso','Ambientação Virtual de Aprendizagem','ambientação','Ambientação','acessar','plataforma','Portal','Senha','Acesso','canva','portal do aluno','acesso','Canvas','login na plataforma','senha do AVA','Ava','ava','AVA', 'acessar o ava', 'acesso', 'acessa','RA','senha do curso', 'aplicativo','Aplicativo','App','app','Senha no aplicativo'],
    # Categoria Material/Conteúdo (Refinado)
    'Material/Conteúdo': ['Tarefa','tarefa','Tarefas','tarefas','Prazo','Prazos','prazo','prazos','Atividade','atividades','Atividades','Matérias do curso', 'Matérias', 'materia', 'atividade','Matéria','Envio de trabalho','Exercício','Exercícios','exercício','exercicios','exercicio','exercício','conteúdo','Conteúdo'],
    # Categoria Prática
    'Prática Extensionista': ['prática','Prática','praticas','PRÁTICA EXTENSIONISTA','práticas extensionistas','Pratica','pratica','Prática Extensionista'],
    # Categoria Relatório
    'Relatório': ['Máscara de relatório e liberação da pasta star'],
    # VET
    'Veterinario': ['veterinario','Veterinario','dona do','dona da','dono do','dono do','internação','Hospital veterinário'],
    # Cancelamento do Curso
    'Cancelamento do curso': ['cancelamento do curso','cancelamento do meu curso','Cancelamento do curso','cancelar minha matricula','Cancelar matrícula'],
    # Chamadas
    'Lista de Chamada': ['lista de chamada','chamada','trocar minha foto da chamada'],
    # ônibus
    'Bilhetes/Ônibus fretados': ['serviço de transporte público','ônibus fretados','Sobre ônibus','Passe escolar','passe escolar','emtu escolar','Bilhete escolar','bilhete escolar','bilhete unico','bilhete único','Bilhete único','carteira de meia passagem','Cartão de meia passagem','Cartão','cartão','Carteira de meia passagem','cartão de meia passagem'],
    # Salas
    'Sobre Salas': ['sobre laboratórios'],
    }

# Função para categorizar
def categorize_assunto2(assunto):
    if not isinstance(assunto, str):
        return 'Outros'
    assunto_lower = assunto.lower()
    for category, patterns in category_patterns2.items():
        for pattern in patterns:
            if pattern.lower() in assunto_lower:
                return category
    return 'Outros'

df_pres_semi_limpo['Categoria'] = df_pres_semi_limpo['Assunto'].apply(categorize_assunto2)

# --------------------------------------------------------------------------------------------------------------------------------
## Processamento Suporte DataFrames (Ead)

df_colunas3 = df_sup_ead['Ações,%,Total'].str.split('|', expand=True).iloc[:, :3] 
df_colunas3.columns = ['Nome', 'Telefone', 'Assunto']

df_colunas3['Nome'] = df_colunas3['Nome'].str.replace('Nome:', '', regex=False).str.strip()
df_colunas3['Telefone'] = df_colunas3['Telefone'].str.replace('Telefone:', '', regex=False).str.strip()
df_colunas3['Assunto'] = df_colunas3['Assunto'].str.replace('Assunto:', '', regex=False).str.strip()

df_sup_ead_limpo = df_colunas3.copy()
df_sup_ead_limpo['Tipo'] = 'Suporte EAD' 

# Reutiliza o pattern2/3 para suporte EAD
category_patterns3 = category_patterns2

# Função para categorizar
def categorize_assunto3(assunto):
    if not isinstance(assunto, str):
        return 'Outros'
    assunto_lower = assunto.lower()
    for category, patterns in category_patterns3.items():
        for pattern in patterns:
            if pattern.lower() in assunto_lower:
                return category
    return 'Outros'

df_sup_ead_limpo['Categoria'] = df_sup_ead_limpo['Assunto'].apply(categorize_assunto3)

# --------------------------------------------------------------------------------------------------------------------------------

## Processamento Suporte DataFrames (Presencial e Semipresencial)

df_colunas4 = df_sup_pres_semi['Ações,%,Total'].str.split('|', expand=True).iloc[:, :3] 
df_colunas4.columns = ['Nome', 'Telefone', 'Assunto']

df_colunas4['Nome'] = df_colunas4['Nome'].str.replace('Nome:', '', regex=False).str.strip()
df_colunas4['Telefone'] = df_colunas4['Telefone'].str.replace('Telefone:', '', regex=False).str.strip()
df_colunas4['Assunto'] = df_colunas4['Assunto'].str.replace('Assunto:', '', regex=False).str.strip()

df_sup_pres_semi_limpo = df_colunas4.copy()
df_sup_pres_semi_limpo['Tipo'] = 'Suporte Presencial/Semi'

# Reutiliza o pattern2/3 para suporte Presencial/Semi
category_patterns4 = category_patterns2 

# Função para categorizar
def categorize_assunto4(assunto):
    if not isinstance(assunto, str):
        return 'Outros'
    assunto_lower = assunto.lower()
    for category, patterns in category_patterns4.items():
        for pattern in patterns:
            if pattern.lower() in assunto_lower:
                return category
    return 'Outros'

df_sup_pres_semi_limpo['Categoria'] = df_sup_pres_semi_limpo['Assunto'].apply(categorize_assunto4)

# --------------------------------------------------------------------------------------------------------------------------------

df_total_limpo = pd.concat([df_ead_limpo, df_pres_semi_limpo, df_sup_ead_limpo, df_sup_pres_semi_limpo], ignore_index=True)

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro por Tipo de Atendimento/Curso
tipos_disponiveis = sorted(df_total_limpo['Tipo'].unique())
tipos_selecionados = st.sidebar.multiselect(
    "Filtrar por Tipo de Atendimento", tipos_disponiveis, default=tipos_disponiveis
)

# Filtrar por Categoria
categorias_disponiveis = sorted(df_total_limpo[df_total_limpo['Tipo'].isin(tipos_selecionados)]['Categoria'].unique())
categorias_selecionadas = st.sidebar.multiselect(
    "Filtrar por Categoria", categorias_disponiveis, default=categorias_disponiveis
)

# Filtrar por Nome (opcional)
nomes_disponiveis = sorted(df_total_limpo[df_total_limpo['Tipo'].isin(tipos_selecionados)]['Nome'].unique())
nomes_selecionados = st.sidebar.multiselect(
    "Filtrar por Nome (opcional)", nomes_disponiveis
)


# Aplicar filtros
df_filtrado_global = df_total_limpo.copy()
if tipos_selecionados:
    df_filtrado_global = df_filtrado_global[df_filtrado_global['Tipo'].isin(tipos_selecionados)]
if categorias_selecionadas:
    df_filtrado_global = df_filtrado_global[df_filtrado_global['Categoria'].isin(categorias_selecionadas)]
if nomes_selecionados:
    df_filtrado_global = df_filtrado_global[df_filtrado_global['Nome'].isin(nomes_selecionados)]
    
# Separar novamente para gráficos específicos (se necessário)
df_ead_filtrado = df_filtrado_global[df_filtrado_global['Tipo'] == 'Outros EAD']
df_pres_semi_filtrado = df_filtrado_global[df_filtrado_global['Tipo'] == 'Outros Presencial/Semi']
df_sup_ead_filtrado = df_filtrado_global[df_filtrado_global['Tipo'] == 'Suporte EAD']
df_sup_pres_semi_filtrado = df_filtrado_global[df_filtrado_global['Tipo'] == 'Suporte Presencial/Semi']



# --- MÉTRICAS PRINCIPAIS ---
st.subheader("Métricas Principais")

col1, col2, col3 = st.columns(3)
col1.metric("Total de registros", df_filtrado_global.shape[0])
col2.metric("Categorias", df_filtrado_global['Categoria'].nunique())
col3.metric("Nomes únicos", df_filtrado_global['Nome'].nunique())
#col4.metric("Total de assuntos", df_filtrado_global['Assuntos'].nunique())
st.markdown("---")


# --- GRÁFICOS RELATÓRIO OUTROS (EAD e Presencial/Semipresencial) ---
st.header("Outros Assuntos")
col_graf1, col_graf2 = st.columns(2)
 
with col_graf1:
    if not df_ead_filtrado.empty:
        grafico_categoria_ead = (
            df_ead_filtrado.groupby('Categoria').size()
            .nlargest(10)
            .sort_values(ascending=False)
            .reset_index(name='Quantidade')
        )
        fig_ead = px.bar(
            grafico_categoria_ead,
            x='Categoria',
            y='Quantidade',
            title='Relatório - Outros EAD',
            labels={'Categoria': 'Categoria', 'Quantidade': 'Quantidade'}
        )
        fig_ead.update_layout(
            title_x=0.5, 
            xaxis={'categoryorder': 'total descending'}
        )
        st.plotly_chart(fig_ead, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir em Outros EAD.")
 
with col_graf2:
    if not df_pres_semi_filtrado.empty:
        grafico_categoria_pres_semi = (
            df_pres_semi_filtrado.groupby('Categoria').size()
            .nlargest(10)
            .sort_values(ascending=False)
            .reset_index(name='Quantidade')
        )
        fig_pres_semi = px.bar(
            grafico_categoria_pres_semi,
            x='Categoria', 
            y='Quantidade',
            title='Relatório - Outros Presencial/Semi',
            labels={'Categoria': 'Categoria', 'Quantidade': 'Quantidade'}
        )
        fig_pres_semi.update_layout(
            title_x=0.5,
            xaxis={'categoryorder': 'total descending'}
        )
        st.plotly_chart(fig_pres_semi, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir em Outros Presencial/Semi.")


# --- TABELA RELATÓRIO OUTROS (EAD e Presencial/Semipresencial) ---

st.header("Dados Detalhados - Outros EAD e Presencial/Semipresencial")
st.subheader("")

col_tab1, col_tab2 = st.columns(2)

with col_tab1:
   
    tabela_ead = df_ead_filtrado

    st.markdown("**Tabela - Outros EAD**")

    if not tabela_ead.empty:
       
        st.dataframe(
            tabela_ead[['Nome', 'Telefone', 'Assunto', 'Categoria']],
            use_container_width=True
        )
    else:
        st.info("Nenhum dado detalhado de EAD para exibir.")

with col_tab2:
    tabela_pres_semi_resumo = df_pres_semi_filtrado

    st.markdown("**Tabela - Outros Presencial/Semipresencial**")

    if not tabela_pres_semi_resumo.empty:
        st.dataframe(
            tabela_pres_semi_resumo[['Nome', 'Telefone', 'Assunto', 'Categoria']],
            use_container_width=True
        )
    else:
        st.info("Nenhum dado detalhado de Presencial/Semipresencial para exibir.")


# --------------------------------------------------------------------------------------------------------------------------------

# --- GRÁFICOS RELATÓRIO SUPORTE (EAD e Presencial/Semipresencial) ---
st.header("Relatório: Suporte Técnico")


col_graf1, col_graf2 = st.columns(2)
 
with col_graf1:
    if not df_ead_filtrado.empty:
        grafico_categoria_ead = (
            df_ead_filtrado.groupby('Categoria').size()
            .nlargest(10)
            .sort_values(ascending=False)
            .reset_index(name='Quantidade')
        )
        fig_ead = px.bar(
            grafico_categoria_ead,
            x='Categoria',
            y='Quantidade',
            title='Relatório - Outros EAD',
            labels={'Categoria': 'Categoria', 'Quantidade': 'Quantidade'}
        )
        fig_ead.update_layout(
            title_x=0.5, 
            xaxis={'categoryorder': 'total descending'}
        )
        st.plotly_chart(fig_ead, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir em Outros EAD.")
 
with col_graf2:
    if not df_pres_semi_filtrado.empty:
        grafico_categoria_pres_semi = (
            df_pres_semi_filtrado.groupby('Categoria').size()
            .nlargest(10)
            .sort_values(ascending=False)
            .reset_index(name='Quantidade')
        )
        fig_pres_semi = px.bar(
            grafico_categoria_pres_semi,
            x='Categoria', 
            y='Quantidade',
            title='Relatório - Outros Presencial/Semi',
            labels={'Categoria': 'Categoria', 'Quantidade': 'Quantidade'}
        )
        fig_pres_semi.update_layout(
            title_x=0.5,
            xaxis={'categoryorder': 'total descending'}
        )
        st.plotly_chart(fig_pres_semi, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir em Outros Presencial/Semi.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_sup_ead_filtrado.empty:
        grafico_categoria_sup_ead = (
            df_sup_ead_filtrado.groupby('Categoria').size()
            .nlargest(10)
            .sort_values(ascending=False)
            .reset_index(name='Quantidade')
        )
        fig_sup_ead = px.bar(
            grafico_categoria_sup_ead,
            y='Categoria',
            x='Quantidade',
            title='Relatório - Suporte EAD',
            labels={'Categoria': 'Categoria', 'Quantidade': 'Quantidade'}
        )
        fig_sup_ead.update_layout(
            title_x=0.5,
            xaxis={'categoryorder': 'total descending'}
        )
        st.plotly_chart(fig_sup_ead, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir em Suporte EAD (Verifique os filtros).")

with col_graf4:
    if not df_sup_pres_semi_filtrado.empty:
        grafico_sup_pres_semi = (
            df_sup_pres_semi_filtrado.groupby('Categoria').size()
            .nlargest(10)
            .sort_values(ascending=True)
            .reset_index(name='Quantidade')
        )
        fig_sup_pres_semi = px.bar(
            grafico_sup_pres_semi,
            y='Categoria',
            x='Quantidade',
            title='Relatório - Suporte Presencial/Semi',
            labels={'Categoria': 'Categoria', 'Quantidade': 'Quantidade'}
        )
        fig_sup_pres_semi.update_layout(
            title_x=0.5,
            xaxis={'categoryorder': 'total descending'}
        )
        st.plotly_chart(fig_sup_pres_semi, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir em Suporte Presencial/Semi (Verifique os filtros).")


# --- TABELA RELATÓRIO SUPORTE (EAD e Presencial/Semipresencial) ---
st.subheader("Dados Detalhados - Suporte EAD e Presencial/Semipresencial")

col_tab3, col_tab4 = st.columns(2)

with col_tab3:
   
    tabela_sup_ead = df_sup_ead_filtrado

    st.markdown("**Tabela - Suporte EAD**")

    if not tabela_sup_ead.empty:

        st.dataframe(
            tabela_sup_ead[['Nome', 'Telefone', 'Assunto', 'Categoria']],
            use_container_width=True
        )
    else:
        st.info("Nenhum dado detalhado de EAD para exibir.")

with col_tab4:

    tabela_sup_pres_semi = df_sup_pres_semi_filtrado
    
    st.markdown("**Tabela - Suporte Presencial/Semipresencial**")

    if not tabela_sup_pres_semi.empty:

        st.dataframe(
            tabela_sup_pres_semi[['Nome', 'Telefone', 'Assunto', 'Categoria']],
            use_container_width=True
        )
    else:
        st.info("Nenhum dado detalhado de Presencial/Semipresencial para exibir.")
# --------------------------------------------------------------------------------------------------------------------------------
