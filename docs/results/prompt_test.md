# CLINC150 prompt test (#46): does a clearer prompt change the Qwen3 results?

Issue #46 asks whether part of the Qwen3-4B's lower CLINC150 scores comes from how it reads the prompt (background in
[`clinc150_summarizers.md`](clinc150_summarizers.md) §2.4 and §4). This file holds the pilot, which needs no clustering
scores. Section 8 holds the main runs: all three sizes under the clearer prompt, next to the #31 runs, with the paired differences and what they mean for the size trend (#36).

Everything below comes from outputs that already exist. The pilot's run directories are under `results/` and not
committed; [`prompt_test_pilot.csv`](prompt_test_pilot.csv) and [`prompt_test_pilot_examples.md`](prompt_test_pilot_examples.md)
are written from them by `scripts/prompt_test_pilot.py` (see "Reproduce").

## 1. Setup

- **Fixed workload.** The inputs of seed 0's first summary step in the logged #31 run of each size: 150 clusters, from the
  step-0 partition that every method shares for a seed (`step0_sha1` 2b3858a965ae721d5e2bb27201fbc3728c31e716).
  The workload is rebuilt from the logged partition and the cached embeddings, so the members and their order are the
  ones the #31 run sent. The input tokens of the old-prompt rows are identical across sizes (234,011), as expected for one workload.
- **Batch sizes.** The logged ones: 4B 1, 1.7B 4, 0.6B 8. A larger batch for the 4B overflows the 12 GB card.
- **What changes.** Only the instruction. The system prompt, the `Question:` member lines, greedy decoding, thinking off,
  `max_new_tokens` 64, `max_input_tokens` 4096 and the #28 member selection are the #31 ones. The old prompt is the CLINC150
  dataset prompt, "The following is cluster of questions. Write a question that summarizes the following cluster:".
  The clearer prompt is `summarizer.prompt` in [`configs/clinc150_prompt_v2.yaml`](../../configs/clinc150_prompt_v2.yaml):
  "The following questions were asked by users. Write one new question that a user could have asked, in the same style, that
  covers what these questions have in common. Write only the question. Do not mention the questions, a group, a cluster or a topic."
- **One prompt, fixed in advance.** It was written and committed before any run (commit fe257e2, 2026-11-11; the pilot ran on 2026-11-12). There was no prompt search.
- **Counts.** The surface rules are those of §2.4 (`kslimeans.surface`): a summary "mentions the cluster" if it contains
  "cluster" or "summar" in any case; a duplicate group is a set of clusters with exactly the same summary.

## 2. Pilot table

Seed 0, first summary step, 150 summaries per row. The same numbers are in `prompt_test_pilot.csv`.

| Size | Prompt | Batch | Mention the cluster | Duplicate groups (clusters in them) | Mean words | Ends with "?" | Input tokens | Output tokens | Equal to logged |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4B | old | 1 | 49 (33%) | 4 (18) | 17.2 | 130 (87%) | 234,011 | 3,160 | 100% |
| 4B | clearer | 1 | 0 (0%) | 1 (2) | 11.1 | 98 (65%) | 239,561 | 1,975 | 2% |
| 1.7B | old | 4 | 14 (9%) | 1 (2) | 20.4 | 146 (97%) | 234,011 | 3,786 | 100% |
| 1.7B | clearer | 4 | 0 (0%) | 0 (0) | 13.4 | 148 (99%) | 239,561 | 2,410 | 0% |
| 0.6B | old | 8 | 13 (9%) | 2 (4) | 11.3 | 133 (89%) | 234,011 | 2,157 | 100% |
| 0.6B | clearer | 8 | 0 (0%) | 0 (0) | 8.8 | 135 (90%) | 239,561 | 1,725 | 5% |

"Equal to logged" is the share of the 150 summaries identical to the summary the #31 run wrote for the same cluster.
For the clearer prompt it is not expected to be high (3, 0 and 7 summaries). The 4B's largest old-prompt group has 7 clusters
("What is the main topic of the following cluster of questions?"). Its one remaining clearer-prompt group has 2 clusters
("How can I transfer money between different bank accounts?"). Input tokens are 2.4% higher with the clearer prompt (its
instruction is longer), the same at every size.

## 3. Decision

The rule, fixed before the pilot: choose the prompt with the fewest cluster-mentioning and duplicate 4B summaries. The
prompt is never chosen by clustering scores.

Outcome: the clearer prompt wins on both counts for the 4B (cluster-mentioning 49 to 0; clusters in duplicate groups 18 to 2),
so **the clearer prompt is adopted** for the main runs. The system-prompt variant (also dropping "clusters" from the system
prompt) was reserved for the case where the 4B still writes about the cluster under the clearer prompt. No size has any
cluster-mentioning summary under it (0 of 150 at each size), so **the variant is not needed** and is not run.

## 4. Determinism

With the old prompt, every size regenerated its logged summaries exactly (150 of 150, 100%) at the logged batch size.
So greedy decoding at that batch size, with this code and environment, reproduces the #31 run on this workload. The clearer-prompt rows
are therefore comparable to the old ones: the difference between them is the prompt. (Each pilot ran once, so the pilot
alone does not test repeatability; the 100% match to the run of 27 October is the evidence.)

## 5. Side-by-side examples

