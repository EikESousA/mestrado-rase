\subsection{Comparação e Análise dos Resultados}

Os resultados produzidos ao longo das etapas experimentais foram analisados de forma integrada, considerando conjuntamente os níveis N1 e N2, bem como os três experimentos definidos (EN1, EN2 e EN1N2). A comparação foi orientada pelos fundamentos teóricos da automação normativa em BIM e pelos princípios de validação semântica em Processamento de Linguagem Natural (PLN), permitindo avaliar não apenas a qualidade das saídas geradas pelo Modelo de Linguagem de Grande Porte, mas também a adequação das métricas empregadas para validar essas saídas.

No experimento EN1, a comparação concentrou-se na proximidade semântica entre as regras N1 geradas automaticamente pelo LLM e as regras N1 reais presentes no dataset. As métricas de validação textual foram aplicadas para verificar se a fragmentação automática preserva o significado normativo original, mesmo diante de variações lexicais ou sintáticas. Nesse contexto, observou-se maior estabilidade para métricas semânticas (SBERT e Multilingual), com médias de 0.710 e 0.749, respectivamente, superiores às métricas lexicais (TF-IDF 0.460; FuzzyWuzzy 0.638). Entre os modelos, o Dolphin apresentou os melhores resultados nas métricas semânticas e de distância (SBERT 0.840; Multilingual 0.873; WMD\_ft 0.748; WMD\_nilc 0.740), enquanto o Gemma obteve a maior pontuação em FuzzyWuzzy (0.724).

No experimento EN2, a análise focou na qualidade da identificação e estruturação dos operadores da metodologia RASE. As representações N2 geradas pelo modelo foram comparadas semanticamente com o N2 real do dataset, considerando tanto o texto completo quanto os campos individuais (Requisito, Aplicabilidade, Seleção e Exceção). A média global das métricas mostra um desempenho inferior ao de EN1, com SBERT 0.587 e Multilingual 0.668, indicando maior dificuldade na formalização estruturada. Ainda assim, as métricas de distância semântica (WMD\_ft 0.694; WMD\_nilc 0.655) superaram TF-IDF (0.462) e FuzzyWuzzy (0.528), sinalizando maior robustez a variações de superfície. O modelo Llama apresentou liderança consistente em todas as métricas (por exemplo, Multilingual 0.869 e WMD\_ft 0.857), configurando-se como o melhor desempenho global para EN2.

Já no experimento EN1N2, a comparação teve como objetivo avaliar a robustez de um pipeline totalmente automatizado, no qual as saídas de uma etapa servem como entrada para a etapa seguinte. Nesse caso, analisou-se se desvios semânticos introduzidos na geração do N1 propagam-se ou se amplificam na geração do N2. Os resultados confirmam degradação em relação ao EN2 direto, com quedas nas médias de TF-IDF (0.360), SBERT (0.567) e Multilingual (0.650). Essa redução é consistente com a hipótese de propagação de erros no encadeamento, embora a queda não seja uniforme entre métricas. O Llama manteve a melhor performance em métricas semânticas (SBERT 0.678; Multilingual 0.743), enquanto o Dolphin foi superior em TF-IDF e WMD (WMD\_ft 0.692; WMD\_nilc 0.669), indicando perfis de desempenho complementares no cenário encadeado.

De forma transversal aos três experimentos, foram avaliados os seguintes aspectos:

\begin{itemize}
\item a precisão na identificação dos operadores RASE na etapa N2, tanto de forma global quanto por operador individual;
\item a consistência semântica das regras formalizadas em formato JSON, considerando equivalência de significado entre as saídas geradas e os valores reais do dataset;
\item a eficiência computacional das métricas de validação, medida por meio do tempo de processamento necessário para cada técnica;
\item a capacidade do LLM em diferenciar regras semanticamente semelhantes de regras distintas, evitando falsos positivos e falsos negativos na validação.
\end{itemize}

A Tabela~\ref{tab:metricas_resultados} sintetiza as medias por metrica (agregadas por modelo) para os tres experimentos, evidenciando a superioridade das metricas baseadas em embeddings em todos os cenarios, bem como a perda de desempenho na transicao de EN2 para EN1N2.
\begin{table}[ht]
\centering
\caption{Medias por metrica nos tres experimentos.}
\label{tab:metricas_resultados}
\begin{tabular}{lcccccc}
\hline
Experimento & FuzzyWuzzy & TF-IDF & SBERT & Multilingual & WMD\_ft & WMD\_nilc \\
\hline
EN1 & 0.638 & 0.460 & 0.710 & 0.749 & 0.661 & 0.659 \\
EN2 & 0.528 & 0.462 & 0.587 & 0.668 & 0.694 & 0.655 \\
EN1N2 & 0.502 & 0.360 & 0.567 & 0.650 & 0.628 & 0.608 \\
\hline
\end{tabular}
\end{table}

