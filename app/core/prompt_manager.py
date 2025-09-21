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
    
  def get_criteria_check_prompt(self, context_text: str, instruction: str) -> str:
          """
          Cria um prompt para verificar um critério específico.
  
          Args:
              context_text (str): O texto extraído dos documentos relevantes.
              instruction (str): A instrução específica da regra (vinda do JSON).
  
          Returns:
              str: O prompt formatado para a verificação do critério.
          """
          prompt_template = f"""
  **Contexto:** Você é um assistente de IA especialista em analisar a conformidade de documentos para a outorga de rádios comunitárias no Brasil. Sua análise deve ser objetiva e baseada estritamente no texto fornecido.
  
  **Tarefa:** Com base na instrução a seguir, analise o 'Texto dos Documentos' e forneça uma resposta estruturada em JSON.
  
  **Instrução de Análise:**
  ---
  {instruction}
  ---
  
  **Texto dos Documentos para Análise:**
  ---
  {context_text}
  ---
  
  **Formato de Saída Obrigatório:**
  Retorne **APENAS** um objeto JSON válido, sem nenhum texto ou explicação adicional antes ou depois.
  """
          return prompt_template.strip()

  def get_multimodal_extraction_prompt(
      self, 
      category: str, 
      content_fields: List[str], 
      ignored_fields: List[str]
  ) -> str:
      """
      Cria um prompt para extração estruturada a partir de IMAGENS de um documento.
      """
      prompt_template = f"""
    **Contexto:** Você é um assistente de IA especialista em análise de documentos, equipado com OCR avançado. Sua tarefa é analisar as **imagens das páginas** de um documento fornecido.
    
    **Tarefa:** Analise as imagens das páginas de um documento da categoria '{category}' e extraia as informações relevantes, preenchendo os campos no formato JSON solicitado. Ignore qualquer texto de baixa qualidade ou irrelevante.
    
    **Instruções de Extração:**
    1.  **Campos de Conteúdo (`content_fields`):** Preencha cada campo a seguir com o trecho correspondente do texto encontrado nas imagens. Se uma informação não for encontrada, deixe o valor como uma string vazia ("").
        - Campos a extrair: {', '.join(content_fields)}
    
    2.  **Campos Ignorados (`ignored_fields`):** Identifique e extraia qualquer texto que se encaixe nas categorias de "ruído" (cabeçalhos, rodapés, carimbos, etc.).
        - Campos a ignorar: {', '.join(ignored_fields)}
    
    **Formato de Saída Obrigatório:**
    Retorne **APENAS** um objeto JSON válido, sem nenhum texto ou explicação adicional.
    """
      
      return prompt_template.strip()