# Cost timing on an idle GPU (#35, parts 3 and 4)

This re-times the CLINC150 summarizers on one fixed workload, with the card checked as idle before each run and sampled during it, so that model size and batch size can be told apart and the #31 timings can be compared with a clean measurement. Parts 1 and 2 (what the counters count, and the idle check itself) are in [`cost_verification.md`](cost_verification.md).

Scope, in one place: **3 repeats, one workload (150 clusters of one seed's first summary step), one card.** Every number below is a measurement of that workload on that card, not a general speed of the models.

## TL;DR

- **At batch size 1** the three sizes run at 16.7 (0.6B), 14.5 (1.7B) and 10.1 (4B) output tokens per second, and take 0.89, 1.74 and 2.10 s per call. The 4B is 2.4 times the 0.6B's time on the same prompts. Seconds per call also depends on how long each model's summaries are (2,225, 3,795 and 3,160 output tokens for the same 150 prompts), so tokens per second is the fairer size comparison.
- **Batching matters about as much as size here.** The 1.7B goes from 261 s at batch 1 to 166 s at batch 4 (1.57 times faster), the 0.6B from 133 s at batch 1 to 94 s at batch 8 (1.41 times faster). The cost is memory (1.7B: 4.2 to 6.3 GB reserved; 0.6B: 1.9 to 6.1 GB) and, at these two settings, different summaries (below).
- **The #31 step-1 timings were inflated, by 1.72 times (1.7B), 1.76 times (0.6B) and 1.15 times (4B).** That is a measured ratio per size for step 1 of seed 0 only. It replaces the single 1.7x estimate for step 1; it does not measure the inflation over whole runs (see section 4).
- **Batch size changes the summaries.** At the batch size of the #31 run the regenerated summaries equal the logged ones exactly (150 of 150, for all three sizes). At batch 1 instead of the logged batch, 25 of 150 (0.6B, batch 8 logged) and 42 of 150 (1.7B, batch 4 logged) summaries differ.

## 1. What was run

`scripts/fixed_workload.py` re-summarizes the 150 prompts that the #31 run of each size sent to its summarizer at its first summary step (seed 0, step 1 of the trace; the step-0 partition is the same for every size, `step0_sha1` is shared). The prompts are rebuilt from the logged partition and the cached embeddings, so they are identical across sizes and batch sizes: **234,011 input tokens, 150 calls** (no empty clusters and no memo-cache hits at this step, as logged), no truncated cluster. Each setting does 1 untimed warm-up pass over the first batch, then 3 timed repeats of the whole workload. The clock wraps the whole `summarize_batch` call (render, tokenize, generate, decode), the span `summarizer_seconds` measures (`cost_verification.md`, section 3).

| Setting | Source run (#31) | Batch size | Directory (under `results/fixed_workload/`) |
| --- | --- | ---: | --- |
| `time_4b_bs1` | `clinc150_qwen3-4b/20261027-221042` | 1 | `time_4b_bs1/20261116-170737` |
| `time_1.7b_bs1` | `clinc150_qwen3-1.7b/20261027-202532` | 1 | `time_1.7b_bs1/20261116-172358` |
| `time_1.7b_bs4` | same | 4 | `time_1.7b_bs4/20261116-173720` |
| `time_0.6b_bs1` | `clinc150_qwen3-0.6b/20261027-190908` | 1 | `time_0.6b_bs1/20261116-174621` |
| `time_0.6b_bs8` | same | 8 | `time_0.6b_bs8/20261116-175332` |

The 4B only fits at batch 1 on this card, so batch 1 is the common setting; the other two settings are each size's #31 batch size (1.7B: 4, 0.6B: 8). All five used the #31 prompt (the dataset's own), `max_new_tokens` 64, `max_input_tokens` 4096, thinking off.

### What ran at the same time

- **GPU:** idle-checked before each run (table below) and sampled every 5 s during it (`gpu.json`, `gpu_samples.csv` in each directory). The largest estimated foreign GPU memory during the runs was 1,145 to 1,162 MiB against pre-run baselines of 1,000 to 1,015 MiB, a rise of 136 to 152 MiB, about the size of our own CUDA context. No other GPU job was running.
- **Queue:** the steps ran one after another, 17:07 to 17:58 on 2026-11-16, and the queue ran nothing else during them. A first attempt of `time_4b_bs1` was stopped by hand 43 s in, at 17:02, so that a CPU analysis job could run first (17:02 to 17:07); its partial directory was moved out of `results/fixed_workload/` and none of its numbers are used. The kept 4B run started after that job had finished.
- **CPU:** not monitored, and the logs do not record it. Light, low-priority, thread-limited work for other issues ran at times (documentation edits and small report scripts, at most 2 BLAS threads each, `nice -n 19`), including a few seconds of the report script of this issue during `time_1.7b_bs1`. No test suite or other heavy job ran during the five runs. The timings are therefore close to, but not guaranteed to be, free of CPU contention.
- **Code:** the runs were made at commit `341e420` (clean tree). Since then only `prompt_test.py`, `rq2.py`, `synthesis.py` and two configs changed, none of them on the timing path.

## 2. Fixed-workload table

Median and range over the 3 repeats. Seconds per call is a repeat's total seconds over 150 calls; output tokens per second is a repeat's output tokens over its total seconds (so it includes prefill and decoding of the input).

| Setting | Model | Batch | Repeats | s per call, median (range) | Output tok/s, median (range) | Total s, median (range) | Same summaries in every repeat |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `time_4b_bs1` | Qwen3-4B | 1 | 3 | 2.10 (2.06-2.12) | 10.1 (9.9-10.2) | 314 (309-318) | yes |
| `time_1.7b_bs1` | Qwen3-1.7B | 1 | 3 | 1.74 (1.61-1.75) | 14.5 (14.5-15.7) | 261 (242-262) | yes |
| `time_1.7b_bs4` | Qwen3-1.7B | 4 | 3 | 1.11 (1.06-1.11) | 22.8 (22.7-23.7) | 166 (160-167) | yes |
| `time_0.6b_bs1` | Qwen3-0.6B | 1 | 3 | 0.89 (0.87-0.90) | 16.7 (16.5-17.1) | 133 (130-135) | yes |
| `time_0.6b_bs8` | Qwen3-0.6B | 8 | 3 | 0.63 (0.63-0.63) | 22.8 (22.7-22.9) | 94 (94-95) | yes |

The three repeats of one setting differ by at most 8% (`time_1.7b_bs1`: 242, 262, 261 s, with the first repeat the fast one) and by 1 to 3% for the others. Every setting gave the same summaries in all three repeats, so the output-token counts are the same in every repeat.

Setup, idle check and memory (peak and reserved are PyTorch's maxima over the repeats; "above baseline" is the largest non-torch card memory seen during the run minus the pre-run idle median):

| Setting | Batch | dtype | GPU | Idle at start | Max non-torch MiB above baseline | Calls | Input tokens | Output tokens | Peak GB | Reserved GB |
| --- | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `time_4b_bs1` | 1 | bfloat16 | RTX 3060 12 GB | yes | 152 | 150 of 150 | 234,011 | 3,160 | 8.95 | 9.12 |
| `time_1.7b_bs1` | 1 | bfloat16 | RTX 3060 12 GB | yes | 144 | 150 of 150 | 234,011 | 3,795 | 4.12 | 4.24 |
| `time_1.7b_bs4` | 4 | bfloat16 | RTX 3060 12 GB | yes | 136 | 150 of 150 | 234,011 | 3,786 | 6.18 | 6.30 |
| `time_0.6b_bs1` | 1 | bfloat16 | RTX 3060 12 GB | yes | 138 | 150 of 150 | 234,011 | 2,225 | 1.76 | 1.85 |
| `time_0.6b_bs8` | 8 | bfloat16 | RTX 3060 12 GB | yes | 152 | 150 of 150 | 234,011 | 2,157 | 5.93 | 6.11 |

"Idle at start" is the `gpu_check` verdict recorded before the model loaded: the median of 4 samples 1 s apart was within 1,400 MiB used, 15% utilization and 65 W. The medians were 1,000 to 1,015 MiB, 2% and 43 to 44 W for the five runs. During the runs the mean sampled utilization was 35 to 94% (it depends on the batch size and on how much time goes to the host side), and the highest power draw 100 to 149 W.

## 3. Model size and batch size

### Model size, batch size held at 1

| Model | s per call | Output tok/s | Total s | Output tokens | Reserved GB |
| --- | ---: | ---: | ---: | ---: | ---: |
| Qwen3-0.6B | 0.89 | 16.7 | 133 | 2,225 | 1.85 |
| Qwen3-1.7B | 1.74 | 14.5 | 261 | 3,795 | 4.24 |
| Qwen3-4B | 2.10 | 10.1 | 314 | 3,160 | 9.12 |

- On identical prompts and identical batching the 1.7B takes 1.96 times, and the 4B 2.36 times, the 0.6B's time. Per output token the speeds are 16.7, 14.5 and 10.1 tok/s, so the 4B is 0.60 times the 0.6B's rate.
- The seconds per call mix speed with summary length: the 1.7B writes the longest summaries (3,795 tokens in total) and the 0.6B the shortest, so its seconds per call are high for its per-token rate. Use tokens per second to compare speed, and total seconds to compare what each model costs for this workload.
- At batch 1 the work is dominated by decoding one sequence at a time. The three sizes are within a factor of 1.7 of each other in tokens per second although the 4B has 6.7 times the parameters of the 0.6B, which suggests that per-step overhead (kernel launches, the host loop) is a large share at these sizes on this card; this was not profiled.
- Memory grows with the weights: 1.85, 4.24 and 9.12 GB reserved.

### Effect of batch size

| Model | Batch | Total s | Output tok/s | Speed-up in total s | Reserved GB | Summaries equal to the logged run |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Qwen3-1.7B | 1 | 261 | 14.5 | | 4.24 | 108 of 150 (logged batch: 4) |
| Qwen3-1.7B | 4 | 166 | 22.8 | 1.57 times | 6.30 | 150 of 150 |
| Qwen3-0.6B | 1 | 133 | 16.7 | | 1.85 | 125 of 150 (logged batch: 8) |
| Qwen3-0.6B | 8 | 94 | 22.8 | 1.41 times | 6.11 | 150 of 150 |

- Batching helps the smaller models too, but far less than the batch ratio (4 times, 8 times): the speed-ups are 1.57 and 1.41 times. The 0.6B at batch 8 and the 1.7B at batch 4 both reach 22.8 tok/s, which is a coincidence of these two measurements, not a ceiling shown here.
- At a model's own #31 batch size the three sizes are no longer in size order for seconds per call (0.63, 1.11, 2.10 for 0.6B at 8, 1.7B at 4, 4B at 1), because the batching differs. A comparison of #31 per-call seconds across sizes mixes the two effects, as the issue said.
- The 0.6B's peak memory at batch 8 is 3.4 times its batch-1 peak, though the weights are the same: presumably the activations and the key-value cache of 8 padded sequences (not profiled). Under `expandable_segments:True` (as in #31), reserved memory is only 0.1 to 0.2 GB above the peak.

## 4. Inflation of the #31 timings, measured at step 1

For each size, the fixed workload at that size's #31 batch size (4B: 1, 1.7B: 4, 0.6B: 8) against the #31 run's own logged seconds for the same work. The logged number is the `summarizer_seconds` field of the **`trace.jsonl` row for seed 0, method `k-SLMmeans`, `step` 1** (the first summary step; 150 calls, 234,011 input tokens, equal to the fixed workload's). The per-run `summarizer_seconds` in `metrics.jsonl` covers all five steps and is not used here.

| Model | Batch | Calls | #31 logged step-1 s | Fixed workload s, median (range) | Logged / fixed workload |
| --- | ---: | ---: | ---: | ---: | ---: |
| Qwen3-0.6B | 8 | 150 | 165.9 | 94.5 (94.4-95.2) | **1.76** |
| Qwen3-1.7B | 4 | 150 | 286.8 | 166.3 (159.5-166.6) | **1.72** |
| Qwen3-4B | 1 | 150 | 360.8 | 314.4 (309.1-317.7) | **1.15** |

- Against the pilot's single no-warm-up runs on 2026-11-12 (`prompt_test.md`, section 7: 0.6B 94.8 s, 1.7B 160.1 s, 4B 297.3 s, taken while a CPU job overlapped), the new medians are within 6%, so the idle-card times for this workload are about the same on two days.
- **What the ratio is.** It compares two measurements of the same prompts and the same summaries (the regenerated summaries are identical, section 5), one made while the card was shared in the way described in `clinc150_summarizers.md`, section 3, and one on a card checked as idle. A ratio above 1 is the slowdown of that single step. One step of one seed per size, one logged measurement against three repeats.
- **What it does not say.** The logged step also includes the one-off start-up of the first call (the fixed workload has a warm-up pass, which the #31 run did not), so a small part of each ratio is that, not contention; the data cannot separate the two. The size of the contention also moved over the #31 run (the section 3 text shows 1.7B seed 4 at 1,081 s against 1,260 to 1,367 s for seeds 0 to 3), so a step-1 ratio is not a whole-run ratio.
- **The earlier estimate.** The 1.7x estimate came from one BANKING77 check. For the 0.6B and the 1.7B the CLINC150 step-1 measurement agrees with it (1.76 and 1.72). For the 4B it does not: 1.15. The 4B run is the longest (about 32 minutes per seed), and it ran last, at about 22:10 on October 27; the card was probably less loaded then, but the load was not recorded, so this is a guess.
- **Deferred.** The full-seed re-time (`retime_0.6b`, `retime_1.7b` and `retime_4b` in the run queue: one whole #31 seed per size on the idle card) was deferred on 2026-11-16 and not run tonight. **The inflation over whole runs is therefore not measured**; only step 1 is. Until it is, the #31 per-seed seconds should be read as inflated by an unknown factor between about 1.15 and 1.8.

## 5. Determinism

Greedy decoding, so a different output means a different computation, not sampling. The batch size changes the computation in two ways: left padding shifts the positions of shorter prompts, and the matrix shapes change with the batch, which likely changes floating-point results in bf16 (not isolated). Either can flip a token and the rest of a greedy summary with it.

| Comparison | Identical | Differing |
| --- | ---: | ---: |
| 4B, batch 1 against the #31 log (batch 1) | 150 | 0 |
| 1.7B, batch 4 against the #31 log (batch 4) | 150 | 0 |
| 0.6B, batch 8 against the #31 log (batch 8) | 150 | 0 |
| 1.7B, batch 1 against the #31 log (batch 4) = 1.7B batch 1 against batch 4 | 108 | 42 |
| 0.6B, batch 1 against the #31 log (batch 8) = 0.6B batch 1 against batch 8 (the requested diff) | 125 | 25 |
| Repeats of one setting against each other (all five settings) | 150 of 150 each | 0 |

- **Regeneration is exact at the logged batch size** for all three sizes (as the pilot showed: 150 of 150), on a different day and process: the summaries do not depend on the day or on contention, only on the batch composition. The step-1 summary text of #31 can therefore be reproduced.
- **The 0.6B at batch 1 against batch 8 differs in 25 of 150 summaries (17%), the 1.7B at batch 1 against batch 4 in 42 of 150 (28%).** The 0.6B's output-token total is 2,225 at batch 1 and 2,157 at batch 8, the 1.7B's 3,795 and 3,786, so the totals barely move.
- Examples (cut at 110 characters):
  - 0.6B, cluster 0, batch 8 against batch 1: `... How would you say "can I borrow five dollars in...` against `... How would you say can I borrow five dollars in ...` (a quotation mark).
  - 0.6B, cluster 4: `Can you make a reservation at the restaurant for tomorrow? Please make a reservation for me: party of two, ...` against `Can you help me make a reservation at Chili's for tomorrow? Please confirm the details: party of two, Febru...`.
  - 0.6B, cluster 8: `What is your age?` against `How old are you?`.
  - 1.7B, cluster 3: `What is the meaning of life, and how can one determine or understand it?` against `What is the meaning of life, and how can it be understood or determined?`.
- This counts differing strings, not differing quality. Whether the batch-1 and logged summaries cluster differently was not measured here. It does mean that **a model at two batch sizes is two slightly different summarizers**, so the #31 comparison of sizes at batch 8, 4 and 1 carries a small batch effect on the summaries as well as on the seconds.

## 6. Cost table per method, CLINC150 (part 4)

From `scripts/aggregate_results.py --cost-md` on the #31 runs and the three v2 runs (`clinc150_v2_qwen3-*`, #46), mean over seeds 0 to 4 (± is the standard deviation over seeds). Seconds per call is mean summarizer seconds over mean calls, and output tokens per second is mean output tokens over mean summarizer seconds; both include the effect of everything in the seconds, as logged. Calls differ between runs because the memo cache and the clusterings differ, and the per-call mix differs between sizes, so the per-call columns of different rows are not a controlled comparison: section 2 is.

| Method | Calls | Input tokens | Output tokens | Summarizer s | Total s | s per call | Output tok/s | Peak / reserved GB | Batch | dtype | Hardware | Card verified idle |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| k-means | n/a | n/a | n/a | n/a | 5.3 ± 1.6 | n/a | n/a | n/a | n/a | n/a | RTX 3060 | no (CPU method) |
| k-NLPmeans (LSA) | 636 ± 8 | 0 | 0 | 14.8 ± 1.8 | 23.7 ± 2.5 | 0.02 | n/a | 0.37 / 0.53 | n/a | n/a | RTX 3060 | no (not checked) |
| k-SLMmeans Qwen3-0.6B (#31) | 707 ± 7 | 1,113,037 ± 8,773 | 10,227 ± 211 | 895.8 ± 29.7 | 903.9 ± 29.6 | 1.27 | 11.4 | 6.51 / 6.70 | 8 | bfloat16 | RTX 3060 | **no; timings inflated** |
| k-SLMmeans Qwen3-1.7B (#31) | 702 ± 6 | 1,101,755 ± 11,449 | 18,288 ± 387 | 1238.6 ± 102.5 | 1247.5 ± 103.4 | 1.76 | 14.8 | 6.54 / 6.68 | 4 | bfloat16 | RTX 3060 | **no; timings inflated** |
| k-SLMmeans Qwen3-4B (#31) | 714 ± 6 | 1,120,190 ± 7,604 | 15,620 ± 463 | 1855.0 ± 188.6 | 1861.7 ± 189.8 | 2.60 | 8.4 | 9.25 / 9.42 | 1 | bfloat16 | RTX 3060 | **no; timings inflated** |
| k-SLMmeans-v2 Qwen3-0.6B | 689 ± 2 | 1,120,788 ± 8,825 | 7,806 ± 79 | 373.4 ± 8.5 | 381.1 ± 8.3 | 0.54 | 20.9 | 6.51 / 6.70 | 8 | bfloat16 | RTX 3060 | yes at start; +139 MiB foreign during the run |
| k-SLMmeans-v2 Qwen3-1.7B | 701 ± 6 | 1,137,714 ± 3,013 | 11,239 ± 47 | 737.0 ± 198.1 | 744.4 ± 199.3 | 1.05 | 15.2 | 6.54 / 6.68 | 4 | bfloat16 | RTX 3060 | yes at start, **not clean during the run** (+1,625 MiB foreign, up to 2,841 MiB; std 198 s) |
| k-SLMmeans-v2 Qwen3-4B | 698 ± 10 | 1,131,772 ± 11,868 | 9,068 ± 185 | 1093.7 ± 20.7 | 1098.8 ± 20.6 | 1.57 | 8.3 | 9.25 / 9.41 | 1 | bfloat16 | RTX 3060 | yes at start; +139 MiB foreign during the run |

Reading it:

- **The #31 rows are not idle-verified** (the idle check was added after them, in part 2) and their seconds are inflated. The measured step-1 ratio for each size is in section 4 (0.6B 1.76, 1.7B 1.72, 4B 1.15); there is no whole-run ratio. Their calls, tokens, truncation and memory columns are unaffected (`cost_verification.md`).
- **The v2 rows were idle-checked at start** and monitored. Two of the three stayed within about 140 MiB of the baseline (our own CUDA context). The v2 1.7B run did not: the monitor saw up to 2,841 MiB of non-torch memory (1,625 MiB above the baseline), and its seconds vary far more between seeds (737 ± 198 s) than the other two v2 rows (± 9 and ± 21 s). Its timing is probably contaminated; do not use its seconds as a clean 1.7B figure. The fixed-workload runs of section 2 are the clean ones.
- **The v2 rows use a different prompt**, so their output tokens, and with them the seconds, are lower than in #31 (24 to 42% fewer output tokens); they are not a measure of the prompt change alone either, since the clusterings also differ.
- Compare the fixed-workload seconds per call (section 2) with the per-run ones here: the #31 4B run takes 2.60 s per call over a whole run against 2.10 s on the fixed workload, but a whole run has different clusters and summaries at steps 2 to 5, so that difference is not an inflation figure.
- **Tokens, calls and memory** columns are the same kind of number as in `clinc150_summarizers.md`, section 3.

## 7. What the timings cover

One RTX 3060 12 GB (12.88 GB reported), NVIDIA driver 610.88, under WSL2 (Linux 6.6.114.1-microsoft-standard-WSL2). Hugging Face `generate` with the model in `torch.bfloat16`, greedy decoding, left padding, `max_new_tokens` 64, thinking off; no vLLM, no quantization, no compilation, no speculative decoding. Versions (from `environment.json` of the runs): Python 3.14.7, torch 2.14.0+cu130 (CUDA 13.0), transformers 5.17.0, sentence-transformers 6.0.1, scikit-learn 1.9.1, numpy 2.5.3.

What this means for a reader:

- The seconds are wall-clock for one process on one card, batching as stated. A different card, an inference server or quantization would change all of them, and the ratios between sizes could change too.
- Nothing here measures energy, price or the quality of the summaries.
- The summarizer is the whole cost of the language-model rows: in #31 it was 99.1 to 99.7% of `total s` (`cost_verification.md`, section 2). The embedding of the corpus is cached and not counted.

## 8. Reproduce

Run from the checkout that holds `results/` (the runs are not in git). Wait for the card to be idle first; each command logs the idle check and the monitor into its output directory.

```
# the five timings (1 warm-up pass, 3 timed repeats each)
python scripts/fixed_workload.py results/clinc150_qwen3-4b/20261027-221042 --name time_4b_bs1 --set batch_size=1 --repeat 3
python scripts/fixed_workload.py results/clinc150_qwen3-1.7b/20261027-202532 --name time_1.7b_bs1 --set batch_size=1 --repeat 3
python scripts/fixed_workload.py results/clinc150_qwen3-1.7b/20261027-202532 --name time_1.7b_bs4 --set batch_size=4 --repeat 3
python scripts/fixed_workload.py results/clinc150_qwen3-0.6b/20261027-190908 --name time_0.6b_bs1 --set batch_size=1 --repeat 3
python scripts/fixed_workload.py results/clinc150_qwen3-0.6b/20261027-190908 --name time_0.6b_bs8 --set batch_size=8 --repeat 3

# sections 2, 4 and 5: the tables, the summaries against the logged run, the step-1 inflation, and two batch-size diffs
d() { ls -d results/fixed_workload/$1/* | sort | tail -1; }
python scripts/timing_report.py $(d time_4b_bs1) $(d time_1.7b_bs1) $(d time_1.7b_bs4) $(d time_0.6b_bs1) $(d time_0.6b_bs8) \
    --logged --inflation --diff $(d time_0.6b_bs1) $(d time_0.6b_bs8) --diff $(d time_1.7b_bs1) $(d time_1.7b_bs4)

# section 6: the per-method cost table
python scripts/aggregate_results.py results/clinc150_lsa/20261027-174631 \
    results/clinc150_qwen3-0.6b/20261027-190908 results/clinc150_qwen3-1.7b/20261027-202532 results/clinc150_qwen3-4b/20261027-221042 \
    results/clinc150_v2_qwen3-0.6b/20261112-200926 results/clinc150_v2_qwen3-1.7b/20261112-204127 results/clinc150_v2_qwen3-4b/20261112-181256 \
    --cost-md cost.md
```

The seconds per call and output tokens per second in section 6 are computed from that table's means (summarizer s over calls, output tokens over summarizer s). `scripts/compare_workloads.py` tabulates the surface counts of the same directories (mention rate, duplicates), not the timing statistics, so `scripts/timing_report.py` is used here. The `retime_*` full-seed runs are in the run queue (`results/runq/queue.txt`) but were not run.