A leitura por metrica evidencia comportamentos distintos. FuzzyWuzzy apresentou maior media em EN1 (0.638) e quedas progressivas ate EN1N2 (0.502); seus melhores resultados por experimento foram Gemma em EN1 (0.724), Llama em EN2 (0.761) e Llama em EN1N2 (0.654), indicando que aproximacoes lexicais tendem a penalizar reformulacoes. TF-IDF variou pouco entre EN1 e EN2 (0.460 e 0.462), mas caiu em EN1N2 (0.360), com lideranca do Dolphin em EN1 (0.650) e EN1N2 (0.506), e do Llama em EN2 (0.777). SBERT manteve as maiores medias em EN1 (0.710) e EN2 (0.587), com melhor modelo Dolphin em EN1 (0.840) e Llama em EN2 (0.806) e EN1N2 (0.678), reforcando a capacidade de embeddings captarem equivalencia semantica. Multilingual seguiu padrao semelhante, com melhores medias em EN1 (0.749) e EN2 (0.668), liderados por Dolphin em EN1 (0.873) e Llama em EN2 (0.869) e EN1N2 (0.743). As metricas WMD foram mais altas em EN2 (WMD\_ft 0.694; WMD\_nilc 0.655), indicando maior sensibilidade a estruturacao correta de operadores; Llama liderou WMD\_ft e WMD\_nilc em EN2 (0.857; 0.806), enquanto Dolphin liderou WMD\_ft e WMD\_nilc em EN1 (0.748; 0.740) e EN1N2 (0.692; 0.669).

FuzzyWuzzy e TF-IDF, por serem baseadas em sobreposicao lexical, apresentaram maior sensibilidade a reformulacoes sintaticas e sinonimias, o que explica sua queda mais acentuada em EN1N2 (0.502 e 0.360). Em contraste, SBERT e Multilingual, baseadas em embeddings, mantiveram maior estabilidade e capturaram equivalencias semanticas mesmo com variacoes superficiais, sustentando resultados superiores em todos os experimentos. As medidas WMD (ft e nilc) tiveram desempenho intermediario: superaram as metricas estritamente lexicais, mas ainda sofreram impacto quando houve propagacao de erros no pipeline. Esse comportamento reforca que, para validacao normativa em linguagem natural, metricas semanticas sao mais adequadas para comparar regras com estruturas reformuladas ou parcialmente condensadas.

Ao analisar os modelos, observa-se um padrao consistente de lideranca do Dolphin em EN1, especialmente em metricas semanticas e de distancia, sugerindo melhor capacidade de segmentacao e preservacao do sentido original das regras. O Gemma, embora menos consistente em metricas semanticas, destacou-se em FuzzyWuzzy no EN1, indicando maior proximidade lexical na fragmentacao. No EN2, o Llama foi dominante em todas as metricas, evidenciando maior precisao na identificacao e estruturacao dos operadores RASE; essa superioridade tambem se manteve no EN1N2 para metricas semanticas, sugerindo maior robustez a erros acumulados. O Mistral apresentou desempenho intermediario em todos os cenarios, com estabilidade razoavel, mas sem lideranca em nenhuma metrica. Alpaca e Qwen exibiram os menores valores em EN1 e EN2, e continuaram com resultados mais baixos em EN1N2, indicando menor capacidade de preservar semantica e estruturar corretamente o N2 em comparacao aos demais modelos.

