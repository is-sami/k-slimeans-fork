Paired difference vs k-means (method minus reference):

| Method | Metric | mean diff | 95% CI | wins/n |
| --- | ---: | ---: | ---: | ---: |
| k-NLPmeans (LSA) | ACC | +0.009 | [+0.001, +0.017] | 4/5 |
| k-NLPmeans (LSA) | NMI | +0.004 | [+0.001, +0.008] | 5/5 |
| k-NLPmeans (LSA) | ARI | +0.010 | [+0.002, +0.018] | 5/5 |
| k-SLMmeans (Qwen3-0.6B) | ACC | -0.010 | [-0.018, -0.002] | 0/5 |
| k-SLMmeans (Qwen3-0.6B) | NMI | -0.001 | [-0.004, +0.003] | 1/5 |
| k-SLMmeans (Qwen3-0.6B) | ARI | -0.001 | [-0.007, +0.004] | 2/5 |
| k-SLMmeans (Qwen3-1.7B) | ACC | +0.018 | [+0.004, +0.033] | 4/5 |
| k-SLMmeans (Qwen3-1.7B) | NMI | +0.012 | [+0.005, +0.019] | 5/5 |
| k-SLMmeans (Qwen3-1.7B) | ARI | +0.022 | [+0.011, +0.034] | 5/5 |
| k-SLMmeans (Qwen3-4B) | ACC | -0.040 | [-0.058, -0.022] | 0/5 |
| k-SLMmeans (Qwen3-4B) | NMI | -0.009 | [-0.017, -0.000] | 0/5 |
| k-SLMmeans (Qwen3-4B) | ARI | -0.018 | [-0.027, -0.009] | 0/5 |
| k-SLMmeans-v2 (Qwen3-0.6B) | ACC | +0.011 | [+0.005, +0.017] | 5/5 |
| k-SLMmeans-v2 (Qwen3-0.6B) | NMI | +0.007 | [+0.005, +0.008] | 5/5 |
| k-SLMmeans-v2 (Qwen3-0.6B) | ARI | +0.014 | [+0.008, +0.021] | 5/5 |
| k-SLMmeans-v2 (Qwen3-1.7B) | ACC | +0.012 | [+0.005, +0.018] | 5/5 |
| k-SLMmeans-v2 (Qwen3-1.7B) | NMI | +0.006 | [+0.001, +0.011] | 5/5 |
| k-SLMmeans-v2 (Qwen3-1.7B) | ARI | +0.015 | [+0.005, +0.025] | 5/5 |
| k-SLMmeans-v2 (Qwen3-4B) | ACC | +0.016 | [+0.009, +0.023] | 5/5 |
| k-SLMmeans-v2 (Qwen3-4B) | NMI | +0.012 | [+0.007, +0.017] | 5/5 |
| k-SLMmeans-v2 (Qwen3-4B) | ARI | +0.018 | [+0.007, +0.029] | 5/5 |

Paired difference vs k-NLPmeans (LSA) (method minus reference):

| Method | Metric | mean diff | 95% CI | wins/n |
| --- | ---: | ---: | ---: | ---: |
| k-means | ACC | -0.009 | [-0.017, -0.001] | 1/5 |
| k-means | NMI | -0.004 | [-0.008, -0.001] | 0/5 |
| k-means | ARI | -0.010 | [-0.018, -0.002] | 0/5 |
| k-SLMmeans (Qwen3-0.6B) | ACC | -0.019 | [-0.032, -0.007] | 0/5 |
| k-SLMmeans (Qwen3-0.6B) | NMI | -0.005 | [-0.012, +0.001] | 1/5 |
| k-SLMmeans (Qwen3-0.6B) | ARI | -0.012 | [-0.023, -0.001] | 1/5 |
| k-SLMmeans (Qwen3-1.7B) | ACC | +0.010 | [-0.011, +0.030] | 4/5 |
| k-SLMmeans (Qwen3-1.7B) | NMI | +0.008 | [-0.002, +0.018] | 4/5 |
| k-SLMmeans (Qwen3-1.7B) | ARI | +0.012 | [-0.007, +0.031] | 4/5 |
| k-SLMmeans (Qwen3-4B) | ACC | -0.049 | [-0.072, -0.026] | 0/5 |
| k-SLMmeans (Qwen3-4B) | NMI | -0.013 | [-0.023, -0.002] | 0/5 |
| k-SLMmeans (Qwen3-4B) | ARI | -0.028 | [-0.043, -0.014] | 0/5 |
| k-SLMmeans-v2 (Qwen3-0.6B) | ACC | +0.002 | [-0.006, +0.010] | 3/5 |
| k-SLMmeans-v2 (Qwen3-0.6B) | NMI | +0.002 | [-0.000, +0.005] | 4/5 |
| k-SLMmeans-v2 (Qwen3-0.6B) | ARI | +0.004 | [-0.004, +0.012] | 3/5 |
| k-SLMmeans-v2 (Qwen3-1.7B) | ACC | +0.003 | [-0.003, +0.008] | 3/5 |
| k-SLMmeans-v2 (Qwen3-1.7B) | NMI | +0.002 | [-0.004, +0.007] | 3/5 |
| k-SLMmeans-v2 (Qwen3-1.7B) | ARI | +0.004 | [-0.006, +0.015] | 3/5 |
| k-SLMmeans-v2 (Qwen3-4B) | ACC | +0.007 | [-0.001, +0.016] | 5/5 |
| k-SLMmeans-v2 (Qwen3-4B) | NMI | +0.008 | [+0.002, +0.014] | 5/5 |
| k-SLMmeans-v2 (Qwen3-4B) | ARI | +0.008 | [-0.002, +0.017] | 4/5 |

