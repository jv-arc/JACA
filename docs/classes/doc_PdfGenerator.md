# Resumo das Classes para Geração de PDF

O código apresenta duas classes principais que trabalham em conjunto para gerar documentos PDF de requerimentos .

## Classe _DataResolver

**Propósito:** Classe com métodos para obter os dados para geração de relatórios PDF .

### Dependências Principais
- **datetime** - Para manipulação de datas
- **Logger** - Sistema de logging  
- **ProjectState** - Modelo de dados do projeto
- **PathManager** - Gerenciamento de caminhos

### Variáveis de Instância
- **project_data** - Dados do projeto (ProjectState)
- **report_config** - Configuração do relatório (Dict)
- **user_overrides** - Substituições do usuário (Dict)
- **resolved_cache** - Cache de valores resolvidos

### Métodos

**`__init__(project_data, report_config, user_overrides)`**
- Inicializa o resolvedor com dados do projeto, configuração e overrides
- **Dependências:** Logger, _prepare_dynamic_placeholders

**`_prepare_dynamic_placeholders()`**
- Prepara placeholders dinâmicos (data atual, cidade, nomes para assinaturas)
- **Dependências:** datetime.now, get_value, get_value_from_config

**`get_value_from_config(field_label, default_override=None)`**
- Busca valor baseado na label do campo na configuração
- **Retorna:** Any (valor encontrado ou mensagem de erro)
- **Dependências:** get_value

**`get_value(key, default="Não informado")`**
- Busca valor seguindo hierarquia: cache → user_overrides → dados extraídos → padrão
- **Retorna:** Any (valor resolvido)
- **Dependências:** project_data.extracted_data, getattr, hasattr

**`format_text(text)`**
- Substitui placeholders no formato {chave} no texto
- **Retorna:** str (texto com placeholders substituídos)
- **Dependências:** get_value

## Classe PdfGenerator

**Propósito:** Gera PDF da requisição, herdando de FPDF para customização .

**Herança:** FPDF

### Dependências Principais
- **os** - Operações do sistema operacional
- **fpdf** (FPDF, XPos, YPos) - Biblioteca de geração de PDF
- **Logger** - Sistema de logging
- **PathManager** - Para localizar assets (fontes)

### Métodos

**`__init__()`**
- Inicializa o gerador configurando fontes DejaVu e margens automáticas
- **Dependências:** FPDF.__init__, set_auto_page_break, add_font, PathManager.get_asset_str

**`header()`**
- Define cabeçalho padrão "Requerimento de Outorga - RadCom"
- **Dependências:** set_font, cell, ln

**`footer()`** 
- Define rodapé com numeração das páginas
- **Dependências:** set_y, set_font, cell, page_no

**`_draw_title(title)`**
- Desenha título centralizado em negrito
- **Dependências:** set_font, multi_cell, ln

**`_draw_table(table_config, resolver)`**
- Desenha tabela com campos formatados (label: valor)
- **Dependências:** set_font, cell, ln, multi_cell, get_x, get_y, set_xy, _DataResolver.get_value

**`_write_formatted_text(text, resolver)`**
- Escreve texto justificado com placeholders substituídos
- **Dependências:** _DataResolver.format_text, set_font, multi_cell, ln

**`create_request_pdf(project_data, report_config, user_overrides, output_path)`**
- **Método principal** que cria o PDF completo seguindo estrutura:
  1. Título principal
  2. Tabelas de dados
  3. Texto boilerplate  
  4. Declaração final e assinaturas
- **Retorna:** bool (sucesso/erro)
- **Dependências:** _DataResolver, set_title, add_page, _draw_title, _draw_table, _write_formatted_text, os.makedirs, output

## Fluxo de Funcionamento

As classes trabalham em conjunto onde **_DataResolver** resolve e formata os dados do projeto, enquanto **PdfGenerator** estrutura e renderiza o documento PDF final. O sistema utiliza configurações flexíveis permitindo customização de layout e conteúdo através dos parâmetros report_config e user_overrides .