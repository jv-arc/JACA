# Salvando Dados Extraídos Automaticamente
## Onde Ocorre?
É o workflow utilizado pelo programa na segunda página da aplicação após a extração automática ocorrer

```mermaid
sequenceDiagram
UI --> ProjectManager: run_extraction()
ProjectManager --> ProjectWorkflowOrchestrator: run_extraction_for_category()
ProjectWorkflowOrchestrator --> ProjectDataService: save_extructured_extraction()
ProjectDataService --> ExtractedDataManager: 