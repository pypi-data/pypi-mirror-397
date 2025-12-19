import pandas as pd
import numpy as np
import statsmodels.api as sm
from patsy import dmatrices  # formula parsing


class SunLM_Model:
    """
    Simple, social-science–friendly OLS wrapper using formula syntax.

    - Uses patsy to parse formulas
    - Fits OLS via statsmodels
    - Provides unstandardized B, standardized Beta, semi-partial R² (sr²), etc.

    Notes
    -----
    - Std. Err. (unstd): standard errors of unstandardized coefficients (B), from OLS.
    - Std. Err. (Std): standard errors of standardized coefficients (β), derived via the delta method:
        β = B * (SDx / SDy)
        SE(β) = SE(B) * (SDx / SDy)
      This treats SDx and SDy as fixed scaling constants (common reporting approximation).
    """

    def __init__(self, formula: str, data: pd.DataFrame):
        self.formula = formula
        self.data = data
        self.fit_result = None
        self.X = None
        self.y = None

        # 1) Parse formula and create design matrices using patsy
        self.y, self.X = dmatrices(formula, data, return_type="dataframe")

        # 2) Run OLS Regression
        model = sm.OLS(self.y, self.X)
        self.fit_result = model.fit()

    def summary(self):
        """
        Prints a regression summary in a social-science style table.
        """
        if self.fit_result is None:
            print("Model has not been fitted.")
            return

        df_result, model_stats = self._calculate_sslm_metrics()

        print("## 📊 SSLM Regression Summary")
        print("---------------------------------------------------------")
        print(df_result[
            ['Unstd. B', 'Std. Err. (unstd)', 'Std. β', 'Std. Err. (Std)', 't-value', 'p-print', 'Semi-partial R²']
        ])
        print("\n## 📈 Model Fit Statistics")
        print("---------------------------------------------------------")
        print(pd.Series(model_stats).to_string(header=False))
        print("---------------------------------------------------------")

    def as_dataframe(self):
        """
        Returns the coefficient table as a pandas DataFrame
        (for further formatting/export).
        """
        df_result, _ = self._calculate_sslm_metrics()
        return df_result

    def _calculate_sslm_metrics(self):
        """
        Internal method to calculate standardized coefficients (β),
        their delta-method standard errors, and semi-partial R² (sr²).
        """
        model_results = self.fit_result
        X = self.X
        y = self.y.iloc[:, 0]  # y is a 1-column DataFrame from patsy

        # Identify intercept-like column (patsy usually names it 'Intercept')
        exog_names = list(model_results.params.index)
        intercept_candidates = [name for name in exog_names if "Intercept" in name]
        intercept_name = intercept_candidates[0] if intercept_candidates else None

        # For SDx, use predictors excluding intercept (if present)
        if intercept_name is not None:
            X_vars = X.drop(columns=[intercept_name], errors="ignore")
        else:
            X_vars = X.copy()

        sd_y = y.std(ddof=1)
        R2_full = model_results.rsquared

        # Base results table
        results_df = pd.DataFrame({
            'Unstd. B': model_results.params,
            'Std. Err. (unstd)': model_results.bse,
            't-value': model_results.tvalues,
            'p-value': model_results.pvalues
        })

        beta_list = []
        se_beta_list = []
        sr2_list = []

        for var_name, B in model_results.params.items():
            # Skip intercept for Std. β, Std. Err. (Std), and sr²
            if var_name == intercept_name:
                beta_list.append(np.nan)
                se_beta_list.append(np.nan)
                sr2_list.append(np.nan)
                continue

            # Handle potential edge cases (e.g., sd_y=0)
            if sd_y == 0:
                beta_list.append(np.nan)
                se_beta_list.append(np.nan)
            else:
                sd_x = X_vars[var_name].std(ddof=1)
                ratio = sd_x / sd_y if sd_x is not None else np.nan

                # Standardized beta
                beta = B * ratio
                beta_list.append(beta)

                # Delta-method SE for standardized beta
                se_b = model_results.bse[var_name]
                se_beta = se_b * ratio
                se_beta_list.append(se_beta)

            # Semi-partial R² (ΔR²): R²_full - R²_reduced_without_var
            X_reduced = X.drop(columns=[var_name], errors="ignore")
            model_reduced = sm.OLS(y, X_reduced).fit()
            sr2 = R2_full - model_reduced.rsquared
            sr2_list.append(sr2)

        results_df['Std. β'] = beta_list
        results_df['Std. Err. (Std)'] = se_beta_list
        results_df['Semi-partial R²'] = sr2_list

        # p-value formatting
        results_df['p-print'] = results_df['p-value'].apply(
            lambda x: f"{x:.3f}" if x >= .001 else "< .001"
        )

        # Model fit stats
        model_fit_stats = {
            'Dependent variable': self.y.columns[0],
            'N': int(model_results.nobs),
            'R-squared': model_results.rsquared,
            'Adjusted R-squared': model_results.rsquared_adj,
            'F-statistic': model_results.fvalue,
            'Prob (F-statistic)': model_results.f_pvalue,
        }

        return results_df, model_fit_stats


def ols(formula: str, data: pd.DataFrame) -> SunLM_Model:
    """
    High-level user function:
    Runs OLS regression using formula notation and returns a SunLM_Model object.

    Example
    -------
    model = ols("y ~ x1 + x2 + x3", data=df)
    model.summary()
    """
    return SunLM_Model(formula, data)