Eight clusters of the 150 (all three sizes, same clusters), each with three member questions. Drawn by a seeded rule that
looks only at the old prompt's summaries: `random.Random(46)` draws 3 clusters at random from those where the old prompt
gave, at any size, a summary that mentions the cluster or an exact duplicate (`old_prompt_flags`), then 5 more at random from
the other clusters, and the result is sorted by index. Members are 3 random members of the cluster's selected members
(same generator, seed 46). Long summaries are cut at 200 characters and marked. Nothing was picked by hand; the heading
of a flagged cluster says why it was drawn. A different draw would show different clusters. The examples are not a
sample for estimating rates; the table above is.

#### Cluster 8

Members (sampled):
- how old is al
- tell me your age please
- how many years do you have

| Size | Old prompt | Clearer prompt |
| --- | --- | --- |
| 4b | What is your age? | how old are you |
| 1.7b | How old are you? | What is the exact date you were born? |
| 0.6b | How old are you? | how old are you again? |

#### Cluster 16 (old prompt: 4b mentions the cluster, 0.6b mentions the cluster)

Members (sampled):
- how many points do i have with my american express
- how expensive is my internet
- what's the status of the order i placed online last week with target

| Size | Old prompt | Clearer prompt |
| --- | --- | --- |
| 4b | What is the summary of the following cluster of questions? The cluster of questions revolves around various financial and account-related inquiries, including transferring funds between accounts, chec [...] | Can you check the status of my recent online purchases and provide information about my account balances and transaction fees? |
| 1.7b | What are the key financial and transaction-related concerns and requests related to multiple accounts, including checking, savings, credit cards, and online purchases, and how can they be addressed? | What are the common concerns users have about their financial transactions and card fees? |
| 0.6b | What are the key points you're asking about in this cluster of questions? | What are the international transaction fees associated with my card? |

#### Cluster 48

Members (sampled):
- when will the replaecment card arrive
- how soon will you mail me a new card
- how can i find a new credit card to apply to

| Size | Old prompt | Clearer prompt |
| --- | --- | --- |
| 4b | When can I expect to receive my new or replacement credit card and what is the typical delivery time? | When will my new credit card arrive? |
| 1.7b | What is the expected timeline for receiving a replacement card, including delivery time, shipping, and when the new card will arrive? | When will my new credit card arrive in the mail? |
| 0.6b | How soon will you send me a replacement card? | when will my new card arrive? |

#### Cluster 63 (old prompt: 4b mentions the cluster, 4b duplicate)

Members (sampled):
- how do you spell "exactly
- will you help me with a math problem
- please help me apply for a silver card

| Size | Old prompt | Clearer prompt |
| --- | --- | --- |
| 4b | What is the main topic that the cluster of questions revolves around? | How do you spell various words and translate terms into different languages? |
| 1.7b | What are some common spelling challenges and how can I learn to spell words like "potato," "water," "university," and others, especially when I'm unsure of the correct spelling? | How do you spell "emolument" for me? |
| 0.6b | What is the correct way to spell "emolument"? | can you spell "emolument" for me? |

#### Cluster 106

Members (sampled):
- how do they say no in germany
- do i need a socket converter if i'm going to be in germany
- how would i say i love you if i were german

| Size | Old prompt | Clearer prompt |
| --- | --- | --- |
| 4b | What are the common German language phrases, travel tips, and cultural considerations for visiting Germany? | How do you say common phrases and ask about travel information in german? |
| 1.7b | What are the most common ways to communicate in German, including greetings, farewells, and everyday phrases, as well as travel-related questions and recommendations? | How do you express feelings in German? |
| 0.6b | How do you say "goodnight" in German? | How do I know if I need a visa to travel to Germany? |

#### Cluster 124

Members (sampled):
- how long will a new card take to reach me
- how long will it take to get a new card
- whats the wait time for a replacement card

| Size | Old prompt | Clearer prompt |
| --- | --- | --- |
| 4b | How long does it take to replace a credit card and what is the expiration date of a credit card? | How long does it take to replace a credit card and what is the expiration date of my credit card? |
| 1.7b | What is the typical time frame for receiving a replacement credit card after losing or having a stolen credit card, including the time it takes for the new card to be mailed and delivered? | How long does it take for a credit card company to process and send a replacement card after a loss or theft? |
| 0.6b | How long will it take for your credit card to be replaced after it gets stolen? | How long will it take for my credit card to be replaced when I lose it? |

#### Cluster 133

Members (sampled):
- change back to default settings
- i want my original settings back
- i need you to switch to my original settings

| Size | Old prompt | Clearer prompt |
| --- | --- | --- |
| 4b | **How can I reset the settings to their original or default state?** | Can you revert to the original settings please? |
| 1.7b | How can I revert my settings to their original state? | Can you reset all settings to their original state? |
| 0.6b | Please go back to the original settings. | What is the main factor that influences the success of a project? |

#### Cluster 146 (old prompt: 4b mentions the cluster, 0.6b mentions the cluster)

Members (sampled):
- text christopher and tell him i will stop by
- text steve and tell him i am running late
- make sure my to do list is completely clear please

| Size | Old prompt | Clearer prompt |
| --- | --- | --- |
| 4b | The cluster of questions summarizes a variety of requests related to scheduling, reminders, task management, travel alerts, account information, and communication tasks. | How can I manage my schedule, set reminders, confirm reservations, and handle notifications? |
| 1.7b | How can I manage my calendar, reminders, and appointments, including setting reminders, confirming reservations, adding events, and ensuring my schedule is clear and up-to-date? | How can I ensure my calendar is clear and organized for upcoming events and tasks? |
| 0.6b | Please summarize the key points of the cluster of questions. | Please schedule a meeting with Sam at 1:00 PM on Tuesday. |

