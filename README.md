<p align="center">
  <img src="docs/images/ufs.png" alt="Logo da UFS" aling="center" width="10%"/>
  <img src="docs/images/procc.png" alt="Logo da PROCC" aling="center" width="18%"/>
</p>

<p align="center">
  <img src="docs/tags/release.svg" alt="Icone da Versão" />
  <img src="docs/tags/license.svg" alt="Icone de Licença" />
  <img src="docs/tags/contributors.svg" alt="Icone da Cobertura" />
</p>

<p align="center">
  <img src="docs/tags/plataform.svg" alt="Icone da Versão" />
  <img src="docs/tags/build.svg" alt="Icone da Construção" />  
  <img src="docs/tags/coverage.svg" alt="Icone da Cobertura" />
</p>

## Descrição

Este código foi desenvolvido como parte do Mestrado do aluno Eike Natan Sousa Brito, no Programa de Pós-Graduação em Ciência da Computação (PROCC) da Fundação Universidade Federal de Sergipe (UFS), durante o período de 2024-2025.

O objetivo principal do projeto é a leitura e interpretação automatizada de normas de engenharia, convertendo um código RASE para o formato JSON. Para isso, utiliza-se o modelo LLaMA 3, explorando técnicas avançadas de Engenharia de Prompt, Fine-Tuning e Recuperação Aumentada por Geração (RAG). Esse processo visa aprimorar a compreensão e estruturação dos dados extraídos das normas, proporcionando maior precisão e eficiência na conversão para um formato estruturado e de fácil manipulação.

## Instalação

### Sistema Operacional

Deve funcionar conforme pretendido no **Windows**, **Linux** ou **macOS**.

### Interpretador Python

Atualmente requer Python **3.11.9**.

### Requisitos

Todos os requisitos dos módulos principais estão listados em **[requirements.txt](https://github.com/EikESousA/mestrado-rase/blob/main/requirements.txt)**.

para instalar as depedências do projeto rode o comando dentro da pasta do projeto.

```
pip install -r requirements.txt
```

## Ambiente Virtual

Recomendamos **fortemente** que você utilize um ambiente virtual usando **[venv](https://docs.python.org/3/library/venv.html)** ou **[conda](https://www.anaconda.com/)**.

Segue o exemplo como instalar e utilizar o virtualenv:

Instale o virtualenv, crie seu ambiente e ative.

```
pip install virtualenv

```

```
virtualenv env
```

Se for linux

```
source env/bin/activate
```

Se for windows

```
.\env\Scripts\activate.bat
```

## Organização do Código

O código é configurado em vários diretórios principais:

- **[databases](https://github.com/EikESousA/mestrado-rase/blob/main/src/databases)**: contém as os dados que serão avaliados.
- **[helpers](https://github.com/EikESousA/mestrado-rase/blob/main/src/helpers)**: contém alguns arquivos podem ser utilizados para ajudar no processo.
- **[utils](https://github.com/EikESousA/mestrado-rase/blob/main/src/models)**: contém algumas funções que ajudam no processo.
- **[models](https://github.com/EikESousA/mestrado-rase/blob/main/src/utils)**: contém todos os arquivos dos modelos LLM e Word Embeddings;

## Ajuda

Se você tiver dúvidas, relatórios de bugs ou solicitações de recursos, não hesite em nos mandar mensagem para o email **eike.sousa@hotmail.com**.

Lembre-se de seguir nosso **[Código de Conduta](https://github.com/EikESousA/IAnvisa/blob/main/CODE_OF_CONDUCT.md)**.

## Licença

Licenciado pelo CC0-1.0 license. Consulte o arquivo **[LICENSE](https://github.com/EikESousA/IAnvisa/blob/main/LICENSE)** para obter detalhes.
