import streamlit as st
import pandas as pd
import os
import openai
import json
from datetime import date

# Definir o nome do arquivo CSV
csv_file = "projetos_ti.csv"

# Lista de opções de status do projeto
status_options = ["Iniciação", "Planejamento", "Execução", "Encerramento", "Em andamento", "Concluído", "Cancelado"]

# Chave da API da OpenAI (substitua pela sua chave)
openai.api_key = "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"  # Coloque sua chave de API aqui

# Função para melhorar o texto com GPT-4 usando o endpoint correto de chat
def melhorar_texto_gpt4(texto):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em gestão de projetos de TI."},
                {"role": "user", "content": f"Melhore o seguinte texto utilizando uma linguagem técnica de gestão de projetos de TI: {texto}"}
            ],
            max_tokens=300,
            temperature=0.7,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.error(f"Erro ao processar o texto: {str(e)}")
        return texto  # Retorna o texto original em caso de erro

# Função para gerar o resumo do projeto com GPT-4
def gerar_resumo_projeto(data):
    try:
        prompt = f"""
        Crie um resumo curto e técnico para um projeto de TI com as seguintes informações:
        Nome do Projeto: {data['Nome do Projeto']}
        Descrição do Projeto: {data['Descrição do Projeto']}
        Sponsor: {data['Sponsor']}
        Gerente do Projeto: {data['Gerente do Projeto']}
        Stakeholders: {data['Stakeholders']}
        Objetivos do Projeto: {data['Objetivos do Projeto']}
        Data de Início: {data['Data de Início']}
        Data de Término Prevista: {data['Data de Término Prevista']}
        Data de Término Real: {data['Data de Término Real']}
        Orçamento: {data['Orçamento Alocado']}
        Status: {data['Status do Projeto']}
        Riscos: {data['Riscos Identificados']}
        Ações Mitigadoras: {data['Ações Mitigadoras']}
        Últimas Atualizações: {data['Últimas Atualizações']}
        Próximas Atividades: {data['Próximas Atividades']}
        Dependências: {data['Dependências']}
        Escopo do Projeto: {data['Escopo do Projeto']}
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em gestão de projetos de TI."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.error(f"Erro ao gerar o resumo do projeto: {str(e)}")
        return "Erro ao gerar o resumo do projeto."

# Função para carregar dados do CSV
def load_data():
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        # Desserializar campos complexos do JSON
        if 'Plano de Ações' in df.columns:
            df['Plano de Ações'] = df['Plano de Ações'].apply(lambda x: json.loads(x) if pd.notnull(x) and isinstance(x, str) and x.strip() else [])
        if 'Recursos Alocados' in df.columns:
            df['Recursos Alocados'] = df['Recursos Alocados'].apply(lambda x: json.loads(x) if pd.notnull(x) and isinstance(x, str) and x.strip() else [])
        if 'Entregáveis' in df.columns:
            df['Entregáveis'] = df['Entregáveis'].apply(lambda x: json.loads(x) if pd.notnull(x) and isinstance(x, str) and x.strip() else [])
        return df
    else:
        return pd.DataFrame(columns=[
            "Número do Projeto", "Nome do Projeto", "Descrição do Projeto", "Sponsor", "Gerente do Projeto",
            "Stakeholders", "Objetivos do Projeto", "Fase do Projeto", "Data de Início",
            "Data de Término Prevista", "Data de Término Real", "Orçamento Alocado",
            "Custos Realizados", "Status do Projeto",
            "Riscos Identificados", "Ações Mitigadoras", "Últimas Atualizações",
            "Próximas Atividades", "Dependências", "Recursos Alocados", "Escopo do Projeto",
            "Entregáveis", "Mudanças no Escopo", "Plano de Ações", "Resumo atual do Projeto"
        ])

# Função para salvar dados no CSV
def save_data(df):
    df = df.copy()
    # Serializar campos complexos para JSON
    if 'Plano de Ações' in df.columns:
        df['Plano de Ações'] = df['Plano de Ações'].apply(json.dumps)
    if 'Recursos Alocados' in df.columns:
        df['Recursos Alocados'] = df['Recursos Alocados'].apply(json.dumps)
    if 'Entregáveis' in df.columns:
        df['Entregáveis'] = df['Entregáveis'].apply(json.dumps)
    df.to_csv(csv_file, index=False)

# Função para adicionar nova entrada
def add_entry(data):
    df = load_data()
    new_entry = pd.DataFrame([data])
    df = pd.concat([df, new_entry], ignore_index=True)
    save_data(df)

# Função para editar uma entrada
def edit_entry(index, data):
    df = load_data()

    # Verificar se todas as chaves em 'data' estão presentes nas colunas do DataFrame
    for key in data:
        if key not in df.columns:
            st.error(f"Erro: A chave '{key}' não está presente no DataFrame.")
            return

    # Certificar que o dicionário 'data' tem todas as colunas necessárias
    missing_columns = set(df.columns) - set(data.keys())
    if missing_columns:
        for col in missing_columns:
            data[col] = None  # Adicionar valores None para as colunas que faltam no dicionário 'data'

    try:
        # Certificar que o número de colunas e valores correspondem
        df.loc[index] = pd.Series(data)
        save_data(df)
        st.success("Projeto editado com sucesso!")
    except ValueError as ve:
        st.error(f"Erro ao salvar alterações: {ve}")

# Função para melhorar texto em campos específicos
def campo_com_melhoria_gpt4(label, valor_inicial, key_prefix=""):
    key_text = f"{key_prefix}_{label}_text"
    key_button = f"{key_prefix}_{label}_button"

    # Se a chave não está no session_state, inicialize-a
    if key_text not in st.session_state:
        st.session_state[key_text] = valor_inicial

    # Definir uma função de callback para melhorar o texto
    def melhorar_texto_callback():
        valor_melhorado = melhorar_texto_gpt4(st.session_state[key_text])
        st.session_state[key_text] = valor_melhorado
        st.success(f"Texto de {label} melhorado com sucesso!")

    # Criar o text_area sem o parâmetro 'value' (usar apenas a 'key')
    st.text_area(label, key=key_text)

    # Botão que chama o callback
    st.button(f"Melhorar texto com IA - {label}", key=key_button, on_click=melhorar_texto_callback)

    return st.session_state[key_text]

# Função para permitir inserção de várias ações
def plano_acoes_widget(plano_acoes_key, key_prefix=""):
    if plano_acoes_key not in st.session_state:
        st.session_state[plano_acoes_key] = []

    plano_acoes = st.session_state[plano_acoes_key]

    add_action = st.button("Adicionar Nova Ação", key=f"add_acao_{key_prefix}")

    if add_action:
        plano_acoes.append({
            "Descrição": "",
            "Responsável": "",
            "Data de Início": str(date.today()),
            "Data de Fim": str(date.today())
        })
        st.session_state[plano_acoes_key] = plano_acoes

    # Para armazenar o índice da ação a ser removida
    action_to_remove = None

    for i, acao in enumerate(plano_acoes):
        with st.expander(f"Ação {i+1}"):
            key_suffix = f"{key_prefix}_acao_{i}"
            descricao = st.text_input(f"Descrição da Ação {i+1}", value=acao.get("Descrição", ""), key=f"descricao_{key_suffix}")
            responsavel = st.text_input(f"Responsável {i+1}", value=acao.get("Responsável", ""), key=f"responsavel_{key_suffix}")
            data_inicio = st.date_input(f"Data de Início {i+1}", value=pd.to_datetime(acao.get("Data de Início", date.today())).date(), key=f"data_inicio_{key_suffix}")
            data_fim = st.date_input(f"Data de Fim {i+1}", value=pd.to_datetime(acao.get("Data de Fim", date.today())).date(), key=f"data_fim_{key_suffix}")

            # Atualizar a ação no session_state
            plano_acoes[i] = {
                "Descrição": st.session_state.get(f"descricao_{key_suffix}", ""),
                "Responsável": st.session_state.get(f"responsavel_{key_suffix}", ""),
                "Data de Início": str(st.session_state.get(f"data_inicio_{key_suffix}", date.today())),
                "Data de Fim": str(st.session_state.get(f"data_fim_{key_suffix}", date.today()))
            }

            # Botão para remover a ação
            remove_action = st.button(f"Remover Ação {i+1}", key=f"remover_{key_suffix}")
            if remove_action:
                action_to_remove = i

    if action_to_remove is not None:
        # Remover a ação selecionada
        del plano_acoes[action_to_remove]
        # Limpar as chaves relacionadas no session_state
        for key in ["descricao_", "responsavel_", "data_inicio_", "data_fim_"]:
            st.session_state.pop(f"{key}{key_prefix}_acao_{action_to_remove}", None)
        st.session_state[plano_acoes_key] = plano_acoes

    return plano_acoes

# Função para inserir novo projeto
def inserir_dados():
    st.header("Inserir Novo Projeto")
    key_prefix = "inserir"

    numero_projeto = st.text_input("Número do Projeto", key=f"numero_projeto_{key_prefix}")
    nome_projeto = st.text_input("Nome do Projeto", key=f"nome_projeto_{key_prefix}")

    descricao_projeto = campo_com_melhoria_gpt4("Descrição do Projeto", "", key_prefix)
    sponsor = st.text_input("Sponsor", key=f"sponsor_{key_prefix}")
    gerente_projeto = st.text_input("Gerente do Projeto", key=f"gerente_projeto_{key_prefix}")
    stakeholders = st.text_area("Stakeholders", key=f"stakeholders_{key_prefix}")
    objetivos_projeto = campo_com_melhoria_gpt4("Objetivos do Projeto", "", key_prefix)

    data_inicio = st.date_input("Data de Início", key=f"data_inicio_{key_prefix}")
    data_termino_prevista = st.date_input("Data de Término Prevista", key=f"data_termino_prevista_{key_prefix}")
    data_termino_real = st.date_input("Data de Término Real", value=None, key=f"data_termino_real_{key_prefix}")
    orcamento = st.number_input("Orçamento Alocado", min_value=0.0, key=f"orcamento_{key_prefix}")
    custos_realizados = st.number_input("Custos Realizados", min_value=0.0, key=f"custos_realizados_{key_prefix}")
    status_projeto = st.selectbox("Status do Projeto", status_options, key=f"status_projeto_{key_prefix}")

    riscos_identificados = campo_com_melhoria_gpt4("Riscos Identificados", "", key_prefix)
    acoes_mitigadoras = campo_com_melhoria_gpt4("Ações Mitigadoras", "", key_prefix)
    ultimas_atualizacoes = campo_com_melhoria_gpt4("Últimas Atualizações", "", key_prefix)
    proximas_atividades = campo_com_melhoria_gpt4("Próximas Atividades", "", key_prefix)
    escopo_projeto = campo_com_melhoria_gpt4("Escopo do Projeto", "", key_prefix)

    dependencias = st.text_area("Dependências", key=f"dependencias_{key_prefix}")
    recursos_alocados = st.text_area("Recursos Alocados (insira um recurso por linha)", key=f"recursos_alocados_{key_prefix}")
    entregaveis = st.text_area("Entregáveis (insira um entregável por linha)", key=f"entregaveis_{key_prefix}")
    mudancas_escopo = st.text_area("Mudanças no Escopo", key=f"mudancas_escopo_{key_prefix}")

    # Plano de Ações
    plano_acoes_key = f"plano_acoes_{key_prefix}"
    plano_acoes = plano_acoes_widget(plano_acoes_key, key_prefix)
    st.session_state[plano_acoes_key] = plano_acoes

    data = {
        "Número do Projeto": numero_projeto,
        "Nome do Projeto": nome_projeto,
        "Descrição do Projeto": descricao_projeto,
        "Sponsor": sponsor,
        "Gerente do Projeto": gerente_projeto,
        "Stakeholders": stakeholders,
        "Objetivos do Projeto": objetivos_projeto,
        "Data de Início": data_inicio,
        "Data de Término Prevista": data_termino_prevista,
        "Data de Término Real": data_termino_real,
        "Orçamento Alocado": orcamento,
        "Custos Realizados": custos_realizados,
        "Status do Projeto": status_projeto,
        "Riscos Identificados": riscos_identificados,
        "Ações Mitigadoras": acoes_mitigadoras,
        "Últimas Atualizações": ultimas_atualizacoes,
        "Próximas Atividades": proximas_atividades,
        "Dependências": dependencias,
        "Escopo do Projeto": escopo_projeto,
        "Plano de Ações": plano_acoes  # Adicionando o Plano de Ações
    }

    # Botão para gerar o resumo com IA
    if st.button("Gerar Resumo com IA", key=f"gerar_resumo_{key_prefix}"):
        resumo_projeto = gerar_resumo_projeto(data)
        st.session_state[f"resumo_projeto_{key_prefix}"] = resumo_projeto

    resumo_projeto = st.text_area("Resumo atual do Projeto", value=st.session_state.get(f"resumo_projeto_{key_prefix}", ""), key=f"resumo_projeto_{key_prefix}")

    # Botão para salvar
    if st.button("Salvar Projeto", key=f"salvar_projeto_{key_prefix}"):
        data.update({
            "Resumo atual do Projeto": resumo_projeto,
            "Recursos Alocados": recursos_alocados.split("\n") if recursos_alocados else [],
            "Entregáveis": entregaveis.split("\n") if entregaveis else [],
            "Mudanças no Escopo": mudancas_escopo
        })
        add_entry(data)
        st.success("Projeto salvo com sucesso!")

        # Limpar os campos após salvar
        for key in list(st.session_state.keys()):
            if key.startswith(key_prefix):
                del st.session_state[key]

# Função para editar dados do projeto existente
def editar_dados():
    st.header("Editar Projeto Existente")
    df = load_data()

    if df.empty:
        st.warning("Nenhum projeto encontrado.")
        return

    # Armazenar o projeto selecionado anteriormente
    if 'projeto_selecionado_antigo' not in st.session_state:
        st.session_state['projeto_selecionado_antigo'] = None

    # Selecionar o projeto com index=0 para selecionar o primeiro projeto por padrão
    projeto_selecionado = st.selectbox("Selecione o projeto", df["Nome do Projeto"], index=0)
    projeto_index = df[df["Nome do Projeto"] == projeto_selecionado].index[0]
    key_prefix = f"editar_{projeto_index}"

    # Verificar se o projeto selecionado mudou
    if st.session_state['projeto_selecionado_antigo'] != projeto_selecionado:
        # Limpar o session_state relacionado ao projeto anterior
        keys_to_delete = [key for key in st.session_state.keys() if key.startswith("editar_")]
        for key in keys_to_delete:
            del st.session_state[key]
        # Atualizar o projeto selecionado antigo
        st.session_state['projeto_selecionado_antigo'] = projeto_selecionado

    # Carregar os dados existentes
    if f"data_carregado_{key_prefix}" not in st.session_state:
        st.session_state[f"data_carregado_{key_prefix}"] = True

        # Função auxiliar para atribuir valores com segurança
        def assign_session_state(key, value, default_value=""):
            if pd.notnull(value):
                st.session_state[key] = str(value)
            else:
                st.session_state[key] = default_value

        assign_session_state(f"numero_projeto_{key_prefix}", df.at[projeto_index, "Número do Projeto"])
        assign_session_state(f"nome_projeto_{key_prefix}", df.at[projeto_index, "Nome do Projeto"])
        assign_session_state(f"sponsor_{key_prefix}", df.at[projeto_index, "Sponsor"])
        assign_session_state(f"gerente_projeto_{key_prefix}", df.at[projeto_index, "Gerente do Projeto"])
        assign_session_state(f"stakeholders_{key_prefix}", df.at[projeto_index, "Stakeholders"])
        assign_session_state(f"dependencias_{key_prefix}", df.at[projeto_index, "Dependências"])
        assign_session_state(f"mudancas_escopo_{key_prefix}", df.at[projeto_index, "Mudanças no Escopo"])

        # Tratamento para listas
        def assign_list_session_state(key, value):
            if isinstance(value, list):
                st.session_state[key] = "\n".join(value)
            elif pd.notnull(value):
                # Se por algum motivo não for uma lista, mas não for nulo
                st.session_state[key] = str(value)
            else:
                st.session_state[key] = ""

        assign_list_session_state(f"recursos_alocados_{key_prefix}", df.at[projeto_index, "Recursos Alocados"])
        assign_list_session_state(f"entregaveis_{key_prefix}", df.at[projeto_index, "Entregáveis"])

        # Tratamento para datas
        def assign_date_session_state(key, value):
            if pd.notnull(value):
                st.session_state[key] = pd.to_datetime(value).date()
            else:
                st.session_state[key] = None

        assign_date_session_state(f"data_inicio_{key_prefix}", df.at[projeto_index, "Data de Início"])
        assign_date_session_state(f"data_termino_prevista_{key_prefix}", df.at[projeto_index, "Data de Término Prevista"])
        assign_date_session_state(f"data_termino_real_{key_prefix}", df.at[projeto_index, "Data de Término Real"])

        # Tratamento para números
        def assign_number_session_state(key, value):
            if pd.notnull(value):
                st.session_state[key] = float(value)
            else:
                st.session_state[key] = 0.0

        assign_number_session_state(f"orcamento_{key_prefix}", df.at[projeto_index, "Orçamento Alocado"])
        assign_number_session_state(f"custos_realizados_{key_prefix}", df.at[projeto_index, "Custos Realizados"])

        # Status do Projeto
        status_value = df.at[projeto_index, "Status do Projeto"]
        if pd.notnull(status_value) and status_value in status_options:
            st.session_state[f"status_projeto_{key_prefix}"] = status_value
        else:
            st.session_state[f"status_projeto_{key_prefix}"] = status_options[0]  # Valor padrão

        # Campos de texto com melhorias de IA
        campos_ia = ["Descrição do Projeto", "Objetivos do Projeto", "Riscos Identificados", "Ações Mitigadoras", "Últimas Atualizações", "Próximas Atividades", "Escopo do Projeto"]
        for campo in campos_ia:
            campo_value = df.at[projeto_index, campo]
            if pd.notnull(campo_value):
                st.session_state[f"{key_prefix}_{campo}_text"] = str(campo_value)
            else:
                st.session_state[f"{key_prefix}_{campo}_text"] = ""

        # Resumo do Projeto
        resumo_value = df.at[projeto_index, "Resumo atual do Projeto"]
        if pd.notnull(resumo_value):
            st.session_state[f"resumo_projeto_{key_prefix}"] = resumo_value
        else:
            st.session_state[f"resumo_projeto_{key_prefix}"] = ""

        # Plano de Ações
        plano_acoes_value = df.at[projeto_index, "Plano de Ações"]
        if isinstance(plano_acoes_value, list):
            st.session_state[f"plano_acoes_{key_prefix}"] = plano_acoes_value
        else:
            st.session_state[f"plano_acoes_{key_prefix}"] = []

    # Agora, podemos utilizar os valores do st.session_state com segurança
    numero_projeto = st.text_input("Número do Projeto", key=f"numero_projeto_{key_prefix}")
    nome_projeto = st.text_input("Nome do Projeto", key=f"nome_projeto_{key_prefix}")

    descricao_projeto = campo_com_melhoria_gpt4("Descrição do Projeto", "", key_prefix)
    sponsor = st.text_input("Sponsor", key=f"sponsor_{key_prefix}")
    gerente_projeto = st.text_input("Gerente do Projeto", key=f"gerente_projeto_{key_prefix}")
    stakeholders = st.text_area("Stakeholders", key=f"stakeholders_{key_prefix}")
    objetivos_projeto = campo_com_melhoria_gpt4("Objetivos do Projeto", "", key_prefix)

    data_inicio = st.date_input("Data de Início", key=f"data_inicio_{key_prefix}")
    data_termino_prevista = st.date_input("Data de Término Prevista", key=f"data_termino_prevista_{key_prefix}")
    data_termino_real = st.date_input("Data de Término Real", key=f"data_termino_real_{key_prefix}")
    orcamento = st.number_input("Orçamento Alocado", min_value=0.0, key=f"orcamento_{key_prefix}")
    custos_realizados = st.number_input("Custos Realizados", min_value=0.0, key=f"custos_realizados_{key_prefix}")
    status_projeto = st.selectbox("Status do Projeto", status_options, index=status_options.index(st.session_state[f"status_projeto_{key_prefix}"]), key=f"status_projeto_{key_prefix}")

    riscos_identificados = campo_com_melhoria_gpt4("Riscos Identificados", "", key_prefix)
    acoes_mitigadoras = campo_com_melhoria_gpt4("Ações Mitigadoras", "", key_prefix)
    ultimas_atualizacoes = campo_com_melhoria_gpt4("Últimas Atualizações", "", key_prefix)
    proximas_atividades = campo_com_melhoria_gpt4("Próximas Atividades", "", key_prefix)
    escopo_projeto = campo_com_melhoria_gpt4("Escopo do Projeto", "", key_prefix)

    dependencias = st.text_area("Dependências", key=f"dependencias_{key_prefix}")
    recursos_alocados = st.text_area("Recursos Alocados (insira um recurso por linha)", key=f"recursos_alocados_{key_prefix}")
    entregaveis = st.text_area("Entregáveis (insira um entregável por linha)", key=f"entregaveis_{key_prefix}")
    mudancas_escopo = st.text_area("Mudanças no Escopo", key=f"mudancas_escopo_{key_prefix}")

    # Plano de Ações
    plano_acoes_key = f"plano_acoes_{key_prefix}"
    plano_acoes = plano_acoes_widget(plano_acoes_key, key_prefix)
    st.session_state[plano_acoes_key] = plano_acoes

    data = {
        "Número do Projeto": numero_projeto,
        "Nome do Projeto": nome_projeto,
        "Descrição do Projeto": descricao_projeto,
        "Sponsor": sponsor,
        "Gerente do Projeto": gerente_projeto,
        "Stakeholders": stakeholders,
        "Objetivos do Projeto": objetivos_projeto,
        "Data de Início": data_inicio,
        "Data de Término Prevista": data_termino_prevista,
        "Data de Término Real": data_termino_real,
        "Orçamento Alocado": orcamento,
        "Custos Realizados": custos_realizados,
        "Status do Projeto": status_projeto,
        "Riscos Identificados": riscos_identificados,
        "Ações Mitigadoras": acoes_mitigadoras,
        "Últimas Atualizações": ultimas_atualizacoes,
        "Próximas Atividades": proximas_atividades,
        "Dependências": dependencias,
        "Escopo do Projeto": escopo_projeto,
        "Plano de Ações": plano_acoes  # Atualizando o Plano de Ações no dicionário data
    }

    if st.button("Gerar Resumo com IA", key=f"gerar_resumo_{key_prefix}"):
        resumo_projeto = gerar_resumo_projeto(data)
        st.session_state[f"resumo_projeto_{key_prefix}"] = resumo_projeto

    resumo_projeto = st.text_area("Resumo atual do Projeto", value=st.session_state.get(f"resumo_projeto_{key_prefix}", ""), key=f"resumo_projeto_{key_prefix}")

    # Botão para salvar as edições
    if st.button("Salvar Alterações", key=f"salvar_alteracoes_{key_prefix}"):
        data.update({
            "Resumo atual do Projeto": resumo_projeto,
            "Recursos Alocados": recursos_alocados.split("\n") if recursos_alocados else [],
            "Entregáveis": entregaveis.split("\n") if entregaveis else [],
            "Mudanças no Escopo": mudancas_escopo
        })
        edit_entry(projeto_index, data)
        st.success("Projeto editado com sucesso!")

        # Limpar os campos após salvar
        for key in list(st.session_state.keys()):
            if key.startswith(key_prefix):
                del st.session_state[key]

# Função para interagir com o chatbot sobre os projetos
def perguntar_sobre_projeto():
    st.header("Perguntar sobre o Projeto")
    df = load_data()

    if df.empty:
        st.warning("Nenhum projeto encontrado.")
        return

    # Selecionar o projeto para o qual fazer perguntas
    projeto_selecionado = st.selectbox("Selecione o projeto", df["Nome do Projeto"])
    projeto_dados = df[df["Nome do Projeto"] == projeto_selecionado].iloc[0].to_dict()

    # Inicializar o histórico de mensagens
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Exibir o histórico de mensagens
    for message in st.session_state["chat_history"]:
        if message["role"] == "user":
            st.markdown(f"**Você:** {message['content']}")
        else:
            st.markdown(f"**Assistente:** {message['content']}")

    # Campo de entrada para a pergunta do usuário
    pergunta = st.text_input("Faça sua pergunta sobre o projeto selecionado:")

    if st.button("Enviar"):
        if pergunta:
            # Adicionar a pergunta ao histórico
            st.session_state["chat_history"].append({"role": "user", "content": pergunta})

            # Construir o contexto com os dados do projeto
            contexto = f"Dados do projeto:\n"
            for key, value in projeto_dados.items():
                if pd.notnull(value):
                    contexto += f"{key}: {value}\n"

            # Construir a mensagem para o modelo
            messages = [
                {"role": "system", "content": "Você é um assistente especializado em gestão de projetos de TI. Responda às perguntas com base nos dados fornecidos."},
                {"role": "system", "content": contexto}
            ] + st.session_state["chat_history"]

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=messages,
                    max_tokens=200,
                    temperature=0.7,
                )
                resposta_assistente = response['choices'][0]['message']['content'].strip()
                st.session_state["chat_history"].append({"role": "assistant", "content": resposta_assistente})
                st.markdown(f"**Assistente:** {resposta_assistente}")
            except Exception as e:
                st.error(f"Erro ao gerar resposta: {str(e)}")
        else:
            st.warning("Por favor, insira uma pergunta.")

    # Botão para limpar o histórico
    if st.button("Limpar Conversa"):
        st.session_state["chat_history"] = []

# Menu de navegação
st.sidebar.title("Menu")
menu_option = st.sidebar.selectbox("Escolha a opção", ["Inserir Projeto", "Editar Projeto", "Perguntar sobre o Projeto"])

if menu_option == "Inserir Projeto":
    inserir_dados()
elif menu_option == "Editar Projeto":
    editar_dados()
elif menu_option == "Perguntar sobre o Projeto":
    perguntar_sobre_projeto()