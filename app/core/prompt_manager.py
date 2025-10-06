from typing import List


#============================================================================
# Centraliza a criação e formatação de todos os prompts enviados para a IA.
#  Isso permite fácil manutenção e otimização das instruções.
#============================================================================
class PromptManager:

    # ==========================================================================
    # 1. Prompts para Consolidação Primária de Texto
    # (Objetivo: Transformar um documento em um texto limpo)
    # ==========================================================================


    def get_text_consolidation_prompt(self, document_text: str) -> str:
        instructions = """Sua única tarefa é ler o texto de um documento oficial fornecido a seguir e criar uma versão limpa e consolidada em um único bloco de texto.
Remova todos os elementos que não fazem parte do conteúdo principal, como cabeçalhos repetidos, rodapés com números de página, e outros artefatos de formatação.
Preserve todo o conteúdo textual principal, como artigos, parágrafos e o conteúdo de tabelas, de forma legível e contínua.
Retorne APENAS o texto limpo e consolidado, sem nenhuma introdução, explicação ou formatação adicional.
"""
        return f"{instructions}\n\n--- INÍCIO DO TEXTO DO DOCUMENTO ---\n\n{document_text}\n\n--- FIM DO TEXTO DO DOCUMENTO ---"

    def get_multimodal_consolidation_prompt(self) -> str:
        return """Sua única tarefa é analisar as imagens das páginas de um documento oficial fornecidas a seguir e criar uma versão limpa e consolidada de seu conteúdo em um único bloco de texto.
Realize um OCR de alta qualidade. Ignore elementos que não fazem parte do conteúdo principal, como cabeçalhos, rodapés, números de página, manchas ou carimbos.
Preserve todo o conteúdo textual principal, como artigos e parágrafos.
Retorne APENAS o texto limpo e consolidado, sem nenhuma introdução, explicação ou formatação adicional.
"""

    # ==========================================================================
    # 2. Prompts para Extração Secundária de Dados
    # (Objetivo: Extrair campos específicos de um texto já limpo)
    # ==========================================================================

    def get_secondary_extraction_prompt(self, fields_to_extract: List[str]) -> str:
        fields_str = ", ".join(f'"{f}"' for f in fields_to_extract)
        return f"""Sua tarefa é uma extração de dados focada a partir do texto de um documento oficial. Extraia as seguintes informações: {fields_str}.
**Regra de Saída Obrigatória:** Sua resposta DEVE ser um único objeto JSON.
- As chaves deste objeto devem ser EXATAMENTE as que foram solicitadas.
- Se você não conseguir encontrar a informação para uma chave específica, o valor para essa chave DEVE ser `null`.
- Não omita nenhuma chave da sua resposta, mesmo que não encontre a informação.
"""

    def get_ata_director_extraction_prompt(self) -> str:
        return """Analise o texto da ata fornecido. Encontre a lista de todos os dirigentes eleitos.
Sua resposta DEVE ser um único objeto JSON com uma única chave: "lista_dirigentes_eleitos".
O valor desta chave deve ser uma LISTA de objetos, onde cada objeto representa um dirigente e contém as chaves "nome" e "cargo".
Exemplo: {"lista_dirigentes_eleitos": [{"nome": "João da Silva", "cargo": "Presidente"}, {"nome": "Maria Oliveira", "cargo": "Tesoureira"}]}
Se nenhum dirigente for encontrado, retorne uma lista vazia.
"""

    def get_id_document_extraction_prompt(self) -> str:
        return """Analise o texto dos documentos de identificação fornecidos. Para cada pessoa, extraia o nome completo, o número do CPF e o número do RG.
Sua resposta DEVE ser um único objeto JSON com uma única chave: "lista_pessoas_identificadas".
O valor desta chave deve ser uma LISTA de objetos, onde cada objeto representa uma pessoa e contém as chaves "nome", "cpf" e "rg".
Exemplo: {"lista_pessoas_identificadas": [{"nome": "João da Silva", "cpf": "111.222.333-44", "rg": "55.666.777-8"}]}
Se nenhuma pessoa for identificada, retorne uma lista vazia.
"""

    # ==========================================================================
    # 3. Prompt para Verificação de Critérios
    # (Objetivo: Avaliar um texto contra uma regra específica)
    # ==========================================================================

    def get_criteria_check_prompt(self, context_text: str, instruction: str) -> str:
        prompt_template = f"""
**Contexto:** Você é um assistente de IA especialista em analisar a conformidade de documentos para a outorga de rádios comunitárias no Brasil. Sua análise deve ser objetiva e baseada estritamente no texto fornecido.

**Tarefa:** Com base na instrução a seguir, analise o 'Texto do Documento Consolidado' e forneça uma resposta estruturada em JSON com as chaves 'analise' e 'resultado'.

**Instrução de Análise Específica:**
---
{instruction}
---

**Texto do Documento Consolidado para Análise:**
---
{context_text}
---

**Formato de Saída Obrigatório:**
Sua resposta DEVE ser um único objeto JSON contendo duas chaves principais: `analise` e `resultado`.
- Na chave `analise` (string), descreva seu raciocínio passo a passo.
- Na chave `resultado` (objeto), forneça sua conclusão final com as chaves `conformidade` ('Conforme', 'Não Conforme' ou 'Inconclusivo') e `justificativa` (um resumo curto).
"""
        return prompt_template.strip()
