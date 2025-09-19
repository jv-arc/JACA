from typing import List


#===========================================================================
# CLASS: PromptManager
#---------------------------------------------------------------------------
# Gerencia e formata prompts para uso pela IA
#===========================================================================
class PromptManager:
    




    #---------------------------------------------------------------------------------
    # Obtem o Prompt de extracao de conteudo
    #---------------------------------------------------------------------------------
    # Recebe a categoria em questão, o texto do qual queremos extrair dados,
    # os campos a serem extraídos e os campos a serem ignorados.
    # Retorna o prompt formatado pronto para o envio.
    #---------------------------------------------------------------------------------
    def get_extraction_prompt(
        self, 
        category: str, 
        document_text: str, 
        content_fields: List[str], 
        ignored_fields: List[str]
    ) -> str:
        
        prompt_template = f"""
**Contexto:** Você é um assistente de IA especialista em análise de documentos jurídicos e administrativos. Sua tarefa é extrair informações de forma precisa e estruturada.

**Tarefa:** Analise o texto do documento fornecido abaixo, que pertence à categoria '{category}'. Extraia as informações relevantes e popule os campos no formato JSON solicitado.

**Texto do Documento:**
---
{document_text}
---

**Instruções de Extração:**
1.  **Campos de Conteúdo (`content_fields`):** Preencha cada campo a seguir com o trecho correspondente do texto. Se uma informação não for encontrada, o valor do campo deve ser uma string vazia ("").
    - Campos a extrair: {', '.join(content_fields)}

2.  **Campos Ignorados (`ignored_fields`):** Identifique e extraia qualquer texto que se encaixe nas seguintes categorias de "ruído" (cabeçalhos, rodapés, números de página, assinaturas, selos, carimbos, etc.). Isso ajuda a limpar o conteúdo principal.
    - Campos a ignorar: {', '.join(ignored_fields)}

**Formato de Saída Obrigatório:**
Retorne **APENAS** um objeto JSON válido, sem nenhum texto ou explicação adicional antes ou depois. O JSON deve ter a seguinte estrutura:
{{
  "content_fields": {{
    "campo1": "valor1",
    "campo2": "valor2"
  }},
  "ignored_fields": {{
    "campo_ignorado1": "valor_ignorado1"
  }}
}}
"""
        return prompt_template.strip()