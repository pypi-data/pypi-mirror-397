import json
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from scipy.optimize import minimize


class BoxJenkinsPandas:
    def __init__(
        self, data, dates=None, freq=None, run_name=None, base_dir="runs", show_plots=False
    ):
        """
        Inicializa com a série temporal.

        Args:
            data: Lista de valores da série temporal
            dates: Índice de datas (opcional)
            freq: Frequência temporal (opcional)
            run_name: Nome da execução (opcional, gera automaticamente se None)
            base_dir: Diretório base para salvar resultados (padrão: 'runs')
            show_plots: Se True, exibe gráficos interativamente (padrão: False)
        """
        if dates is not None:
            self.raw_series = pd.Series(data, index=pd.DatetimeIndex(dates))
            if freq:
                self.raw_series.index.freq = freq
        else:
            self.raw_series = pd.Series(data)

        self.n = len(data)
        self.z = self.raw_series.copy()  # Será modificada se d > 0
        self.d = 0
        self.p = 0
        self.q = 0
        self.params = {}
        self.residuals = None
        self.mean_z = 0

        # Configuração de execução (MLflow-like)
        self.show_plots = show_plots
        self.base_dir = Path(base_dir)

        # Criar nome da execução
        if run_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.run_name = f"run_{timestamp}"
        else:
            self.run_name = run_name

        # Criar diretório da execução
        self.run_dir = self.base_dir / self.run_name
        self.run_dir.mkdir(parents=True, exist_ok=True)

        # Criar subdiretórios
        self.plots_dir = self.run_dir / "plots"
        self.plots_dir.mkdir(exist_ok=True)

        # Armazenar metadados
        self.metadata = {
            "run_name": self.run_name,
            "start_time": datetime.now().isoformat(),
            "n_observations": self.n,
            "has_dates": dates is not None,
            "frequency": freq,
        }

        print(f"📁 Execução iniciada: {self.run_dir}")

    # ==========================================
    # 1. IDENTIFICAÇÃO
    # ==========================================

    def _calcular_acf_pacf(self, series, max_lag=20):
        """
        Calcula FAC e FACP usando pandas para deslocamento (shift).
        """
        # Centralizar a série
        mean = series.mean()
        s_centered = series - mean
        n = len(series)

        # Variância (c0) - Denominador da FAC
        c0 = np.sum(s_centered**2) / n

        acf = []
        for k in range(max_lag + 1):
            if k == 0:
                acf.append(1.0)
            else:
                # Covariância ck: sum((z_t - mean)(z_{t+k} - mean)) / N
                # Usamos shift(-k) para alinhar z_{t+k} com z_t
                series_k = s_centered.shift(-k)

                # O produto ignora NaNs gerados pelo shift
                ck = np.sum(s_centered * series_k) / n
                acf.append(ck / c0)

        acf = np.array(acf)

        # FACP via Durbin-Levinson (Recursivo)
        pacf = np.zeros(max_lag + 1)
        pacf[0] = 1.0

        if max_lag >= 1:
            pacf[1] = acf[1]

        phi = np.zeros((max_lag + 1, max_lag + 1))
        phi[1, 1] = acf[1]

        for k in range(2, max_lag + 1):
            num = acf[k] - np.sum(phi[k - 1, 1:k] * acf[1:k][::-1])
            den = 1 - np.sum(phi[k - 1, 1:k] * acf[1:k])
            phi[k, k] = num / den
            pacf[k] = phi[k, k]
            for j in range(1, k):
                phi[k, j] = phi[k - 1, j] - phi[k, k] * phi[k - 1, k - j]

        return acf, pacf

    def identificacao(self, d=0):
        """
        Aplica diferenciação usando pandas e plota FAC/FACP.
        """
        self.d = d

        # Diferenciação com Pandas
        if d > 0:
            # diff(d) calcula a diferença de ordem d
            self.z = self.raw_series.diff(periods=1)
            if d > 1:
                for _ in range(d - 1):
                    self.z = self.z.diff(periods=1)
            # Removemos os NaNs gerados pela diferenciação para o cálculo
            self.z = self.z.dropna()
        else:
            self.z = self.raw_series

        self.mean_z = self.z.mean()
        w_t = self.z - self.mean_z  # Série estacionária centrada

        lag_max = min(35, len(w_t) // 2)

        # Calcular ACF/PACF da série original e diferenciada
        acf_original, _ = self._calcular_acf_pacf(self.raw_series - self.raw_series.mean(), lag_max)
        acf_diff, pacf_diff = self._calcular_acf_pacf(w_t, lag_max)

        # Plotagem estilo statsmodels (2x2 layout)
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.subplots_adjust(hspace=0.35, wspace=0.25)

        # 1. Série Original (Superior Esquerdo)
        axes[0, 0].plot(self.raw_series.index, self.raw_series.values, color="#1f77b4", linewidth=1)
        axes[0, 0].set_title("Série Original", fontsize=11)
        axes[0, 0].set_xlabel("")
        axes[0, 0].grid(True, alpha=0.3, linestyle="-", linewidth=0.5)
        axes[0, 0].spines["top"].set_visible(True)
        axes[0, 0].spines["right"].set_visible(True)

        # 2. Autocorrelação Original (Superior Direito)
        lags = np.arange(len(acf_original))
        conf = 1.96 / np.sqrt(len(self.raw_series))

        # Barras verticais
        for lag, acf_val in zip(lags, acf_original):
            axes[0, 1].plot([lag, lag], [0, acf_val], color="#1f77b4", linewidth=2)
            axes[0, 1].plot(lag, acf_val, "o", color="#1f77b4", markersize=5)

        # Banda de confiança preenchida
        axes[0, 1].fill_between(lags, conf, -conf, alpha=0.25, color="#1f77b4")
        axes[0, 1].axhline(0, color="black", linewidth=0.8)
        axes[0, 1].set_title("Autocorrelação (Original)", fontsize=11)
        axes[0, 1].set_xlabel("")
        axes[0, 1].set_ylabel("")
        axes[0, 1].set_xlim(-1, lag_max + 1)
        axes[0, 1].set_ylim(-1, 1.05)
        axes[0, 1].grid(True, alpha=0.3, linestyle="-", linewidth=0.5)
        axes[0, 1].spines["top"].set_visible(True)
        axes[0, 1].spines["right"].set_visible(True)

        # 3. Série Diferenciada (Inferior Esquerdo)
        if d > 0:
            axes[1, 0].plot(self.z.index, self.z.values, color="#1f77b4", linewidth=1)
            axes[1, 0].set_title(f"Série Diferenciada (d={d})", fontsize=11)
        else:
            axes[1, 0].plot(
                self.raw_series.index, self.raw_series.values, color="#1f77b4", linewidth=1
            )
            axes[1, 0].set_title("Série Original", fontsize=11)
        axes[1, 0].set_xlabel("")
        axes[1, 0].grid(True, alpha=0.3, linestyle="-", linewidth=0.5)
        axes[1, 0].spines["top"].set_visible(True)
        axes[1, 0].spines["right"].set_visible(True)

        # 4. Autocorrelação da série diferenciada (Inferior Direito)
        conf_diff = 1.96 / np.sqrt(len(w_t))

        # Barras verticais
        for lag, acf_val in zip(lags, acf_diff):
            axes[1, 1].plot([lag, lag], [0, acf_val], color="#1f77b4", linewidth=2)
            axes[1, 1].plot(lag, acf_val, "o", color="#1f77b4", markersize=5)

        # Banda de confiança preenchida
        axes[1, 1].fill_between(lags, conf_diff, -conf_diff, alpha=0.25, color="#1f77b4")
        axes[1, 1].axhline(0, color="black", linewidth=0.8)
        axes[1, 1].set_title(f"Autocorrelação (d={d})", fontsize=11)
        axes[1, 1].set_xlabel("")
        axes[1, 1].set_ylabel("")
        axes[1, 1].set_xlim(-1, lag_max + 1)
        axes[1, 1].set_ylim(-1, 1.05)
        axes[1, 1].grid(True, alpha=0.3, linestyle="-", linewidth=0.5)
        axes[1, 1].spines["top"].set_visible(True)
        axes[1, 1].spines["right"].set_visible(True)

        plt.tight_layout()

        # Salvar gráfico
        plot_path = self.plots_dir / f"01_identificacao_d{d}.png"
        plt.savefig(plot_path, dpi=300, bbox_inches="tight")
        print(f"📊 Gráfico salvo: {plot_path}")

        if self.show_plots:
            plt.show()
        else:
            plt.close()

        print(f"Identificação (d={d}): Observe o decaimento para escolher p e q.")

    # ==========================================
    # 2. ESTIMAÇÃO
    # ==========================================

    def _calcular_residuos_recursivos(self, params, p, q, w_values):
        """
        Calcula a série a_t.
        Fórmula: a_t = w_t - AR_terms + MA_terms
        """
        phi = params[:p]
        theta = params[p : p + q]
        n = len(w_values)
        a = np.zeros(n)

        # Loop numérico (mais rápido com numpy puro dentro do loop)
        for t in range(max(p, q), n):
            ar_term = np.dot(phi, w_values[t - p : t][::-1]) if p > 0 else 0
            # Convenção negativa para theta: (1 - theta*B)
            ma_term = np.dot(theta, a[t - q : t][::-1]) if q > 0 else 0

            a[t] = w_values[t] - ar_term + ma_term

        return a

    def _funcao_custo(self, params, p, q, w_values):
        a = self._calcular_residuos_recursivos(params, p, q, w_values)
        return np.sum(a[max(p, q) :] ** 2)

    def estimacao(self, p, q):
        """
        Estimação dos parâmetros phi e theta.
        """
        self.p = p
        self.q = q

        # Trabalhamos com numpy array para a otimização
        w_t = (self.z - self.mean_z).values

        initial_guess = np.array([0.1] * (p + q))

        res = minimize(self._funcao_custo, initial_guess, args=(p, q, w_t), method="L-BFGS-B")

        self.phi = res.x[:p]
        self.theta = res.x[p : p + q]

        # Gerar resíduos finais e salvar como pd.Series (alinhado ao índice de z)
        a_vals = self._calcular_residuos_recursivos(res.x, p, q, w_t)
        self.residuals = pd.Series(a_vals, index=self.z.index)
        self.sigma2 = np.var(a_vals[max(p, q) :])

        # Exibir resultados em DataFrame
        df_res = pd.DataFrame(
            {
                "Parâmetro": [f"phi_{i+1}" for i in range(p)] + [f"theta_{i+1}" for i in range(q)],
                "Valor Estimado": np.concatenate([self.phi, self.theta]),
            }
        )

        print("\n=== ESTIMAÇÃO (Mínimos Quadrados Condicionais) ===")
        print(f"Modelo: ARIMA({p},{self.d},{q})")
        print(df_res)
        print(f"Sigma^2 (Variância do Ruído): {self.sigma2:.4f}")

        # Salvar resultados da estimação
        estimacao_path = self.run_dir / "02_estimacao.txt"
        with open(estimacao_path, "w") as f:
            f.write(f"Modelo: ARIMA({p},{self.d},{q})\n\n")
            f.write(df_res.to_string())
            f.write(f"\n\nSigma^2 (Variância do Ruído): {self.sigma2:.4f}\n")
        print(f"📄 Resultados salvos: {estimacao_path}")

    # ==========================================
    # 3. DIAGNÓSTICO
    # ==========================================

    def diagnostico(self):
        """
        Análise de resíduos e Teste Ljung-Box (estilo statsmodels).
        """
        # Removemos os primeiros resíduos (burn-in)
        valid_res = self.residuals.iloc[max(self.p, self.q) :]

        acf_res, _ = self._calcular_acf_pacf(valid_res, max_lag=20)

        n = len(valid_res)
        q_stat = 0
        lag_max = min(20, n // 2)

        for k in range(1, lag_max + 1):
            q_stat += (acf_res[k] ** 2) / (n - k)
        q_stat *= n * (n + 2)

        print("\n=== DIAGNÓSTICO ===")
        print(f"Estatística Q (Ljung-Box) para {lag_max} lags: {q_stat:.4f}")
        print(f"Graus de liberdade (K - p - q): {lag_max - self.p - self.q}")

        # Resíduos padronizados
        std_res = valid_res / np.sqrt(self.sigma2)

        # Plotagem estilo statsmodels (4 painéis de diagnóstico)
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

        # 1. Resíduos Padronizados ao longo do tempo
        ax1 = fig.add_subplot(gs[0, 0])
        std_res.plot(ax=ax1, color="steelblue", linewidth=1)
        ax1.set_title("Standardized residual", fontsize=12, fontweight="bold")
        ax1.set_xlabel("")
        ax1.set_ylabel("")
        ax1.axhline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)
        ax1.grid(True, alpha=0.3)

        # 2. Histograma + KDE + Curva Normal N(0,1)
        ax2 = fig.add_subplot(gs[0, 1])

        # Histograma
        ax2.hist(std_res, bins=30, density=True, alpha=0.6, color="steelblue", edgecolor="black")

        # KDE (Kernel Density Estimate)
        try:
            sns.kdeplot(data=std_res.values, ax=ax2, color="steelblue", linewidth=2, label="KDE")
        except:
            # Fallback se seaborn falhar
            pass

        # Curva Normal N(0,1) para comparação
        x_range = np.linspace(std_res.min(), std_res.max(), 100)
        ax2.plot(x_range, stats.norm.pdf(x_range), "r--", linewidth=2, label="N(0,1)")

        ax2.set_title("Histogram plus estimated density", fontsize=12, fontweight="bold")
        ax2.set_xlabel("")
        ax2.set_ylabel("Density")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # 3. Gráfico Q-Q (Normal)
        ax3 = fig.add_subplot(gs[1, 0])
        stats.probplot(std_res, dist="norm", plot=ax3)
        ax3.set_title("Normal Q-Q", fontsize=12, fontweight="bold")
        ax3.set_xlabel("Theoretical Quantiles")
        ax3.set_ylabel("Sample Quantiles")
        ax3.grid(True, alpha=0.3)

        # 4. Correlograma (ACF dos Resíduos)
        ax4 = fig.add_subplot(gs[1, 1])

        lags = np.arange(len(acf_res))
        conf = 1.96 / np.sqrt(n)

        # Plot ACF com barras verticais
        markerline, stemlines, baseline = ax4.stem(lags, acf_res, basefmt=" ")
        plt.setp(stemlines, linewidth=1.5, color="steelblue")
        plt.setp(markerline, markersize=4, color="steelblue")

        # Banda de confiança preenchida
        ax4.fill_between(lags, conf, -conf, alpha=0.15, color="steelblue")
        ax4.axhline(0, color="black", linewidth=0.8)
        ax4.set_title("Correlogram", fontsize=12, fontweight="bold")
        ax4.set_xlabel("Lag")
        ax4.set_ylabel("ACF")
        ax4.set_xlim(-1, len(acf_res))
        ax4.set_ylim(-1, 1)
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()

        # Salvar gráfico
        plot_path = self.plots_dir / f"03_diagnostico_p{self.p}_q{self.q}.png"
        plt.savefig(plot_path, dpi=300, bbox_inches="tight")
        print(f"📊 Gráfico salvo: {plot_path}")

        if self.show_plots:
            plt.show()
        else:
            plt.close()

        # Salvar resultados do diagnóstico
        diagnostico_path = self.run_dir / "03_diagnostico.txt"
        with open(diagnostico_path, "w") as f:
            f.write(f"Estatística Q (Ljung-Box) para {lag_max} lags: {q_stat:.4f}\n")
            f.write(f"Graus de liberdade (K - p - q): {lag_max - self.p - self.q}\n")
        print(f"📄 Resultados salvos: {diagnostico_path}")

    # ==========================================
    # 4. PREVISÃO
    # ==========================================

    def previsao(self, steps=10):
        """
        Gera previsões futuras.
        """
        # Histórico (convertido para lista para facilitar append)
        w_hist = list((self.z - self.mean_z).values)
        a_hist = list(self.residuals.values)

        forecast_w = []

        # Equação de diferenças para prever w_{t+l}
        for l in range(1, steps + 1):
            ar_part = 0
            for j in range(1, self.p + 1):
                # Pega valor mais recente do histórico + previsões
                val = w_hist[-j]
                ar_part += self.phi[j - 1] * val

            ma_part = 0
            for j in range(1, self.q + 1):
                # Se l - j <= 0, o choque ocorreu no passado e é conhecido
                if l - j <= 0:
                    val_a = a_hist[-(j - (l - 1))]  # Ajuste de índice reverso
                    ma_part += self.theta[j - 1] * val_a
                else:
                    # Choque futuro esperado é 0
                    ma_part += 0

            # w_hat = AR - MA (convenção de sinal Box-Jenkins)
            pred_w = ar_part - ma_part
            w_hist.append(pred_w)
            forecast_w.append(pred_w + self.mean_z)

        # Integração (Reconstruir Z a partir de W)
        last_date = self.raw_series.index[-1]

        # Criar índice futuro com Pandas
        if isinstance(last_date, pd.Timestamp):
            freq = self.raw_series.index.freq if self.raw_series.index.freq else "D"
            future_dates = pd.date_range(start=last_date, periods=steps + 1, freq=freq)[1:]
        else:
            future_dates = range(len(self.raw_series), len(self.raw_series) + steps)

        forecast_z = []

        if self.d == 0:
            forecast_z = forecast_w
        elif self.d == 1:
            # Z_{t+1} = Z_t + W_{t+1} -> Soma cumulativa
            last_z = self.raw_series.iloc[-1]
            forecast_z = np.r_[last_z, forecast_w].cumsum()[1:]
        elif self.d == 2:
            # Integração dupla
            last_z = self.raw_series.iloc[-1]
            last_diff = self.raw_series.diff().iloc[-1]  # Z_t - Z_{t-1}

            temp_diff = np.r_[last_diff, forecast_w].cumsum()[1:]  # Primeira integral
            forecast_z = np.r_[last_z, temp_diff].cumsum()[1:]  # Segunda integral

        # Criar Série Pandas para o resultado
        pred_series = pd.Series(forecast_z, index=future_dates)

        # Calcular intervalos de confiança (95%)
        # A variância da previsão cresce com o horizonte
        # Para ARIMA, usamos aproximação: var(h) ≈ sigma2 * (1 + psi_1^2 + ... + psi_{h-1}^2)
        # Simplificação: var(h) = sigma2 * h para modelos AR(1) ou MA(1) simples
        # Para modelos complexos, seria necessário calcular psi-weights

        # Aproximação conservadora: variância cresce linearmente
        std_errors = np.sqrt(self.sigma2 * (1 + np.arange(steps)))
        ci_lower = forecast_z - 1.96 * std_errors
        ci_upper = forecast_z + 1.96 * std_errors

        # Plotagem final estilo statsmodels
        fig, ax = plt.subplots(figsize=(14, 7))

        # Histórico
        self.raw_series.plot(ax=ax, label="Observado", color="steelblue", linewidth=1.5)

        # Previsão
        pred_series.plot(ax=ax, label="Previsão", color="orangered", linewidth=2, linestyle="--")

        # Intervalo de confiança 95%
        ax.fill_between(
            future_dates,
            ci_lower,
            ci_upper,
            alpha=0.2,
            color="orangered",
            label="Intervalo de Confiança 95%",
        )

        ax.set_title(
            f"Previsão ARIMA({self.p},{self.d},{self.q}) - {steps} passos à frente",
            fontsize=14,
            fontweight="bold",
        )
        ax.set_xlabel("")
        ax.set_ylabel("Valor")
        ax.legend(loc="best", frameon=True)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        # Salvar gráfico
        plot_path = self.plots_dir / f"04_previsao_{steps}steps.png"
        plt.savefig(plot_path, dpi=300, bbox_inches="tight")
        print(f"📊 Gráfico salvo: {plot_path}")

        if self.show_plots:
            plt.show()
        else:
            plt.close()

        print("\n=== PREVISÃO ===")
        print(pred_series)

        # Salvar previsões
        previsao_csv = self.run_dir / "04_previsao.csv"
        pred_series.to_csv(previsao_csv, header=["previsao"])
        print(f"📄 Previsões salvas: {previsao_csv}")

        # Salvar metadados finais
        self.metadata.update(
            {
                "model": f"ARIMA({self.p},{self.d},{self.q})",
                "sigma2": float(self.sigma2),
                "phi": self.phi.tolist() if self.p > 0 else [],
                "theta": self.theta.tolist() if self.q > 0 else [],
                "forecast_steps": steps,
                "end_time": datetime.now().isoformat(),
            }
        )

        metadata_path = self.run_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(self.metadata, f, indent=2)
        print(f"📄 Metadados salvos: {metadata_path}")

        print(f"\n✅ Execução completa! Resultados em: {self.run_dir}")

        return pred_series
