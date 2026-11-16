### Step 1 (shared step-0 partition; replayed from the summary embeddings): means over seeds

Objective (J_before; relative jump at replacement; relative change at block end vs before and vs the no-replacement counterfactual; iterations run)

| model | j_before | jump_rel | end_vs_before_rel | end_vs_cf_rel | n_iter |
| --- | ---: | ---: | ---: | ---: | ---: |
| bbc_dense_lsa | 380 | 0.756 | -0.00286 | -0.00286 | 7 |
| bbc_dense_qwen3-0.6b | 380 | 1.1 | -0.000529 | -0.000529 | 8 |
| bbc_dense_qwen3-1.7b | 380 | 1.11 | -0.000548 | -0.000548 | 6.4 |
| bbc_dense_qwen3-4b | 380 | 1.15 | -0.00322 | -0.00322 | 7.6 |

Centroid movement (per-cluster medians in pre RMS radii, cosine, share whose nearest pre center is its own, distance from summary to block-end center in radii, distance from block-end center to the pre center in radii, fraction by which the block shortens the summary-to-center distance)

| model | drift_median | cosine_median | own_nearest_share | to_end_radii_median | end_vs_pre_radii_median | pulled_back_median |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| bbc_dense_lsa | 0.887 | 0.658 | 1 | 0.882 | 0.0359 | -0.00259 |
| bbc_dense_qwen3-0.6b | 1.07 | 0.372 | 1 | 1.07 | 0.0438 | -0.000381 |
| bbc_dense_qwen3-1.7b | 1.06 | 0.404 | 0.96 | 1.06 | 0.0217 | 0.000966 |
| bbc_dense_qwen3-4b | 1.07 | 0.349 | 0.92 | 1.07 | 0.0205 | -1.68e-05 |

Partition change (fraction of points moved at the replacement and over the block; ARI and mean cluster Jaccard against the pre partition)

| model | frac_moved_replacement | frac_moved_end | ari_replacement_vs_pre | ari_end_vs_pre | jaccard_end_mean |
| --- | ---: | ---: | ---: | ---: | ---: |
| bbc_dense_lsa | 0.173 | 0.0704 | 0.634 | 0.901 | 0.881 |
| bbc_dense_qwen3-0.6b | 0.25 | 0.0668 | 0.493 | 0.892 | 0.888 |
| bbc_dense_qwen3-1.7b | 0.238 | 0.0292 | 0.526 | 0.948 | 0.932 |
| bbc_dense_qwen3-4b | 0.216 | 0.0644 | 0.543 | 0.908 | 0.891 |