Paired difference vs k-SLMmeans (Qwen3-0.6B) (method minus reference):

| Method | Metric | mean diff | 95% CI | wins/n |
| --- | ---: | ---: | ---: | ---: |
| k-means | ACC | +0.010 | [+0.002, +0.018] | 5/5 |
| k-means | NMI | +0.001 | [-0.003, +0.004] | 4/5 |
| k-means | ARI | +0.001 | [-0.004, +0.007] | 3/5 |
| k-NLPmeans (LSA) | ACC | +0.019 | [+0.007, +0.032] | 5/5 |
| k-NLPmeans (LSA) | NMI | +0.005 | [-0.001, +0.012] | 4/5 |
| k-NLPmeans (LSA) | ARI | +0.012 | [+0.001, +0.023] | 4/5 |
| k-SLMmeans (Qwen3-1.7B) | ACC | +0.029 | [+0.009, +0.048] | 5/5 |
| k-SLMmeans (Qwen3-1.7B) | NMI | +0.013 | [+0.009, +0.017] | 5/5 |
| k-SLMmeans (Qwen3-1.7B) | ARI | +0.024 | [+0.015, +0.033] | 5/5 |
| k-SLMmeans (Qwen3-4B) | ACC | -0.030 | [-0.051, -0.008] | 0/5 |
| k-SLMmeans (Qwen3-4B) | NMI | -0.008 | [-0.015, -0.001] | 1/5 |
| k-SLMmeans (Qwen3-4B) | ARI | -0.017 | [-0.029, -0.004] | 0/5 |
| k-SLMmeans-v2 (Qwen3-0.6B) | ACC | +0.022 | [+0.010, +0.033] | 5/5 |
| k-SLMmeans-v2 (Qwen3-0.6B) | NMI | +0.008 | [+0.004, +0.012] | 5/5 |
| k-SLMmeans-v2 (Qwen3-0.6B) | ARI | +0.016 | [+0.005, +0.027] | 5/5 |
| k-SLMmeans-v2 (Qwen3-1.7B) | ACC | +0.022 | [+0.010, +0.034] | 5/5 |
| k-SLMmeans-v2 (Qwen3-1.7B) | NMI | +0.007 | [+0.001, +0.013] | 5/5 |
| k-SLMmeans-v2 (Qwen3-1.7B) | ARI | +0.016 | [+0.006, +0.026] | 5/5 |
| k-SLMmeans-v2 (Qwen3-4B) | ACC | +0.027 | [+0.019, +0.034] | 5/5 |
| k-SLMmeans-v2 (Qwen3-4B) | NMI | +0.013 | [+0.008, +0.018] | 5/5 |
| k-SLMmeans-v2 (Qwen3-4B) | ARI | +0.019 | [+0.008, +0.031] | 5/5 |

Paired difference vs k-SLMmeans (Qwen3-1.7B) (method minus reference):

