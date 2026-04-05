# Solitario app

## Run the app

### uv

Run as a desktop app:

```
uv run flet run
```

Run as a web app:

```
uv run flet run --web
```

For more details on running the app, refer to the [Getting Started Guide](https://docs.flet.dev/).

## Build the app

### Android

```
flet build apk -v
```

For more details on building and signing `.apk` or `.aab`, refer to the [Android Packaging Guide](https://docs.flet.dev/publish/android/).

### iOS

```
flet build ipa -v
```

For more details on building and signing `.ipa`, refer to the [iOS Packaging Guide](https://docs.flet.dev/publish/ios/).

### macOS

```
flet build macos -v
```

For more details on building macOS package, refer to the [macOS Packaging Guide](https://docs.flet.dev/publish/macos/).

### Linux

```
flet build linux -v
```

For more details on building Linux package, refer to the [Linux Packaging Guide](https://docs.flet.dev/publish/linux/).

### Windows

```
flet build windows -v
```

For more details on building Windows package, refer to the [Windows Packaging Guide](https://docs.flet.dev/publish/windows/).



python -m venv .venv
 
source .venv/Scripts/activate
 
pip install -r solitario/src/requirements.txt

## Solitário em Flet — Documentação das funcionalidades extra

Este projeto consiste no desenvolvimento de um jogo de Solitário (Klondike) utilizando Python e a framework Flet. Para além dos requisitos base, foram implementadas várias funcionalidades extra com o objetivo de melhorar a experiência do utilizador, aumentar a usabilidade e demonstrar domínio técnico sobre a framework e sobre a construção de interfaces interativas. Este documento descreve detalhadamente cada uma dessas funcionalidades, justificando a sua inclusão e explicando o seu funcionamento.

---

## ⭐ Funcionalidade Extra 1 — Leaderboard (Top 3 Pontuações)  

A implementação de um leaderboard surgiu da necessidade de introduzir um elemento competitivo e motivador no jogo. O Solitário é, por natureza, um jogo individual, mas a inclusão de um sistema de pontuação e tempos registados permite ao utilizador acompanhar a sua evolução e tentar superar os seus próprios recordes.

O leaderboard guarda automaticamente as três melhores pontuações, ordenadas por desempenho. Cada entrada contém a pontuação final e o tempo total da partida, permitindo ao utilizador comparar não apenas a eficácia, mas também a rapidez com que completou o jogo. Esta informação é apresentada numa janela modal simples e clara, acessível através do botão **"Pontuações"**.

A escolha de limitar o leaderboard ao Top 3 foi intencional: evita poluição visual, mantém o foco nas melhores prestações e reduz a complexidade de armazenamento. A implementação utiliza métodos internos da classe `Solitaire` para calcular pontuações e gerir o histórico.

### **Instruções de utilização**
- Completar uma partida para que a pontuação seja automaticamente registada.  
- Aceder ao leaderboard através do botão **"Pontuações"**.  
- Os resultados são apresentados por ordem decrescente de pontuação.

Esta funcionalidade acrescenta profundidade ao jogo, incentiva a repetição e demonstra a capacidade de integrar sistemas de avaliação e persistência de dados.

---

## ⭐ Funcionalidade Extra 2 — Painel de Desafios (Challenge Panel)  

O painel de desafios foi criado para introduzir variedade e dinamismo no jogo, oferecendo objetivos alternativos além da simples conclusão da partida. Estes desafios podem incluir metas como completar o jogo dentro de um tempo limite, realizar um número específico de movimentos ou alcançar uma pontuação mínima.

A inclusão desta funcionalidade visa aumentar o envolvimento do utilizador, proporcionando uma experiência mais rica e adaptada a diferentes estilos de jogo. Jogadores mais competitivos podem focar‑se em desafios de tempo, enquanto outros podem preferir desafios estratégicos baseados em movimentos.

O painel é apresentado como um elemento lateral fixo, sempre visível durante a partida, permitindo ao utilizador acompanhar o progresso em tempo real. A implementação modular permite adicionar novos desafios facilmente, sem alterar a lógica principal do jogo.

### **Instruções de utilização**
- Consultar o painel lateral para ver os desafios ativos.  
- Cumprir os objetivos propostos durante a partida.  
- Alguns desafios podem desbloquear mensagens de sucesso ou registar pontuações especiais.

Esta funcionalidade demonstra capacidade de design modular, integração de elementos de gamificação e criação de interfaces dinâmicas.

---

## Instruções Gerais de Utilização

- **Reiniciar jogo:** botão *Reiniciar*  
- **Desfazer jogada:** botão *Undo*  
- **Alterar traseira das cartas:** menu de seleção no topo  
- **Guardar/Carregar jogo:** botões dedicados  
- **Consultar leaderboard:** botão *Pontuações*  

---

## Conclusão

As funcionalidades extra foram escolhidas para melhorar a experiência do utilizador, aumentar a profundidade do jogo e demonstrar competências técnicas relevantes. Cada funcionalidade foi implementada de forma modular, intuitiva e integrada com a interface geral.

---