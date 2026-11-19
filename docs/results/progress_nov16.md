# Progress summary for the Nov 16 submission

Issue #45 (tracker). This page condenses the detailed write-ups, one section per request from the professor's November feedback. Every number is copied from the linked document. Unless a line says otherwise: CLINC150, Qwen3 models, 5 seeds (0-4), one RTX 3060, paired by seed, 95% Student-t intervals over seeds (4 degrees of freedom, not corrected for multiple comparisons). Sizes are Qwen3 sizes; "old" is the October prompt (#31), "v2" is the clearer prompt (#46).

Evidence tags used below: **[exact]** a direct measurement of logged runs (the replay reproduces them), **[intervention]** the experimenter changed summary text or its use, **[association]** a descriptive relation in logged data. The only interventions in the project are #47's swaps and guarded run, and the prompt change, which is a multi-factor two-run intervention.

## Headline findings

1. Replacing the centroids with summaries raises the k-means objective by 72% (LSA) to 98% (old 4B) at step 1, Lloyd removes most of that within a couple of iterations, and yet 9% (LSA) to 45% (old 4B) of the points end in a different cluster than before the replacement. [exact]
2. At step 1 the old 4B's partition has lower ACC than plain Lloyd from the same state in 5 of 5 seeds (-0.0159), with 18.8 duplicate summaries and 10.8 emptied clusters per seed (1.7B: 0.8 and 0.6; its ACC is above plain Lloyd, +0.0106, 0 of 5 below). [exact]
3. Putting the 1.7B's summaries into the 4B's flagged clusters (duplicate or mentions the cluster; 43-56 of 150) raises step-1 ACC by +0.026 [+0.019, +0.034], 5 of 5 seeds, about all of the 4B-to-1.7B gap; the same swap into random unflagged clusters changes it by -0.002 [-0.012, +0.007]. [intervention, step 1 only]
4. Starting the flagged clusters from their k-means center at every step does not recover the 4B's final scores: ACC +0.009 [-0.006, +0.024] over the unguarded 4B, still 0.031 below k-means. [intervention, 5 steps]
5. Under the clearer prompt the 4B scores 0.568 ACC against 0.511 (+0.056 [+0.039, +0.074], 5 of 5 seeds) and the 0.6B gains +0.022 [+0.010, +0.033], the 1.7B is unchanged within noise (-0.007 [-0.023, +0.010]), and the size order is no longer detectable on ACC (0.563 / 0.563 / 0.568; the 4B keeps a small NMI edge of +0.006). [multi-factor two-run intervention]
6. Summary-quality scores do not rank final ACC across the seven model runs (coverage 0.49-0.69, ACC 0.511-0.570); within a run they track which members leave a cluster (rank correlation with nearest-summary share, the coverage measure, -0.78 / -0.72 / -0.83 for 0.6B / 1.7B / 4B), largely by construction. [association]
7. Whether a cluster's purity rises or falls after the replacement is not predicted by the summary scores once starting purity and size are controlled; starting purity separates the sign (step 1, against plain Lloyd: clusters with purity <= 0.4 gain +0.04 to +0.06 for the three October models, clusters above 0.9 lose 0.04 to 0.09). [association]
8. The cost counters have no counting bug (calls and input tokens exact; output tokens within 0.1%), every size sends about 1.1M input tokens per seed, and output tokens are 24-42% lower under the clearer prompt; on an idle card the same 150 prompts take 94 / 166 / 314 s for the 0.6B (batch 8) / 1.7B (batch 4) / 4B (batch 1), and the #31 step-1 seconds of seed 0 were inflated by 1.76 / 1.72 / 1.15, with the whole-run factor not measured. [exact]
9. Batch size changes the greedy summaries: at the logged batch size the regenerated summaries equal the logged ones (150 of 150 for all three sizes), but at batch 1 instead of the logged batch 25 of 150 (0.6B, logged batch 8) and 42 of 150 (1.7B, logged batch 4) differ. [exact]
10. On BBC (500 articles, TF-IDF) every summary method has a higher mean ACC than k-means (0.788 against 0.839-0.873), but 28 of 30 paired intervals include 0; the dense control is driven by two seeds with a bad start. [association, 5 seeds]
11. arXiv: the three baselines ran at full scale (3.0M abstracts, seed 0; ACC 0.260-0.275), and the 1.7B pilot and LSA ran end to end on a 200k subsample (k-SLMmeans ACC 0.266, k-means 0.274, LSA 0.269, one seed each, so no difference is claimed). The pilot's rate, measured on a shared machine, puts the #49 full summary run at about 3.5 GPU-hours as a ceiling. Section 5.