| Method | Metric | mean diff | 95% CI | wins/n |
| --- | ---: | ---: | ---: | ---: |
| k-means | ACC | -0.018 | [-0.033, -0.004] | 1/5 |
| k-means | NMI | -0.012 | [-0.019, -0.005] | 0/5 |
| k-means | ARI | -0.022 | [-0.034, -0.011] | 0/5 |
| k-NLPmeans (LSA) | ACC | -0.010 | [-0.030, +0.011] | 1/5 |
| k-NLPmeans (LSA) | NMI | -0.008 | [-0.018, +0.002] | 1/5 |
| k-NLPmeans (LSA) | ARI | -0.012 | [-0.031, +0.007] | 1/5 |
| k-SLMmeans (Qwen3-0.6B) | ACC | -0.029 | [-0.048, -0.009] | 0/5 |
| k-SLMmeans (Qwen3-0.6B) | NMI | -0.013 | [-0.017, -0.009] | 0/5 |
| k-SLMmeans (Qwen3-0.6B) | ARI | -0.024 | [-0.033, -0.015] | 0/5 |
| k-SLMmeans (Qwen3-4B) | ACC | -0.059 | [-0.072, -0.045] | 0/5 |
| k-SLMmeans (Qwen3-4B) | NMI | -0.021 | [-0.027, -0.015] | 0/5 |
| k-SLMmeans (Qwen3-4B) | ARI | -0.040 | [-0.053, -0.028] | 0/5 |
| k-SLMmeans-v2 (Qwen3-0.6B) | ACC | -0.007 | [-0.022, +0.008] | 1/5 |
| k-SLMmeans-v2 (Qwen3-0.6B) | NMI | -0.006 | [-0.013, +0.002] | 1/5 |
| k-SLMmeans-v2 (Qwen3-0.6B) | ARI | -0.008 | [-0.025, +0.008] | 2/5 |
| k-SLMmeans-v2 (Qwen3-1.7B) | ACC | -0.007 | [-0.023, +0.010] | 1/5 |
| k-SLMmeans-v2 (Qwen3-1.7B) | NMI | -0.006 | [-0.016, +0.003] | 1/5 |
| k-SLMmeans-v2 (Qwen3-1.7B) | ARI | -0.008 | [-0.025, +0.010] | 1/5 |
| k-SLMmeans-v2 (Qwen3-4B) | ACC | -0.002 | [-0.021, +0.017] | 2/5 |
| k-SLMmeans-v2 (Qwen3-4B) | NMI | -0.000 | [-0.007, +0.007] | 2/5 |
| k-SLMmeans-v2 (Qwen3-4B) | ARI | -0.005 | [-0.023, +0.014] | 2/5 |

Paired difference vs k-SLMmeans (Qwen3-4B) (method minus reference):

| Method | Metric | mean diff | 95% CI | wins/n |
| --- | ---: | ---: | ---: | ---: |
| k-means | ACC | +0.040 | [+0.022, +0.058] | 5/5 |
| k-means | NMI | +0.009 | [+0.000, +0.017] | 5/5 |
| k-means | ARI | +0.018 | [+0.009, +0.027] | 5/5 |
| k-NLPmeans (LSA) | ACC | +0.049 | [+0.026, +0.072] | 5/5 |
| k-NLPmeans (LSA) | NMI | +0.013 | [+0.002, +0.023] | 5/5 |
| k-NLPmeans (LSA) | ARI | +0.028 | [+0.014, +0.043] | 5/5 |
| k-SLMmeans (Qwen3-0.6B) | ACC | +0.030 | [+0.008, +0.051] | 5/5 |
| k-SLMmeans (Qwen3-0.6B) | NMI | +0.008 | [+0.001, +0.015] | 4/5 |
| k-SLMmeans (Qwen3-0.6B) | ARI | +0.017 | [+0.004, +0.029] | 5/5 |
| k-SLMmeans (Qwen3-1.7B) | ACC | +0.059 | [+0.045, +0.072] | 5/5 |
| k-SLMmeans (Qwen3-1.7B) | NMI | +0.021 | [+0.015, +0.027] | 5/5 |
| k-SLMmeans (Qwen3-1.7B) | ARI | +0.040 | [+0.028, +0.053] | 5/5 |
| k-SLMmeans-v2 (Qwen3-0.6B) | ACC | +0.051 | [+0.035, +0.068] | 5/5 |
| k-SLMmeans-v2 (Qwen3-0.6B) | NMI | +0.015 | [+0.007, +0.024] | 5/5 |
| k-SLMmeans-v2 (Qwen3-0.6B) | ARI | +0.032 | [+0.020, +0.045] | 5/5 |
| k-SLMmeans-v2 (Qwen3-1.7B) | ACC | +0.052 | [+0.033, +0.070] | 5/5 |
| k-SLMmeans-v2 (Qwen3-1.7B) | NMI | +0.015 | [+0.003, +0.026] | 5/5 |
| k-SLMmeans-v2 (Qwen3-1.7B) | ARI | +0.033 | [+0.014, +0.051] | 5/5 |
| k-SLMmeans-v2 (Qwen3-4B) | ACC | +0.056 | [+0.039, +0.074] | 5/5 |
| k-SLMmeans-v2 (Qwen3-4B) | NMI | +0.021 | [+0.013, +0.029] | 5/5 |
| k-SLMmeans-v2 (Qwen3-4B) | ARI | +0.036 | [+0.019, +0.053] | 5/5 |