## 6. Observations

These describe the 150 pilot summaries per row. They are not tested for significance.

- **The share ending in "?" drops for the 4B, 87% to 65%.** 52 of the 4B's 150 clearer-prompt summaries do not end in "?" (old: 20,
  11 of them multi-line "What is ... cluster? ... The cluster ..." answers). All 52 are fully lowercase, as are 2 more
  that end in "?", and the old prompt gave no lowercase summary. The members are lowercase questions without "?", so this
  looks like copying the users' style, "in the same style" in the prompt. Of the 52, 46 open with a question word or an
  auxiliary verb ("how do i change the oil in my car", "are you a bot or a human"): they are questions in form with the mark
  left off. The other 6 are requests ("order everything on my shopping list", "play the next song on the playlist",
  "set a timer or alarm for me", "cancel my dinner reservation please", "help me find my lost phone and disconnect it from your system",
  "please remove an item from my list"). The question-word check is a heuristic on the first word; it was read through by hand for the 4B. The 1.7B and 0.6B
  shares are 99% and 90% (old: 97% and 89%).
- **Summaries get shorter.** Mean words go from 17.2 to 11.1 (4B), 20.4 to 13.4 (1.7B) and 11.3 to 8.8 (0.6B).
- **Output tokens fall:** 3,160 to 1,975 (-37.5%, 4B), 3,786 to 2,410 (-36%, 1.7B) and 2,157 to 1,725 (-20%, 0.6B). This is for
  one step of 150 summaries. It says the generated text is shorter, not what a full run costs.
- **Cluster-mentioning summaries and duplicates vanish at the 1.7B and 0.6B too** (14 to 0 and 13 to 0 mentions). Those sizes
  had few of them to begin with (9%).
- **Clearer is not the same as faithful.** The examples include clearer-prompt summaries that look unrelated to their
  members (0.6B, clusters 133 and 146). The pilot counts surface form; it does not
  measure whether a summary represents its cluster. That is what the main runs' clustering scores and #33/#34 address.

## 7. Timing caveat

The pilot's seconds are not used for cost. A low-priority CPU job (the `nice -n 19` replays of #33, #47 and #50 from the GPU summary embeddings, recorded in the run log, not in these directories) ran at the same time, and the pilot has no warm-up pass (repeat 0
includes the one-off CUDA start-up). Cost timing is #35 part 3. The idle check each directory's `gpu.json` recorded before the
model loaded says idle for all six ("median sample within all thresholds"; median 1,215 MiB used, 0-1% utilization, 43-45 W):

| Directory | Idle at start |
| --- | --- |
| `pilot_old_4b/20261112-154657` | yes |
| `pilot_v2_4b/20261112-155229` | yes |
| `pilot_old_1.7b/20261112-155653` | yes |
| `pilot_v2_1.7b/20261112-160011` | yes |
| `pilot_old_0.6b/20261112-160249` | yes |
| `pilot_v2_0.6b/20261112-160456` | yes |

The idle check says nothing about the CPU job, which the check does not look at.


## 8. Main runs

Seeds 0-4 on the #31 protocol, with the #31 batch sizes (0.6B 8, 1.7B 4, 4B 1), for all three sizes under the clearer prompt.
The #31 rows are the old-prompt runs; "k-SLMmeans-v2" marks the clearer prompt. Sizes in the tables below are Qwen3 sizes.

### 8.1 Results

| Method | ACC | NMI | ARI | s/seed | seeds |
| --- | ---: | ---: | ---: | ---: | ---: |
| k-means | 0.551 ± 0.007 | 0.748 ± 0.002 | 0.439 ± 0.005 | 5.3 | 5 |
| k-NLPmeans (LSA) | 0.560 ± 0.008 | 0.752 ± 0.004 | 0.449 ± 0.007 | 23.7 | 5 |
| k-SLMmeans (Qwen3-0.6B) | 0.541 ± 0.013 | 0.747 ± 0.003 | 0.437 ± 0.008 | 903.9 | 5 |
| k-SLMmeans (Qwen3-1.7B) | 0.570 ± 0.011 | 0.760 ± 0.006 | 0.461 ± 0.012 | 1247.5 | 5 |
| k-SLMmeans (Qwen3-4B) | 0.511 ± 0.015 | 0.740 ± 0.006 | 0.421 ± 0.010 | 1861.7 | 5 |
| k-SLMmeans-v2 (Qwen3-0.6B) | 0.563 ± 0.008 | 0.755 ± 0.002 | 0.453 ± 0.006 | 381.1 | 5 |
| k-SLMmeans-v2 (Qwen3-1.7B) | 0.563 ± 0.007 | 0.754 ± 0.006 | 0.454 ± 0.010 | 744.4 | 5 |
| k-SLMmeans-v2 (Qwen3-4B) | 0.568 ± 0.010 | 0.760 ± 0.005 | 0.457 ± 0.012 | 1098.8 | 5 |

Mean ± standard deviation over seeds. The s/seed column is not comparable across the old and clearer prompt, and the v2 1.7B
figure is not a clean timing at all (Section 8.4). The k-means and LSA rows are from the #31 LSA run; neither depends on the prompt.

Under the old prompt the means ranged from 0.511 to 0.570 ACC across sizes. Under the clearer prompt they range from 0.563 to 0.568.

### 8.2 Paired differences

Same seed, same step-0 partition, difference per seed, 95% t-interval over the 5 seeds (df = 4). "Wins" is the number of seeds
with a difference above 0. Every method is paired against every other in [`prompt_test_paired.md`](prompt_test_paired.md) and
[`prompt_test_paired.csv`](prompt_test_paired.csv); the rows below are copied from them. The intervals are not corrected for the
many comparisons, and several sit close to 0.