Movers at the replacement (total, counts toward/away from the gold majority and ending in their own gold majority, each beside the mean of a shuffled-destination baseline; share of all points in their own cluster's majority; move rates by margin and flag)

| model | n_moved_replacement | toward_replacement | toward_shuffled | away_replacement | away_shuffled | ends_in_own_majority_replacement | ends_in_own_majority_shuffled | share_in_own_majority_pre | move_rate_boundary | move_rate_core | move_rate_flagged | move_rate_unflagged | share_movers_from_flagged | share_points_in_flagged |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bbc_dense_lsa | 86.6 | 6.2 | 1.95 | 55.8 | 55.3 | 18 | 14.2 | 0.88 | 0.408 | 0.0949 | n/a | 0.173 | 0 | 0 |
| bbc_dense_qwen3-0.6b | 125 | 6.8 | 1.88 | 92.4 | 80.9 | 12.8 | 19.3 | 0.88 | 0.474 | 0.175 | n/a | 0.25 | 0 | 0 |
| bbc_dense_qwen3-1.7b | 119 | 5 | 1.56 | 86.8 | 82.2 | 15.6 | 16.7 | 0.88 | 0.44 | 0.17 | n/a | 0.238 | 0 | 0 |
| bbc_dense_qwen3-4b | 108 | 7.8 | 2.46 | 72 | 68.3 | 17.6 | 16 | 0.88 | 0.496 | 0.122 | n/a | 0.216 | 0 | 0 |

Duplicates and collapsed centroids (clusters per step)

| model | n_dup_clusters | n_meta_clusters | n_empty_replacement | n_empty_end | n_reseeded |
| --- | ---: | ---: | ---: | ---: | ---: |
| bbc_dense_lsa | 0 | 0 | 0 | 0 | 0 |
| bbc_dense_qwen3-0.6b | 0 | 0 | 0 | 0 | 0 |
| bbc_dense_qwen3-1.7b | 0 | 0 | 0 | 0 | 0 |
| bbc_dense_qwen3-4b | 0 | 0 | 0 | 0 | 0 |

### All five steps pooled (replayed; from step 2 on the previous block is replayed too): means over seeds

Objective (J_before; relative jump at replacement; relative change at block end vs before and vs the no-replacement counterfactual; iterations run)

| model | j_before | jump_rel | end_vs_before_rel | end_vs_cf_rel | n_iter |
| --- | ---: | ---: | ---: | ---: | ---: |
| bbc_dense_lsa | 381 | 0.763 | -0.00123 | -0.00123 | 6.15 |
| bbc_dense_qwen3-0.6b | 379 | 1.09 | -0.00141 | -0.00141 | 7.27 |
| bbc_dense_qwen3-1.7b | 380 | 1.12 | -0.000836 | -0.000836 | 6.26 |
| bbc_dense_qwen3-4b | 381 | 1.15 | -0.00144 | -0.00144 | 8 |

Centroid movement (per-cluster medians in pre RMS radii, cosine, share whose nearest pre center is its own, distance from summary to block-end center in radii, distance from block-end center to the pre center in radii, fraction by which the block shortens the summary-to-center distance)

| model | drift_median | cosine_median | own_nearest_share | to_end_radii_median | end_vs_pre_radii_median | pulled_back_median |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| bbc_dense_lsa | 0.887 | 0.651 | 1 | 0.884 | 0.0274 | 0.000347 |
| bbc_dense_qwen3-0.6b | 1.06 | 0.389 | 0.991 | 1.06 | 0.0205 | -0.000174 |
| bbc_dense_qwen3-1.7b | 1.06 | 0.405 | 0.968 | 1.06 | 0.0146 | 0.000331 |
| bbc_dense_qwen3-4b | 1.07 | 0.343 | 0.909 | 1.08 | 0.0246 | -0.000104 |

Partition change (fraction of points moved at the replacement and over the block; ARI and mean cluster Jaccard against the pre partition)

| model | frac_moved_replacement | frac_moved_end | ari_replacement_vs_pre | ari_end_vs_pre | jaccard_end_mean |
| --- | ---: | ---: | ---: | ---: | ---: |
| bbc_dense_lsa | 0.152 | 0.0378 | 0.667 | 0.945 | 0.926 |
| bbc_dense_qwen3-0.6b | 0.24 | 0.0413 | 0.509 | 0.935 | 0.937 |
| bbc_dense_qwen3-1.7b | 0.207 | 0.0282 | 0.572 | 0.953 | 0.945 |
| bbc_dense_qwen3-4b | 0.234 | 0.042 | 0.515 | 0.939 | 0.919 |

Movers at the replacement (total, counts toward/away from the gold majority and ending in their own gold majority, each beside the mean of a shuffled-destination baseline; share of all points in their own cluster's majority; move rates by margin and flag)

| model | n_moved_replacement | toward_replacement | toward_shuffled | away_replacement | away_shuffled | ends_in_own_majority_replacement | ends_in_own_majority_shuffled | share_in_own_majority_pre | move_rate_boundary | move_rate_core | move_rate_flagged | move_rate_unflagged | share_movers_from_flagged | share_points_in_flagged |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bbc_dense_lsa | 76.2 | 5.85 | 1.93 | 48.2 | 46.7 | 12.8 | 10.4 | 0.86 | 0.38 | 0.0763 | n/a | 0.152 | 0 | 0 |
| bbc_dense_qwen3-0.6b | 120 | 6.36 | 2.52 | 103 | 85.5 | 7.73 | 21.3 | 0.917 | 0.454 | 0.168 | n/a | 0.24 | 0 | 0 |
| bbc_dense_qwen3-1.7b | 104 | 6.26 | 2.6 | 78.5 | 71.7 | 10.9 | 14 | 0.883 | 0.405 | 0.141 | n/a | 0.207 | 0 | 0 |
| bbc_dense_qwen3-4b | 117 | 6 | 1.94 | 72.8 | 70.3 | 18.4 | 16.8 | 0.854 | 0.497 | 0.146 | n/a | 0.234 | 0 | 0 |

Duplicates and collapsed centroids (clusters per step)

| model | n_dup_clusters | n_meta_clusters | n_empty_replacement | n_empty_end | n_reseeded |
| --- | ---: | ---: | ---: | ---: | ---: |
| bbc_dense_lsa | 0 | 0 | 0 | 0 | 0 |
| bbc_dense_qwen3-0.6b | 0 | 0 | 0 | 0 | 0 |
| bbc_dense_qwen3-1.7b | 0 | 0 | 0 | 0 | 0 |
| bbc_dense_qwen3-4b | 0 | 0 | 0 | 0 | 0 |

### Outcome

**Step 1 headline.** Step 0 replays exactly, so at step 1 the pre state and the plain-Lloyd counterfactual are exact and `assignments_evolution[1]` is the real post-block partition. Mean over seeds of (score of the logged partition after the block) minus (score after plain Lloyd from the step-0 partition, same 20 iterations); `seeds_below` counts seeds with a lower ACC than the counterfactual; `d_acc_replayed` is the same from the replay, as a check.

| model | d_acc | d_nmi | d_ari | seeds_below | d_acc_replayed | replay_vs_logged_points |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| bbc_dense_lsa | +0.0328 | +0.0196 | +0.0350 | 3/5 | +0.0328 | 0 |
| bbc_dense_qwen3-0.6b | +0.0160 | -0.0063 | +0.0038 | 0/5 | +0.0160 | 0 |
| bbc_dense_qwen3-1.7b | +0.0060 | +0.0096 | +0.0072 | 1/5 | +0.0060 | 0 |
| bbc_dense_qwen3-4b | +0.0428 | +0.0364 | +0.0541 | 0/5 | +0.0428 | 0 |

Per seed, step 1, logged partition minus counterfactual.

| model | seed | d_acc | d_nmi | d_ari |
| --- | ---: | ---: | ---: | ---: |
| bbc_dense_lsa | 0 | -0.0340 | -0.0602 | -0.0608 |
| bbc_dense_lsa | 1 | -0.0040 | -0.0086 | -0.0089 |
| bbc_dense_lsa | 2 | +0.2040 | +0.1707 | +0.2491 |
| bbc_dense_lsa | 3 | -0.0040 | -0.0119 | -0.0089 |
| bbc_dense_lsa | 4 | +0.0020 | +0.0080 | +0.0047 |
| bbc_dense_qwen3-0.6b | 0 | +0.0400 | -0.0864 | -0.0365 |
| bbc_dense_qwen3-0.6b | 1 | +0.0000 | +0.0016 | +0.0002 |
| bbc_dense_qwen3-0.6b | 2 | +0.0320 | +0.0339 | +0.0372 |
| bbc_dense_qwen3-0.6b | 3 | +0.0020 | +0.0028 | +0.0047 |
| bbc_dense_qwen3-0.6b | 4 | +0.0060 | +0.0164 | +0.0136 |
| bbc_dense_qwen3-1.7b | 0 | +0.0000 | +0.0063 | -0.0016 |
| bbc_dense_qwen3-1.7b | 1 | -0.0020 | -0.0069 | -0.0048 |
| bbc_dense_qwen3-1.7b | 2 | +0.0260 | +0.0273 | +0.0287 |
| bbc_dense_qwen3-1.7b | 3 | +0.0000 | +0.0012 | +0.0001 |
| bbc_dense_qwen3-1.7b | 4 | +0.0060 | +0.0200 | +0.0138 |
| bbc_dense_qwen3-4b | 0 | +0.0020 | +0.0062 | +0.0039 |
| bbc_dense_qwen3-4b | 1 | +0.0000 | -0.0031 | -0.0002 |
| bbc_dense_qwen3-4b | 2 | +0.2040 | +0.1707 | +0.2491 |
| bbc_dense_qwen3-4b | 3 | +0.0020 | -0.0019 | +0.0043 |
| bbc_dense_qwen3-4b | 4 | +0.0060 | +0.0100 | +0.0133 |

**Step 1, both sides run to sklearn's own stop** (cap 300 iterations; replayed from the summary embeddings). A fixed 20-iteration budget can leave the replacement block less converged than the counterfactual (which starts converged), so this separates a worse end state from less convergence. `n_iter` and `n_iter_cf` are mean iterations to the stop, `capped*` the runs that hit the cap, `j_end_rel` the mean relative objective of the replacement run over the counterfactual's, and `d_*` the score differences (replacement minus counterfactual).

| model | n_iter | n_iter_cf | capped | capped_cf | j_end_rel | d_acc | d_nmi | d_ari | seeds_below |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| bbc_dense_lsa | 7 | 1 | 0 | 0 | -0.0029 | +0.0328 | +0.0196 | +0.0350 | 3/5 |
| bbc_dense_qwen3-0.6b | 8 | 1 | 0 | 0 | -0.0005 | +0.0160 | -0.0063 | +0.0038 | 0/5 |
| bbc_dense_qwen3-1.7b | 6.4 | 1 | 0 | 0 | -0.0005 | +0.0060 | +0.0096 | +0.0072 | 1/5 |
| bbc_dense_qwen3-4b | 7.6 | 1 | 0 | 0 | -0.0032 | +0.0428 | +0.0364 | +0.0541 | 0/5 |

**Per step, replayed.** From step 2 on every row starts from a replayed previous block.

Mean over seeds of (replayed score after the block) minus (score after plain Lloyd from the replayed pre-replacement state, same iterations).

| model | step | d_acc | d_nmi | d_ari |
| --- | ---: | ---: | ---: | ---: |
| bbc_dense_lsa | 1 | +0.0328 | +0.0196 | +0.0350 |
| bbc_dense_lsa | 2 | -0.0035 | -0.0025 | -0.0049 |
| bbc_dense_lsa | 3 | +0.0090 | +0.0183 | +0.0248 |
| bbc_dense_lsa | 4 | +0.0000 | -0.0062 | -0.0063 |
| bbc_dense_lsa | 5 | -0.0100 | -0.0107 | -0.0071 |
| bbc_dense_qwen3-0.6b | 1 | +0.0160 | -0.0063 | +0.0038 |
| bbc_dense_qwen3-0.6b | 2 | +0.0452 | +0.0416 | +0.0571 |
| bbc_dense_qwen3-0.6b | 3 | +0.0425 | +0.0383 | +0.0569 |
| bbc_dense_qwen3-0.6b | 4 | +0.0005 | +0.0026 | +0.0013 |
| bbc_dense_qwen3-0.6b | 5 | -0.0010 | -0.0035 | -0.0024 |
| bbc_dense_qwen3-1.7b | 1 | +0.0060 | +0.0096 | +0.0072 |
| bbc_dense_qwen3-1.7b | 2 | +0.0268 | +0.0170 | +0.0310 |
| bbc_dense_qwen3-1.7b | 3 | +0.0005 | +0.0047 | +0.0053 |
| bbc_dense_qwen3-1.7b | 4 | +0.0067 | +0.0003 | +0.0048 |
| bbc_dense_qwen3-1.7b | 5 | +0.0020 | +0.0009 | +0.0036 |
| bbc_dense_qwen3-4b | 1 | +0.0428 | +0.0364 | +0.0541 |
| bbc_dense_qwen3-4b | 2 | +0.0013 | +0.0015 | +0.0023 |
| bbc_dense_qwen3-4b | 3 | +0.0000 | +0.0000 | +0.0000 |
| bbc_dense_qwen3-4b | 4 | -0.0320 | -0.0678 | -0.0533 |
| bbc_dense_qwen3-4b | 5 | -0.0040 | +0.0041 | -0.0013 |

Final scores against k-means from the same initialization (logged values; mean over seeds).

| model | acc | kmeans_acc | d_acc | d_nmi | d_ari |
| --- | ---: | ---: | ---: | ---: | ---: |
| bbc_dense_lsa | 0.897 | 0.866 | +0.0316 | +0.0215 | +0.0384 |
| bbc_dense_qwen3-0.6b | 0.960 | 0.866 | +0.0948 | +0.0652 | +0.1055 |
| bbc_dense_qwen3-1.7b | 0.904 | 0.866 | +0.0380 | +0.0308 | +0.0468 |
| bbc_dense_qwen3-4b | 0.902 | 0.866 | +0.0364 | +0.0246 | +0.0445 |

Spearman correlation across all (model, seed) pairs at step 1; a descriptive number, not a test. The pooled correlation mixes between-model and within-model variation.

| step-1 measure | outcome | spearman (n=20) |
| --- | --- | ---: |
| jump_rel | d_step_acc | +0.42 |
| jump_rel | d_final_acc | +0.30 |
| jump_rel | d_final_nmi | +0.24 |
| drift_median | d_step_acc | +0.41 |
| drift_median | d_final_acc | +0.23 |
| drift_median | d_final_nmi | +0.19 |
| n_empty_replacement | d_step_acc | n/a |
| n_empty_replacement | d_final_acc | n/a |
| n_empty_replacement | d_final_nmi | n/a |
| frac_moved_replacement | d_step_acc | +0.60 |
| frac_moved_replacement | d_final_acc | +0.37 |
| frac_moved_replacement | d_final_nmi | +0.32 |

### Do the displayed (final-step) summaries describe the final partition?

Share of final summaries that are out of date: Jaccard between the members each summary was written from and the final members below the threshold, or its embedding nearest to another cluster's final center; `stale@t` is either condition. All seeds pooled; 0.5 is the documented convention, 0.3 and 0.7 show sensitivity.

| model | summaries | mean_jaccard | jaccard<0.3 | jaccard<0.5 | jaccard<0.7 | nearest_not_own | stale@0.3 | stale@0.5 | stale@0.7 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bbc_dense_lsa | 5 | 0.959 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| bbc_dense_qwen3-0.6b | 20 | 0.993 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| bbc_dense_qwen3-1.7b | 10 | 0.978 | 0 | 0 | 0 | 0.1 | 0.1 | 0.1 | 0.1 |
| bbc_dense_qwen3-4b | 5 | 0.782 | 0 | 0.2 | 0.2 | 0 | 0 | 0.2 | 0.2 |

Share stale@0.5 by summary step (summary of step j against the partition after its own block).

| model | 1 | 2 | 3 | 4 | 5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| bbc_dense_lsa | 0.120 | 0.000 | 0.000 | 0.000 | 0.000 |
| bbc_dense_qwen3-0.6b | 0.040 | 0.080 | 0.100 | 0.000 | 0.000 |
| bbc_dense_qwen3-1.7b | 0.000 | 0.120 | 0.000 | 0.067 | 0.100 |
| bbc_dense_qwen3-4b | 0.120 | 0.067 | 0.200 | 0.200 | 0.200 |
