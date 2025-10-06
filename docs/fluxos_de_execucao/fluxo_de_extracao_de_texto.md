# Fluxo de Execução de de Extração de Texto
Esse fluxo consiste de duas etapas principais.


## Etapa A. "Consolidação de Texto"

1. Na UI, mais especificamente na página "page2_extracao" o usuário clica em "Iniciar Extração de IA" para uma categoria específica. Chamando na instância do ProjectManager na sessão da página o método "run_text_consolidation_for_category()"


2. O ProjectManager delega a tareva para o ExtractedDataManager e o método run_text_consolidation() passando o caminho para os arquivos


3. esse método chama o seu método interno _extract_content_from_files() para ler o conteúdo bruto dos arquivos. 

Esse método realiza:
- verifica se o conteúdo é de texto ou de iamgens para determinar como deve ser lido.

- chama PromptManager na sequência para obter o prompt de consolidação correto para o caso.

- Chama o GeminiManager e o método `generate_text_<XXXX>` apropriado (texto ou imagem) para obter um único bloco de texto limpo

- O texto é empacotado em um único dicionário com o consolidated_text vazio e devolve para o ProjectManager

4. Projectmanager recebe o `consolidated_text`, carrega o projeto, atualiza os dados da categoria em questão e por fim salva o arquivo.

5. A UI recarrega a página com o consolidated_text na caixa de texto

## Etapa B. "Extração Secundária"

1. Na UI, a página `page2_extracao` o usuário revisa o consolidated_text e clica em Salvar texto e Atualizar campos, chamando `ProjectManager.save_edited_text()` 

2. `save_edited_text()" recebe o texto modificado e salva no arquivo equivalente como "estatuto.json"

3. O método run_secondary_extraction é ativado, nele o campo report_config.json é lido para determinar quais campos são necessários.

4. PromptManager é executado para obter o prompt neceesário

5. GeminiClient é chamado para obter o JSON com os campos extraídos.

6. O content_fields agora não mais vazio é escrito no arquivo.