**Clearer prompt against the old prompt, same size** (v2 minus old):

| Size | ACC | NMI | ARI |
| --- | --- | --- | --- |
| 0.6B | +0.022 [+0.010, +0.033], 5/5 | +0.008 [+0.004, +0.012], 5/5 | +0.016 [+0.005, +0.027], 5/5 |
| 1.7B | -0.007 [-0.023, +0.010], 1/5 | -0.006 [-0.016, +0.003], 1/5 | -0.008 [-0.025, +0.010], 1/5 |
| 4B | +0.056 [+0.039, +0.074], 5/5 | +0.021 [+0.013, +0.029], 5/5 | +0.036 [+0.019, +0.053], 5/5 |

**Clearer prompt against k-means and LSA** (v2 minus reference):

| Size | Reference | ACC | NMI | ARI |
| --- | --- | --- | --- | --- |
| 0.6B | k-means | +0.011 [+0.005, +0.017], 5/5 | +0.007 [+0.005, +0.008], 5/5 | +0.014 [+0.008, +0.021], 5/5 |
| 1.7B | k-means | +0.012 [+0.005, +0.018], 5/5 | +0.006 [+0.001, +0.011], 5/5 | +0.015 [+0.005, +0.025], 5/5 |
| 4B | k-means | +0.016 [+0.009, +0.023], 5/5 | +0.012 [+0.007, +0.017], 5/5 | +0.018 [+0.007, +0.029], 5/5 |
| 0.6B | LSA | +0.002 [-0.006, +0.010], 3/5 | +0.002 [-0.000, +0.005], 4/5 | +0.004 [-0.004, +0.012], 3/5 |
| 1.7B | LSA | +0.003 [-0.003, +0.008], 3/5 | +0.002 [-0.004, +0.007], 3/5 | +0.004 [-0.006, +0.015], 3/5 |
| 4B | LSA | +0.007 [-0.001, +0.016], 5/5 | +0.008 [+0.002, +0.014], 5/5 | +0.008 [-0.002, +0.017], 4/5 |

**Size order under the clearer prompt** (larger v2 size minus smaller v2 size):

| Comparison | ACC | NMI | ARI |
| --- | --- | --- | --- |
| 1.7B minus 0.6B | +0.000 [-0.002, +0.003], 4/5 | -0.001 [-0.006, +0.004], 3/5 | +0.000 [-0.008, +0.009], 3/5 |
| 4B minus 0.6B | +0.005 [-0.002, +0.012], 4/5 | +0.006 [+0.000, +0.011], 4/5 | +0.004 [-0.005, +0.013], 3/5 |
| 4B minus 1.7B | +0.005 [-0.003, +0.012], 4/5 | +0.006 [+0.002, +0.011], 5/5 | +0.003 [-0.003, +0.010], 3/5 |

For comparison, the same table under the old prompt (old larger minus old smaller, from the same file):

| Comparison | ACC | NMI | ARI |
| --- | --- | --- | --- |
| 1.7B minus 0.6B | +0.029 [+0.009, +0.048], 5/5 | +0.013 [+0.009, +0.017], 5/5 | +0.024 [+0.015, +0.033], 5/5 |
| 4B minus 0.6B | -0.030 [-0.051, -0.008], 0/5 | -0.008 [-0.015, -0.001], 1/5 | -0.017 [-0.029, -0.004], 0/5 |
| 4B minus 1.7B | -0.059 [-0.072, -0.045], 0/5 | -0.021 [-0.027, -0.015], 0/5 | -0.040 [-0.053, -0.028], 0/5 |

- **0.6B.** The clearer prompt raises ACC by 0.022 on all 5 seeds, and NMI and ARI move the same way. The old 0.6B was
  below k-means and LSA on ACC; the v2 0.6B is above k-means and level with LSA.
- **1.7B.** The change is -0.007 ACC [-0.023, +0.010], higher on 1 of 5 seeds, and the NMI and ARI intervals include 0 too.
  The data do not say whether the clearer prompt helped or hurt the 1.7B. The point estimate is slightly negative and the
  interval is about 0.03 wide. It is not called "worse".
- **4B.** Higher by 0.056 on 5 of 5 seeds, as before.
- **Against k-means** all three v2 sizes are above on all three metrics with intervals that exclude 0, by 0.011 to 0.016 ACC.
  Under the old prompt that held only for the 1.7B (+0.018 [+0.004, +0.033]).
- **Against LSA** no v2 size is separated on ACC or ARI (all intervals include 0). Only the 4B's NMI interval excludes 0
  (+0.008 [+0.002, +0.014]); the 0.6B's NMI interval ends at -0.000.
- **Size order under the clearer prompt.** On ACC and ARI no pair of sizes is separated: all six intervals include 0, and
  the means are 0.563, 0.563 and 0.568. On NMI the 4B is ahead of the 0.6B and the 1.7B by 0.006 (lower bounds +0.000 and +0.002).
  That is a small difference, in one of three metrics, on 5 seeds, among nine uncorrected intervals, and it does not
  separate the 0.6B from the 1.7B. It is not read as an order. Under the old prompt every pair was separated on all three
  metrics (the 4B against the 0.6B on NMI only just, upper bound -0.001): the 1.7B was above the 0.6B, and the 4B was below both.

