# arXiv at full scale: status for the November 16 submission (#48)

This is a progress status, not a results report. Every score below is from one seed, so there are no intervals, and none of the gaps between methods is evidence of a difference.

**Status (Nov 16, evening).** Run tonight, one seed (0) each, on the same code (git 341e420), as one queue step starting about 18:00 and ending 19:41:

- the three baselines at full scale (3,035,644 abstracts, k = 171), section 2.4: finished;
- the pilot, k-SLMmeans with Qwen3-1.7B on the 200k subsample, with the three baselines on the same 200k rows, section 5.1: finished;
- LSA (k-NLPmeans) on the 200k subsample, section 5b: finished.

The pipeline ran end to end at 200k, and the cheap methods ran at 3.0M rows. The summary method has not been run at full scale, and nothing here says how it behaves there (that is #49). The three jobs overlapped on one box, so every time in this file is an upper bound, not an idle-machine figure (section 5.1).

## TL;DR

- **Baselines at full scale** (3,035,644 abstracts, k = 171), seed 0 only, ran as a CPU job (`configs/arxiv_full_baselines.yaml`, section 2.4): ACC 0.260 / 0.275 / 0.264 for minibatchkmeans / seqminibatchkmeans / kmeans, 54 s to 12.4 min each, `peak_rss_mb` 9,491 at the `kmeans` row (the estimate was about 7 GB, the stop rule 10 GB; it ran beside the pilot). The memory guard did not fire. Seeds 1-2 were not run. Full-batch k-means fits the 15 GB box only with `copy_x: false`; with sklearn's default copy it would need 11-13 GB and is not safe.
- **LSA (k-NLPmeans) should use the 200k subsample, not the full corpus.** At full scale the sentence embeddings alone are 29 GB in float32 and segmentation is about 10 hours on one CPU core.
- **The current streaming schedule is out of reach**: up to 259,920 summarizer calls, about 74 GPU-hours with Qwen3-0.6B and 103 with Qwen3-1.7B.
- **Recommended for the full summary run (#49): Qwen3-1.7B, 150,000-row batches (21 batches), two summary steps per batch.** At most 7,182 calls, **2.9 GPU-hours if the card is idle, up to 4.9 if it is as slow as during the CLINC150 runs.** The idle figure divides the logged rates by 1.7, which rests on a single BANKING77 re-timing (185 s against 105-115 s), so treat the range, not 2.9 alone, as the budget. **Update (Nov 16):** the pilot measured 1.75 s per scheduled call on a shared box, which puts this schedule at about 3.5 GPU-hours as a ceiling for one seed (section 5.1); 2.9 h is no longer supported.
- **LSA** (`configs/arxiv_sub200k_lsa.yaml`): 200k subsample, ran in 55 min of sentence preprocessing plus 39 s of clustering (estimate 45-80 min), ACC 0.269 / NMI 0.538 / ARI 0.181. Its GPU check found the card busy (the pilot), so its timings are inflated.
- **Pilot** (`configs/arxiv_sub200k_pilot.yaml`): the same model and steps on the 200k subsample with 20,000-row batches, at most 3,360 calls. k-SLMmeans reached ACC 0.266 / NMI 0.535 / ARI 0.175 in 5,885 s, against 0.274 / 0.542 / 0.171 for k-means on the same rows (n = 1 each; not a difference). That is 1.75 s per scheduled (maximum) call, and it is an upper bound on the idle-card cost because CPU jobs ran alongside. At that rate the #49 schedule is at most about 3.5 GPU-hours, not 2.9 (section 5.1).

## 1. What exists

Data (#17, PR #27), built by `scripts/prepare_arxiv.py` from the `librarian-bots/arxiv-metadata-snapshot` revision recorded in `data/arxiv/manifest.json`:

| | |
| --- | --- |
| Abstracts | 3,035,644 after filtering (3,205,432 read; 5,587 withdrawn, 163,016 shorter than 50 words, 1,185 duplicates dropped) |
| Labels | 171 primary categories (38 archives); the 200k subsample (seed 0) contains 168 of them |
| Vectors | `all-MiniLM-L6-v2`, 384-d, normalized, stored as a float16 memmap (2.3 GB); 4.7 GB as float32 |
| Text | mean 152 words, 210 Qwen3 tokens per abstract (sample of 2,000 from the subsample) |

The 20k smoke run (first 20,000 rows of the 200k subsample, 149 clusters, batches of 5,000, Qwen3-0.6B at batch size 8, seed 0, `eval_assign: lloyd1`):

| Method | ACC | NMI | ARI | time |
| --- | ---: | ---: | ---: | ---: |
| MiniBatchKMeans | 0.2327 | 0.5269 | 0.1238 | 0.9 s |
| Sequential mini-batch k-means | 0.2553 | 0.5231 | 0.1391 | 0.3 s |
| k-means | 0.2462 | 0.5362 | 0.1315 | 1.3 s |
| k-SLMmeans (Qwen3-0.6B) | 0.2595 | 0.5304 | 0.1358 | 2,938 s (49 min) |

One seed, a non-random prefix of the subsample (file order), so these say only that the pipeline works and the methods are in the same range; they support no claim about which is better. The run predates the cost fields (#30) and the summary-distance fix (#29), so its call count and distance columns are not usable. Its runtime is used below as one calibration point.

## 2. Full-scale baselines

`configs/arxiv_full_baselines.yaml`: the three `run_streaming.py` baselines, seeds 0-2, `max_batch_size: 10000` (the batch size of `seqminibatchkmeans` and of `minibatchkmeans`), no summarizer, no GPU.

### 2.1 Changes this needed

- A config without a `summarizer` block is baseline-only: no schedule, embedder object, summarizer or sentence corpus is built, and the summary-method keys are not required. With a `summarizer` nothing changes (the same keys are required, the typo guard is intact).
- `dataset.load_texts: false` skips the abstracts. At full scale they are about 3 GB of Python strings that the baselines never read. The arXiv loaders return `""` for every text and keep the labels and vector rows.
- Every metrics row now logs `peak_rss_mb`, the process high-water mark after that method (so it never decreases within a run).
- New `summary_every` for the summary method, see section 4. With `summary_every > 1` the last batch may be skipped; the summary-distance columns (`sum_cen_dist`, `sum_sum_dist`) then compare the last *summarized* batch's summaries with the end-of-stream centroids, not the final batch's.

### 2.2 Peak RAM

The box has 15 GB (about 12 GB available when idle; the Windows side and other jobs take the rest). Estimates, not measurements at full scale:

| Piece | Size | Notes |
| --- | ---: | --- |
| Interpreter, numpy, sklearn, torch imports | ~1.0 GB | measured: 0.95 GB RSS after imports |
| Embeddings as float32 | 4.7 GB | 3,035,644 x 384 x 4 B; materialized once from the float16 memmap |
| Labels, oracle centroids, metrics | < 0.1 GB | |
| Load transient | + up to 2.3 GB | file-backed memmap pages, reclaimable, released after the conversion |

The logged `peak_rss_mb` can read higher than these steady figures, about 7.5-8 GB at load: `ru_maxrss` counts mapped file pages, and the float16 mapping is touched (clean, reclaimable pages, up to 2.3 GB) while the float32 array fills. `oracle_centroids` adds small transients (a copy of each class's rows, at most about 0.15 GB for the largest class). The rule stays: stop if the first `kmeans` row reads above about 10 GB.

**The vectors cannot stay memory-mapped.** `cache.dataset_embeddings` reads the float16 memmap and converts it to a float32 array in one step, which is the 4.7 GB. That is necessary: sklearn accepts float32 or float64 only, and given float16 it upcasts to float64 (9.3 GB). The memmap is used only so the conversion streams from disk.

| Baseline | Peak RAM (estimate) | Basis |
| --- | ---: | --- |
| `seqminibatchkmeans` | ~5.7-6 GB | X + one 10k-row batch; `partial_fit` copies nothing else |
| `minibatchkmeans` | ~6-7 GB | X + 30k-row init sample + sklearn's chunked distance buffers (capped by `working_memory`, 1 GiB) |
| `kmeans`, default | ~11-13 GB | X + a second 4.7 GB centered copy (`copy_x=True`) + buffers. Not safe in 12 GB. |
| `kmeans`, `copy_x: false` | ~7 GB | centers X in place and restores it; exact up to float32 rounding (~1e-7 per value) |

Checked at small scale only (`tracemalloc`, synthetic 40k x 384 float32): default `KMeans` allocates one extra copy of X, `copy_x=False` allocates none beyond the buffers, and the mini-batch variants stay near X. The config therefore uses `kmeans: {copy_x: false}`, so no baseline is dropped or chunked. The first thing to look at when it runs is `peak_rss_mb` after the first `kmeans` row; if it passes about 10 GB, stop. A slice check (3,000 rows, `load_texts: false`, `copy_x: false`) ran through the real memmap and loader without problems.

The metrics code is not a memory risk: `cluster_metrics` loops over the 3M assignments in Python (seconds) and builds a 171 x 171 confusion matrix.

### 2.3 Runtime

Extrapolated from the smoke run's baseline timings (20k rows, k = 149) by work: scaling by rows x k is 152 x 1.15 = 174x. The box was shared with other jobs while this was prepared (load average 17), so a clean-box run may be faster.

| Baseline | Smoke | Full scale, per seed | Reasoning |
| --- | ---: | ---: | --- |
| `seqminibatchkmeans` | 0.34 s | ~1-3 min | one pass, no convergence loop: 0.34 s x 174 = 1 min, plus labelling |
| `minibatchkmeans` | 0.89 s | ~2-13 min | the work per step is fixed; the step count depends on early stopping (upper bound `max_iter` = 100 epochs = 30,356 steps at about 25 ms) |
| `kmeans` | 1.29 s | ~4-30 min | one Lloyd iteration is 394 GFLOP; same iteration count as the smoke run gives 3.7 min, a few times more iterations is typical at 150x the rows |

Three seeds: about 45-60 minutes nominal, about 2.5 hours worst case, plus a few minutes to read 2.3 GB and convert it. Run seed 0 first (`--set seeds=[0]`), check the RSS and time, then the other two.

### 2.4 Results (seed 0)

Run: `scripts/run_streaming.py configs/arxiv_full_baselines.yaml --set 'seeds=[0]'`, 3,035,644 abstracts, k = 171, `max_batch_size` 10,000, started 17:59, finished about 18:14, exit code 0. One seed, so no intervals.

| Baseline | ACC | NMI | ARI | runtime | `peak_rss_mb` (after the row) | estimate in 2.2 / 2.3 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `minibatchkmeans` | 0.2600 | 0.5304 | 0.1636 | 134.4 s | 6,688 | 6-7 GB; 2-13 min |
| `seqminibatchkmeans` | 0.2752 | 0.5297 | 0.1758 | 53.5 s | 6,688 | 5.7-6 GB; 1-3 min |
| `kmeans` (`copy_x: false`) | 0.2645 | 0.5347 | 0.1643 | 746.8 s (12.4 min) | 9,491 | about 7 GB; 4-30 min |

- **Runtimes** fall inside the estimated ranges (seqminibatchkmeans at the low end, kmeans in the lower half).
- **Peak RAM:** `peak_rss_mb` is the process high-water mark, so the first two rows share one value. The 6,688 MB at the first row is inside the 7.5-8 GB load allowance. The 9,491 MB at the `kmeans` row is 2.5 GB above the 7 GB estimate and under the 10 GB stop rule. The cause was not investigated, so the 7 GB estimate for `copy_x: false` is too low by about that much.
- **Memory guard:** `results/runq/logs/memguard.log` shows `guard start` at 18:01:24 and `guard end` at 18:15:15, with no kill and no low-memory line. The job ended on its own, exit code 0.
- **Not run:** seeds 1-2 and the 150k-batch sequential baseline from section 6.
- **Reading:** the three baselines are within 0.015 ACC and 0.005 NMI of each other on one seed. The full-scale numbers are not comparable with the 200k numbers below (different data, k = 171 against 168, and `seqminibatchkmeans` used 10k-row batches here and 20k there).

## 3. LSA (k-NLPmeans) feasibility

k-NLPmeans needs every abstract split into sentences, and every sentence embedded (`SentenceCorpus.build`). Measured on 2,000 random abstracts of the subsample (`scripts/estimate_stream_cost.py --measure --lsa`, spaCy `en_core_web_sm` on one CPU core, MiniLM tokenizer), and extrapolated:

| Quantity | Sample | 200k subsample | 3,035,644 (full) |
| --- | ---: | ---: | ---: |
| Sentences per abstract (kept, >= 5 tokens) | 6.31 (p5-p95: 3-11) | 1.26 M sentences | 19.2 M sentences |
| spaCy segmentation | 73-90 abstracts/s | 37-46 min | 9.4-11.5 h |
| MiniLM sentence embedding, by tokens | 234 tokens per abstract's sentences vs 200 for the abstract | ~5 min | ~1.4 h |
| ... pessimistic, by rows (725 rows/s) | | ~29 min | 7.3 h |
| Sentence embeddings, float32 | | 1.9 GB | 29.4 GB |
| Sentence text | 166 chars each | 0.2 GB | 3.2 GB (about twice that as Python strings) |

The embedding time by tokens takes the 725 abstracts/s measured for the corpus (manifest.json) as a token rate (about 145k tokens/s); sentences are short, so per-row speed would be higher. Both ends are given. Not measured: the GPU embedding, and spaCy with several processes (`n_process` > 1 should divide segmentation roughly by the process count, at some RAM per process).

**Recommendation: run LSA on the 200k subsample.** At full scale the sentence corpus does not fit in RAM (`SentenceCorpus.build` encodes all sentences in one call and keeps the float32 matrix; the cache then writes an `.npz` and a JSON of all sentences), segmentation alone is most of a working day on one core, and it would need new chunked/float16-memmap code. The 200k subsample costs under an hour of preprocessing and 2 GB, and is the same subsample the pilot uses, so LSA, the pilot and the baselines on the subsample are directly comparable. Say so in the report: LSA is run at 200k, not at 3.0M.

## 4. Cost of the summary methods

### 4.1 What a run costs

`mini_batch_summary_kmeans` runs a whole summary schedule on every batch. The summarizer is called once per non-empty cluster per summary step (a memo-cache hit or an empty cluster is free, so the call counts below are upper bounds):

    calls <= ceil(ceil(N / batch) / summary_every) x k x summary steps

For arXiv: N = 3,035,644 and k = 171. A call sends 10 abstracts (`force_context_length: 10`).

**Input tokens per call.** Measured on the sample with the Qwen3 tokenizer and the exact `HFSummarizer` prompt: 53 tokens of template, system prompt, task prompt and the `Topic:` prefill, plus 210 tokens per abstract and one newline each, so 53 + 10 x 211 = 2,163 tokens. Rendering 300 random 10-abstract prompts gave a mean of 2,134 (max 3,091, none near the 4,096 limit and none truncated). The CLINC150 prompts averaged about 1,570 tokens.

**Rate per input token.** From the CLINC150 table (`clinc150_summarizers.md` section 3): summarizer seconds divided by input tokens, at each size's logged batch size (8 / 4 / 1): 0.805, 1.124 and 1.656 ms per token. Those runs shared the GPU and were about 1.7x slow, so the estimator divides by 1.7 (`--gpu-slowdown`) to get an idle-card figure: **0.473, 0.661 and 0.974 ms per input token** for 0.6B / 1.7B / 4B. This is a single all-in rate (prefill, decoding of the roughly 15-25 output tokens, padding, tokenization), not a split into prefill and decode, because the data to separate them do not exist yet; the pilot will provide it.

**Check against the smoke run.** Qwen3-0.6B, 4 batches x 149 clusters x 5 steps = at most 2,980 calls at 2,163 tokens: 3,049 s predicted, 2,938 s measured (+4%). The smoke call count is an upper bound, and its GPU load is unknown, so the agreement is a sanity check on the order of magnitude, not a validation. The check assumes all 2,980 calls were made at 2,163 tokens (an upper bound; the run predates the cost fields, so the real count is unknown), compares against the run's total runtime rather than its summarizer seconds, and the smoke run's GPU load is unknown. It is an order-of-magnitude sanity check only.

### 4.2 Options

New code makes (c) possible: `mini_batch_summary_kmeans(summary_every=m)` runs the summary schedule only on batches 0, m, 2m, ... (the first batch is always summarized). The other batches run plain k-means from the carried centroids with the schedule's whole `max_iter` budget in one fit and make no calls. The default `summary_every=1` is unchanged and byte-identical. (b) and (d) need no code (`n_summaries`, `max_batch_size`).

GPU-hours on an idle card (bold = within 4 h); `scripts/estimate_stream_cost.py`:

| Option | batches | summarized | calls (max) | input tok/call | Qwen3-0.6B | Qwen3-1.7B | Qwen3-4B |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| (a) current: 10k batches, 5 steps, every batch | 304 | 304 | 259,920 | 2,163 | 73.9 | 103.3 | 152.2 |
| (b) one summary step per batch: 10k batches | 304 | 304 | 51,984 | 2,163 | 14.8 | 20.7 | 30.4 |
| (c1) 10k batches, 5 steps, every 20th batch | 304 | 16 | 13,680 | 2,163 | **3.9** | 5.4 | 8.0 |
| (c2) 10k batches, 1 step, every 4th batch | 304 | 76 | 12,996 | 2,163 | **3.7** | 5.2 | 7.6 |
| (d1) 100k batches, 5 steps, every batch | 31 | 31 | 26,505 | 2,163 | 7.5 | 10.5 | 15.5 |
| (d2) 100k batches, 2 steps, every batch | 31 | 31 | 10,602 | 2,163 | **3.0** | 4.2 | 6.2 |
| (d3) 100k batches, 1 step, every batch | 31 | 31 | 5,301 | 2,163 | **1.5** | **2.1** | **3.1** |
| (d4) 150k batches, 2 steps, every batch | 21 | 21 | 7,182 | 2,163 | **2.0** | **2.9** | 4.2 |
| (d5) 250k batches, 2 steps, every batch | 13 | 13 | 4,446 | 2,163 | **1.3** | **1.8** | **2.6** |

If the card is as slow as during the CLINC150 runs (`--gpu-slowdown 1`), multiply by 1.7: (d4) becomes 3.5 / 4.9 / 7.1 h, (d3) 2.6 / 3.6 / 5.3 h. The CPU k-means time is separate: at most 0.44 h in total for any option (every batch running all 120 Lloyd iterations at an assumed 30 GFLOP/s, independent of the batching; warm-started batches stop earlier). It is an assumption, not a measurement.

### 4.3 Recommendation

**Qwen3-1.7B, `max_batch_size: 150000` (21 batches), `schedule: {type: fixed, n_summaries: 2, max_iter: 120}`, `summary_every: 1`, `force_context_length: 10`, summarizer batch size 4: at most 7,182 calls, about 2.9 GPU-hours idle-equivalent (4.9 as logged), one seed.**

- **Why 1.7B:** it is the size the issue calls best on CLINC150, and it costs 1.4x the 0.6B and 0.68x the 4B per token. The 4B needs 4.2 h for the same schedule on an idle card (7.1 as logged).
- **Why large batches rather than every m-th batch:** cost depends on the number of summarized batches x steps, not on the rows. Big batches give each cluster hundreds of members per batch (about 880 at 150k) and every batch is summarized; (c) keeps small noisy batches and uses summaries on a few of them, so most of the stream never sees a summary. (c) also gives 4 to 20 plain batches in a row.
- **Why two steps, not five:** each step is 3,591 calls (1.4 GPU-hours). Two steps keep the summarize-then-refit loop that distinguishes the method; five steps (d1) need 10.5 h.

**Trade-off.** Fewer, larger batches mean fewer centroid updates from the stream (21 instead of 304), and fewer summary steps per batch than the 5 of the paper. Both reduce how often a summary can move a centroid, so the method gets less of a chance to differ from k-means than in the paper's setup. The summary-distance columns and the replacement diagnostic (#33) in #49 will show whether the summaries are doing anything. This is a budget choice, not evidence that 2 steps are enough. If the pilot's measured seconds per call is above about 1.7 s (idle-equivalent estimate: 1.43 s), drop to one summary step (about 1.4 h).

**Reading of the budget.** The 3-4 GPU-hours is per run, that is, one seed. Seeds multiply it: seeds 0-2 would be about 9 GPU-hours idle-equivalent (about 15 as logged), so the first full run is seed 0 only, and more seeds wait for the pilot's measured per-call cost and for review.

## 5. Pilot

`configs/arxiv_sub200k_pilot.yaml`: the 200k subsample (168 clusters), Qwen3-1.7B, two summary steps, `max_batch_size: 20000` (10 batches), `force_context_length: 10`, seed 0, the three baselines alongside, `gpu_check: {require_idle: fail}` (#35: it must run on an idle card).

- **Calls:** at most 10 x 168 x 2 = 3,360, 2,163 tokens each.
- **GPU time:** about 1.3 h idle-equivalent, 2.3 h as logged; the baselines on 200k add a few minutes of CPU and the model load about a minute. Plan for 1.5-2.5 hours wall.
- **Resources:** an RTX 3060 with enough free VRAM for the 1.7B at batch size 4 (the CLINC150 run peaked at 6.5 GB; the longer arXiv prompts raise the KV cache somewhat, so expect 7 GB or a little more), about 3 GB RAM. Not an LSA run.
- **What it settles:** the real seconds per call and per input token at arXiv prompt lengths for the 1.7B (the one number the estimate rests on), the real call count against the upper bound (memo hits, empty clusters), the cost fields of #30, and a first look at whether summaries move the centroids at 200k.
- **What it does not match:** the pilot has 10 batches of 20k rows; the full run has 21 batches of 150k. The per-call cost carries over, the batch dynamics do not.

### 5.1 Pilot results (seed 0)

Run `20261116-175906`, git 341e420, exit code 0 (queue step total 6,120 s). 200,000 abstracts, k = 168, ten batches of 20,000, two summary steps per batch, Qwen3-1.7B at summarizer batch size 4, `eval_assign: lloyd1`. One seed, so no intervals. All five methods below are on the same 200k rows:

| Method | ACC | NMI | ARI | runtime |
| --- | ---: | ---: | ---: | ---: |
| `minibatchkmeans` | 0.2468 | 0.5301 | 0.1534 | 83.7 s |
| `seqminibatchkmeans` (20k batches) | 0.2536 | 0.5264 | 0.1682 | 1.8 s |
| `kmeans` | 0.2737 | 0.5421 | 0.1713 | 118.4 s |
| k-SLMmeans (Qwen3-1.7B) | 0.2663 | 0.5355 | 0.1746 | 5,884.7 s (98 min) |
| k-NLPmeans (LSA, section 5b) | 0.2694 | 0.5383 | 0.1809 | 3,357.8 s, see 5b |

The k-SLMmeans row ranks below `kmeans` on ACC and NMI and above it on ARI. With one seed there is no way to tell these gaps from seed-to-seed variation, so this is not evidence for or against the summaries. The pipeline ran end to end; that is the result.

**Cost.** `run_streaming.py` did not record the cost fields of #30 (calls, input tokens, output tokens, summarizer seconds) in `metrics.jsonl` for this run; the row carries only `runtime`. So the call count, the token counts and the summarizer seconds are not measured. What the run does give:

- All 168 clusters were non-empty in all 10 batches (`summaries.jsonl`: 168 summaries per batch), so the call upper bound of 3,360 is the number of scheduled calls. Memo hits could make the real count lower; that is not logged.
- The k-SLMmeans `runtime` is 5,884.7 s, including 8.1 s of embedding and the CPU k-means refits (the estimate for those is at most about 2 minutes). Taking all of it as summarizer time: **1.75 s per scheduled call**, **0.81 ms per input token** at the 2,163 tokens per call estimated in 4.1 (the tokens are the estimate, not logged).
- The estimate this calibrates: 3,360 calls at 1.43 s (idle-equivalent) is 1.33 h and 2.43 s (as logged) is 2.3 h. The measured 1.64 h lies between them, closer to the idle figure. It equals a slowdown divisor of about 1.39 where the estimate used 1.7.
- **Concurrency, so this rate is an upper bound.** The pilot did not have the machine to itself. The full-scale baselines ran next to it until about 18:14 (multi-core k-means, up to 9.5 GB), then LSA ran from about 18:15 to 19:11 (spaCy on one core, then a short MiniLM embedding that shared the card), and some thread-limited doc work ran at times. Its seconds, and the seconds per call, are therefore an upper bound on what an idle machine gives, not an idle-card measurement. The GPU idle check passed at 17:59 (1,013 MiB in use, 2 % utilization), and the pilot's monitor (`gpu.json`, `gpu_samples.csv`, 1,212 samples at 5 s) recorded 1,308 MiB of memory on average and 1,609 MiB at most that did not belong to the pilot's torch process, in a total peak of 7,729 MiB; mean utilization 83 %.
- **Implication for #49** (`scripts/estimate_stream_cost.py --gpu-slowdown 1.3885`, so that the 1.7B costs the measured 0.81 ms per token): (d4), 150k batches, two steps, 7,182 scheduled calls, comes to **about 3.5 GPU-hours** (4.9 at the as-logged rate, 2.9 in the earlier idle-equivalent estimate). So plan on 3.5 h as a ceiling for one seed, and treat 2.9 h as no longer supported. The earlier rule said to drop to one summary step if the rate is above about 1.7 s per call; the measured 1.75 s is at that line, and it is inflated by the concurrent jobs, so this does not by itself decide it. An idle-card rerun of a few batches would settle it, and logging the cost fields would make the call count a measurement.

**Truncation.** The log carries one warning, from `HFSummarizer`: a cluster's rendered prompt exceeded `max_input_tokens=4096` and 1 of 10 texts was dropped. The warning is issued once per summarizer instance, so at least one cluster and one text were affected and the real count may be higher; it is not logged. The 300-prompt sample in 4.1 found none over the limit, so these are rare outliers.

**GPU check and monitor.** `require_idle: fail` passed (above). The monitor recorded no sampling errors. The pilot's peak GPU memory was 7,729 MiB, inside the 7 GB or a little more expected for the 1.7B, plus the 1 GB the card already held.

**Process memory.** `peak_rss_mb` was 5,110 MB for the whole process, above the "about 3 GB" in section 5.

**Distance columns.** k-SLMmeans logged `sum_cen_dist` = `sum_sum_dist` = 0.870 (k-NLPmeans 0.836), and `cen_sum_dist` equals `cen_cen_dist` in every row. The two summary columns are identical, which suggests they are not independent measurements; they are not interpreted here.

## 5b. LSA on the 200k subsample

`configs/arxiv_sub200k_lsa.yaml`: k-NLPmeans (extractive LSA summaries) on the 200k subsample with the pilot's schedule (20k-row batches, two summary steps per batch, `force_context_length: 10`, seed 0), so there is an extractive baseline at that scale. It has no baselines of its own; the pilot run has them (a different run directory), and `scripts/aggregate_results.py` tabulates the two run directories together.

| Stage | Where | Estimate |
| --- | --- | --- |
| spaCy segmentation of 200k abstracts (1.26 M sentences) | CPU, one core | 37-46 min (73-90 abstracts/s measured) |
| MiniLM embedding of the sentences | **GPU** | about 5 min by tokens, up to about 29 min by rows (section 3) |
| Cache write (`cache/arxiv_sub200k__minilm_sentences.*`) | disk | about 2 GB; reruns read it |
| 10 batches x 2 steps x 168 LSA summaries, k-means, final `lloyd1` assignment | CPU | about 1-3 min (estimate; CLINC150 LSA took 15 s of summarizing per seed) |

**Total about 45-80 minutes**, almost all of it spaCy, plus about 3 GB of RAM (sentence text 0.2 GB as raw characters, about 0.5 GB as Python strings, and 1.9 GB of float32 embeddings). The embedding step uses the GPU (MiniLM), so this run needs approval like the others; it is light (a few hundred MB of VRAM) but should not overlap with the pilot, whose timing needs an idle card. The first run builds the sentence cache; run it before or after the pilot, not during.

```
HF_HUB_OFFLINE=1 PYTHONPATH=$PWD/src KSLIMEANS_DATA_DIR=<path to the data directory> \
  python -u scripts/run_streaming.py configs/arxiv_sub200k_lsa.yaml
```

### 5b.1 Results (seed 0)

Run `20261116-181519`, exit code 0, k-NLPmeans on the 200k subsample, k = 168, pilot schedule. It was queued behind the full baselines and so started at about 18:15, while the pilot was running (against the advice above, which asked for no overlap).

| Method | ACC | NMI | ARI |
| --- | ---: | ---: | ---: |
| k-NLPmeans | 0.2694 | 0.5383 | 0.1809 |

- **Time:** sentence corpus (spaCy segmentation and MiniLM embedding of 1.26 M sentences) 3,319 s (55 min), the rest of the method 38.7 s. The estimate was 45-80 min in all.
- **Inflated timings:** the GPU idle check warned that the card was busy (7,149 MiB in use, 96.5 % utilization, 138.6 W: the pilot), so `require_idle: warn` let it run and the embedding time is inflated. The spaCy part ran on a CPU shared with the other jobs. Neither time is an idle-machine figure.
- **RAM:** `peak_rss_mb` was 8,075 MB, against the 3 GB estimated above. Not investigated.
- **Reading:** compare it only with the other 200k rows in 5.1. It is within 0.01 of `kmeans` and k-SLMmeans on ACC and NMI and highest on ARI, on one seed; that is a statement about this run, not a ranking.

## 6. What is left

- **Done tonight:** the seed-0 baselines at full scale, the pilot and LSA at 200k. **Not done:** seeds 1-2 at full scale, the 150k-batch sequential baseline (below), an idle-card timing of the summarizer, and the logged cost fields (calls, tokens, summarizer seconds), which `run_streaming.py` did not write for the pilot. #49 (the full summary run, Nov 30) should log them, and should run on an idle machine so its rate is not an upper bound.
- **#49:** the full summary run needs about 8 GB for the vectors and texts together (4.7 GB + about 3.3 GB of Python strings) before sklearn's buffers. The final evaluation step `assign_to_centroids(..., "lloyd1")` fits `KMeans(max_iter=1)` on the full X, which makes a second 4.7 GB copy; at full scale use `eval_assign: nearest` (chunked, no copy) or add `copy_x=False` there. Not changed here because `lloyd1` reproduces upstream's evaluation.
- **Aggregation:** `aggregate_runs` (and so `scripts/aggregate_results.py`) now accepts a baseline-only run directory, so the full-scale baselines can be tabulated alone or next to a summary run. The streaming runner's `runtime` column is read as `runtime_s`.
- **Like-for-like baseline for the recommended schedule (run it too).** The baselines config uses 10k batches, while the recommended summary run uses 150k batches, and `seqminibatchkmeans` makes one `partial_fit` per batch. 10k batches is the stronger baseline; the like-for-like one has the same 21 batches:

  ```
  ... scripts/run_streaming.py configs/arxiv_full_baselines.yaml \
      --set max_batch_size=150000 --set name=arxiv_full_baselines_b150k \
      --set 'baselines={seqminibatchkmeans: {}}'
  ```

  CPU only, X is the same 4.7 GB (about 6 GB peak), and 21 `partial_fit` calls of 150k rows each cost about the same total work as the 10k run, so about 1-3 minutes per seed. Only `seqminibatchkmeans` depends on the batch size in this way; `minibatchkmeans`' `batch_size` is its SGD step and `kmeans` ignores it, so they need not be repeated. Report both seq rows and say which batch size each used.
- **LSA on the 200k subsample:** `configs/arxiv_sub200k_lsa.yaml`, section 5b.1; done, one seed, timings inflated by overlap.

## Reproducing the numbers

```
HF_HUB_OFFLINE=1 python scripts/estimate_stream_cost.py --measure --lsa --save-stats docs/results/arxiv_token_stats.json
python scripts/estimate_stream_cost.py                                           # the table in 4.2
python scripts/estimate_stream_cost.py --gpu-slowdown 1                          # as logged
python scripts/estimate_stream_cost.py --n-rows 20000 --k 149 --option 5000:5    # the smoke-run check
python scripts/estimate_stream_cost.py --n-rows 200000 --k 168 --option 20000:2  # the pilot
python scripts/estimate_stream_cost.py --gpu-slowdown 1.3885                     # the pilot's measured rate, for #49
python scripts/run_streaming.py configs/arxiv_full_baselines.yaml --set 'seeds=[0]'   # section 2.4 (CPU)
python scripts/run_streaming.py configs/arxiv_sub200k_pilot.yaml                      # section 5.1 (idle GPU)
python scripts/run_streaming.py configs/arxiv_sub200k_lsa.yaml                        # section 5b.1
python scripts/aggregate_results.py results/arxiv_sub200k_pilot/<stamp> results/arxiv_sub200k_lsa/<stamp>
```

The measured sample statistics are in `docs/results/arxiv_token_stats.json`.