Detalhamento quantitativo por modelo:
Llama apresentou EN1 com FuzzyWuzzy 0.711, TF-IDF 0.535, SBERT 0.764, Multilingual 0.788, WMD\_ft 0.674 e WMD\_nilc 0.665; em EN2, liderou com FuzzyWuzzy 0.761, TF-IDF 0.777, SBERT 0.806, Multilingual 0.869, WMD\_ft 0.857 e WMD\_nilc 0.806; em EN1N2, manteve FuzzyWuzzy 0.654, TF-IDF 0.492, SBERT 0.678, Multilingual 0.743, WMD\_ft 0.663 e WMD\_nilc 0.650.
Dolphin obteve EN1 com FuzzyWuzzy 0.667, TF-IDF 0.650, SBERT 0.840, Multilingual 0.873, WMD\_ft 0.748 e WMD\_nilc 0.740; em EN2, FuzzyWuzzy 0.581, TF-IDF 0.524, SBERT 0.629, Multilingual 0.711, WMD\_ft 0.707 e WMD\_nilc 0.672; em EN1N2, FuzzyWuzzy 0.554, TF-IDF 0.506, SBERT 0.661, Multilingual 0.740, WMD\_ft 0.692 e WMD\_nilc 0.669.
Gemma apresentou EN1 com FuzzyWuzzy 0.724, TF-IDF 0.550, SBERT 0.765, Multilingual 0.789, WMD\_ft 0.687 e WMD\_nilc 0.681; em EN2, FuzzyWuzzy 0.468, TF-IDF 0.555, SBERT 0.655, Multilingual 0.740, WMD\_ft 0.761 e WMD\_nilc 0.710; em EN1N2, FuzzyWuzzy 0.450, TF-IDF 0.407, SBERT 0.586, Multilingual 0.671, WMD\_ft 0.651 e WMD\_nilc 0.628.
Mistral registrou EN1 com FuzzyWuzzy 0.656, TF-IDF 0.508, SBERT 0.747, Multilingual 0.804, WMD\_ft 0.669 e WMD\_nilc 0.667; em EN2, FuzzyWuzzy 0.652, TF-IDF 0.584, SBERT 0.669, Multilingual 0.734, WMD\_ft 0.747 e WMD\_nilc 0.703; em EN1N2, FuzzyWuzzy 0.594, TF-IDF 0.429, SBERT 0.638, Multilingual 0.718, WMD\_ft 0.654 e WMD\_nilc 0.634.
Alpaca apresentou EN1 com FuzzyWuzzy 0.576, TF-IDF 0.331, SBERT 0.605, Multilingual 0.645, WMD\_ft 0.608 e WMD\_nilc 0.630; em EN2, FuzzyWuzzy 0.355, TF-IDF 0.196, SBERT 0.400, Multilingual 0.482, WMD\_ft 0.552 e WMD\_nilc 0.527; em EN1N2, FuzzyWuzzy 0.389, TF-IDF 0.208, SBERT 0.449, Multilingual 0.530, WMD\_ft 0.560 e WMD\_nilc 0.547.
Qwen teve EN1 com FuzzyWuzzy 0.491, TF-IDF 0.189, SBERT 0.538, Multilingual 0.596, WMD\_ft 0.580 e WMD\_nilc 0.569; em EN2, FuzzyWuzzy 0.351, TF-IDF 0.136, SBERT 0.364, Multilingual 0.471, WMD\_ft 0.543 e WMD\_nilc 0.513; em EN1N2, FuzzyWuzzy 0.369, TF-IDF 0.119, SBERT 0.393, Multilingual 0.501, WMD\_ft 0.545 e WMD\_nilc 0.522.

Considerando a media global de todas as metricas e experimentos, o Llama foi o modelo com melhor desempenho geral (media 0.716), seguido por Dolphin (0.676) e Mistral (0.656). O modelo com pior desempenho geral foi o Qwen (media 0.433), com Alpaca em seguida (0.477). Essa hierarquia tambem aparece nos rankings por experimento: em EN1, o Dolphin obteve a maior media por metrica, enquanto em EN2 e EN1N2 o Llama apresentou as maiores medias. Qwen manteve as menores medias em EN1, EN2 e EN1N2, caracterizando-o como o modelo menos consistente em preservacao semantica e estruturacao RASE ao longo do pipeline.

A análise conjunta desses critérios permitiu comparar o desempenho relativo das diferentes métricas de validação textual, identificando quais técnicas são mais sensíveis a pequenas variações lexicais e quais são mais eficazes na captura de equivalência semântica profunda. Além disso, tornou-se possível avaliar o equilíbrio entre precisão semântica e custo computacional, aspecto fundamental para a aplicação prática da verificação de conformidade em fluxos de trabalho baseados em BIM.

O arcabouço metodológico adotado demonstra que a integração entre BIM, RASE e Modelos de Linguagem de Grande Porte constitui uma estratégia promissora para a automação da verificação de conformidade em projetos AEC. O BIM fornece o modelo digital rico em dados; a metodologia RASE orienta a estruturação lógica das normas; o LLM realiza a interpretação automatizada dos textos normativos; e métricas consolidadas de PLN asseguram a validação sistemática dos resultados. Dessa forma, torna-se possível avaliar de maneira rigorosa a aplicação de modelos de linguagem na extração e interpretação de normas técnicas, contribuindo para o avanço das pesquisas em conformidade normativa automatizada no setor de Arquitetura, Engenharia e Construção.