**What was checked before pairing.** The pairing needs each v2 run and its #31 run to differ only in the prompt and to start
from the same step-0 partition. This was checked for all three sizes.

- Config: `diff` of the `config.yaml` saved in each v2 run directory against its old counterpart shows the same four
  differences at every size. `name` and `method_name` (labels), the added `summarizer.prompt`, and the added `gpu_check` policy
  (the monitor, no effect on results). The old configs also list `baselines: kmeans` (the k-means row, not rerun here).
  Model, batch size (0.6B 8, 1.7B 4, 4B 1), `max_new_tokens`, `max_input_tokens`, schedule, `tol`, seeds, embedder and dataset are identical.
- Step-0 partition: `step0_sha1` (a hash of the step-0 labels) is identical per seed between each v2 run and its old run, and across all
  sizes (seeds 0-4: 2b3858a9, 41db4cd8, 4f942754, 142872d5, f74393e0; the paired script's own check agrees, "step0_sha1 shared across all methods for seeds 0-4: yes").
  The step-0 `inertia` in `trace.jsonl` agrees between each v2 run and its old run for all five seeds to float32 rounding (largest
  difference 0.001 in about 10,700, at every size). The k-means row is the same in all #31 runs (ACC 0.5473, 0.5600, 0.5569, 0.5495, 0.5437).
- Code revision: the old runs ran at git 8222515 and the three v2 runs at 341e420 (`environment.json`, clean tree in all six). The changes in
  `src` between them are meant to be behavior-neutral at default settings (summary guard off, `max_words_per_text` None).
  Evidence for that: Section 4 shows this code regenerates the old-prompt logged summaries exactly (150 of 150 at every size),
  and `step0_sha1` and the step-0 inertia match. It is not a proof for later steps.
- Not checked: the step-1 summaries' inputs. They are the same by construction (same partition and member selection), and
  the pilot (Section 4) showed the same inputs reproduce the logged summaries exactly. After step 1 the partitions
  differ between prompts, as they should.

### 8.3 Surface counts on the full runs

From `scripts/surface_counts.py`, pooled over the 5 seeds and 5 summary steps (750 summaries per step set, 3,750 per run), with the
rules of Section 1 and of `clinc150_summarizers.md` §2.4. The table is in [`prompt_test_surface.md`](prompt_test_surface.md).

| Run | Summaries | Mean words | End with "?" | Mention the cluster | Final step: mention | Final step: clusters in an identical-summary group, per seed | Largest group | Start with a quote mark |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v2 4B | 3,750 | 10.9 | 2,300 (61%) | 0 (0%) | 0/750 | 0-2 | 2 | 0 |
| v2 1.7B | 3,750 | 13.5 | 3,706 (99%) | 0 (0%) | 0/750 | 0 | 0 | 0 |
| v2 0.6B | 3,750 | 8.7 | 3,452 (92%) | 0 (0%) | 0/750 | 0 | 0 | 13 |
| old 4B | 3,750 | 17.7 | 3,205 (85%) | 1,291 (34%) | 272/750 | 16-21 | 13 | 25 |
| old 1.7B | 3,750 | 21.0 | 3,623 (97%) | 316 (8%) | 68/750 | 0-4 | 2 | 0 |
| old 0.6B | 3,750 | 11.2 | 3,301 (88%) | 314 (8%) | 69/750 | 0-5 | 3 | 2 |

- The pilot's result holds over the whole run at every size: no v2 summary mentions the cluster, against 34% (4B) and 8% (1.7B,
  0.6B) under the old prompt. The 4B's final-step identical-summary groups go from 16-21 clusters per seed to 0-2, and the
  other two sizes have none at the final step.
- Summaries are shorter at the 4B and 1.7B (10.9 against 17.7 and 13.5 against 21.0 words) and a little shorter at the 0.6B (8.7 against 11.2).
  The sizes are also closer to each other: 8.7 to 13.5 words under the clearer prompt, 11.2 to 21.0 under the old one.
- The 4B's share ending in "?" is 61% (old 85%), below the pilot's 65% at step 1. The pilot (Section 6) found that the "?"-less ones
  are lowercase copies of the users' style; the full run was not read for this. The 1.7B and 0.6B share barely moves (99% and 92%).
- The 0.6B has 13 summaries starting with a quote mark under the clearer prompt, against 2 under the old one. This is
  small (0.3%), and the quote handling of #36 question 3 is not looked at here. No `<think>` text in any run.
- These are counts of form. They say the clearer prompt removed the cluster-talk and duplicate failure, not that the summaries represent their clusters better.

### 8.4 Cost

From `--cost-md` ([`prompt_test_cost.md`](prompt_test_cost.md), the six SLM rows here; the file has all rows); mean ± std over seeds.

| Run | Calls | Input tokens | Output tokens | Summarizer s | Total s | Truncated clusters | Dropped texts |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| old 0.6B | 707 ± 7 | 1,113,037 ± 8,773 | 10,227 ± 211 | 895.8 ± 29.7 | 903.9 ± 29.6 | 6.6 ± 3.5 | 173.0 ± 147.1 |
| v2 0.6B | 689 ± 2 | 1,120,788 ± 8,825 | 7,806 ± 79 | 373.4 ± 8.5 | 381.1 ± 8.3 | 5.2 ± 2.8 | 167.4 ± 102.9 |
| old 1.7B | 702 ± 6 | 1,101,755 ± 11,449 | 18,288 ± 387 | 1238.6 ± 102.5 | 1247.5 ± 103.4 | 6.8 ± 2.4 | 304.0 ± 42.8 |
| v2 1.7B | 701 ± 6 | 1,137,714 ± 3,013 | 11,239 ± 47 | 737.0 ± 198.1 | 744.4 ± 199.3 | 4.2 ± 2.4 | 113.8 ± 63.0 |
| old 4B | 714 ± 6 | 1,120,190 ± 7,604 | 15,620 ± 463 | 1855.0 ± 188.6 | 1861.7 ± 189.8 | 10.2 ± 3.4 | 502.4 ± 264.2 |
| v2 4B | 698 ± 10 | 1,131,772 ± 11,868 | 9,068 ± 185 | 1093.7 ± 20.7 | 1098.8 ± 20.6 | 3.8 ± 2.2 | 86.2 ± 69.0 |

