# Auditoria WCAG 2.2 — Skill para Claude

[English](./README.md) · **Português**

Plugin para Claude Code e Claude Desktop que faz auditorias de acessibilidade WCAG 2.2 nível AA em páginas web, arquivos HTML e bibliotecas de componentes em Storybook. Ele verifica o contraste de forma programática e gera um relatório de auditoria em HTML.

## Resultados

Avaliado em 10 páginas de teste feitas para isso, com 56 falhas de acessibilidade documentadas:

| Métrica | Resultado |
|---------|-----------|
| Taxa de verdadeiros positivos | **100%** (56/56 falhas conhecidas detectadas) |
| Falsos negativos | **0** |
| Falsos positivos | **0** (confirmado por investigação manual) |
| Cobertura na avaliação | **28/28** critérios do checklist da época |

A skill também encontrou falhas reais de contraste não textual (SC 1.4.11) na página de teste "totalmente conforme", que tinham passado despercebidas por quem montou o teste.

> A avaliação foi feita com o checklist anterior, de 28 critérios. Hoje a skill cobre os 55 critérios A + AA, e a avaliação ainda não foi refeita com os novos.

[Ver o relatório completo da avaliação →](https://gdakuzak.github.io/wcag-audit-claude-skill/eval-report.html)

## Instalação

### Claude Code

```
/plugin marketplace add gdakuzak/wcag-audit-claude-skill
/plugin install wcag-audit@wcag-audit
/reload-plugins
```

O `marketplace add` só registra o catálogo. É o `install` que instala o plugin.

A partir de um clone local: `/plugin marketplace add ./wcag-audit-claude-skill`.

Para atualizar: `/plugin update wcag-audit`.

Só a skill, sem o plugin: `cp -r plugin/skills/wcag-audit ~/.claude/skills/`.

### Claude Desktop

Baixe o [`wcag-audit.plugin`](./wcag-audit.plugin) e abra no Claude Desktop. O plugin aparece como um card de instalação; clique em Aceitar.

## Uso

Chamada direta:

```
/wcag-audit:wcag-audit https://exemplo.com.br
```

Se você instalou só a skill, o comando é `/wcag-audit`.

Também não é preciso chamar pelo nome: a skill é acionada sozinha quando o assunto é acessibilidade. Por exemplo:

- "Essa página está em conformidade com a WCAG?"
- "Faz uma auditoria de acessibilidade nessa URL"
- "Verifica o contraste das cores desse HTML"
- "Audita o Storybook do design system"

A skill aceita URL, arquivo HTML local, arquivo enviado ou um build de Storybook.

## Como funciona

### Página única

1. **Obtenção do código**: baixa a página pela URL ou lê o arquivo.
2. **Extração de cores do CSS**: levanta todos os pares de cor de texto e fundo, incluindo temas claro e escuro, estados de hover e foco, e `rgba()` sobre fundos conhecidos.
3. **Verificação programática de contraste**: calcula as razões de contraste com a fórmula de luminância relativa da WCAG, via `contrast_checker.py`.
4. **Revisão manual dos critérios**: avalia os 55 critérios WCAG 2.2 A + AA no código. Cada um recebe um status (Passa, Falha, Alerta ou N/A) e a evidência.
5. **Relatório**: gera um relatório em HTML autocontido, com tema claro e escuro.

### Storybook / biblioteca de componentes

1. Gera o build estático do Storybook e lê o `index.json`.
2. Roda o `scripts/storybook_audit.mjs`, que executa o axe-core em cada story e em cada tema e navega por Tab comparando screenshots para achar elementos sem indicador de foco visível:
   ```bash
   THEMES=theme:light,theme:dark STORY_FILTER='^components-' \
     node plugin/skills/wcag-audit/scripts/storybook_audit.mjs <dir-do-build> sb-audit.json
   ```
   Rode a partir da raiz do projeto, que precisa ter `playwright` e `axe-core` instalados. Use `AXE_PATH` se o pnpm esconder o `axe-core` e `CHROME` se o navegador do Playwright não estiver instalado.
3. **Atribui cada violação antes de contar.** Ela pode ser do componente, da story (galerias, grades de exemplo, textos de demonstração) ou de props ruins passadas pela story. Só o que é do componente reprova o componente. O restante vai para uma seção separada.
4. Revisa à mão o que o axe não cobre: teclado, gestão de foco em overlays, alternativa a arrastar (2.5.7), mensagens de status (4.1.3), tooltips (1.4.13), tamanho de alvo (2.5.8) e o contraste dos design tokens em todos os temas.

### Correção de contraste

`suggest_fixes(fg, bg, razão)` devolve a cor mais próxima que passa em duas versões: ajustando o texto e ajustando o fundo. Para texto branco ou preto sobre uma superfície colorida, a correção certa é no fundo; nunca deixar o texto branco cinza.

## Estrutura do repositório

```
├── .claude-plugin/marketplace.json  # Marketplace do Claude Code
├── wcag-audit.plugin                # Pacote instalável no Claude Desktop
├── plugin/                          # Código do plugin
│   ├── .claude-plugin/plugin.json   #   Manifesto
│   └── skills/wcag-audit/
│       ├── SKILL.md                 #   Instruções da skill
│       ├── references/              #   Checklist dos 55 critérios
│       └── scripts/                 #   contrast_checker.py, storybook_audit.mjs
├── evals/                           # Suíte de avaliação
│   ├── test-pages/                  #   10 páginas de teste com gabarito (comentários HTML)
│   ├── reports/                     #   Relatórios gerados na avaliação
│   ├── grade_all.py                 #   Script de correção automática
│   └── grading_results.json         #   Resultados estruturados
├── docs/eval-report.html            # Painel da avaliação (GitHub Pages)
└── original-work/                   # Auditoria OKLIS-2026 que inspirou a skill
```

## Páginas de teste da avaliação

| # | Foco | Falhas conhecidas | Detectadas |
|---|------|-------------------|------------|
| 01 | Contraste sutil (razões no limite, rgba, não textual) | 5 | 5 |
| 02 | Estrutura semântica (títulos, landmarks, lang) | 8 | 8 |
| 03 | Teclado e foco (armadilhas, visibilidade, tabindex) | 7 | 7 |
| 04 | Específicos da WCAG 2.2 (tamanho de alvo, foco encoberto) | 4 | 4 |
| 05 | Acessibilidade de formulários (labels, fieldsets, ARIA) | 7 | 7 |
| 06 | Mídia (texto alternativo, legendas, transcrições) | 7 | 7 |
| 07 | Totalmente conforme (teste de falso positivo) | 0* | — |
| 08 | Conteúdo dinâmico (widgets, estados ARIA, live regions) | 6 | 6 |
| 09 | Informação só por cor (links, status, erros) | 6 | 6 |
| 10 | Responsividade e reflow (viewport, tamanho do texto, espaçamento) | 6 | 6 |

\*A página 07 foi feita para estar totalmente conforme, mas a auditoria achou falhas reais de contraste de borda (SC 1.4.11) no tema escuro.

## Limitações

Para páginas avulsas, a skill faz análise estática do código. Ela não testa navegação real por teclado, leitores de tela nem mudanças de estado feitas por JavaScript em um navegador. O modo Storybook roda em navegador, mas cobre só o que o axe-core e o teste de foco por Tab conseguem detectar. Para verificar a conformidade por completo, combine a auditoria com testes manuais usando tecnologias assistivas.

## Licença

MIT
