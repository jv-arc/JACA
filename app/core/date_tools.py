import re
from datetime import datetime
from dateutil.parser import parse as parsedate
from dateutil.relativedelta import relativedelta
from typing import Dict

def extract_and_verify_mandate(text_ata: str, text_estatuto: str, gemini_client, prompt_manager, logger) -> Dict:
    logger.info("Iniciando verificação de vigência de mandato por processo híbrido...")

    # Monta o prompt específico para a extração de datas
    context_text = f"TEXTO DA ATA: {text_ata}\nTEXTO DO ESTATUTO: {text_estatuto}"
    instruction = (
        "Sua única tarefa é extrair informações e retorná-las em um JSON. "
        "Analise os textos da ATA e do ESTATUTO. Encontre a data exata da eleição na ata. "
        "Encontre a string exata que define a duração do mandato no estatuto. "
        "Exemplo de retorno: {\"dataeleicao\": \"15 de março de 2024\", \"duracaomandatostr\": \"4 quatro anos\"}. "
        "Se não encontrar uma das informações, retorne o valor como null."
    )
    prompt = prompt_manager.get_criteria_check_prompt(context_text, instruction)
    model_name = gemini_client.settings.criteriamodel
    date_data = gemini_client.generatejsonfromprompt(prompt, model_name)

    # Verifica se a IA retornou os campos necessários
    if (
        not date_data 
        or not date_data.get("dataeleicao") 
        or not date_data.get("duracaomandatostr")
    ):
        logger.error("A IA não conseguiu extrair as strings de data necessárias.")
        return {"status": False, "justificativa": "Não foi possível extrair a data da eleição ou a duração do mandato."}

    try:
        # Conversão e cálculo em Python
        eleicao_str = date_data["dataeleicao"]
        duracao_str = date_data["duracaomandatostr"]
        # Parse da data de eleição
        date_eleicao = parsedate(eleicao_str, dayfirst=True, default=datetime(1900, 1, 1))
        # Extrai o número de anos da string de duração
        anos_match = re.search(r"(\d+)", duracao_str)
        if not anos_match:
            raise ValueError("Não foi possível encontrar um número de anos na string de duração do mandato.")
        anos_mandato = int(anos_match.group(1))
        # Calcula data final do mandato
        data_fim_mandato = date_eleicao + relativedelta(years=anos_mandato)

        # Verifica vigência
        if data_fim_mandato < datetime.now():
            return {"status": False, "justificativa": f"Mandato expirado em {data_fim_mandato.date()}"}
        return {"status": True}

    except Exception as e:
        logger.error(f"Erro ao verificar vigência do mandato: {e}", exc_info=True)
        return {"status": False, "justificativa": str(e)}