- **Do not read the drop in s/seed as an effect of the prompt.** The #31 timings were inflated about 1.7 times by another process on
  the card (see `clinc150_summarizers.md`, Section 3 and its summary line on cost, the header of `scripts/run_clinc150_prompt_v2.sh`, and #35).
  The v2 runs were idle-checked before they started, but the two prompts differ in output length as well as in contention,
  and the data cannot split them. The clean comparison is the #35 re-time of the old-prompt runs under idle checks, which is running now and is not in this file.
- **What can be said about concurrency during the v2 runs.**
  - *Queue.* The run queue (`results/runq`) runs one job at a time and waits for three idle GPU samples before each. Its status
    file shows `bbc_dense` done at 20:08:53 and `v2_small` (the v2 0.6B then the v2 1.7B, one script call) from 20:09:13 to 21:43:43, at git 341e420 with a clean
    tree and an idle line (1,216 MiB, 1% utilization, 43 W) before it. The next entry is on 2026-11-16. So no other queued
    job overlapped the 0.6B and 1.7B runs. The v2 4B is the same: guard run done 18:12:18, v2 4B 18:12:38-19:44:35, next job 19:44:56.
  - *Start checks.* Each run's `gpu.json` records an idle check before the model loaded: 0.6B 20:09:19 and 1.7B 20:41:18, median 1,216 MiB, 0-1%
    utilization, 43-45 W, "median sample within all thresholds".
  - *Not covered by the GPU check.* Light CPU work for other issues (test suites and report scripts) ran at times, and from about 20:10 to
    21:00 a niced multi-core CPU replay (`replacement_diagnostic.py`) ran for another issue (from the job notes; it is not recorded in
    these run directories). The GPU check does not look at CPU, so the timings cannot be called free of CPU contention.
  - *In-run monitor* (`gpu.json`, `gpu_samples.csv`, a sample every 5 s; the estimate is used memory minus what torch has reserved).
    The 4B (1,092 samples) and the 0.6B (380 samples) stay flat at 1,319-1,355 MiB, 139 MiB above the pre-run baseline
    of 1,216 MiB. **The 1.7B (739 samples) does not.** Its estimate is 1,319-1,355 MiB for the first 25 minutes,
    about 1,500-1,530 MiB from 21:06:40, 2,309-2,841 MiB from 21:09:51 (peak 2,841 at 21:21:38, +1,625 MiB over baseline),
    and about 2,490-2,530 MiB from 21:32:48 to the end at 21:43:30.
  - *Per-seed times of the 1.7B.* The summarizer took 568, 590 and 622 s on seeds 0-2 (mean 593 s) and 965 and 941 s on seeds 3 and 4,
    about 1.6 times longer, with about the same number of calls (697-711 on every seed) and the same tokens (11,188-11,284 output tokens on every seed). The first rise in the memory estimate
    is in the last two minutes of seed 2. The 0.6B's seeds are all 360-382 s.
  - *What this means.* The memory estimate counts every non-torch use of the card: other processes (the idle check lists Windows
    desktop processes on the card, with no memory attributed to them) and non-torch memory inside this process. It cannot tell which
    one grew. The slowdown at identical call counts, the same thing that inflated the #31 timings, makes another process on the
    card likely, but this is not shown. The replay was over by then (about 21:00). The v2 1.7B s/seed (744.4 ± 199.3) is therefore
    **not** treated as a timing. Its first three seeds (mean 593 s) are the cleaner figure, and even those are one run, not a #35 measurement.
  - *Does it touch the scores?* Greedy decoding at a fixed batch size gives the same outputs (Section 4), so contention should change the time and
    not the summaries. The 1.7B's ACC on seeds 3 and 4 (0.565, 0.551) is in the range of the others (0.564, 0.564, 0.571). This is a reason to
    expect no effect, not a test of it.
- **Tokens are not affected by contention.** Output tokens per seed fall from 15,620 to 9,068 (-42%, 4B), 18,288 to 11,239 (-39%, 1.7B)
  and 10,227 to 7,806 (-24%, 0.6B), in line with the pilot's -37.5%, -36% and -20% at step 1. Input tokens rise by 1.0%, 3.3% and 0.7%: the
  instruction is longer, and the members differ after step 1.
- The call counts are 689, 701 and 698 against 707, 702 and 714. Calls are made for clusters whose summary has to be rewritten, so they depend on how the
  partitions move. The differences are small (0.1% to 2.5%) and are not read as an effect.
- Peak GPU memory is the same under both prompts at each size (6.51, 6.54 and 9.25 GB allocated).
- Truncation: the v2 logs warn once per summarizer (for example, `dropped 19 of 370 text(s)` in the 0.6B, `dropped 10 of 365 text(s)` in the 1.7B). The warning is printed once, so the counts come
  from the metrics: 3-10, 2-8 and 1-7 truncated clusters per seed (0.6B, 1.7B, 4B) and 15-347 dropped texts, in about 700 calls. The figures are lower
  than under the old prompt at the 1.7B and 4B and close at the 0.6B, but they depend on the partitions of later steps, so they are not a
  prompt effect. The truncation rate on the #15 runs is in [`rq2_truncation_check.md`](rq2_truncation_check.md) (#37).
- One more timing point: the guarded 4B run (`results/clinc150_guard_qwen3-4b/20261112-160734`, old prompt, batch 1, seeds 0-4,
  idle-checked at start) had a mean summarizer time of 1488.6 s per seed (676.6 calls, 14,937 output tokens), between 1855 and
  1094. It follows different partitions (the guard) and overlapped CPU reruns of #33, #47 and #50 for about its first hour
  (timing caveat in `summary_guard.md`), so it does not split contention from prompt either.

### 8.5 Lloyd iterations

`trace.jsonl` has 30 records per run (6 k-means fits per seed, 5 seeds), and in every one `last_n_iter` equals the cap
`last_max_iter` of 20, in the old 4B and in all three v2 runs (120 iterations per seed). `metrics.jsonl` has `converged` False for all 5 seeds in those runs. The counts
do not depend on the prompt. They only show that these runs did not converge by the cap. The old 0.6B and 1.7B were not re-read for this.

### 8.6 Reading

The question of #46 has two parts: does a clearer prompt change the 4B results, and does the order of the sizes change?

What the runs show:

- **The 4B changes a lot.** It scores 0.568 ACC against 0.511, +0.056 [+0.039, +0.074] on the same seeds and step-0 partitions, higher on all 5 seeds.
  NMI and ARI move the same way (+0.021, +0.036). It goes from below k-means on 5 of 5 seeds (-0.040) to above it on 5 of 5 (+0.016), and
  is not separated from LSA on ACC (+0.007 [-0.001, +0.016]) or ARI, only on NMI (+0.008 [+0.002, +0.014]).
- **The 0.6B also gains** (+0.022 ACC [+0.010, +0.033], 5/5), to a level above k-means and level with LSA.
- **The 1.7B does not detectably change:** -0.007 ACC [-0.023, +0.010], 1 of 5 seeds higher. The interval is compatible with a small loss
  or a small gain. Its advantage over k-means is +0.012 [+0.005, +0.018] under the clearer prompt and was +0.018 [+0.004, +0.033] under the old one.
- **The size order is not detectable under the clearer prompt.** The three means are 0.563, 0.563 and 0.568 ACC. The paired ACC and ARI intervals
  between sizes all include 0, and only the 4B's small NMI edge (+0.006 over each smaller size) has intervals that exclude 0. Under the old
  prompt the order was clear (1.7B above 0.6B above 4B, ACC differences of 0.029 to 0.059, all intervals excluding 0). So the order
  changes: from a clear one to none that these 5 seeds can resolve. In particular, the 4B is no longer last.
- **The surface failure is gone at every size.** No v2 summary mentions the cluster, and the identical-summary groups are 0-2 clusters per seed at
  the 4B and 0 at the other sizes (Section 8.3).
- This is consistent with #47. There, the 4B's flagged summaries (duplicates and cluster mentions) were worse than the 1.7B's
  at step 1, but replacing them with the k-means centroid did not bring the 4B back above k-means (+0.009 [-0.006, +0.024]).
  The clearer prompt changes every summary, not only the flagged third (10.9 against 17.7 words, 61% against 85% ending in "?" for the 4B),
  so these runs do not show that the gain comes from removing the flagged summaries.

What it does not show:

- It is one prompt change that altered several things in the wording at once (the task, the "same style", "write only the question",
  and the banned words). It does not say which of them matters. No test of single parts was run.
- The prompt was chosen by the 4B's surface counts (Section 3). The other two sizes had few such failures, so the change was fitted to the 4B's
  problem, not tuned for each size. The gains at the 0.6B and 4B and the null at the 1.7B should not be read as a ranking of how the sizes "like" the prompt.
- It is one dataset (CLINC150) and 5 seeds. The intervals are narrow for the old-versus-new comparison at the 4B and 0.6B and wide for the
  comparison at the 1.7B and for the comparisons with LSA. "Not detectable" means not detectable with 5 seeds: differences of about 0.005 ACC between the
  sizes cannot be ruled out, and seeds 5-9 (#36 question 2) would narrow the intervals.
- It does not say the summaries are better or more faithful: the surface counts measure form. #33 and #34 look at that.
- It does not give a prompt effect on cost (Section 8.4), and the v2 1.7B timing is not clean.
- Truncation affected some clusters' prompts in all runs (Section 8.4).

Per the reading rule of the issue, the 4B recovers to the level of k-means and above it, and to the level of the other two sizes. So the
old size comparison was confounded by how the sizes read the prompt, and sizes have to be reported under both prompts.

### 8.7 What this means for the size trend (#36)

The October finding was that quality does not rise with size (Bank77 NMI 0.645 / 0.648 / 0.648; CLINC150 with the 4B last and the 1.7B first). With both
prompts on CLINC150 (ACC, mean ± std over seeds 0-4; differences are larger size minus smaller size, 95% interval, seeds above 0):

| Prompt | 0.6B | 1.7B | 4B | 1.7B minus 0.6B | 4B minus 0.6B | 4B minus 1.7B |
| --- | ---: | ---: | ---: | --- | --- | --- |
| Old (#31) | 0.541 ± 0.013 | 0.570 ± 0.011 | 0.511 ± 0.015 | +0.029 [+0.009, +0.048], 5/5 | -0.030 [-0.051, -0.008], 0/5 | -0.059 [-0.072, -0.045], 0/5 |
| Clearer (v2) | 0.563 ± 0.008 | 0.563 ± 0.007 | 0.568 ± 0.010 | +0.000 [-0.002, +0.003], 4/5 | +0.005 [-0.002, +0.012], 4/5 | +0.005 [-0.003, +0.012], 4/5 |

- The shape of the size comparison on CLINC150 depends on the prompt: a non-monotone order with the 4B last under the old one, and no detectable ACC difference
  between sizes under the clearer one. So the "missing size trend" of October is not a property of size alone. Part of it was the 4B reading
  the old CLINC150 prompt as a request to describe the cluster.
- This does not establish a size trend either way. Under the clearer prompt the means rise by 0.005 from the 0.6B/1.7B to the 4B, with intervals that include 0 (NMI
  is the exception, +0.006), and the tests have no power to separate effects of that size. A size threshold is not supported, and neither is a flat line; the data are consistent with both a null and a small
  positive effect of the 4B.
- Open for #36: Bank77 under a clearer prompt (not run), seeds 5-9, the quote artifacts and batch-size questions (3 and 4), and the
  Qwen3 training differences (6), which a one-family comparison cannot separate from parameter count.

### 8.8 Run directories handed on

- v2 4B, for #33 (replacement diagnostic) and #34 (summary quality): `results/clinc150_v2_qwen3-4b/20261112-181256`
  (git 341e420, clean tree, GPU idle-checked; has `gpu.json` and `gpu_samples.csv`).
- v2 0.6B: `results/clinc150_v2_qwen3-0.6b/20261112-200926` (git 341e420, clean tree, idle-checked, flat in-run monitor).
- v2 1.7B: `results/clinc150_v2_qwen3-1.7b/20261112-204127` (git 341e420, clean tree, idle-checked at start; the in-run monitor shows
  extra non-torch GPU memory from 21:09, Section 8.4, so use its seconds with care; the scores and summaries are unaffected as far as we know).
- The old-prompt runs they pair with: `results/clinc150_lsa/20261027-174631`, `results/clinc150_qwen3-0.6b/20261027-190908`,
  `results/clinc150_qwen3-1.7b/20261027-202532`, `results/clinc150_qwen3-4b/20261027-221042`.

## Reproduce

Run in the checkout that holds `results/` and `cache/` (CPU only, no model runs):

```bash
# Pilot (Sections 1-7)
python scripts/compare_workloads.py $(for n in old_4b v2_4b old_1.7b v2_1.7b old_0.6b v2_0.6b; do ls -d results/fixed_workload/pilot_$n/* | sort | tail -1; done)
python scripts/prompt_test_pilot.py --out-csv docs/results/prompt_test_pilot.csv --out-examples docs/results/prompt_test_pilot_examples.md
```

The pilot directories were made with `scripts/fixed_workload.py` (README, "Prompt test and fixed workloads (#46)").

Main runs (Section 8), GPU, one size at a time on an idle card:

```bash
PYTHON=/path/to/venv/bin/python scripts/run_clinc150_prompt_v2.sh 4b
PYTHON=/path/to/venv/bin/python scripts/run_clinc150_prompt_v2.sh 0.6b 1.7b
```

Tables for Section 8 (all seven runs; CPU only):

```bash
OLD="results/clinc150_lsa/20261027-174631 results/clinc150_qwen3-0.6b/20261027-190908 results/clinc150_qwen3-1.7b/20261027-202532 results/clinc150_qwen3-4b/20261027-221042"
V2="results/clinc150_v2_qwen3-0.6b/20261112-200926 results/clinc150_v2_qwen3-1.7b/20261112-204127 results/clinc150_v2_qwen3-4b/20261112-181256"

python scripts/aggregate_results.py $OLD $V2 \
    --paired-md docs/results/prompt_test_paired.md --paired-csv docs/results/prompt_test_paired.csv \
    --references "k-means" "k-NLPmeans (LSA)" \
    "k-SLMmeans (Qwen3-0.6B)" "k-SLMmeans (Qwen3-1.7B)" "k-SLMmeans (Qwen3-4B)" \
    "k-SLMmeans-v2 (Qwen3-0.6B)" "k-SLMmeans-v2 (Qwen3-1.7B)" "k-SLMmeans-v2 (Qwen3-4B)"
python scripts/aggregate_results.py $OLD $V2 --out-md /dev/null --cost-md docs/results/prompt_test_cost.md
python scripts/surface_counts.py results/clinc150_v2_qwen3-4b/20261112-181256 results/clinc150_v2_qwen3-1.7b/20261112-204127 \
    results/clinc150_v2_qwen3-0.6b/20261112-200926 results/clinc150_qwen3-4b/20261027-221042 \
    results/clinc150_qwen3-1.7b/20261027-202532 results/clinc150_qwen3-0.6b/20261027-190908 > docs/results/prompt_test_surface.md
```

The first command without `--paired-*` (or `scripts/run_clinc150_prompt_v2.sh table`) prints the Section 8.1 table. The
Lloyd iteration counts (Section 8.5) were read from each run's `trace.jsonl` (`last_n_iter`, `last_max_iter`). The concurrency
figures in Section 8.4 come from `results/runq/status.txt` and `results/runq/logs/v2_small.log`, and from each run's `gpu.json` and `gpu_samples.csv`.