Paired difference vs k-SLMmeans-v2 (Qwen3-0.6B) (method minus reference):

| Method | Metric | mean diff | 95% CI | wins/n |
| --- | ---: | ---: | ---: | ---: |
| k-means | ACC | -0.011 | [-0.017, -0.005] | 0/5 |
| k-means | NMI | -0.007 | [-0.008, -0.005] | 0/5 |
| k-means | ARI | -0.014 | [-0.021, -0.008] | 0/5 |
| k-NLPmeans (LSA) | ACC | -0.002 | [-0.010, +0.006] | 2/5 |
| k-NLPmeans (LSA) | NMI | -0.002 | [-0.005, +0.000] | 1/5 |
| k-NLPmeans (LSA) | ARI | -0.004 | [-0.012, +0.004] | 2/5 |
| k-SLMmeans (Qwen3-0.6B) | ACC | -0.022 | [-0.033, -0.010] | 0/5 |
| k-SLMmeans (Qwen3-0.6B) | NMI | -0.008 | [-0.012, -0.004] | 0/5 |
| k-SLMmeans (Qwen3-0.6B) | ARI | -0.016 | [-0.027, -0.005] | 0/5 |
| k-SLMmeans (Qwen3-1.7B) | ACC | +0.007 | [-0.008, +0.022] | 4/5 |
| k-SLMmeans (Qwen3-1.7B) | NMI | +0.006 | [-0.002, +0.013] | 4/5 |
| k-SLMmeans (Qwen3-1.7B) | ARI | +0.008 | [-0.008, +0.025] | 3/5 |
| k-SLMmeans (Qwen3-4B) | ACC | -0.051 | [-0.068, -0.035] | 0/5 |
| k-SLMmeans (Qwen3-4B) | NMI | -0.015 | [-0.024, -0.007] | 0/5 |
| k-SLMmeans (Qwen3-4B) | ARI | -0.032 | [-0.045, -0.020] | 0/5 |
| k-SLMmeans-v2 (Qwen3-1.7B) | ACC | +0.000 | [-0.002, +0.003] | 4/5 |
| k-SLMmeans-v2 (Qwen3-1.7B) | NMI | -0.001 | [-0.006, +0.004] | 3/5 |
| k-SLMmeans-v2 (Qwen3-1.7B) | ARI | +0.000 | [-0.008, +0.009] | 3/5 |
| k-SLMmeans-v2 (Qwen3-4B) | ACC | +0.005 | [-0.002, +0.012] | 4/5 |
| k-SLMmeans-v2 (Qwen3-4B) | NMI | +0.006 | [+0.000, +0.011] | 4/5 |
| k-SLMmeans-v2 (Qwen3-4B) | ARI | +0.004 | [-0.005, +0.013] | 3/5 |

Paired difference vs k-SLMmeans-v2 (Qwen3-1.7B) (method minus reference):

