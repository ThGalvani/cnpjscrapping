# Contribuindo para o CNPJ Scraper

Obrigado por considerar contribuir para o CNPJ Scraper! 🎉

## Código de Conduta

Este projeto adere aos princípios de web scraping ético. Ao contribuir, você concorda em:

- Respeitar os termos de uso dos sites
- Implementar rate limiting adequado
- Não criar features que facilitem uso abusivo
- Manter o foco em dados públicos apenas

## Como Contribuir

### Reportando Bugs

1. Verifique se o bug já não foi reportado nas [Issues](https://github.com/seu-usuario/cnpjscrapping/issues)
2. Abra uma nova issue com:
   - Descrição clara do problema
   - Passos para reproduzir
   - Comportamento esperado vs. observado
   - Versão do Python e sistema operacional
   - Logs relevantes (se aplicável)

### Sugerindo Melhorias

1. Abra uma issue descrevendo:
   - A funcionalidade desejada
   - Casos de uso
   - Benefícios para o projeto
   - Possíveis implementações

### Pull Requests

1. **Fork** o repositório
2. **Clone** seu fork localmente
3. **Crie uma branch** para sua feature:
   ```bash
   git checkout -b feature/minha-feature
   ```

4. **Faça suas alterações** seguindo as diretrizes de código

5. **Teste** suas alterações:
   ```bash
   # Execute os testes
   python -m pytest tests/

   # Valide o código
   python scraper.py --cnpj 00000000000191 --dry-run
   ```

6. **Commit** suas mudanças:
   ```bash
   git commit -m "Adiciona funcionalidade X"
   ```

7. **Push** para seu fork:
   ```bash
   git push origin feature/minha-feature
   ```

8. **Abra um Pull Request** descrevendo suas mudanças

## Diretrizes de Código

### Estilo Python

- Siga [PEP 8](https://pep8.org/)
- Use type hints quando possível
- Docstrings em todas as funções e classes
- Máximo de 100 caracteres por linha

### Exemplo de Docstring

```python
def minha_funcao(parametro: str, opcao: bool = False) -> dict:
    """
    Descrição breve da função

    Args:
        parametro: Descrição do parâmetro
        opcao: Descrição da opção

    Returns:
        Dicionário com os resultados

    Raises:
        ValueError: Quando parametro é inválido
    """
    pass
```

### Commits

Use mensagens de commit claras e descritivas:

- ✅ `Adiciona validação de CPF`
- ✅ `Corrige erro no parser de endereços`
- ✅ `Atualiza documentação do filtro de CNAE`
- ❌ `fix bug`
- ❌ `update`
- ❌ `changes`

### Testes

- Adicione testes para novas funcionalidades
- Mantenha cobertura de testes acima de 80%
- Use pytest para testes

## Estrutura de Novos Scrapers

Ao adicionar um novo scraper:

```python
from .base_scraper import BaseScraper
from ..utils import clean_cnpj, validate_cnpj

class MeuScraper(BaseScraper):
    """Scraper para MinhaAPI"""

    BASE_URL = "https://api.exemplo.com/"

    def get_source_name(self) -> str:
        """Retorna o nome da fonte"""
        return "MinhaAPI"

    def fetch_company_data(self, cnpj: str) -> Optional[Dict[str, Any]]:
        """
        Busca dados de uma empresa

        Args:
            cnpj: CNPJ da empresa

        Returns:
            Dados normalizados ou None
        """
        # Implementação
        pass
```

## Checklist para Pull Requests

- [ ] Código segue PEP 8
- [ ] Docstrings adicionadas/atualizadas
- [ ] Testes adicionados (se aplicável)
- [ ] Documentação atualizada (README.md)
- [ ] Respeita rate limiting e robots.txt
- [ ] Não adiciona dependências desnecessárias
- [ ] Commits são descritivos
- [ ] Branch está atualizada com main

## Áreas que Precisam de Ajuda

- 📝 Melhorias na documentação
- 🧪 Adição de testes unitários
- 🌐 Novos scrapers para fontes públicas
- 🐛 Correção de bugs reportados
- ⚡ Otimizações de performance
- 🎨 Melhorias na CLI

## Perguntas?

Abra uma [Discussion](https://github.com/seu-usuario/cnpjscrapping/discussions) ou entre em contato através das issues.

## Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a Licença MIT.

---

Obrigado por contribuir! 🙏
