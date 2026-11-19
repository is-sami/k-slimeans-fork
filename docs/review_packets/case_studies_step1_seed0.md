**Open this only after you have submitted your #34 ratings.**

# Cluster case studies, CLINC150 seed 0, step 1 (issue #50, for Samiksha)

This packet shows which model wrote which summary. The #34 hand check has to stay blind, so please finish and submit those ratings first.

Regenerate: `python scripts/export_review_packets.py --results-root ../../k-slimeans/results --out-dir docs/review_packets` (reads the gitignored logged runs of the main checkout; `scripts/export_review_packets.py`).

## How the clusters were chosen

The rule was fixed before any text was read and uses numbers only.

- **Runs:** the five CLINC150 runs with an exact #33 replay: extractive (LSA), Qwen3 0.6B, 1.7B and 4B with the old
  prompt, and Qwen3 4B with the clearer prompt (#46). Seed 0, first summary step (step 1 in #33's numbering). All five
  start from the same step-0 partition, so cluster `c` has the same members in each; this is checked when the packet is
  built.
- **Measure:** for a cluster, the share of its members whose gold intent is the majority intent of the cluster they are in
  after the step's Lloyd block, minus the cluster's purity before (`d_member_purity`, `synthesis.md` section 1); then minus
  the same change under the no-replacement counterfactual (plain Lloyd from the same step-0 state, `synthesis.md` section
  5). That difference is the **selection number**. Positive means helped, negative hurt.
- **Rule:** the 10 largest positive and the 10 most negative selection numbers over all (run, cluster) pairs, with at most
  4 per run on each side. Candidates are taken in rank order; a candidate is skipped if its run already has
  4 on that side, or (first pass) if its cluster id is already on that side. If the first pass cannot fill 10,
  a second pass takes the next-ranked candidates without the distinct-id condition (the cap still holds).
  Equal scores are ordered by run (LSA, 0.6B, 1.7B, 4B, 4B clearer prompt) and then by cluster id.
- **Rank** is the pick order within a side (pass 1 first, then pass 2), not strictly the score order.
- **This packet:** helped: extractive (LSA) (1), Qwen3-0.6B, old prompt (4), Qwen3-1.7B, old prompt (1), Qwen3-4B, old prompt (3), Qwen3-4B, clearer prompt (1); hurt: Qwen3-0.6B, old prompt (3), Qwen3-1.7B, old prompt (2), Qwen3-4B, old prompt (4), Qwen3-4B, clearer prompt (1). 0 of the 20 came from the second pass (a repeated cluster id on its side).
- **Purity ceiling:** a cluster with purity above 0.9 cannot be helped by much (purity cannot exceed 1), so the helped side is
  mostly clusters that were mixed before, and the hurt side is where a pure cluster had room to fall. This selection
  therefore shows the extremes of one measure, not a random sample of clusters.
- **Not shown:** the automatic quality scores and flags (#34). Judge coverage yourself.
- **Members:** samples of up to 10 are random with a fixed seed. "Left" members are those of the cluster that sit in
  another cluster after the Lloyd block; for each, the majority intent of its new cluster is given. "Arrived" members are
  in the cluster after the block and were elsewhere before.
- LSA is called "extractive": its summary is a few sentences copied from the members.

## How to write each case

For each cluster, write 3 to 5 lines:

- what the cluster was (which intents, and how mixed);
- what the summary covers and what it misses;
- whether the members that left were the ones the summary didn't cover;
- a one-line verdict (helped because ..., hurt because ...).

Then add a short paragraph across all 20: what the helped cases have in common, what the hurt ones have in common, and
**any case that contradicts the synthesis**. Flag those clearly; they matter most.

Check the Arrived list as well: a cluster can be hurt because arrivals change its majority intent, even when few of its own
members leave (the measure follows the cluster's own members to wherever they end up).

Read `docs/results/synthesis.md`
section 9 first for context. Deliver `docs/results/synthesis_case_studies.md` in a PR (#50). Don't run anything or change
the analysis code.

## The 20 clusters

### Helped 1: Qwen3-4B, old prompt, cluster 92

- **Size:** 136 members; **purity before:** 0.49
- **Selection number:** +0.404 = change in member purity +0.404 minus the no-replacement counterfactual +0.000
- **Gold intents before:** change\_speed 66 (49%), change\_volume 60 (44%), whisper\_mode 3 (2%), what\_song 2 (1%), definition 1 (1%)

**Summary**

```text
What are the common requests users have for adjusting the speech speed and volume of the assistant?
```

**Sample of 10 members before the step**

- please speed up your speaking pattern _(gold: change\_speed)_
- speed up your speech _(gold: change\_speed)_
- can you speak a little faster, please _(gold: change\_speed)_
- make my volume louder please _(gold: change\_volume)_
- the speaker volume needs to be increased _(gold: change\_volume)_
- speed up your rate of speech _(gold: change\_speed)_
- could you speak faster _(gold: change\_speed)_
- can you talk faster _(gold: change\_speed)_
- double the speaking speed please _(gold: change\_speed)_
- speed up speech please _(gold: change\_speed)_

**Left the cluster** (75 of 136; showing 10), with the majority intent of the cluster each went to

- can you speed up your speech please _(gold: change\_speed; went to a cluster mostly about change\_speed)_
- please increase the speed of your talking _(gold: change\_speed; went to a cluster mostly about change\_speed)_
- i'd like you to talk faster _(gold: change\_speed; went to a cluster mostly about change\_speed)_
- i need you to speak faster _(gold: change\_speed; went to a cluster mostly about change\_speed)_
- talker faster please _(gold: change\_speed; went to a cluster mostly about change\_speed)_
- why are you talking so sloooooooooowly, please speed it up! _(gold: change\_speed; went to a cluster mostly about change\_speed)_
- is it possible to speed up of your replies _(gold: change\_speed; went to a cluster mostly about change\_speed)_
- please speak faster _(gold: change\_speed; went to a cluster mostly about change\_speed)_
- speak more quickly _(gold: change\_speed; went to a cluster mostly about change\_speed)_
- speed up speech please _(gold: change\_speed; went to a cluster mostly about change\_speed)_

**Arrived** (4 documents; showing 4)

- i need you to your volume _(gold: change\_volume; came from cluster 52)_
- please your volume _(gold: change\_volume; came from cluster 52)_
- i want you to your volume _(gold: change\_volume; came from cluster 52)_
- can you play right above it _(gold: play\_music; came from cluster 112)_

### Helped 2: extractive (LSA), cluster 73

- **Size:** 133 members; **purity before:** 0.53
- **Selection number:** +0.398 = change in member purity +0.398 minus the no-replacement counterfactual +0.000
- **Gold intents before:** insurance 70 (53%), vaccines 51 (38%), insurance\_change 3 (2%), directions 2 (2%), carry\_on 1 (1%)

**Summary**

```text
what health benefits do i have
do i need to get vaccines before my trip
can you let me know what health plan i'm on
which vaccines are meant for cuba
do i need vaccinations to travel there
```

**Sample of 10 members before the step**

- what health benefits are available to me _(gold: insurance)_
- are my health benefits good _(gold: insurance)_
- can i obtain health benefits _(gold: insurance)_
- what was my health plan again _(gold: insurance)_
- do i need any vaccinations before going to indonesia _(gold: vaccines)_
- will this trip require vaccines _(gold: vaccines)_
- what are my health benefits like _(gold: insurance)_
- could you list my health benefits _(gold: insurance)_
- can you tell me what health plan i am on _(gold: insurance)_
- google find out what health plan i am under _(gold: insurance)_

**Left the cluster** (80 of 133; showing 10), with the majority intent of the cluster each went to

- what health benefits do i have _(gold: insurance; went to a cluster mostly about insurance)_
- i need to know more about my health plan _(gold: insurance; went to a cluster mostly about insurance)_
- what's the deal with my health care _(gold: insurance; went to a cluster mostly about insurance)_
- what healthcare plan do you have me on _(gold: insurance; went to a cluster mostly about insurance)_
- can i see my health benefits _(gold: insurance; went to a cluster mostly about insurance)_
- tell me my health plan _(gold: insurance; went to a cluster mostly about insurance)_
- what is the definition of my health benefits _(gold: insurance; went to a cluster mostly about insurance)_
- what are the details on my health care plan _(gold: insurance; went to a cluster mostly about insurance)_
- what are my health insurance benefits _(gold: insurance; went to a cluster mostly about insurance)_
- google find out what health plan i am under _(gold: insurance; went to a cluster mostly about insurance)_

**Arrived** (3 documents; showing 3)

- can i use something else if i don't have eggs _(gold: ingredient\_substitution; came from cluster 87)_
- what vaccinations do i needs to travel to paris _(gold: vaccines; came from cluster 139)_
- what vaccinations are required to enter paris from outside the country _(gold: vaccines; came from cluster 139)_

### Helped 3: Qwen3-4B, old prompt, cluster 46

- **Size:** 77 members; **purity before:** 0.23
- **Selection number:** +0.364 = change in member purity +0.364 minus the no-replacement counterfactual +0.000
- **Gold intents before:** book\_flight 18 (23%), distance 9 (12%), time 7 (9%), carry\_on 6 (8%), timezone 6 (8%)

**Summary**

```text
What is the summary of the following cluster of questions?
```

**Sample of 10 members before the step**

- how long before i get to dallas , in time, not miles _(gold: distance)_
- find the applicable timezone for austin _(gold: timezone)_
- can you help me find my luggage it was lost on delta flight abc123 from houston _(gold: lost\_luggage)_
- let me know how many carry ons i can take on a flight with southwest airlines to dallas _(gold: carry\_on)_
- i want to fly southwest from dallas to phoenix _(gold: book\_flight)_
- can my car get to dallas with the gas currently in my tank _(gold: gas)_
- could i rent a car out of dallas from april 1-10 _(gold: car\_rental)_
- can you tell me what time it is in dallas _(gold: time)_
- how is the weather in austin _(gold: weather)_
- tell me what meal to eat from texas _(gold: meal\_suggestion)_

**Left the cluster** (76 of 77; showing 10), with the majority intent of the cluster each went to

- what time is it in fredericksburg, tx _(gold: time; went to a cluster mostly about time)_
- how long will it take me to get to the mcdonald's in the city _(gold: distance; went to a cluster mostly about restaurant\_reviews)_
- find the applicable timezone for austin _(gold: timezone; went to a cluster mostly about time)_
- tell me how many carry ons i can take on a flight with southwest airlines to dallas _(gold: carry\_on; went to a cluster mostly about carry\_on)_
- i'd like you to book me a room in austin near google's headquarters from january 01, 2020 to february 02, 2020 _(gold: book\_hotel; went to a cluster mostly about book\_hotel)_
- show me roundtrip flights from dallas to houston for march 7 and march 10 _(gold: book\_flight; went to a cluster mostly about book\_flight)_
- are there 8pm tables available at texas roadhouse _(gold: restaurant\_reservation; went to a cluster mostly about confirm\_reservation)_
- what is the timezone for houston _(gold: timezone; went to a cluster mostly about time)_
- give me some ideas of what to do during my trip to dallas _(gold: travel\_suggestion; went to a cluster mostly about distance)_
- where do i go if i am seeking the routing number of dallas capital _(gold: routing; went to a cluster mostly about routing)_

**Arrived** (209 documents; showing 10)

- plase hold my account for now _(gold: freeze\_account; came from cluster 51)_
- i'm traveling between denver and la so tell my bank _(gold: travel\_notification; came from cluster 2)_
- i need to let my bank know i am traveling to detroit _(gold: travel\_notification; came from cluster 2)_
- i'm traveling to ca soon and want to inform my bank _(gold: travel\_notification; came from cluster 2)_
- alert the bank that i am traveling to tokyo on the 7th until the 21st _(gold: travel\_notification; came from cluster 2)_
- tell my bank i will be in brazil from june 1st to july 1st _(gold: travel\_notification; came from cluster 0)_
- clear all settings in a reset _(gold: reset\_settings; came from cluster 133)_
- make sure my calendar is clear for june 1 _(gold: calendar\_update; came from cluster 146)_
- how much time to drive to the closest bank _(gold: distance; came from cluster 62)_
- let my bank know i'm going to be in russia for a month _(gold: travel\_notification; came from cluster 2)_

### Helped 4: Qwen3-0.6B, old prompt, cluster 60

- **Size:** 274 members; **purity before:** 0.44
- **Selection number:** +0.350 = change in member purity +0.350 minus the no-replacement counterfactual +0.000
- **Gold intents before:** where\_are\_you\_from 120 (44%), who\_made\_you 120 (44%), how\_old\_are\_you 21 (8%), meaning\_of\_life 2 (1%), repeat 2 (1%)

**Summary**

```text
What is the purpose of creation?
```

**Sample of 10 members before the step**

- where is your place of origin _(gold: where\_are\_you\_from)_
- where do you hail from _(gold: where\_are\_you\_from)_
- where is the location that you were made _(gold: where\_are\_you\_from)_
- where did you live before here _(gold: where\_are\_you\_from)_
- where were you born _(gold: where\_are\_you\_from)_
- tell me your date of birth _(gold: how\_old\_are\_you)_
- what do you make in a year _(gold: income)_
- who are you manufactured by _(gold: who\_made\_you)_
- what company designed this _(gold: who\_made\_you)_
- when were you made _(gold: how\_old\_are\_you)_

**Left the cluster** (139 of 274; showing 10), with the majority intent of the cluster each went to

- what is your nationality _(gold: where\_are\_you\_from; went to a cluster mostly about where\_are\_you\_from)_
- what is the area that you came from _(gold: where\_are\_you\_from; went to a cluster mostly about where\_are\_you\_from)_
- you came from where _(gold: where\_are\_you\_from; went to a cluster mostly about where\_are\_you\_from)_
- what's your hometown _(gold: where\_are\_you\_from; went to a cluster mostly about where\_are\_you\_from)_
- who is responsible for who you are _(gold: who\_made\_you; went to a cluster mostly about definition)_
- when were you created _(gold: how\_old\_are\_you; went to a cluster mostly about where\_are\_you\_from)_
- tell me your date of birth _(gold: how\_old\_are\_you; went to a cluster mostly about where\_are\_you\_from)_
- you were made where _(gold: where\_are\_you\_from; went to a cluster mostly about greeting)_
- the place you were born is _(gold: where\_are\_you\_from; went to a cluster mostly about where\_are\_you\_from)_
- in what place are you originally from _(gold: where\_are\_you\_from; went to a cluster mostly about where\_are\_you\_from)_

**Arrived** (10 documents; showing 10)

- what company's software engineers gave you life _(gold: who\_made\_you; came from cluster 27)_
- by which company are you designed by _(gold: who\_made\_you; came from cluster 28)_
- to which company is your design accredited to _(gold: who\_made\_you; came from cluster 28)_
- tell me your brand _(gold: who\_made\_you; came from cluster 99)_
- find me a mechanic _(gold: schedule\_maintenance; came from cluster 89)_
- tell me the artist currently playing _(gold: what\_song; came from cluster 126)_
- when did i go to the mechanic _(gold: last\_maintenance; came from cluster 28)_
- tell me how much i make _(gold: income; came from cluster 112)_
- which company were you designed by _(gold: who\_made\_you; came from cluster 28)_
- who controls you _(gold: who\_do\_you\_work\_for; came from cluster 117)_

### Helped 5: Qwen3-4B, old prompt, cluster 129

- **Size:** 183 members; **purity before:** 0.57
- **Selection number:** +0.350 = change in member purity +0.350 minus the no-replacement counterfactual +0.000
- **Gold intents before:** traffic 105 (57%), travel\_alert 68 (37%), travel\_suggestion 4 (2%), current\_location 2 (1%), directions 1 (1%)

**Summary**

```text
What are the current travel alerts for various countries and regions?
```

**Sample of 10 members before the step**

- what street am i on right now _(gold: current\_location)_
- is there traffic up ahead _(gold: traffic)_
- how much traffic is there before the stadium _(gold: traffic)_
- what's the traffic at lexington _(gold: traffic)_
- is traffic heavy on my route to washington _(gold: traffic)_
- is the traffic typically bad at noon on the route to the hopsital _(gold: traffic)_
- if im traveling to the hospital around noon what is the traffic typically like _(gold: traffic)_
- does greece currently have any travel alerts in place _(gold: travel\_alert)_
- is there much traffic between here and work right now _(gold: traffic)_
- i need to know what traffic looks like nearest the smithsonian institute in washington, dc for the next hour _(gold: traffic)_

**Left the cluster** (114 of 183; showing 10), with the majority intent of the cluster each went to

- what's a good use of my time in toronto _(gold: travel\_suggestion; went to a cluster mostly about travel\_suggestion)_
- what's the traffic like on the way to patterson _(gold: traffic; went to a cluster mostly about traffic)_
- give me the traffic at lexington _(gold: traffic; went to a cluster mostly about traffic)_
- i would like to know the traffic in tempe please _(gold: traffic; went to a cluster mostly about traffic)_
- is any traffic on my route to work _(gold: traffic; went to a cluster mostly about traffic)_
- what does traffic look like at 9 en route to the aquarium _(gold: traffic; went to a cluster mostly about traffic)_
- how bad is the traffic on the way to downtown _(gold: traffic; went to a cluster mostly about traffic)_
- how does the traffic look on my way to work right now _(gold: traffic; went to a cluster mostly about traffic)_
- will there be heavy traffic near downtown philadelphia from lincoln drive in the next two hours _(gold: traffic; went to a cluster mostly about traffic)_
- on the way to work is there traffic _(gold: traffic; went to a cluster mostly about traffic)_

**Arrived** (13 documents; showing 10)

- does argentina have a travel alert _(gold: travel\_alert; came from cluster 65)_
- are there travel notifications for columbia _(gold: travel\_alert; came from cluster 65)_
- do i need to read any travel alerts for kenya _(gold: travel\_alert; came from cluster 139)_
- what are your best travel suggestions _(gold: travel\_suggestion; came from cluster 71)_
- are there any current travel alerts for brazil _(gold: travel\_alert; came from cluster 65)_
- are there any travel alerts for antarctica _(gold: travel\_alert; came from cluster 65)_
- are there any travel alerts for brazil _(gold: travel\_alert; came from cluster 65)_
- are there any travel advisories for the us _(gold: travel\_alert; came from cluster 65)_
- are there any travel bulletins about haiti _(gold: travel\_alert; came from cluster 65)_
- can you do some research about the best places to travel _(gold: travel\_suggestion; came from cluster 71)_

### Helped 6: Qwen3-4B, clearer prompt, cluster 134

- **Size:** 150 members; **purity before:** 0.31
- **Selection number:** +0.320 = change in member purity +0.320 minus the no-replacement counterfactual +0.000
- **Gold intents before:** make\_call 46 (31%), change\_accent 41 (27%), change\_user\_name 16 (11%), change\_ai\_name 12 (8%), share\_location 11 (7%)

**Summary**

```text
How can I request to be called by a specific name or set a phone call reminder?
```

**Sample of 10 members before the step**

- i want to be called mollie _(gold: change\_user\_name)_
- remind me friday to call my mother _(gold: reminder\_update)_
- call mymother _(gold: make\_call)_
- i want to talk to sarah _(gold: make\_call)_
- i need to to the female voice _(gold: change\_accent)_
- go to the female voice _(gold: change\_accent)_
- can you switch to female voice _(gold: change\_accent)_
- i would like to share my location with my mom _(gold: share\_location)_
- can you call michelle on the home phone _(gold: make\_call)_
- use the female voice _(gold: change\_accent)_

**Left the cluster** (62 of 150; showing 10), with the majority intent of the cluster each went to

- i want to hear the female voice option _(gold: change\_accent; went to a cluster mostly about change\_accent)_
- i would prefer to hear the female voice _(gold: change\_accent; went to a cluster mostly about change\_accent)_
- i gotta to the female voice _(gold: change\_accent; went to a cluster mostly about change\_accent)_
- use a woman's voice _(gold: change\_accent; went to a cluster mostly about change\_accent)_
- use female voice now instead _(gold: change\_accent; went to a cluster mostly about change\_accent)_
- let cora and nancy know were i am now _(gold: share\_location; went to a cluster mostly about share\_location)_
- use phone to call alexa _(gold: make\_call; went to a cluster mostly about share\_location)_
- female voice please _(gold: change\_accent; went to a cluster mostly about change\_accent)_
- change voice to female _(gold: change\_accent; went to a cluster mostly about change\_accent)_
- what do you think about me calling you cora _(gold: change\_ai\_name; went to a cluster mostly about share\_location)_

**Arrived** (80 documents; showing 10)

- my name is stu, not sue! _(gold: change\_user\_name; came from cluster 113)_
- call home _(gold: make\_call; came from cluster 113)_
- can you call someone _(gold: make\_call; came from cluster 37)_
- it's necessary to call michael _(gold: make\_call; came from cluster 113)_
- i need to go now _(gold: goodbye; came from cluster 146)_
- hello, anyone there _(gold: greeting; came from cluster 112)_
- hello there! _(gold: greeting; came from cluster 112)_
- i want to call up jan _(gold: make\_call; came from cluster 146)_
- i need you to phone sal _(gold: make\_call; came from cluster 11)_
- can i get to susan's house with my current tank _(gold: gas; came from cluster 85)_

### Helped 7: Qwen3-0.6B, old prompt, cluster 123

- **Size:** 243 members; **purity before:** 0.41
- **Selection number:** +0.284 = change in member purity +0.284 minus the no-replacement counterfactual +0.000
- **Gold intents before:** accept\_reservations 100 (41%), confirm\_reservation 44 (18%), restaurant\_reviews 41 (17%), translate 7 (3%), book\_hotel 6 (2%)

**Summary**

```text
How would you say "I am a tourist" if you were Mongolian?
```

**Sample of 10 members before the step**

- can you speak to me in chinese _(gold: change\_language)_
- do cheetos have a lot of calories _(gold: calories)_
- how good are the ratings for red robin _(gold: restaurant\_reviews)_
- how are the ratings like for buffalo wild wings _(gold: restaurant\_reviews)_
- please find out if napolis takes lunch reservations _(gold: accept\_reservations)_
- will they take reservations at chillis _(gold: accept\_reservations)_
- can you make a reservation at michael's _(gold: accept\_reservations)_
- what are the reviews like for l'auberge aubergine _(gold: restaurant\_reviews)_
- will bj's take reservations _(gold: accept\_reservations)_
- eleven madison park takes reservations right _(gold: accept\_reservations)_

**Left the cluster** (168 of 243; showing 10), with the majority intent of the cluster each went to

- how could i say twin in chinese _(gold: translate; went to a cluster mostly about change\_language)_
- how good are the ratings for red robin _(gold: restaurant\_reviews; went to a cluster mostly about restaurant\_reviews)_
- tell me the reviews for bjs _(gold: restaurant\_reviews; went to a cluster mostly about restaurant\_reviews)_
- what kind of reviews does wendy's have _(gold: restaurant\_reviews; went to a cluster mostly about restaurant\_reviews)_
- does redrobin do reservations _(gold: accept\_reservations; went to a cluster mostly about accept\_reservations)_
- tell me if luigis in brick takes reservations _(gold: accept\_reservations; went to a cluster mostly about accept\_reservations)_
- can you tell me if zeus does reservations _(gold: accept\_reservations; went to a cluster mostly about accept\_reservations)_
- what are the ratings for yardhouse _(gold: restaurant\_reviews; went to a cluster mostly about restaurant\_reviews)_
- do you have any idea if central needs reservations _(gold: accept\_reservations; went to a cluster mostly about accept\_reservations)_
- i need to know what's good for chinese around here _(gold: meal\_suggestion; went to a cluster mostly about change\_language)_

**Arrived** (77 documents; showing 10)

- is my 10am village inn reservation valid _(gold: confirm\_reservation; came from cluster 102)_
- will you make sure robert has a reservation at ruth's steakhouse _(gold: confirm\_reservation; came from cluster 83)_
- can you confirm my reservation for steve at olive garden _(gold: confirm\_reservation; came from cluster 96)_
- make sure my reservation is happening for john at olive garden _(gold: confirm\_reservation; came from cluster 96)_
- where's a good place to go if i want to see mountains _(gold: travel\_suggestion; came from cluster 62)_
- what can a tourist in denver do _(gold: travel\_suggestion; came from cluster 62)_
- to visit cambodia, do i need an international visa _(gold: international\_visa; came from cluster 65)_
- how safe is it to travel to guatemala right now and are there any alerts _(gold: travel\_alert; came from cluster 62)_
- confirm my johnny rockets reservation for this evening _(gold: confirm\_reservation; came from cluster 27)_
- can you let michael and julie know my location _(gold: share\_location; came from cluster 121)_

### Helped 8: Qwen3-0.6B, old prompt, cluster 6

- **Size:** 273 members; **purity before:** 0.52
- **Selection number:** +0.278 = change in member purity +0.278 minus the no-replacement counterfactual +0.000
- **Gold intents before:** tell\_joke 143 (52%), fun\_fact 103 (38%), restaurant\_reviews 7 (3%), travel\_suggestion 6 (2%), definition 3 (1%)

**Summary**

```text
What are some fun facts about the world?
```

**Sample of 10 members before the step**

- i want to know all about trivia for the office _(gold: fun\_fact)_
- see you later, alligator _(gold: goodbye)_
- what are some funny things about food _(gold: tell\_joke)_
- please tell me a joke _(gold: tell\_joke)_
- read me some different cat trivia items _(gold: fun\_fact)_
- i want to hear something hilarious _(gold: tell\_joke)_
- tell my something funny _(gold: tell\_joke)_
- are the reviews ned get's good _(gold: restaurant\_reviews)_
- tell me a joke about elephants _(gold: tell\_joke)_
- tell me a joke about the subject of sailing _(gold: tell\_joke)_

**Left the cluster** (151 of 273; showing 10), with the majority intent of the cluster each went to

- do you know any trivia about ostriches _(gold: fun\_fact; went to a cluster mostly about restaurant\_reviews)_
- what's the funniest joke you know _(gold: tell\_joke; went to a cluster mostly about tell\_joke)_
- i would like to listen to a funny joke _(gold: tell\_joke; went to a cluster mostly about tell\_joke)_
- could you please tell me a good joke _(gold: tell\_joke; went to a cluster mostly about tell\_joke)_
- i want to hear something funny _(gold: tell\_joke; went to a cluster mostly about tell\_joke)_
- tell me a non-offensive joke _(gold: tell\_joke; went to a cluster mostly about tell\_joke)_
- let me hear something funny _(gold: tell\_joke; went to a cluster mostly about tell\_joke)_
- are the reviews ned get's good _(gold: restaurant\_reviews; went to a cluster mostly about restaurant\_reviews)_
- do you have any monkey jokes _(gold: tell\_joke; went to a cluster mostly about tell\_joke)_
- do you know any dad jokes _(gold: tell\_joke; went to a cluster mostly about tell\_joke)_

**Arrived** (58 documents; showing 10)

- tell me something cool about elephants _(gold: fun\_fact; came from cluster 96)_
- what sorts of subjects are you well versed in _(gold: what\_can\_i\_ask\_you; came from cluster 101)_
- what's fun to do in thailand _(gold: travel\_suggestion; came from cluster 81)_
- what are some fun things i can partake in in atlanta _(gold: travel\_suggestion; came from cluster 71)_
- how good are the ratings for outback _(gold: restaurant\_reviews; came from cluster 123)_
- i'd love to hear when you were born _(gold: how\_old\_are\_you; came from cluster 27)_
- what's the best place to visit in arizona _(gold: travel\_suggestion; came from cluster 62)_
- is chocolate healthy _(gold: nutrition\_info; came from cluster 74)_
- give me a list of places that serve the best wings in charlotte _(gold: restaurant\_suggestion; came from cluster 108)_
- x card has earned how many points _(gold: rewards\_balance; came from cluster 41)_

### Helped 9: Qwen3-0.6B, old prompt, cluster 27

- **Size:** 258 members; **purity before:** 0.56
- **Selection number:** +0.275 = change in member purity +0.275 minus the no-replacement counterfactual +0.000
- **Gold intents before:** update\_playlist 145 (56%), play\_music 95 (37%), share\_location 3 (1%), travel\_suggestion 3 (1%), change\_language 2 (1%)

**Summary**

```text
What is the name of the song currently playing on your speakers?
```

**Sample of 10 members before the step**

- please play the new lady gaga song _(gold: play\_music)_
- can you play your guitar right now _(gold: play\_music)_
- add what's playing on my favorite playlist _(gold: update\_playlist)_
- add coming undone by korn to my playlist _(gold: update\_playlist)_
- add welcome to the jungle by guns n roses to my playlist _(gold: update\_playlist)_
- include happy on my rb playlist _(gold: update\_playlist)_
- can you play the beatles _(gold: play\_music)_
- this song i'm listening to would be great on my commute playlist _(gold: update\_playlist)_
- i need this song on my jam playlist _(gold: update\_playlist)_
- please go on amazon so i can buy bluetooth speakers _(gold: order)_

**Left the cluster** (82 of 258; showing 10), with the majority intent of the cluster each went to

- put my music on, please _(gold: play\_music; went to a cluster mostly about play\_music)_
- i wanna play the song that goes like hey jude don't make it bad _(gold: play\_music; went to a cluster mostly about play\_music)_
- please play the song that goes like hey jude don't make it bad _(gold: play\_music; went to a cluster mostly about play\_music)_
- can you play music by the rolling stones _(gold: play\_music; went to a cluster mostly about play\_music)_
- play the song called guerrilla radio _(gold: play\_music; went to a cluster mostly about play\_music)_
- play the song called blood brothers _(gold: play\_music; went to a cluster mostly about play\_music)_
- play the song called baby shark _(gold: play\_music; went to a cluster mostly about play\_music)_
- play the song that goes, "starships were meant to fly _(gold: play\_music; went to a cluster mostly about play\_music)_
- will you play the song that goes like, "starships were meant to fly _(gold: play\_music; went to a cluster mostly about play\_music)_
- can you play music by led zepplin _(gold: play\_music; went to a cluster mostly about play\_music)_

**Arrived** (10 documents; showing 10)

- has the discover card approved my app _(gold: application\_status; came from cluster 136)_
- please put my acupuncture appointment on my to list _(gold: todo\_list\_update; came from cluster 146)_
- add change filters to my to do list _(gold: todo\_list\_update; came from cluster 130)_
- i need to download my w-2 form _(gold: w2; came from cluster 16)_
- alter back to your orginal settings _(gold: reset\_settings; came from cluster 133)_
- use my shower playlist _(gold: play\_music; came from cluster 85)_
- do the shower playlist please _(gold: play\_music; came from cluster 85)_
- grab me a new belt on amazon please _(gold: order; came from cluster 16)_
- please put a block on my discover account immediately _(gold: freeze\_account; came from cluster 69)_
- i ordered some new speakers, so when will they get here _(gold: order\_status; came from cluster 146)_

### Helped 10: Qwen3-1.7B, old prompt, cluster 132

- **Size:** 153 members; **purity before:** 0.60
- **Selection number:** +0.268 = change in member purity +0.268 minus the no-replacement counterfactual +0.000
- **Gold intents before:** text 92 (60%), order\_checks 42 (27%), reminder\_update 4 (3%), order 3 (2%), replacement\_card\_duration 3 (2%)

**Summary**

```text
How can I get more checkbooks mailed to me, and what options are available for ordering additional checkbooks by mail?
```

**Sample of 10 members before the step**

- read some of the reviews for wing stop _(gold: restaurant\_reviews)_
- send text message to _(gold: text)_
- start a new text to maureen and tell her i go mom's christmas present _(gold: text)_
- send a text to someone _(gold: text)_
- what is the process to get some more checkbooks mailed to me _(gold: order\_checks)_
- i do need to get some more checkbooks mailed to me _(gold: order\_checks)_
- send davis a text i'll be there in a few _(gold: text)_
- i'd like you to text marie and let her know to meet me at the hospital _(gold: text)_
- send a text that says hi to abby _(gold: text)_
- i'd like to send a text to jack, say "hi _(gold: text)_

**Left the cluster** (108 of 153; showing 10), with the majority intent of the cluster each went to

- set up a reminder to mail a check tommorow _(gold: reminder\_update; went to a cluster mostly about text)_
- send a text and tell chris i’m not working today _(gold: text; went to a cluster mostly about text)_
- send ally a text message the message is that i just landed _(gold: text; went to a cluster mostly about text)_
- let sal know by text i will be attending _(gold: text; went to a cluster mostly about text)_
- i want you to send a text message for me _(gold: text; went to a cluster mostly about text)_
- i want to send a text _(gold: text; went to a cluster mostly about text)_
- text mom where are you _(gold: text; went to a cluster mostly about text)_
- compose text message _(gold: text; went to a cluster mostly about text)_
- text mary and tell them i'm on my way _(gold: text; went to a cluster mostly about text)_
- will you answer if i call you lexi _(gold: change\_ai\_name; went to a cluster mostly about text)_

**Arrived** (51 documents; showing 10)

- i'd love to order some more checks for my checking account _(gold: order\_checks; came from cluster 2)_
- order more checkbooks for my community account _(gold: order\_checks; came from cluster 51)_
- i need more checkbooks for my fifth third account _(gold: order\_checks; came from cluster 93)_
- can i order for more checkbooks for my chase bank account _(gold: order\_checks; came from cluster 2)_
- will i be able to order for more checkbooks for my chase bank account _(gold: order\_checks; came from cluster 2)_
- is it possible to make an order for more checkbooks for my chase bank account _(gold: order\_checks; came from cluster 2)_
- i am not sure if i have enough money in my chase account to buy a new dress _(gold: balance; came from cluster 2)_
- please notify my bank that i need more checks _(gold: order\_checks; came from cluster 2)_
- how do i order some checkbooks for my chase account _(gold: order\_checks; came from cluster 2)_
- how do i order some more checks for my usaa account _(gold: order\_checks; came from cluster 51)_

### Hurt 1: Qwen3-4B, old prompt, cluster 80

- **Size:** 132 members; **purity before:** 0.98
- **Selection number:** -0.977 = change in member purity -0.977 minus the no-replacement counterfactual +0.000
- **Gold intents before:** roll\_dice 129 (98%), calories 1 (1%), fun\_fact 1 (1%), restaurant\_reservation 1 (1%)

**Summary**

```text
What is a general summary of the cluster of questions?
```

**Sample of 10 members before the step**

- can you get me a table for 6 at johnnys _(gold: restaurant\_reservation)_
- i'd like a 7 sided dice roll please _(gold: roll\_dice)_
- roll die _(gold: roll\_dice)_
- i would like the dice to be rolled _(gold: roll\_dice)_
- roll the dice! _(gold: roll\_dice)_
- tell me the result of a dice roll with five sides _(gold: roll\_dice)_
- i need you to roll a dice that has six sides and tell me what it lands on _(gold: roll\_dice)_
- roll a dice that has seven sides _(gold: roll\_dice)_
- roll the five sided die _(gold: roll\_dice)_
- can you roll an eight sided die and tell me what it comes up as _(gold: roll\_dice)_

**Left the cluster** (132 of 132; showing 10), with the majority intent of the cluster each went to

- roll a 6 sided die _(gold: roll\_dice; went to a cluster mostly about flip\_coin)_
- roll die _(gold: roll\_dice; went to a cluster mostly about flip\_coin)_
- the dice need to be rolled _(gold: roll\_dice; went to a cluster mostly about flip\_coin)_
- toss a die would you _(gold: roll\_dice; went to a cluster mostly about flip\_coin)_
- will you roll a 3 sided dice _(gold: roll\_dice; went to a cluster mostly about flip\_coin)_
- roll a 6 sided dice for me _(gold: roll\_dice; went to a cluster mostly about flip\_coin)_
- what do you get when you roll a dice with five sides _(gold: roll\_dice; went to a cluster mostly about timer)_
- roll an eight sided die _(gold: roll\_dice; went to a cluster mostly about flip\_coin)_
- roll a dice that has seven sides _(gold: roll\_dice; went to a cluster mostly about flip\_coin)_
- can you simulate a dice roll _(gold: roll\_dice; went to a cluster mostly about flip\_coin)_

**Arrived** (129 documents; showing 10)

- how is everything going for you _(gold: greeting; came from cluster 117)_
- how've you been feeling _(gold: greeting; came from cluster 117)_
- how have you been _(gold: greeting; came from cluster 117)_
- how are things treating you _(gold: greeting; came from cluster 101)_
- at free time what do you do _(gold: what\_are\_your\_hobbies; came from cluster 117)_
- in seoul, what things can i do _(gold: travel\_suggestion; came from cluster 117)_
- what time am i meeting john _(gold: meeting\_schedule; came from cluster 117)_
- how ya doin _(gold: greeting; came from cluster 117)_
- tell me how are you _(gold: greeting; came from cluster 117)_
- i'd like to know how you are doing _(gold: greeting; came from cluster 117)_

### Hurt 2: Qwen3-4B, old prompt, cluster 29

- **Size:** 131 members; **purity before:** 0.98
- **Selection number:** -0.977 = change in member purity -0.977 minus the no-replacement counterfactual +0.000
- **Gold intents before:** next\_song 128 (98%), play\_music 2 (2%), update\_playlist 1 (1%)

**Summary**

```text
What are the common ways to request the next song in a playlist?
```

**Sample of 10 members before the step**

- play the next tune _(gold: next\_song)_
- play the next track _(gold: next\_song)_
- go to the next song now _(gold: next\_song)_
- move on to the next song _(gold: next\_song)_
- using this playlist, play next song _(gold: next\_song)_
- could you play the next song on this playlist, please _(gold: next\_song)_
- i am needing the next song to be played _(gold: next\_song)_
- start the next song _(gold: next\_song)_
- i want you to play the next song _(gold: next\_song)_
- play the next song please if you would _(gold: next\_song)_

**Left the cluster** (111 of 131; showing 10), with the majority intent of the cluster each went to

- go to my next song _(gold: next\_song; went to a cluster mostly about what\_song)_
- skip this and go to the next song _(gold: next\_song; went to a cluster mostly about what\_song)_
- go to the next song now _(gold: next\_song; went to a cluster mostly about what\_song)_
- skip to the next song _(gold: next\_song; went to a cluster mostly about what\_song)_
- move on to the next song _(gold: next\_song; went to a cluster mostly about what\_song)_
- would you skip past this song and just play what comes next _(gold: next\_song; went to a cluster mostly about what\_song)_
- i dont want to hear this song, just play the next one _(gold: next\_song; went to a cluster mostly about what\_song)_
- go to upcoming song _(gold: next\_song; went to a cluster mostly about what\_song)_
- play next song _(gold: next\_song; went to a cluster mostly about what\_song)_
- please play the next track _(gold: next\_song; went to a cluster mostly about what\_song)_

**Arrived** (237 documents; showing 10)

- what company's software engineers gave you life _(gold: who\_made\_you; came from cluster 27)_
- please play the new lady gaga song _(gold: play\_music; came from cluster 27)_
- i want to hear my vaporwave playlist _(gold: play\_music; came from cluster 27)_
- i want to hear pop music _(gold: play\_music; came from cluster 27)_
- please add this song to my alternative playlist _(gold: update\_playlist; came from cluster 27)_
- can you add that to my chillwave playlist _(gold: update\_playlist; came from cluster 27)_
- add ruby soho by rancid to my playlist _(gold: update\_playlist; came from cluster 27)_
- i want to have happy added to my rb playlist _(gold: update\_playlist; came from cluster 27)_
- i want to put thank you on my playlist called relaxing jams _(gold: update\_playlist; came from cluster 27)_
- play the song that goes, "starships were meant to fly _(gold: play\_music; came from cluster 27)_

### Hurt 3: Qwen3-4B, old prompt, cluster 15

- **Size:** 111 members; **purity before:** 0.94
- **Selection number:** -0.919 = change in member purity -0.919 minus the no-replacement counterfactual +0.000
- **Gold intents before:** payday 104 (94%), bill\_due 4 (4%), income 2 (2%), next\_holiday 1 (1%)

**Summary**

```text
When is my next paycheck scheduled to arrive?
```

**Sample of 10 members before the step**

- what date do i get my next paycheck _(gold: payday)_
- i need to know the date my next paycheck will be here _(gold: payday)_
- my next paycheck is available when _(gold: payday)_
- can you tell me when i'm supposed to get paid _(gold: payday)_
- what day is my next payday _(gold: payday)_
- when do i get my next paycheck _(gold: payday)_
- when is the next payday i can look forward to _(gold: payday)_
- when will my payment be deposited _(gold: payday)_
- is it payday _(gold: payday)_
- what is my payment going to be _(gold: income)_

**Left the cluster** (16 of 111; showing 10), with the majority intent of the cluster each went to

- tell me when i received my last paycheck _(gold: payday; went to a cluster mostly about spending\_history)_
- please find the receipt date for my last paycheck _(gold: payday; went to a cluster mostly about spending\_history)_
- remind me of the date of my last paycheck _(gold: payday; went to a cluster mostly about spending\_history)_
- whats the deadline for amex payment _(gold: bill\_due; went to a cluster mostly about exchange\_rate)_
- what's the due date for my american express payment _(gold: bill\_due; went to a cluster mostly about exchange\_rate)_
- what was the date of my last paycheck _(gold: payday; went to a cluster mostly about spending\_history)_
- what date is the next day i get paid _(gold: payday; went to a cluster mostly about date)_
- what date do i have to pay the phone bill on _(gold: bill\_due; went to a cluster mostly about bill\_balance)_
- look up the date for my next payday _(gold: payday; went to a cluster mostly about date)_
- what day can i expect to receive payment on _(gold: payday; went to a cluster mostly about next\_holiday)_

**Arrived** (171 documents; showing 10)

- how much is in savings _(gold: balance; came from cluster 75)_
- i want to pay that bill now _(gold: pay\_bill; came from cluster 128)_
- on what day do i have to pay my nordstrom bill _(gold: bill\_due; came from cluster 128)_
- i need details on my income _(gold: income; came from cluster 110)_
- what is the exact number of my salary _(gold: income; came from cluster 54)_
- what is my pay grade at work _(gold: income; came from cluster 54)_
- i need to know my income _(gold: income; came from cluster 110)_
- what's my total earnings _(gold: income; came from cluster 54)_
- how much do i have to pay this month _(gold: bill\_balance; came from cluster 54)_
- what is my compensation _(gold: income; came from cluster 54)_

### Hurt 4: Qwen3-0.6B, old prompt, cluster 8

- **Size:** 93 members; **purity before:** 0.91
- **Selection number:** -0.903 = change in member purity -0.903 minus the no-replacement counterfactual +0.000
- **Gold intents before:** how\_old\_are\_you 85 (91%), date 1 (1%), definition 1 (1%), food\_last 1 (1%), income 1 (1%)

**Summary**

```text
How old are you?
```

**Sample of 10 members before the step**

- do you have any past-times _(gold: what\_are\_your\_hobbies)_
- how many years do you have _(gold: how\_old\_are\_you)_
- how old is al _(gold: how\_old\_are\_you)_
- how late is it now in ourense _(gold: time)_
- what you age on your last birthday _(gold: how\_old\_are\_you)_
- what is your date of birth _(gold: how\_old\_are\_you)_
- what is the year that were you born _(gold: how\_old\_are\_you)_
- can you tell me your age _(gold: how\_old\_are\_you)_
- do you know how old you are _(gold: how\_old\_are\_you)_
- what's your date of birth _(gold: how\_old\_are\_you)_

**Left the cluster** (12 of 93; showing 10), with the majority intent of the cluster each went to

- how many years do you have _(gold: how\_old\_are\_you; went to a cluster mostly about pto\_used)_
- how many years are you _(gold: how\_old\_are\_you; went to a cluster mostly about pto\_used)_
- how old are you alexa _(gold: how\_old\_are\_you; went to a cluster mostly about make\_call)_
- what is your age, ai _(gold: how\_old\_are\_you; went to a cluster mostly about are\_you\_a\_bot)_
- how long have you been functional _(gold: how\_old\_are\_you; went to a cluster mostly about pto\_used)_
- how old are you in 2019 _(gold: how\_old\_are\_you; went to a cluster mostly about date)_
- were you born in the 80s _(gold: how\_old\_are\_you; went to a cluster mostly about calculator)_
- how old were you on your most recent birthday _(gold: how\_old\_are\_you; went to a cluster mostly about date)_
- what you age on your last birthday _(gold: how\_old\_are\_you; went to a cluster mostly about date)_
- what is the expiration date for those eg _(gold: food\_last; went to a cluster mostly about expiration\_date)_

**Arrived** (144 documents; showing 10)

- what is your place of origin _(gold: where\_are\_you\_from; came from cluster 60)_
- you were born where _(gold: where\_are\_you\_from; came from cluster 60)_
- your birthplace is where _(gold: where\_are\_you\_from; came from cluster 60)_
- what's your country of origin _(gold: where\_are\_you\_from; came from cluster 60)_
- where did you last live _(gold: where\_are\_you\_from; came from cluster 60)_
- what's your hometown _(gold: where\_are\_you\_from; came from cluster 60)_
- could you tell me when you were born _(gold: how\_old\_are\_you; came from cluster 60)_
- i am needing to know when you were born _(gold: how\_old\_are\_you; came from cluster 60)_
- are you from here or somewhere else originally _(gold: where\_are\_you\_from; came from cluster 60)_
- where was it you were born _(gold: where\_are\_you\_from; came from cluster 60)_

### Hurt 5: Qwen3-1.7B, old prompt, cluster 133

- **Size:** 56 members; **purity before:** 0.96
- **Selection number:** -0.893 = change in member purity -0.893 minus the no-replacement counterfactual +0.000
- **Gold intents before:** reset\_settings 54 (96%), change\_volume 1 (2%), whisper\_mode 1 (2%)

**Summary**

```text
How can I revert my settings to their original state?
```

**Sample of 10 members before the step**

- restore your original settings now _(gold: reset\_settings)_
- return to your original settings, please _(gold: reset\_settings)_
- is it possible to change to original settings _(gold: reset\_settings)_
- go to default setting _(gold: reset\_settings)_
- return to your original settings _(gold: reset\_settings)_
- can you reset to factor settings _(gold: reset\_settings)_
- go back to default settings _(gold: reset\_settings)_
- now i'd like for you to return to the original settings _(gold: reset\_settings)_
- change all setting to original ones _(gold: reset\_settings)_
- revert to original settings _(gold: reset\_settings)_

**Left the cluster** (6 of 56; showing 6), with the majority intent of the cluster each went to

- clear all settings in a reset _(gold: reset\_settings; went to a cluster mostly about confirm\_reservation)_
- alter back to your orginal settings _(gold: reset\_settings; went to a cluster mostly about change\_ai\_name)_
- reset to default settings please _(gold: reset\_settings; went to a cluster mostly about reset\_settings)_
- reset to default settings _(gold: reset\_settings; went to a cluster mostly about reset\_settings)_
- i want to reset your settings to the original _(gold: reset\_settings; went to a cluster mostly about reset\_settings)_
- can you reset to factor settings _(gold: reset\_settings; went to a cluster mostly about reset\_settings)_

**Arrived** (103 documents; showing 10)

- help me find where i am _(gold: current\_location; came from cluster 121)_
- i wanna know my current location _(gold: current\_location; came from cluster 121)_
- how can i find my current location _(gold: current\_location; came from cluster 121)_
- let dan know where i am _(gold: share\_location; came from cluster 113)_
- can i make it to work with my current fuel level _(gold: gas; came from cluster 21)_
- you were made where _(gold: where\_are\_you\_from; came from cluster 60)_
- let lisa know where i am now _(gold: share\_location; came from cluster 134)_
- i want david to know where i'm at _(gold: share\_location; came from cluster 121)_
- what's the location where i am _(gold: current\_location; came from cluster 121)_
- tell me where i am _(gold: current\_location; came from cluster 121)_

### Hurt 6: Qwen3-1.7B, old prompt, cluster 53

- **Size:** 89 members; **purity before:** 0.89
- **Selection number:** -0.888 = change in member purity -0.888 minus the no-replacement counterfactual +0.000
- **Gold intents before:** change\_accent 79 (89%), change\_language 8 (9%), translate 1 (1%), whisper\_mode 1 (1%)

**Summary**

```text
How can I change my accent to a male British one?
```

**Sample of 10 members before the step**

- please respond in english _(gold: change\_language)_
- i would prefer to hear you speak like a british male _(gold: change\_accent)_
- please change your accent to the male british one _(gold: change\_accent)_
- i need to switch to the male voice _(gold: change\_accent)_
- you need to change your accent to the male british one _(gold: change\_accent)_
- please change your accent the male british one _(gold: change\_accent)_
- can you speak like a british dude _(gold: change\_accent)_
- switch to british male accent _(gold: change\_accent)_
- use the male voice please _(gold: change\_accent)_
- please use a male voice _(gold: change\_accent)_

**Left the cluster** (2 of 89; showing 2), with the majority intent of the cluster each went to

- i want to talk english _(gold: change\_language; went to a cluster mostly about spelling)_
- we have to speak in english _(gold: change\_language; went to a cluster mostly about spelling)_

**Arrived** (226 documents; showing 10)

- hi, i'm john _(gold: change\_user\_name; came from cluster 113)_
- apply for a kbc card for me _(gold: new\_card; came from cluster 113)_
- i have to say affirmative on that one _(gold: yes; came from cluster 113)_
- your name from this point forward is george _(gold: change\_ai\_name; came from cluster 113)_
- my name is nick _(gold: change\_user\_name; came from cluster 113)_
- do you think my name is jeff _(gold: user\_name; came from cluster 113)_
- i need to call my dad _(gold: make\_call; came from cluster 113)_
- x needs to be called by me _(gold: make\_call; came from cluster 146)_
- tell me the ingredients for making tom yum _(gold: ingredients\_list; came from cluster 113)_
- you are going to be called joe now _(gold: change\_ai\_name; came from cluster 113)_

### Hurt 7: Qwen3-0.6B, old prompt, cluster 89

- **Size:** 81 members; **purity before:** 0.85
- **Selection number:** -0.802 = change in member purity -0.802 minus the no-replacement counterfactual +0.000
- **Gold intents before:** schedule\_maintenance 69 (85%), tire\_change 3 (4%), todo\_list 2 (2%), calendar 1 (1%), calendar\_update 1 (1%)

**Summary**

```text
Can you schedule a car maintenance check for me?
```

**Sample of 10 members before the step**

- what have car repairs ran me this month _(gold: spending\_history)_
- where in sacramento ca i schedule maintenance on my car _(gold: schedule\_maintenance)_
- look for auto companies that do scheduled maintenance on my vehicle _(gold: schedule\_maintenance)_
- is there a location i can schedule to check out my tires _(gold: schedule\_maintenance)_
- i have to schedule somewhere get my tires checked out _(gold: schedule\_maintenance)_
- schedule a mechanic _(gold: schedule\_maintenance)_
- help me schedule maintenance for my car _(gold: schedule\_maintenance)_
- my auto tires need to be checked out so where can i get an appointment _(gold: schedule\_maintenance)_
- should i take my car to a maintenance _(gold: schedule\_maintenance)_
- can i make a car maintenance appointment _(gold: schedule\_maintenance)_

**Left the cluster** (46 of 81; showing 10), with the majority intent of the cluster each went to

- what have car repairs ran me this month _(gold: spending\_history; went to a cluster mostly about last\_maintenance)_
- i want to schedule a tire check up somewhere _(gold: schedule\_maintenance; went to a cluster mostly about tire\_change)_
- look for auto companies that do scheduled maintenance on my vehicle _(gold: schedule\_maintenance; went to a cluster mostly about last\_maintenance)_
- is there a special place where i can schedule to check my tires out _(gold: schedule\_maintenance; went to a cluster mostly about tire\_change)_
- how do i schedule getting my tires checked _(gold: schedule\_maintenance; went to a cluster mostly about tire\_change)_
- make a reminder to schedule a tire check _(gold: schedule\_maintenance; went to a cluster mostly about tire\_change)_
- find me a mechanic _(gold: schedule\_maintenance; went to a cluster mostly about who\_made\_you)_
- can you please make an appointment for me to get my tires checked out _(gold: schedule\_maintenance; went to a cluster mostly about tire\_change)_
- my car's tires are due to be looked at, can you help me get an appointment for that _(gold: schedule\_maintenance; went to a cluster mostly about tire\_change)_
- where can i get a appointment for a tire check for the car _(gold: schedule\_maintenance; went to a cluster mostly about tire\_change)_

**Arrived** (152 documents; showing 10)

- put clean stovetop on my list of reminders _(gold: todo\_list\_update; came from cluster 85)_
- i need to add dusting the bookshelf to my to do list _(gold: todo\_list\_update; came from cluster 85)_
- please also list wash laundry on my to do list _(gold: todo\_list\_update; came from cluster 85)_
- cleaning needs to be on my to do list _(gold: todo\_list\_update; came from cluster 85)_
- on my to do list, add cleaning _(gold: todo\_list\_update; came from cluster 85)_
- can you remind me to mop later by putting it on my to do list today _(gold: todo\_list\_update; came from cluster 85)_
- is vacuuming on my list of things to do _(gold: todo\_list; came from cluster 85)_
- can you add laundry to my to do list _(gold: todo\_list\_update; came from cluster 85)_
- i need to do laundry later today _(gold: todo\_list\_update; came from cluster 85)_
- is "cleaning the bathroom" an item on my todo list _(gold: todo\_list; came from cluster 85)_

### Hurt 8: Qwen3-4B, clearer prompt, cluster 26

- **Size:** 53 members; **purity before:** 0.81
- **Selection number:** -0.774 = change in member purity -0.774 minus the no-replacement counterfactual +0.000
- **Gold intents before:** goodbye 43 (81%), greeting 2 (4%), cancel 1 (2%), definition 1 (2%), make\_call 1 (2%)

**Summary**

```text
how do i say goodbye in different languages
```

**Sample of 10 members before the step**

- that's all i need, thanks! _(gold: thank\_you)_
- call my best friend _(gold: make\_call)_
- bye for now _(gold: goodbye)_
- thanks, bye _(gold: goodbye)_
- goodbye! _(gold: goodbye)_
- bye! _(gold: goodbye)_
- peace out _(gold: goodbye)_
- i have to go ai goodbye _(gold: goodbye)_
- what does amicable mean _(gold: definition)_
- thanks bye bye! _(gold: goodbye)_

**Left the cluster** (52 of 53; showing 10), with the majority intent of the cluster each went to

- pass this song _(gold: next\_song; went to a cluster mostly about what\_song)_
- that's all i need, thanks! _(gold: thank\_you; went to a cluster mostly about thank\_you)_
- great chat, talk to you later _(gold: goodbye; went to a cluster mostly about thank\_you)_
- it is time to say goodbye _(gold: goodbye; went to a cluster mostly about cancel)_
- good bye my friend _(gold: goodbye; went to a cluster mostly about thank\_you)_
- peace out _(gold: goodbye; went to a cluster mostly about thank\_you)_
- this was fun, see you around bye _(gold: goodbye; went to a cluster mostly about thank\_you)_
- peace out! _(gold: goodbye; went to a cluster mostly about cancel)_
- sorry i missed that _(gold: repeat; went to a cluster mostly about cancel)_
- have a good day, bye _(gold: goodbye; went to a cluster mostly about thank\_you)_

**Arrived** (96 documents; showing 10)

- let me talk to you in greek _(gold: change\_language; came from cluster 101)_
- please speak to me in chinese _(gold: change\_language; came from cluster 134)_
- what is the current time in china _(gold: time; came from cluster 135)_
- is there anything neat to do in boston _(gold: travel\_suggestion; came from cluster 62)_
- would you translate a sentence into russian for me, please _(gold: translate; came from cluster 130)_
- could you translate this into chinese for me, please _(gold: translate; came from cluster 63)_
- do i have to get a shot for travel to taiwan _(gold: vaccines; came from cluster 139)_
- how would i say nice to meet you if i were russian _(gold: translate; came from cluster 123)_
- how do i say i'm sorry in chinese _(gold: translate; came from cluster 123)_
- i need to know what's good for chinese around here _(gold: meal\_suggestion; came from cluster 123)_

### Hurt 9: Qwen3-4B, old prompt, cluster 20

- **Size:** 57 members; **purity before:** 0.75
- **Selection number:** -0.614 = change in member purity -0.614 minus the no-replacement counterfactual +0.000
- **Gold intents before:** order 43 (75%), transactions 7 (12%), shopping\_list 5 (9%), todo\_list 1 (2%), todo\_list\_update 1 (2%)

**Summary**

```text
What is a general summary of the cluster of questions?  

**Answer:**  
The cluster of questions revolves around retrieving, viewing, and ordering items from various lists, including purchases, to-do lists, and shopping lists. The questions involve actions such as displaying all items, organizing them, and placing orders based on the
```

**Sample of 10 members before the step**

- bring up my most recent purchases _(gold: transactions)_
- get my entire shopping list ordered _(gold: order)_
- take my shopping list and order all _(gold: order)_
- buy everything on my list _(gold: order)_
- please order everything you see on my shopping list _(gold: order)_
- i'd like to have everything on my shopping list _(gold: order)_
- i need everything on my shopping list _(gold: order)_
- i want everything on my shopping list _(gold: order)_
- i'm ready to put in the order for everything on my shopping list _(gold: order)_
- i need everything on my shopping list to be ordered _(gold: order)_

**Left the cluster** (54 of 57; showing 10), with the majority intent of the cluster each went to

- read my entire shopping list to me _(gold: shopping\_list; went to a cluster mostly about shopping\_list)_
- i want my entire shopping list ordered _(gold: order; went to a cluster mostly about shopping\_list)_
- send the order for my entire shopping list _(gold: order; went to a cluster mostly about shopping\_list)_
- go shopping and order everything on the list _(gold: order; went to a cluster mostly about shopping\_list)_
- i want everything on my shopping list to be ordered _(gold: order; went to a cluster mostly about shopping\_list)_
- show all purchases of video games _(gold: transactions; went to a cluster mostly about redeem\_rewards)_
- list all purchases of video games _(gold: transactions; went to a cluster mostly about redeem\_rewards)_
- i want to see all transactions in the past month for all accounts _(gold: transactions; went to a cluster mostly about transactions)_
- i'd like to you order everything that's on my shopping list _(gold: order; went to a cluster mostly about shopping\_list)_
- order my whole shopping list _(gold: order; went to a cluster mostly about shopping\_list)_

**Arrived** (117 documents; showing 10)

- i want you to clear out my to do list _(gold: todo\_list\_update; came from cluster 146)_
- tell me what is on my to do list _(gold: todo\_list; came from cluster 33)_
- read to me my to do list _(gold: todo\_list; came from cluster 33)_
- i want to hear my to do list read out loud _(gold: todo\_list; came from cluster 33)_
- will you please go back over everything on my to do list _(gold: todo\_list; came from cluster 33)_
- have i added anything to my todo list _(gold: todo\_list; came from cluster 85)_
- do i have anything on my todo list _(gold: todo\_list; came from cluster 85)_
- please put lawn mowing on my list of to dos _(gold: todo\_list\_update; came from cluster 85)_
- give me my todo list _(gold: todo\_list; came from cluster 85)_
- what things are on my todo list _(gold: todo\_list; came from cluster 85)_

### Hurt 10: Qwen3-0.6B, old prompt, cluster 11

- **Size:** 107 members; **purity before:** 0.68
- **Selection number:** -0.579 = change in member purity -0.579 minus the no-replacement counterfactual +0.000
- **Gold intents before:** sync\_device 73 (68%), make\_call 17 (16%), find\_phone 12 (11%), bill\_due 2 (2%), change\_ai\_name 1 (1%)

**Summary**

```text
Can you help me find my iPhone?
```

**Sample of 10 members before the step**

- establish a connection to my phone _(gold: sync\_device)_
- would you connect to my phone _(gold: sync\_device)_
- i need for you to connect to my phone _(gold: sync\_device)_
- will you connect to my phone _(gold: sync\_device)_
- pair my phone please _(gold: sync\_device)_
- pair with my phone please _(gold: sync\_device)_
- phone lobby _(gold: make\_call)_
- can you pair yourself with my phone please _(gold: sync\_device)_
- can you get paired to my phone right away _(gold: sync\_device)_
- sync with my phone please _(gold: sync\_device)_

**Left the cluster** (106 of 107; showing 10), with the majority intent of the cluster each went to

- please link up to my cell _(gold: sync\_device; went to a cluster mostly about find\_phone)_
- create a link with my phone _(gold: sync\_device; went to a cluster mostly about find\_phone)_
- i want for you to connect to my phone _(gold: sync\_device; went to a cluster mostly about find\_phone)_
- i need for you to connect to my phone _(gold: sync\_device; went to a cluster mostly about find\_phone)_
- connect with my phone please _(gold: sync\_device; went to a cluster mostly about find\_phone)_
- pair with my phone _(gold: sync\_device; went to a cluster mostly about find\_phone)_
- i need you to pair with my phone please _(gold: sync\_device; went to a cluster mostly about find\_phone)_
- can you pair with my phone _(gold: sync\_device; went to a cluster mostly about find\_phone)_
- please pair with my phone _(gold: sync\_device; went to a cluster mostly about find\_phone)_
- i need you to phone sal _(gold: make\_call; went to a cluster mostly about text)_

**Arrived** (134 documents; showing 10)

- can you tell me how many calories are in an apple _(gold: nutrition\_info; came from cluster 96)_
- i would like to know how much fat is in tbsp of olive oil _(gold: nutrition\_info; came from cluster 96)_
- bananas expire in how long _(gold: food\_last; came from cluster 96)_
- can i substitute apple juice for wine _(gold: ingredient\_substitution; came from cluster 96)_
- tell me how many p's are in apple _(gold: spelling; came from cluster 96)_
- is it allow to switch apples to grapes _(gold: ingredient\_substitution; came from cluster 96)_
- what are the nutrition facts for apple sauce _(gold: nutrition\_info; came from cluster 96)_
- when does the honey expire _(gold: food\_last; came from cluster 96)_
- can i swap applesauce for oil _(gold: ingredient\_substitution; came from cluster 96)_
- what's the average review for olive garden _(gold: restaurant\_reviews; came from cluster 96)_
