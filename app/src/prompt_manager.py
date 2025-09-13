from typing import List

class PromptManager:
    """
    Gerencia a criação e formatação de prompts para a IA.
    """
    def get_extraction_prompt(
        self, 
        category: str, 
        document_text: str, 
        content_fields: List[str], 
        ignored_fields: List[str]
    ) -> str:
        """
        Cria um prompt detalhado para extração estruturada de dados.

        Args:
            category (str): A categoria do documento (ex: 'estatuto').
            document_text (str): O texto completo extraído do documento.
            content_fields (List[str]): Lista de campos de conteúdo a serem extraídos.
            ignored_fields (List[str]): Lista de campos de ruído a serem extraídos e ignorados.

        Returns:
            str: O prompt formatado pronto para ser enviado à IA.
        """
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