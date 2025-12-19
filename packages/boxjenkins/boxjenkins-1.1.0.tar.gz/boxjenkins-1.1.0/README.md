# boxjenkins

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Implementação completa em Python do ciclo Box-Jenkins para modelagem ARIMA (AutoRegressive Integrated Moving Average).

Esta biblioteca implementa manualmente todas as etapas da metodologia Box-Jenkins, sem dependência de statsmodels, para fins educacionais e de pesquisa.

## 🎯 Características

- **Implementação manual completa** do ciclo Box-Jenkins (4 fases)
- **Cálculos estatísticos from scratch**: ACF, PACF, Ljung-Box
- **Suporte completo a Pandas**: índices temporais preservados
- **Otimização via scipy**: estimação por mínimos quadrados condicionais
- **🆕 Gráficos estilo statsmodels**: Diagnósticos profissionais em layout 2x2
- **🆕 Intervalos de confiança**: Previsões com IC 95%
- **Salvamento automático**: Gráficos, resultados e metadados organizados por execução (estilo MLflow)

## 📦 Instalação

### Via pip (local)

```bash
# Clone o repositório
git clone https://github.com/GersonRS/boxjenkins.git
cd boxjenkins

# Instale em modo de desenvolvimento
pip install -e .
```

### Via pip (produção)

```bash
pip install git+https://github.com/GersonRS/boxjenkins.git
```

## 🚀 Uso Rápido

```python
import pandas as pd
from boxjenkins import BoxJenkinsPandas

# Carregue seus dados
df = pd.read_csv('data.csv', index_col=0, parse_dates=True)
precos = df['valor'].tolist()
dates = df.index

# Crie o modelo (gráficos salvos automaticamente em runs/)
model = BoxJenkinsPandas(
    precos, 
    dates=dates, 
    freq='D',
    run_name="minha_analise",  # Nome da execução (opcional)
    show_plots=False            # False=salva apenas, True=exibe e salva
)

# Fase 1: Identificação (diferenciação + ACF/PACF)
model.identificacao(d=1)

# Fase 2: Estimação (ajuste de parâmetros)
model.estimacao(p=1, q=1)

# Fase 3: Diagnóstico (análise de resíduos)
model.diagnostico()

# Fase 4: Previsão
forecast = model.previsao(steps=30)

# Resultados salvos em: runs/minha_analise/
# - plots/ (gráficos PNG)
# - *.txt (resultados)
# - *.csv (previsões)
# - metadata.json (metadados)
```

## 📖 Ciclo Box-Jenkins

A metodologia implementa as 4 fases clássicas:

### 1. **Identificação** (4 painéis)
- Aplica diferenciação para tornar a série estacionária
- Calcula e plota ACF (Função de Autocorrelação)
- Calcula e plota PACF (Função de Autocorrelação Parcial)
- **Layout 2x2**: Série original, série diferenciada, ACF, PACF
- Ajuda a determinar os valores de p, d, q

```python
model.identificacao(d=1)  # d = ordem de diferenciação
```

### 2. **Estimação**
- Estima parâmetros φ (AR) e θ (MA) via otimização
- Usa mínimos quadrados condicionais
- Otimizador: L-BFGS-B do scipy

```python
model.estimacao(p=1, q=1)  # p = AR, q = MA
```

### 3. **Diagnóstico** (4 painéis estilo statsmodels)
- Analisa resíduos para verificar se são ruído branco
- **Standardized Residuals**: Resíduos padronizados ao longo do tempo
- **Histogram + KDE**: Distribuição com curva normal N(0,1) de referência
- **Normal Q-Q Plot**: Teste visual de normalidade
- **Correlogram**: ACF dos resíduos com bandas de confiança
- Calcula estatística Q de Ljung-Box

```python
model.diagnostico()
```

### 4. **Previsão** (com IC 95%)
- Gera previsões futuras usando equação de diferenças
- Aplica integração para reverter diferenciação
- **Intervalos de confiança 95%** visualizados
- Retorna pd.Series com índice temporal

```python
forecast = model.previsao(steps=30)
```

## 📊 Exemplo Completo

```python
import pandas as pd
import numpy as np
from boxjenkins import BoxJenkinsPandas

# Dados sintéticos: random walk com tendência
np.random.seed(42)
dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
vals = [10]
for i in range(1, 100):
    vals.append(vals[-1] + 0.5 + np.random.normal(0, 1))

# Modelagem ARIMA
model = BoxJenkinsPandas(vals, dates=dates, freq='D')

# Workflow completo
model.identificacao(d=1)      # Diferenciação de ordem 1
model.estimacao(p=1, q=0)     # ARIMA(1,1,0)
model.diagnostico()           # Validação
forecast = model.previsao(steps=15)  # Previsão 15 dias

print(forecast)
```

## 🔧 Dependências

- `numpy >= 1.20.0` - Operações numéricas
- `pandas >= 1.3.0` - Manipulação de séries temporais
- `scipy >= 1.7.0` - Otimização numérica
- `matplotlib >= 3.4.0` - Visualização

## 📝 Notas Técnicas

### Convenção de Sinais MA
Esta implementação usa a convenção `(1 - θB)` para termos de média móvel:

```
a_t = w_t - AR_terms + MA_terms
```

Isso pode resultar em sinais opostos comparado a outras implementações que usam `(1 + θB)`.

### Limitações
- Suporta diferenciação até ordem d=2
- Burn-in period: primeiros `max(p,q)` resíduos são ignorados
- Gráficos usam `plt.show()` (bloqueante)

## 📚 Estrutura do Projeto

```
boxjenkins/
├── boxjenkins/
│   ├── __init__.py                   # Exporta BoxJenkinsPandas
│   └── models.py                     # Implementação da classe principal
├── examples/
│   ├── exemplo_basico.py             # Uso básico
│   └── exemplo_avancado.py           # Comparação de modelos
├── runs/                             # Execuções salvas (gerado automaticamente)
│   └── <run_name>/
│       ├── plots/                    # Gráficos PNG (300 DPI)
│       ├── metadata.json             # Metadados da execução
│       ├── 02_estimacao.txt          # Parâmetros estimados
│       ├── 03_diagnostico.txt        # Estatísticas do diagnóstico
│       └── 04_previsao.csv           # Série de previsões
├── setup.py                          # Configuração pip (legacy)
├── pyproject.toml                    # Configuração pip (moderno)
├── README.md                         # Esta documentação
├── FEATURE_STATSMODELS_PLOTS.md      # Documentação dos gráficos
└── LICENSE                           # Licença MIT
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Este é um projeto educacional focado em demonstrar a implementação manual do Box-Jenkins.

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 👤 Autor

**Gerson RS**
- GitHub: [@GersonRS](https://github.com/GersonRS)

## 🔗 Links Úteis

- [Documentação Box-Jenkins](https://en.wikipedia.org/wiki/Box%E2%80%93Jenkins_method)
- [ARIMA Models](https://otexts.com/fpp2/arima.html)
- [Time Series Analysis](https://www.stat.pitt.edu/stoffer/tsa4/)
