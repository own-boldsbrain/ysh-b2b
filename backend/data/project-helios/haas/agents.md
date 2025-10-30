# Gestão de Agentes LLM no Projeto Helios

Este documento descreve a arquitetura e o processo para configurar e estender os agentes de Large Language Model (LLM) utilizados no sistema HaaS, especificamente para a extração de dados estruturados de fontes como os certificados do INMETRO.

## 1. Visão Geral

O sistema utiliza uma arquitetura flexível para interagir com diferentes provedores de LLM. O objetivo é garantir resiliência (se um provedor falhar, outro assume) e otimização de custos, permitindo a seleção do agente mais adequado para cada tarefa.

O componente central é a `LLMFactory`, localizada em `haas/app/services/inmetro_service.py`. Esta fábrica é responsável por instanciar e retornar o agente LLM apropriado com base em uma lista de prioridades.

## 2. Agentes Suportados

Atualmente, os seguintes agentes LLM estão implementados e disponíveis para uso:

| Agente | Classe | Descrição | Configuração |
| :--- | :--- | :--- | :--- |
| **OpenAI** | `OpenAICodexAgent` | Utiliza a API da OpenAI (e.g., `gpt-4o-mini`). É o provedor primário de alta performance. | `OPENAI_API_KEY` |
| **Anthropic** | `AnthropicAdapter` | Utiliza a API da Anthropic (e.g., `claude-3.5-sonnet`). É o provedor secundário de alta performance. | `ANTHROPIC_API_KEY` |
| **Ollama** | `OllamaLLMAgent` | Permite o uso de modelos LLM executados localmente através do servidor Ollama. Ideal para desenvolvimento e testes offline. | `OLLAMA_API_URL` |
| **Mock** | `MockLLM` | Um agente de simulação que retorna dados fixos. Usado como fallback final e para testes unitários, garantindo que o sistema nunca falhe completamente. | Nenhuma |

## 3. Configuração e Prioridade

A seleção do agente é controlada pela `LLMFactory`, que tenta instanciar os LLMs na seguinte ordem de prioridade:

1.  **OpenAI**
2.  **Anthropic**
3.  **Ollama**
4.  **MockLLM** (Fallback)

A fábrica verifica a disponibilidade das chaves de API (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) ou a URL do serviço (`OLLAMA_API_URL`) como variáveis de ambiente no arquivo `.env`. O primeiro provedor para o qual a configuração necessária é encontrada será o utilizado. Se nenhuma configuração for encontrada, o `MockLLM` é usado por padrão.

### Exemplo de Configuração (`.env`)

```env
# .env

# Provedor Primário
OPENAI_API_KEY="sk-..."

# Provedor Secundário
ANTHROPIC_API_KEY="sk-..."

# Para desenvolvimento local com Ollama
OLLAMA_API_URL="http://localhost:11434"
```

## 4. Como Adicionar um Novo Agente LLM

Para estender o sistema com um novo provedor de LLM, siga os passos abaixo:

1.  **Crie a Classe do Agente:**
    *   Vá para o arquivo `haas/validators/inmetro/llm.py`.
    *   Crie uma nova classe que herde de `BaseLLM`.
    *   Implemente o método `structured_extract(self, text: str, schema: dict) -> dict`. Este método deve receber o texto bruto, o schema Pydantic desejado e retornar um dicionário com os dados extraídos.

    ```python
    # Exemplo de esqueleto para um novo agente
    class NovoProvedorLLM(BaseLLM):
        def __init__(self, api_key: str):
            if not api_key:
                raise ValueError("API key para NovoProvedor é necessária.")
            self.api_key = api_key
            # Inicialize o cliente do provedor aqui

        def structured_extract(self, text: str, schema: dict) -> dict:
            # Implemente a lógica para chamar a API do novo provedor
            # e formatar a saída de acordo com o schema.
            # ...
            return {"extracted_data": "example"}
    ```

2.  **Integre na `LLMFactory`:**
    *   Abra o arquivo `haas/app/services/inmetro_service.py`.
    *   Adicione a lógica de instanciação para o seu novo agente dentro do método `create_llm` da `LLMFactory`, respeitando a ordem de prioridade desejada.

    ```python
    # Dentro de LLMFactory.create_llm()
    # ...
    # Tentar instanciar o NovoProvedor
    try:
        novo_provedor_key = os.getenv("NOVO_PROVEDOR_API_KEY")
        if novo_provedor_key:
            logger.info("Usando NovoProvedor LLM")
            return NovoProvedorLLM(api_key=novo_provedor_key)
    except Exception as e:
        logger.warning(f"Falha ao carregar NovoProvedor LLM: {e}")
    
    # ... (outros provedores)
    ```

3.  **Adicione a Variável de Ambiente:**
    *   Adicione a nova variável de ambiente (e.g., `NOVO_PROVEDOR_API_KEY`) ao seu arquivo `.env` e ao arquivo de exemplo `.env.example`.

Seguindo esses passos, o novo agente LLM será automaticamente integrado ao fluxo de trabalho do sistema, respeitando a lógica de fallback e priorização.