| Method | Metric | mean diff | 95% CI | wins/n |
| --- | ---: | ---: | ---: | ---: |
| k-means | ACC | -0.012 | [-0.018, -0.005] | 0/5 |
| k-means | NMI | -0.006 | [-0.011, -0.001] | 0/5 |
| k-means | ARI | -0.015 | [-0.025, -0.005] | 0/5 |
| k-NLPmeans (LSA) | ACC | -0.003 | [-0.008, +0.003] | 2/5 |
| k-NLPmeans (LSA) | NMI | -0.002 | [-0.007, +0.004] | 2/5 |
| k-NLPmeans (LSA) | ARI | -0.004 | [-0.015, +0.006] | 2/5 |
| k-SLMmeans (Qwen3-0.6B) | ACC | -0.022 | [-0.034, -0.010] | 0/5 |
| k-SLMmeans (Qwen3-0.6B) | NMI | -0.007 | [-0.013, -0.001] | 0/5 |
| k-SLMmeans (Qwen3-0.6B) | ARI | -0.016 | [-0.026, -0.006] | 0/5 |
| k-SLMmeans (Qwen3-1.7B) | ACC | +0.007 | [-0.010, +0.023] | 4/5 |
| k-SLMmeans (Qwen3-1.7B) | NMI | +0.006 | [-0.003, +0.016] | 4/5 |
| k-SLMmeans (Qwen3-1.7B) | ARI | +0.008 | [-0.010, +0.025] | 4/5 |
| k-SLMmeans (Qwen3-4B) | ACC | -0.052 | [-0.070, -0.033] | 0/5 |
| k-SLMmeans (Qwen3-4B) | NMI | -0.015 | [-0.026, -0.003] | 0/5 |
| k-SLMmeans (Qwen3-4B) | ARI | -0.033 | [-0.051, -0.014] | 0/5 |
| k-SLMmeans-v2 (Qwen3-0.6B) | ACC | -0.000 | [-0.003, +0.002] | 1/5 |
| k-SLMmeans-v2 (Qwen3-0.6B) | NMI | +0.001 | [-0.004, +0.006] | 2/5 |
| k-SLMmeans-v2 (Qwen3-0.6B) | ARI | -0.000 | [-0.009, +0.008] | 2/5 |
| k-SLMmeans-v2 (Qwen3-4B) | ACC | +0.005 | [-0.003, +0.012] | 4/5 |
| k-SLMmeans-v2 (Qwen3-4B) | NMI | +0.006 | [+0.002, +0.011] | 5/5 |
| k-SLMmeans-v2 (Qwen3-4B) | ARI | +0.003 | [-0.003, +0.010] | 3/5 |

Paired difference vs k-SLMmeans-v2 (Qwen3-4B) (method minus reference):

| Method | Metric | mean diff | 95% CI | wins/n |
| --- | ---: | ---: | ---: | ---: |
| k-means | ACC | -0.016 | [-0.023, -0.009] | 0/5 |
| k-means | NMI | -0.012 | [-0.017, -0.007] | 0/5 |
| k-means | ARI | -0.018 | [-0.029, -0.007] | 0/5 |
| k-NLPmeans (LSA) | ACC | -0.007 | [-0.016, +0.001] | 0/5 |
| k-NLPmeans (LSA) | NMI | -0.008 | [-0.014, -0.002] | 0/5 |
| k-NLPmeans (LSA) | ARI | -0.008 | [-0.017, +0.002] | 1/5 |
| k-SLMmeans (Qwen3-0.6B) | ACC | -0.027 | [-0.034, -0.019] | 0/5 |
| k-SLMmeans (Qwen3-0.6B) | NMI | -0.013 | [-0.018, -0.008] | 0/5 |
| k-SLMmeans (Qwen3-0.6B) | ARI | -0.019 | [-0.031, -0.008] | 0/5 |
| k-SLMmeans (Qwen3-1.7B) | ACC | +0.002 | [-0.017, +0.021] | 3/5 |
| k-SLMmeans (Qwen3-1.7B) | NMI | +0.000 | [-0.007, +0.007] | 3/5 |
| k-SLMmeans (Qwen3-1.7B) | ARI | +0.005 | [-0.014, +0.023] | 3/5 |
| k-SLMmeans (Qwen3-4B) | ACC | -0.056 | [-0.074, -0.039] | 0/5 |
| k-SLMmeans (Qwen3-4B) | NMI | -0.021 | [-0.029, -0.013] | 0/5 |
| k-SLMmeans (Qwen3-4B) | ARI | -0.036 | [-0.053, -0.019] | 0/5 |
| k-SLMmeans-v2 (Qwen3-0.6B) | ACC | -0.005 | [-0.012, +0.002] | 1/5 |
| k-SLMmeans-v2 (Qwen3-0.6B) | NMI | -0.006 | [-0.011, -0.000] | 1/5 |
| k-SLMmeans-v2 (Qwen3-0.6B) | ARI | -0.004 | [-0.013, +0.005] | 2/5 |
| k-SLMmeans-v2 (Qwen3-1.7B) | ACC | -0.005 | [-0.012, +0.003] | 1/5 |
| k-SLMmeans-v2 (Qwen3-1.7B) | NMI | -0.006 | [-0.011, -0.002] | 0/5 |
| k-SLMmeans-v2 (Qwen3-1.7B) | ARI | -0.003 | [-0.010, +0.003] | 2/5 |