\begin{table}[ht]
\centering
\caption{Resultados por modelo em EN1.}
\label{tab:resultados_en1}
\begin{tabular}{lcccccc}
\hline
Modelo & FuzzyWuzzy & TF-IDF & SBERT & Multilingual & WMD\_ft & WMD\_nilc \\
\hline
alpaca & 0.576 & 0.331 & 0.605 & 0.645 & 0.608 & 0.630 \\
dolphin & 0.667 & 0.650 & 0.840 & 0.873 & 0.748 & 0.740 \\
gemma & 0.724 & 0.550 & 0.765 & 0.789 & 0.687 & 0.681 \\
llama & 0.711 & 0.535 & 0.764 & 0.788 & 0.674 & 0.665 \\
mistral & 0.656 & 0.508 & 0.747 & 0.804 & 0.669 & 0.667 \\
qwen & 0.491 & 0.189 & 0.538 & 0.596 & 0.580 & 0.569 \\
\hline
\end{tabular}
\end{table}

\begin{table}[ht]
\centering
\caption{Resultados por modelo em EN2.}
\label{tab:resultados_en2}
\begin{tabular}{lcccccc}
\hline
Modelo & FuzzyWuzzy & TF-IDF & SBERT & Multilingual & WMD\_ft & WMD\_nilc \\
\hline
alpaca & 0.355 & 0.196 & 0.400 & 0.482 & 0.552 & 0.527 \\
dolphin & 0.581 & 0.524 & 0.629 & 0.711 & 0.707 & 0.672 \\
gemma & 0.468 & 0.555 & 0.655 & 0.740 & 0.761 & 0.710 \\
llama & 0.761 & 0.777 & 0.806 & 0.869 & 0.857 & 0.806 \\
mistral & 0.652 & 0.584 & 0.669 & 0.734 & 0.747 & 0.703 \\
qwen & 0.351 & 0.136 & 0.364 & 0.471 & 0.543 & 0.513 \\
\hline
\end{tabular}
\end{table}

\begin{table}[ht]
\centering
\caption{Resultados por modelo em EN1N2.}
\label{tab:resultados_en1n2}
\begin{tabular}{lcccccc}
\hline
Modelo & FuzzyWuzzy & TF-IDF & SBERT & Multilingual & WMD\_ft & WMD\_nilc \\
\hline
alpaca & 0.389 & 0.208 & 0.449 & 0.530 & 0.560 & 0.547 \\
dolphin & 0.554 & 0.506 & 0.661 & 0.740 & 0.692 & 0.669 \\
gemma & 0.450 & 0.407 & 0.586 & 0.671 & 0.651 & 0.628 \\
llama & 0.654 & 0.492 & 0.678 & 0.743 & 0.663 & 0.650 \\
mistral & 0.594 & 0.429 & 0.638 & 0.718 & 0.654 & 0.634 \\
qwen & 0.369 & 0.119 & 0.393 & 0.501 & 0.545 & 0.522 \\
\hline
\end{tabular}
\end{table}

\begin{table}[ht]
\centering
\caption{Tempo total de geracao por modelo em N1.}
\label{tab:tempo_n1}
\begin{tabular}{lrr}
\hline
Modelo & Tempo (s) & Tempo (h:mm:ss) \\
\hline
alpaca & 104.55 & 0:01:44.55 \\
dolphin & 62.65 & 0:01:02.65 \\
gemma & 133.04 & 0:02:13.04 \\
llama & 5676.97 & 1:34:36.97 \\
mistral & 70.04 & 0:01:10.04 \\
qwen & 309.59 & 0:05:09.59 \\
\hline
\end{tabular}
\end{table}

\begin{table}[ht]
\centering
\caption{Tempo total de geracao por modelo em N2.}
\label{tab:tempo_n2}
\begin{tabular}{lrr}
\hline
Modelo & Tempo (s) & Tempo (h:mm:ss) \\
\hline
alpaca & 249.10 & 0:04:09.10 \\
dolphin & 124.69 & 0:02:04.69 \\
gemma & 244.19 & 0:04:04.19 \\
llama & 6895.71 & 1:54:55.71 \\
mistral & 123.63 & 0:02:03.63 \\
qwen & 6515.09 & 1:48:35.09 \\
\hline
\end{tabular}
\end{table}

\begin{table}[ht]
\centering
\caption{Tempo total de geracao por modelo em N1N2.}
\label{tab:tempo_n1n2}
\begin{tabular}{lrr}
\hline
Modelo & Tempo (s) & Tempo (h:mm:ss) \\
\hline
alpaca & 330.84 & 0:05:30.84 \\
dolphin & 104.28 & 0:01:44.28 \\
gemma & 427.22 & 0:07:07.22 \\
llama & 9450.14 & 2:37:30.14 \\
mistral & 138.39 & 0:02:18.39 \\
qwen & 10093.84 & 2:48:13.84 \\
\hline
\end{tabular}
\end{table}