## 1. A summary replaces a centroid (#33, #47)

**What was done.** The logged CLINC150 runs (#31, plus the v2 4B) were replayed offline: every Lloyd block is re-run from the logged summaries, and the replay is exact (150 of 150 fits, 0 label mismatches). It adds a no-replacement counterfactual (plain Lloyd from the pre-replacement state). #47 then edits the 4B's step-1 start centers (swaps between the 4B and the 1.7B, with matched random controls) and runs a guarded 4B for five steps.

Step 1, means over 5 seeds ([`replacement_diagnostic.md`](replacement_diagnostic.md) Sections 3-8):

| Measure | LSA | 0.6B | 1.7B | old 4B | v2 4B |
| --- | ---: | ---: | ---: | ---: | ---: |
| Objective rise at the replacement | 0.72 | 0.78 | 0.95 | 0.98 | 0.70 |
| Points moved at the replacement / net after the block | 25% / 9% | 47% / 33% | 47% / 29% | 56% / 45% | 40% / 27% |
| Duplicate summaries per seed | 0 | 3.0 | 0.8 | 18.8 | 1.2 |
| Empty clusters after the replacement, per seed | 0 | 1.2 | 0.6 | 10.8 | 0.4 |
| ACC, logged minus plain Lloyd (seeds below) | +0.0051 (0/5) | +0.0016 (3/5) | +0.0106 (0/5) | -0.0159 (5/5) | +0.0024 (2/5) |
| Final summaries out of date (Jaccard < 0.5) | 0.5% | 29% | 30% | 55% | 25% |
| Final ACC minus k-means [95%] | +0.009 [+0.001, +0.017] | -0.010 [-0.018, -0.002] | +0.018 [+0.004, +0.033] | -0.040 [-0.058, -0.022] | +0.016 [+0.009, +0.023] |

The old 4B's step-1 deficit also holds with both sides run to convergence (-0.0138, 5 of 5 seeds), so it is not a fixed-budget artifact. Its re-encoding noise floor is 0.003 ACC on average (0.008 at most), so differences below that are not read.

The interventions ([`counterfactual_swaps.md`](counterfactual_swaps.md), [`summary_guard.md`](summary_guard.md)), paired by seed:

| Intervention | Change in ACC [95%] | Reading |
| --- | --- | --- |
| Step 1: 1.7B summaries into the 4B's flagged clusters | +0.0261 [+0.0185, +0.0337], 5/5 seeds | closes 99% of the gap to the 1.7B |
| Same, minus the matched control (random unflagged clusters) | +0.0285 [+0.0149, +0.0420] | the gain is specific to the flagged clusters |
| Step 1: 4B's flagged summaries into the 1.7B, minus control | -0.0248 [-0.0410, -0.0086] | the effect travels with the summary text |
| Step 1: flagged clusters keep their k-means center | +0.0064 [-0.0058, +0.0185] | not shown |
| Five steps: guarded 4B minus unguarded 4B (final) | +0.0093 [-0.0059, +0.0244], 4/5 seeds | not detectable |
| Five steps: guarded 4B minus k-means (final) | -0.0310 [-0.0429, -0.0190], 0/5 seeds | gap remains |

**What it shows.** [exact] A replacement is a large disturbance that Lloyd does not undo: the partition settles somewhere different, most for the old 4B. The old 4B's replacement has duplicate and cluster-mentioning summaries that give identical centers, emptied clusters and out-of-date summaries; the v2 4B looks like the 1.7B on these measures, except ACC against plain Lloyd (+0.0024, 2 of 5 seeds below, not distinguishable from 0; 1.7B +0.0106). [intervention] At step 1 the flagged summaries carry the difference between the 4B and the 1.7B.

**What it does not show.** The swaps cover step 1 only and one model pair; flagged clusters may also be harder clusters. The guard replaces a flagged summary with a k-means center, not a better summary, and acts on a third of the clusters, so it does not test the swap over five steps; an effect up to +0.024 is not excluded. Neither stage shows why the 4B's whole-run score is low. Objective jump size does not rank outcomes (1.7B and 4B jump alike and end on opposite sides).

**Pending.** The #33 replay for the v2 0.6B and 1.7B; BANKING77 (needs a re-run with #30 logging).

## 2. Does a clearer prompt change the 4B results? (#46)

**What was done.** One prompt, fixed and committed before any run (it asks for one new question in the same style, "write only the question", and bans mentioning the questions, a group, a cluster or a topic). All three sizes, seeds 0-4, same step-0 partitions, same batch sizes ([`prompt_test.md`](prompt_test.md) Section 8).

| Size | Final ACC old / v2 | v2 minus old [95%], seeds higher | v2 minus k-means [95%] |
| --- | ---: | --- | --- |
| 0.6B | 0.541 / 0.563 | +0.022 [+0.010, +0.033], 5/5 | +0.011 [+0.005, +0.017] |
| 1.7B | 0.570 / 0.563 | -0.007 [-0.023, +0.010], 1/5 | +0.012 [+0.005, +0.018] |
| 4B | 0.511 / 0.568 | +0.056 [+0.039, +0.074], 5/5 | +0.016 [+0.009, +0.023] |

The 4B mentions the cluster in 34% of summaries under the old prompt and 0% under the new one; its identical-summary groups at the final step go from 16-21 clusters per seed to 0-2. Size order, 4B minus 1.7B: old -0.059 [-0.072, -0.045], v2 +0.005 [-0.003, +0.012]. No v2 size is separated from LSA on ACC.

**What it shows.** The size comparison changes with the prompt: under the clearer prompt the 4B is no longer last and no size order is detectable on ACC and ARI. Between the two 4B runs the summary properties moved more than the cluster outcomes: members lost 0.44 to 0.24 at step 1, but the mean change in member purity at step 1 only from -0.032 to -0.009 (+0.023 [+0.007, +0.039]), and the share of helped clusters fell (14.3% to 10.8%) ([`synthesis.md`](synthesis.md) Section 2).

**What it does not show.** The prompt changed several things at once, was chosen on the 4B's surface counts, and was not tested part by part, so it does not isolate the cluster-talk failure (the 0.6B gained with only 8% cluster talk before). The summaries differ in every cluster. The clearer prompt raises verbatim copies of a member (v2 4B 12%, v2 0.6B 33%; old 1.4% and 14.6%), and whether copying contributes to the ACC gain was not tested. One dataset, 5 seeds; "not detectable" means not detectable with 5 seeds. Bank77 was not run under the clearer prompt. It measures no cost effect.

**Pending.** Seeds 5-9 (#36), the #33 replay of the v2 0.6B and 1.7B.

## 3. Summary-quality evaluation (#34)

**What was done.** Four families scored separately on 27,790 summaries (26,250 CLINC150, 1,540 BANKING77; seven CLINC150 runs): coverage of cluster members, genericity, unsupported information (lexical, so it overstates), and fluency proxies. LSA summaries act as a control. Last summary step, CLINC150 ([`summary_quality.md`](summary_quality.md) Section 3):

| Run | Nearest-summary share | Specificity margin | Generic | Unsupported lemmas | Not fluent | Members lost | Final ACC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| LSA | 0.796 | 0.250 | 0% | 0.000 | 1% | 2% | 0.560 |
| 0.6B | 0.607 | 0.146 | 17% | 0.128 | 29% | 24% | 0.541 |
| 1.7B | 0.614 | 0.112 | 21% | 0.304 | 9% | 25% | 0.570 |
| old 4B | 0.494 | 0.003 | 47% | 0.454 | 35% | 41% | 0.511 |
| v2 0.6B | 0.689 | 0.204 | 6% | 0.013 | 39% | 12% | 0.563 |
| v2 1.7B | 0.603 | 0.122 | 19% | 0.296 | 2% | 21% | 0.563 |
| v2 4B | 0.672 | 0.153 | 17% | 0.140 | 43% | 20% | 0.568 |

**What it shows.** [association] The old 4B is worst on coverage, margin, duplicates and unsupported content and lowest in ACC. Across all seven runs the scores do not rank ACC: the v2 runs score very differently and share an ACC. Members whose intent the summary does not cover leave much more often (old 4B 75% against 14% for covered members), which is partly built in. Fluency proxies are not aligned with the other families and add nothing beyond coverage in predicting outcomes ([`synthesis.md`](synthesis.md) Section 4). Fluent, well-formed summaries ("What is the main theme of the cluster?") can be useless representatives.

**AI-rater stand-in (not a human rating).** Two Claude Sonnet 5.5 instances each rated the blank audit sheets (40 summaries per dataset) blind to method and scores. Their agreement with each other is high (kappa 0.66-1.00 on CLINC150; BANKING77 generic 0.00 from one label), which is as consistent with shared bias as with a clear rubric. Against the automatic flags: not fluent kappa 0.72-0.87; low coverage 0.30 on CLINC150; unsupported -0.05 / -0.09 on CLINC150 (the flag is lexical, the raters accept paraphrase). This is a first look at where flags and a careful reading agree, **not** a validation of the scores and not a hand-check result.

**What it does not show.** How the scores relate to clustering outcome beyond association (#47, #50). The v2 runs are not in the audit sheets.

**Pending.** The human hand check on the blank sheets (the student's job); its agreement numbers replace the stand-in.

## 4. Cost verification and timing (#35)

**What was done.** Part 1: the logged counters were rebuilt from the logged partitions and summaries with the Qwen3 tokenizer, no GPU ([`cost_verification.md`](cost_verification.md)). Part 2: every run since logs a GPU idle check (`gpu.json`) and a monitor (`gpu_samples.csv`). Part 3: one fixed workload re-timed on an idle-checked card ([`cost_timing.md`](cost_timing.md)).

**Results.** [exact] No counting bug. Calls per step and per run, input tokens, truncated clusters and dropped texts match exactly at batch sizes 8, 4 and 1; output tokens match within 0.1% (at most 15 tokens per seed, cause not isolated). `summarizer_seconds` is a wall-clock reading taken after the GPU work finishes; for the language models it is 99.1-99.7% of total seconds. Per seed, from the #31 and #46 runs ([`prompt_test.md`](prompt_test.md) Section 8.4):

| Run | Calls | Input tokens | Output tokens | Summarizer s |
| --- | ---: | ---: | ---: | ---: |
| LSA | 636 | 0 | 0 | 15 |
| 0.6B old / v2 | 707 / 689 | 1.11M / 1.12M | 10.2k / 7.8k | 896 / 373 |
| 1.7B old / v2 | 702 / 701 | 1.10M / 1.14M | 18.3k / 11.2k | 1,239 / 737 |
| 4B old / v2 | 714 / 698 | 1.12M / 1.13M | 15.6k / 9.1k | 1,855 / 1,094 |

Tokens do not depend on the card: output tokens fall 24% / 39% / 42% under the clearer prompt (0.6B / 1.7B / 4B). Truncation touches about 1% of calls; `rq2_truncation_check.md` (#37) concludes the #15 numbers stand with a caveat and a re-run is optional (prepared, not run).

**What it does not show.** The logged seconds above are not a cost comparison: the #31 seconds were taken on a shared card, batch sizes 8 / 4 / 1 mix model size with batching, the v2 seconds are not comparable with the old ones, and the v2 1.7B's later seeds ran about 1.6x slower with a foreign GPU process seen at the end. No time saving from the prompt is claimed. The clean seconds are in the next subsection.

### Fixed-workload timing (#35 part 3, [`cost_timing.md`](cost_timing.md))

**What was done.** The 150 prompts of seed 0's first summary step (234,011 input tokens, identical for every size) were re-summarized on an idle-checked RTX 3060 (checked before each run, sampled every 5 s during it). Each setting had 1 warm-up pass and 3 timed repeats; repeats differ by at most 8% and gave identical summaries. Scope: 3 repeats, one workload, one card.

| Model, batch | s per call | Output tok/s | Total s, median (range) | Reserved GB |
| --- | ---: | ---: | --- | ---: |
| 0.6B, batch 1 | 0.89 | 16.7 | 133 (130-135) | 1.85 |
| 0.6B, batch 8 (#31) | 0.63 | 22.8 | 94 (94-95) | 6.11 |
| 1.7B, batch 1 | 1.74 | 14.5 | 261 (242-262) | 4.24 |
| 1.7B, batch 4 (#31) | 1.11 | 22.8 | 166 (160-167) | 6.30 |
| 4B, batch 1 (#31) | 2.10 | 10.1 | 314 (309-318) | 9.12 |

**Size and batch size.** [exact, this workload]
- At batch 1 the 1.7B takes 1.96 times and the 4B 2.36 times the 0.6B's time on the same prompts; output tokens per second are 16.7, 14.5 and 10.1. Seconds per call also depend on summary length (2,225, 3,795 and 3,160 output tokens), so tokens per second is the fairer size comparison. The 4B fits the card only at batch 1.
- Batching matters about as much as size here: the 1.7B goes from 261 s at batch 1 to 166 s at batch 4 (1.57 times faster), the 0.6B from 133 s to 94 s at batch 8 (1.41 times). The cost is memory (reserved 1.7B 4.2 to 6.3 GB, 0.6B 1.9 to 6.1 GB). At each model's own #31 batch size the per-call seconds are not in size order (0.63, 1.11, 2.10), so #31 per-call seconds mix the two effects.

**Inflation of the #31 timings, step 1 of seed 0 only.** The #31 logged step-1 seconds against the fixed workload at the same batch size: 0.6B 165.9 against 94.5 s (1.76), 1.7B 286.8 against 166.3 s (1.72), 4B 360.8 against 314.4 s (1.15). This is one step of one seed per size, one logged measurement against three repeats; it replaces the single BANKING77 estimate of about 1.7x for step 1 (the 0.6B and 1.7B agree with it, the 4B does not; why is a guess). **The whole-run inflation factor is not measured.** Later steps of the same #31 runs were slower per output token than step 1 (the 4B about 1.3 times the idle rate at steps 2-5, the 0.6B up to 2.6 times at step 5), so the load varied within a run and step 1 is the least inflated step of the 0.6B and 4B runs. A rough projection (calls times idle seconds per call) gives about 2.1, 1.8 and 1.3 for the whole seed; it is not a measurement and is not used to correct the #31 seconds.

**Determinism.** [exact] Greedy decoding, so a different output is a different computation. At each size's logged batch size the regenerated summaries equal the #31 ones in 150 of 150 clusters (different day and process), and repeats of one setting are identical. At batch 1 instead of the logged batch, 25 of 150 (0.6B against batch 8) and 42 of 150 (1.7B against batch 4) summaries differ; the output-token totals barely move (2,225 against 2,157; 3,795 against 3,786). A model at two batch sizes is therefore two slightly different summarizers, and the #31 size comparison at batch 8 / 4 / 1 carries a small batch effect on the summaries as well as on the seconds. This counts differing strings, not quality; whether the differing summaries cluster differently was not measured.

**What it does not show.** Nothing here measures energy, price or summary quality; a different card, inference server or quantization would change the seconds and possibly the ratios between sizes. The v2 rows of the per-method cost table in `cost_timing.md` were idle-checked at start, but the v2 1.7B was not clean during its run.

**Pending.** The full-seed re-time (one whole #31 seed per size on an idle card; deferred, so the whole-run inflation stays unmeasured); the effect of batch-induced summary differences on clustering; the optional pricing comparison (#10).

## 5. Large-scale (arXiv) and high-dimensional (BBC) datasets (#48, #18)

### BBC News, 500 articles, k = 5, 5 seeds ([`bbc.md`](bbc.md))

**What was done.** k-means, LSA and Qwen3 0.6B / 1.7B / 4B on a TF-IDF space (784 terms, the main variant) and a dense MiniLM control, with the #31 protocol; the replacement diagnostic replays all runs exactly (TF-IDF 120 of 120 fits, dense 85 of 85).

| Method (TF-IDF) | ACC | Paired ACC minus k-means [95%], seeds higher |
| --- | ---: | --- |
| k-means | 0.788 +- 0.080 | |
| LSA | 0.839 +- 0.033 | +0.051 [-0.020, +0.121], 4/5 |
| 0.6B | 0.851 +- 0.022 | +0.063 [-0.053, +0.179], 3/5 |
| 1.7B | 0.873 +- 0.021 | +0.085 [-0.009, +0.178], 5/5 |
| 4B | 0.854 +- 0.022 | +0.066 [-0.027, +0.159], 4/5 |

**What it shows.** Summary methods do not lose to k-means here, but only 2 of 30 paired intervals exclude 0 (1.7B against k-means in ARI, 1.7B against LSA in NMI), and size does not order the models. In the dense space the means (k-means 0.866, LSA 0.897, 0.6B 0.960, 1.7B 0.904, 4B 0.902) are set by seeds 0 and 2, whose shared step-0 partition merges business and tech; on the other three seeds all methods are within 0.008. The 0.6B's lead is one seed's outcome. A summary sits about one RMS radius from the centroid it replaces (0.98-1.08; CLINC150 0.89-1.08) but much farther in cosine (0.17-0.43 against 0.67-0.80); no duplicates, no empty clusters, no summary mentions the cluster. Cost: about 24 calls and 84-87k input tokens per seed, 27 / 46 / 87 s for 0.6B / 1.7B / 4B.

**What it does not show.** That summaries beat numerical centroids here, or why BBC differs from CLINC150 (different data, embedding, prompt and 30-word member cut). No cluster-level analysis (5 clusters per seed).

**Pending.** The member-selection ablation (random subset of whole articles instead of the first 30 words) was not run.

### arXiv (3,035,644 abstracts, k = 171) ([`arxiv_status.md`](arxiv_status.md))

Run on Nov 16, one seed (0) each, as one queue step (about 18:00 to 19:41). One seed means no intervals, and none of the gaps below is evidence of a difference between methods. The three jobs overlapped on one machine, so every time here is an upper bound, not an idle-machine figure. Details: `arxiv_status.md` Sections 2.4, 5.1 and 5b.1.

**Full-scale baselines** (3,035,644 abstracts, k = 171, CPU):

| Baseline | ACC | NMI | ARI | runtime |
| --- | ---: | ---: | ---: | ---: |
| minibatchkmeans | 0.2600 | 0.5304 | 0.1636 | 134 s |
| seqminibatchkmeans | 0.2752 | 0.5297 | 0.1758 | 54 s |
| kmeans | 0.2645 | 0.5347 | 0.1643 | 747 s |

Peak RAM was 9.5 GB at the kmeans row: 2.5 GB above the estimate and under the 10 GB stop rule. The memory guard did not fire. Seeds 1-2 were not run.

**200k subsample** (k = 168, ten 20,000-row batches, two summary steps per batch; all five rows on the same rows):

| Method | ACC | NMI | ARI | runtime |
| --- | ---: | ---: | ---: | ---: |
| minibatchkmeans | 0.2468 | 0.5301 | 0.1534 | 84 s |
| seqminibatchkmeans | 0.2536 | 0.5264 | 0.1682 | 2 s |
| kmeans | 0.2737 | 0.5421 | 0.1713 | 118 s |
| k-SLMmeans (Qwen3-1.7B) | 0.2663 | 0.5355 | 0.1746 | 5,885 s |
| k-NLPmeans (LSA) | 0.2694 | 0.5383 | 0.1809 | 3,358 s |

- **What it shows:** the summary pipeline runs end to end at 200k. On one seed, k-SLMmeans is below k-means on ACC and NMI and above it on ARI, so this is not evidence for or against the summaries at this scale. Whether summaries move the centroids at scale is not measured here.
- **Cost:** the run did not log the #30 cost fields (calls, tokens, summarizer seconds). All 168 clusters had a summary in all 10 batches, so 3,360 calls were scheduled. That gives 1.75 s per scheduled call (1.7B, summarizer batch 4), an upper bound, because the full baselines and then LSA ran alongside the pilot.
- **#49 budget:** at that rate the full summary run (1.7B, 150,000-row batches, two steps, at most 7,182 calls) is about 3.5 GPU-hours as a ceiling for one seed. This replaces the earlier 2.9 h idle estimate. The earlier rule was to drop to one summary step above about 1.7 s per call. The measured 1.75 s sits on that line and is inflated, so an idle-card rerun of a few batches should decide it.
- **Truncation:** one warning says a cluster's prompt went over the 4,096-token input limit and 1 of 10 texts was dropped. The warning is shown only once per summarizer instance, so the real count may be higher.
- **LSA:** the GPU was busy with the pilot during its idle check, so its time (55 min of sentence preprocessing, 39 s of clustering) is inflated. Peak RAM was 8.1 GB, against a 3 GB estimate; this was not investigated.

## Reading across the requests (#50, preliminary)

On CLINC150 a summary changes which members a cluster keeps in proportion to how well it covers them; whether that helps depends on the cluster's starting purity and is not predicted by the quality scores. The old 4B's low score went with duplicate and cluster-mentioning summaries; at step 1 swapping them for a better model's summaries closes the gap, but removing them over five steps does not recover the final score. Under the clearer prompt the 4B's drop is gone and the size order is no longer detectable on ACC; with more verbatim copies and better scores, the data cannot separate the wording from the copying. Details and limits: [`synthesis.md`](synthesis.md) Section 9.

## Pending / open items

- Human hand check for #34: the student's job. The AI-rater results above are a stand-in, not a validation.
- #49, the arXiv full summary run (Nov 30), with the cost fields logged and on an idle card; seeds 1-2 of the full-scale baselines.
- #33 replay of the clearer-prompt 0.6B and 1.7B (the synthesis uses them at method level only).
- The #35 full-seed re-timing (deferred; the whole-run inflation of the #31 seconds is unmeasured).
- BBC member-selection ablation.
- #37 re-run on the #31 protocol (optional; about 3.4-5.8 GPU-hours, not run).
- Seeds 5-9 and Bank77 under the clearer prompt (#36); Nov 17 review.

## Caveats that apply throughout

- Five seeds: intervals have 4 degrees of freedom and are wide; no multiplicity correction (about 100 comparisons in #47 alone, about 120 strata in #50). A lone interval that excludes 0 is weak evidence.
- One GPU (RTX 3060), one embedding encoder, one model family (Qwen3), one dataset for most claims (CLINC150); BBC has 5 clusters per seed; arXiv has one seed per method, so its scores are not comparisons.
- Timing: the #31 seconds were inflated at step 1 of seed 0 by 1.76 / 1.72 / 1.15 (0.6B / 1.7B / 4B), the whole-run factor is not measured and later steps ran slower; the fixed-workload timings are 3 repeats of one workload on one card; batch sizes 8 / 4 / 1 mix size with batching and change the greedy summaries (25 of 150 and 42 of 150 differ for the 0.6B and 1.7B at batch 1); v2 seconds are not comparable with old ones and the v2 1.7B is not a clean timing; the guarded run overlapped niced CPU jobs for about its first hour; BBC CPU parts may be slightly inflated.
- Replay exactness depends on re-embedding the summaries on the original device: a CPU encode differs by about 1e-6 per row and changes up to 9% of the old 4B's labels after a block.
- Everything outside #47 and the prompt change is association; summary quality, geometry and members lost are mechanically related.
- #34 scores have no human validation yet; the unsupported and generic flags are loose, and the AI-rater stand-in (two Claude Sonnet 5.5 instances) is not a human rating.
