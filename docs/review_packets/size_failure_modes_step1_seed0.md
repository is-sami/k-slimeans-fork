**Open this only after you have submitted your #34 ratings.**

# Failure modes by size and prompt, CLINC150 seed 0, step 1 (issue #36, for Nabin)

This packet shows which model wrote which summary. The #34 hand check has to stay blind, so please finish and submit those ratings first.

Regenerate: `python scripts/export_review_packets.py --results-root ../../k-slimeans/results --out-dir docs/review_packets`.

## What this is

- 25 clusters of the 150 at the first summary step, seed 0, sampled with a fixed seed (20261119),
  5 from each purity-before bin (all clusters in a bin if it has fewer). Clusters per bin out of 150: 38 <= 0.4, 42 (0.4, 0.6], 26 (0.6, 0.8], 11 (0.8, 0.9], 33 > 0.9.
- **Same members in every run.** All six runs start step 1 from one step-0 partition. This was checked from the logs
  when the packet was built: the step-0 assignments of the six runs are identical and their logged `step0_sha1` agree
  (2b3858a965ae721d5e2bb27201fbc3728c31e716). So each cluster id has the same members under all six summaries.
- Per cluster: its size, purity before, the gold intents, 10 sample members (random, fixed seed, with their gold
  intent), and the six summaries exactly as written, in a code block so quote marks and line breaks stay visible.
- The automatic quality scores and flags (#34) are not shown.
- The tagging template is `size_failure_modes_tags.csv`: one row per (cluster, model, prompt), the summary text, and an
  empty 0/1 column per tag (echoes_instruction, mentions_cluster_or_questions, quote_marks_or_markup, copies_member_verbatim, no_question_mark, answers_instead_of_asking, covers_one_subgroup, adds_detail_no_member_has) plus `other` (say what) and `notes`.
  Tags from the #36 comment: echoes the instruction; talks about "the cluster" or "the questions"; quote marks or
  markup; copies a member word for word; no "?"; answers instead of asking; covers only one sub-group; adds a detail no
  member has; other.
- Read `docs/results/prompt_test.md` sections 5 to 6 and 8.3 and `clinc150_summarizers.md` section 2.4 only after tagging.

## The clusters

### Cluster 16

- **Size:** 223 members; **purity before:** 0.38 (bin <= 0.4)
- **Gold intents:** international\_fees 85 (38%), credit\_limit 16 (7%), order\_status 15 (7%), rewards\_balance 14 (6%)

**10 members**

- deposit ten bucks from my chase account to my ally account _(gold: transfer)_
- what did i spend at target on my barclays card last month _(gold: transactions)_
- how many rewards points do i have for my amazon card _(gold: rewards\_balance)_
- how many points are on my speedway card right now _(gold: rewards\_balance)_
- do i get charged more for using my card in canada _(gold: international\_fees)_
- do i have more than \$100 in my pnc account _(gold: balance)_
- how many points do i have with my american express _(gold: rewards\_balance)_
- does my american express card have any international transaction fees _(gold: international\_fees)_
- using my card in tulsa won't cause me to be charged extra will it _(gold: international\_fees)_
- what hobbies do you have alexa _(gold: what\_are\_your\_hobbies)_

**Qwen3-0.6B, old prompt**

```text
What are the key points you're asking about in this cluster of questions?
```

**Qwen3-0.6B, clearer prompt**

```text
What are the international transaction fees associated with my card?
```

**Qwen3-1.7B, old prompt**

```text
What are the key financial and transaction-related concerns and requests related to multiple accounts, including checking, savings, credit cards, and online purchases, and how can they be addressed?
```

**Qwen3-1.7B, clearer prompt**

```text
What are the common concerns users have about their financial transactions and card fees?
```

**Qwen3-4B, old prompt**

```text
What is the summary of the following cluster of questions? 

The cluster of questions revolves around various financial and account-related inquiries, including transferring funds between accounts, checking balances for purchases, understanding credit card limits and fees, tracking transactions, and monitoring the status of online orders and payments.
```

**Qwen3-4B, clearer prompt**

```text
Can you check the status of my recent online purchases and provide information about my account balances and transaction fees?
```

### Cluster 39

- **Size:** 127 members; **purity before:** 0.21 (bin <= 0.4)
- **Gold intents:** are\_you\_a\_bot 27 (21%), who\_made\_you 23 (18%), greeting 16 (13%), how\_old\_are\_you 11 (9%)

**10 members**

- can you tell me who made ai _(gold: who\_made\_you)_
- what is the name of the person who made the ai _(gold: who\_made\_you)_
- goodbye, ai assistant _(gold: goodbye)_
- hey, ai _(gold: greeting)_
- ai, what do people call you _(gold: what\_is\_your\_name)_
- i want to know if you are a real person or an ai _(gold: are\_you\_a\_bot)_
- are you an actual person, or ai _(gold: are\_you\_a\_bot)_
- change the ai name to a new one _(gold: change\_ai\_name)_
- ai, how many months old are you _(gold: how\_old\_are\_you)_
- how do i ask the ai to help me with math problem _(gold: calculator)_

**Qwen3-0.6B, old prompt**

```text
What are some of the questions you can ask me?
```

**Qwen3-0.6B, clearer prompt**

```text
What can I ask the AI to help me with?
```

**Qwen3-1.7B, old prompt**

```text
What is the primary purpose of the AI and what are the key aspects of its functionality and design?
```

**Qwen3-1.7B, clearer prompt**

```text
What are the different ways to interact with the ai, and what are the various functions it can perform?
```

**Qwen3-4B, old prompt**

```text
What are the common questions asked about the capabilities, origin, and identity of an AI system?
```

**Qwen3-4B, clearer prompt**

```text
What can I ask you, AI?
```

### Cluster 51

- **Size:** 345 members; **purity before:** 0.29 (bin <= 0.4)
- **Gold intents:** balance 99 (29%), transfer 58 (17%), interest\_rate 38 (11%), account\_blocked 29 (8%)

**10 members**

- put \$20000 into my checking account from my savings account _(gold: transfer)_
- send 2000 dollars between chase and rabobank accounts _(gold: transfer)_
- what's my bank balance _(gold: balance)_
- pay my cable bill from my checking account _(gold: pay\_bill)_
- can you find out what triggered a hold on my bank account _(gold: account\_blocked)_
- i need to order more checks for my savings account _(gold: order\_checks)_
- i would like to transfer \$100 from my checking to saving account _(gold: transfer)_
- what's the phone number for my credit card company _(gold: replacement\_card\_duration)_
- whats the combined total of the money inside my bank accounts _(gold: balance)_
- i would like the interest rate for my savings account _(gold: interest\_rate)_

**Qwen3-0.6B, old prompt**

```text
What is the quickest way to transfer money between accounts?
```

**Qwen3-0.6B, clearer prompt**

```text
can you help me unlock my bank account?
```

**Qwen3-1.7B, old prompt**

```text
What are the main tasks and concerns related to transferring money between bank accounts, checking balances, and account management?
```

**Qwen3-1.7B, clearer prompt**

```text
What is the best way to check my bank balance and manage my accounts efficiently?
```

**Qwen3-4B, old prompt**

```text
How can I transfer money between bank accounts and check my bank balances?
```

**Qwen3-4B, clearer prompt**

```text
How can I transfer money between different bank accounts?
```

### Cluster 59

- **Size:** 131 members; **purity before:** 0.15 (bin <= 0.4)
- **Gold intents:** timer 19 (15%), restaurant\_reservation 18 (14%), how\_busy 17 (13%), alarm 15 (11%)

**10 members**

- set a timer for 5 minutes _(gold: timer)_
- set timer of 5 minutes _(gold: timer)_
- "can u set a timer for 5 minutes _(gold: timer)_
- can you get me a table for 5 at johnnys _(gold: restaurant\_reservation)_
- could you make reservations for 2 at olive garden for 5 pm today _(gold: restaurant\_reservation)_
- which day will it be five days from now _(gold: date)_
- set alarm for 5 am _(gold: alarm)_
- i want you to set a meeting with john at 5 pm _(gold: schedule\_meeting)_
- i want to reserve table for 5 at red robin under the name sara at 5 _(gold: restaurant\_reservation)_
- what meeting rooms are available for meeting 5pm friday _(gold: schedule\_meeting)_

**Qwen3-0.6B, old prompt**

```text
What is the date 5 days from today?
```

**Qwen3-0.6B, clearer prompt**

```text
can you set a timer for 5 minutes?
```

**Qwen3-1.7B, old prompt**

```text
What is the main theme or common request in the cluster of questions provided?
```

**Qwen3-1.7B, clearer prompt**

```text
What is the best time to schedule a meeting with john for 5 pm today?
```

**Qwen3-4B, old prompt**

```text
What is the main topic that the cluster of questions revolves around?
```

**Qwen3-4B, clearer prompt**

```text
Can you reserve a table for 5 people at a restaurant at 5 pm?
```

### Cluster 83

- **Size:** 63 members; **purity before:** 0.17 (bin <= 0.4)
- **Gold intents:** cook\_time 11 (17%), restaurant\_reservation 10 (16%), restaurant\_reviews 7 (11%), confirm\_reservation 6 (10%)

**10 members**

- what sort of nutrients does a steak have _(gold: nutrition\_info)_
- how long can i expect to keep steak in the freezer _(gold: food\_last)_
- how long should i cook the steak for _(gold: cook\_time)_
- how long should i cook a steak for _(gold: cook\_time)_
- let me know how the outback steakhouse reviews are _(gold: restaurant\_reviews)_
- do you think longhorn steakhouse will be busy at 5pm _(gold: how\_busy)_
- what ingredients are necessary for a steak _(gold: ingredients\_list)_
- get rid of my 4 pm reservation at the steakhouse please _(gold: cancel\_reservation)_
- set a reminder to check the steak _(gold: reminder\_update)_
- can i make a reservation at chima steakhouse in chicago _(gold: accept\_reservations)_

**Qwen3-0.6B, old prompt**

```text
Can you make a reservation at Outback Steakhouse for a party of 5 at 7:00 PM under Jack Arnold?
```

**Qwen3-0.6B, clearer prompt**

```text
What's a good recipe for steak?
```

**Qwen3-1.7B, old prompt**

```text
What is the best way to reserve a table at Outback Steakhouse for a party of 5 at 7:00 PM, and what are the wait times and reservation policies?
```

**Qwen3-1.7B, clearer prompt**

```text
How can I ensure my reservation at outback steakhouse is confirmed and available for the requested time?
```

**Qwen3-4B, old prompt**

```text
How can I make a reservation at a steakhouse, check its availability, and learn about cooking and nutritional information for steak?
```

**Qwen3-4B, clearer prompt**

```text
can you help me reserve a table at a steakhouse for a group of people at a specific time and name
```

### Cluster 32

- **Size:** 215 members; **purity before:** 0.54 (bin (0.4, 0.6])
- **Gold intents:** meeting\_schedule 117 (54%), schedule\_meeting 74 (34%), calendar 6 (3%), calendar\_update 5 (2%)

**10 members**

- i need meeting rooms between 9:00 am and 11:00 am, are there any available _(gold: schedule\_meeting)_
- for today only, how many meetings are with jake _(gold: meeting\_schedule)_
- share my meeting schedule with me _(gold: meeting\_schedule)_
- do you know if i have any meetings set up with travis today _(gold: meeting\_schedule)_
- what scheduled meetings do i have today _(gold: meeting\_schedule)_
- please schedule a meeting with kim at 10 am _(gold: schedule\_meeting)_
- get me a meeting room for 9am on friday _(gold: schedule\_meeting)_
- can you wake me up at noon _(gold: alarm)_
- when is my meeting with invoicing scheduled _(gold: meeting\_schedule)_
- am i supposed to attend any meetings today _(gold: meeting\_schedule)_

**Qwen3-0.6B, old prompt**

```text
What is the schedule for meetings today?
```

**Qwen3-0.6B, clearer prompt**

```text
How can I schedule a meeting with someone on my calendar?
```

**Qwen3-1.7B, old prompt**

```text
What is the user's schedule for today, including meetings, reminders, and availability for meeting rooms, and how can they schedule or manage their meetings?
```

**Qwen3-1.7B, clearer prompt**

```text
How can I check if there are any meetings scheduled for today and what times they are set for?
```

**Qwen3-4B, old prompt**

```text
What is the summary of the cluster?  
The cluster of questions revolves around scheduling meetings, checking meeting schedules and availability, setting reminders, and managing meeting rooms. The questions cover various aspects such as checking what is on one's schedule, scheduling meetings with specific people and times, setting reminders, checking meeting room availability, and
```

**Qwen3-4B, clearer prompt**

```text
How can I check my schedule for meetings and set up new ones?
```

### Cluster 34

- **Size:** 159 members; **purity before:** 0.54 (bin (0.4, 0.6])
- **Gold intents:** pto\_request 86 (54%), pto\_used 37 (23%), pto\_balance 35 (22%), transactions 1 (1%)

**10 members**

- please put in a pto request for june 5th and 6th _(gold: pto\_request)_
- can you put in a pto request for march 7th to the 9th _(gold: pto\_request)_
- i need help making a pto request for march 3-10 _(gold: pto\_request)_
- look up the amount of pto i have already used _(gold: pto\_used)_
- how many days of pto have i used _(gold: pto\_used)_
- how much pto has been used on my behalf _(gold: pto\_used)_
- can you tell me how much pto i still have _(gold: pto\_balance)_
- can i put in a pto request for august 1st to august 10th _(gold: pto\_request)_
- can i take pto from the end of the month to the 5th of the next month _(gold: pto\_request)_
- it it possible to take pto from the 8th to the 11th _(gold: pto\_request)_

**Qwen3-0.6B, old prompt**

```text
How can I request a PTO request for the dates from March 1 to 2, and when can I schedule a PTO request for the dates from April 22 to May 1?
```

**Qwen3-0.6B, clearer prompt**

```text
can you set up a pto request for me for the dates june 4th to june 8th?
```

**Qwen3-1.7B, old prompt**

```text
How can I request a PTO request for specific dates, including weekends, and what is the status of my PTO usage and remaining days?
```

**Qwen3-1.7B, clearer prompt**

```text
How much pto days are available for me to use in the current month?
```

**Qwen3-4B, old prompt**

```text
How can I submit or schedule a PTO request for specific dates, and what is the current status of my available PTO days?
```

**Qwen3-4B, clearer prompt**

```text
Can you submit a pto request for me from [start date] to [end date]?
```

### Cluster 62

- **Size:** 142 members; **purity before:** 0.50 (bin (0.4, 0.6])
- **Gold intents:** directions 71 (50%), travel\_suggestion 19 (13%), fun\_fact 12 (8%), travel\_alert 10 (7%)

**10 members**

- what are the main attractions in gatlinburg _(gold: travel\_suggestion)_
- what are the big tourist sites in sweden _(gold: travel\_suggestion)_
- set a reminder for the movie _(gold: reminder\_update)_
- does home have a starbucks nearby _(gold: directions)_
- i need to know where the nearest place that has mountain dew is _(gold: directions)_
- what is the traffic nearest lexington _(gold: traffic)_
- how safe is it to travel to guatemala right now and are there any alerts _(gold: travel\_alert)_
- give me a cool fact about seattle _(gold: fun\_fact)_
- how much time to drive to the closest bank _(gold: distance)_
- where is the nearest k mart _(gold: directions)_

**Qwen3-0.6B, old prompt**

```text
What are some fun facts about the mountain range in the area near the closest gas station?
```

**Qwen3-0.6B, clearer prompt**

```text
What is the nearest gas station to Glendale?
```

**Qwen3-1.7B, old prompt**

```text
What is the best way to ask for directions to the nearest gas station, coffee shop, or other essential services while traveling?
```

**Qwen3-1.7B, clearer prompt**

```text
What is the safest place to travel in the world?
```

**Qwen3-4B, old prompt**

```text
What is the best way to summarize the given cluster of questions?
```

**Qwen3-4B, clearer prompt**

```text
Where can I find the closest [specific location or establishment] to my current location?
```

### Cluster 100

- **Size:** 83 members; **purity before:** 0.55 (bin (0.4, 0.6])
- **Gold intents:** distance 46 (55%), directions 37 (45%)

**10 members**

- how long would it take to get to times square by bus _(gold: distance)_
- how long does it take to get to virginia by bus _(gold: distance)_
- how long will a bus ride take if i'm going to the capitol building _(gold: distance)_
- how long will it take to reach central park by bus _(gold: distance)_
- how do i get to the hotel by bus _(gold: directions)_
- what are the directions to get to olympia by bus _(gold: directions)_
- how do i get to the movie theater by bus _(gold: directions)_
- how do i get to the bus stop on foot _(gold: directions)_
- how do i get to the grocery store by bus _(gold: directions)_
- what time will i get to the beach taking the bus _(gold: distance)_

**Qwen3-0.6B, old prompt**

```text
How long will it take to drive to the park in West County?
```

**Qwen3-0.6B, clearer prompt**

```text
How long will it take to get to the library by bus?
```

**Qwen3-1.7B, old prompt**

```text
What is the estimated time for a bus ride to various destinations, including cities, landmarks, and locations like the park, library, airport, and monuments, and how can one plan their journey by bus?
```

**Qwen3-1.7B, clearer prompt**

```text
How long will it take to reach the airport by bus?
```

**Qwen3-4B, old prompt**

```text
What is the estimated travel time by bus to various destinations?
```

**Qwen3-4B, clearer prompt**

```text
how long does it take to get to a specific destination by bus
```

### Cluster 149

- **Size:** 246 members; **purity before:** 0.53 (bin (0.4, 0.6])
- **Gold intents:** damaged\_card 130 (53%), report\_lost\_card 87 (35%), card\_declined 6 (2%), improve\_credit\_score 6 (2%)

**10 members**

- i lost my card, how should i report that _(gold: report\_lost\_card)_
- i can't find my student id card and i want to report it as lost _(gold: report\_lost\_card)_
- my card split in half, how do i report it _(gold: damaged\_card)_
- my card got melted and i need to report it, please _(gold: damaged\_card)_
- my card is cracked and i want to report it _(gold: damaged\_card)_
- i damaged the card; can you replace the card _(gold: damaged\_card)_
- my card fell out of my wallet and i ran over it so it does not work _(gold: damaged\_card)_
- i want to report my damaged card i accidentally cut it up thinking it was my expired card _(gold: damaged\_card)_
- how high is my credit limit for my old navy card _(gold: credit\_limit)_
- what is the route to take to report a lost card _(gold: report\_lost\_card)_

**Qwen3-0.6B, old prompt**

```text
What should I do if my card is lost or damaged?
```

**Qwen3-0.6B, clearer prompt**

```text
what should i do if my card is lost
```

**Qwen3-1.7B, old prompt**

```text
What should I do if my card is lost, damaged, or stolen, and how can I report it to get a replacement?
```

**Qwen3-1.7B, clearer prompt**

```text
What should I do if my card is damaged and I need a replacement?
```

**Qwen3-4B, old prompt**

```text
How do I report a lost or damaged card and what steps should I take to replace it?
```

**Qwen3-4B, clearer prompt**

```text
How do I report a lost or damaged card?
```

### Cluster 4

- **Size:** 154 members; **purity before:** 0.62 (bin (0.6, 0.8])
- **Gold intents:** meal\_suggestion 95 (62%), restaurant\_suggestion 27 (18%), how\_busy 6 (4%), ingredients\_list 5 (3%)

**10 members**

- what's your recommendation for dining out tonight _(gold: restaurant\_suggestion)_
- how long will i have to wait if i want to eat at panera _(gold: how\_busy)_
- how busy it that place for dinner _(gold: how\_busy)_
- i can't decide on dinner, what do you suggest _(gold: meal\_suggestion)_
- i would like to hear what ideas you have about making dinner tonight _(gold: meal\_suggestion)_
- any suggestions for a peruvian meal _(gold: meal\_suggestion)_
- whats a good chinese dinner suggestion _(gold: meal\_suggestion)_
- give recommendations for thai food _(gold: meal\_suggestion)_
- i'd like a meal suggestion from thailand _(gold: meal\_suggestion)_
- please tell me a recipe for this meal _(gold: recipe)_

**Qwen3-0.6B, old prompt**

```text
Can you help me make a reservation at Chili's for tomorrow? Please confirm the details: party of two, February 22nd, two in the afternoon.
```

**Qwen3-0.6B, clearer prompt**

```text
What are some good dinner ideas for the upcoming week?
```

**Qwen3-1.7B, old prompt**

```text
What are some restaurant and meal suggestions for dinner, including reservations, food types, and cooking ideas?
```

**Qwen3-1.7B, clearer prompt**

```text
What should I do if I need to make a reservation for a restaurant and also want to check the availability of a specific table?
```

**Qwen3-4B, old prompt**

```text
What are the various ways to seek restaurant reservations, dining suggestions, meal ideas, and cooking recipe recommendations?
```

**Qwen3-4B, clearer prompt**

```text
What should I eat for dinner?
```

### Cluster 108

- **Size:** 169 members; **purity before:** 0.75 (bin (0.6, 0.8])
- **Gold intents:** book\_flight 126 (75%), lost\_luggage 20 (12%), distance 11 (7%), book\_hotel 4 (2%)

**10 members**

- does it take a long time to get to the airport in la _(gold: distance)_
- will it be long to get to the sky harbor airport _(gold: distance)_
- i'm having trouble finding my luggage i was on delta flight ab123 out of new york _(gold: lost\_luggage)_
- what's the cheapest fares from lax to sfo for round trip flights leaving april 1st and returning april 7th _(gold: book\_flight)_
- book a flight from seattle to dallas-fort worth on april the 1st and returning on april 5th _(gold: book\_flight)_
- look for a flight out of la to chicago on march 3rd for under \$500 _(gold: book\_flight)_
- schedule flight from madison to atlanta on delta _(gold: book\_flight)_
- can you find me a flight from denver international to new york international on the 4th for under 700 dollars _(gold: book\_flight)_
- need airplane ridge from philadelphia to atlanta leaving on the 5th of june and returning on the 8th of june _(gold: book\_flight)_
- can i fly from atlanta to san francisco for less than 100 dollars _(gold: book\_flight)_

**Qwen3-0.6B, old prompt**

```text
What are some roundtrip flights available from Dallas to Los Angeles from March 2 to March 10?
```

**Qwen3-0.6B, clearer prompt**

```text
what roundtrip flights from denver to new york are available from march 2 to march 10?
```

**Qwen3-1.7B, old prompt**

```text
What is the best way to find roundtrip flights from various cities to different destinations, including airports in the US and international locations, and what are the key factors to consider when booking flights for travel dates and budget constraints?
```

**Qwen3-1.7B, clearer prompt**

```text
What is the best way to find roundtrip flights from Dallas to Los Angeles for the dates of March 2 to March 10?
```

**Qwen3-4B, old prompt**

```text
What is the estimated time to get to the airport from current location in LA, and what are the options for booking flights and resolving luggage issues?
```

**Qwen3-4B, clearer prompt**

```text
What are the steps to apply for an american express card?
```

### Cluster 124

- **Size:** 200 members; **purity before:** 0.62 (bin (0.6, 0.8])
- **Gold intents:** expiration\_date 125 (62%), replacement\_card\_duration 61 (30%), food\_last 4 (2%), bill\_due 3 (2%)

**10 members**

- my credit card was stolen; how long before a new one will arrive _(gold: replacement\_card\_duration)_
- how many days does it take to receive a new card _(gold: replacement\_card\_duration)_
- does my credit card expire soon _(gold: expiration\_date)_
- please find the expiration month listed on my card _(gold: expiration\_date)_
- what's the expiry month of my card _(gold: expiration\_date)_
- what's the exact date that my chase card will no longer work _(gold: expiration\_date)_
- my american express card expires on what date _(gold: expiration\_date)_
- how long will it be until my visa card expires _(gold: expiration\_date)_
- what is the expiration date on my card _(gold: expiration\_date)_
- when it my citi card expired _(gold: expiration\_date)_

**Qwen3-0.6B, old prompt**

```text
How long will it take for your credit card to be replaced after it gets stolen?
```

**Qwen3-0.6B, clearer prompt**

```text
How long will it take for my credit card to be replaced when I lose it?
```

**Qwen3-1.7B, old prompt**

```text
What is the typical time frame for receiving a replacement credit card after losing or having a stolen credit card, including the time it takes for the new card to be mailed and delivered?
```

**Qwen3-1.7B, clearer prompt**

```text
How long does it take for a credit card company to process and send a replacement card after a loss or theft?
```

**Qwen3-4B, old prompt**

```text
How long does it take to replace a credit card and what is the expiration date of a credit card?
```

**Qwen3-4B, clearer prompt**

```text
How long does it take to replace a credit card and what is the expiration date of my credit card?
```

### Cluster 128

- **Size:** 157 members; **purity before:** 0.63 (bin (0.6, 0.8])
- **Gold intents:** pay\_bill 99 (63%), bill\_balance 27 (17%), bill\_due 14 (9%), transfer 5 (3%)

**10 members**

- can you assist me in paying my electric bill _(gold: pay\_bill)_
- help me pay my cable bill _(gold: pay\_bill)_
- tell me when i have to pay my bill _(gold: bill\_due)_
- how much can i get away with paying for my college loan _(gold: min\_payment)_
- what's the balance on my bills _(gold: bill\_balance)_
- can you tell me what i owe for this month's phone bill _(gold: bill\_balance)_
- how little can i pay on my phone bill _(gold: min\_payment)_
- what is the total amount i am going to have to pay in bills this month _(gold: bill\_balance)_
- i want to pay my bill through the app _(gold: pay\_bill)_
- pull up my electric bill, i want to pay it _(gold: pay\_bill)_

**Qwen3-0.6B, old prompt**

```text
What is the best way to pay your bills?
```

**Qwen3-0.6B, clearer prompt**

```text
can you help me pay my bill?
```

**Qwen3-1.7B, old prompt**

```text
How can I manage and pay my various bills, including utilities, loans, subscriptions, and other expenses, and what is the best way to track and ensure timely payment of my bills?
```

**Qwen3-1.7B, clearer prompt**

```text
How can I efficiently manage and track all my bill payments to ensure they are paid on time?
```

**Qwen3-4B, old prompt**

```text
How can I pay various bills (electric, water, phone, car, etc.) using different accounts (Charles Schwab, Amex, PayPal, etc.) and manage my bill payments effectively?
```

**Qwen3-4B, clearer prompt**

```text
how can i pay my bill online
```

### Cluster 141

- **Size:** 210 members; **purity before:** 0.64 (bin (0.6, 0.8])
- **Gold intents:** thank\_you 134 (64%), goodbye 56 (27%), greeting 5 (2%), spelling 3 (1%)

**10 members**

- yes, i'd really like that alot _(gold: yes)_
- thanks for the help _(gold: thank\_you)_
- why thank you _(gold: thank\_you)_
- i need to thank you _(gold: thank\_you)_
- it was great to have this conversation with you _(gold: goodbye)_
- that you so much for the help _(gold: thank\_you)_
- thank you for the help _(gold: thank\_you)_
- this was a nice conversation _(gold: goodbye)_
- thank you for the chat, goodbye _(gold: goodbye)_
- it was great to talk to you _(gold: goodbye)_

**Qwen3-0.6B, old prompt**

```text
Is "rescind" a word with a positive connotation?
```

**Qwen3-0.6B, clearer prompt**

```text
"Thank you for helping me out today!"
```

**Qwen3-1.7B, old prompt**

```text
What is the sentiment expressed in the conversation about gratitude and appreciation for help?
```

**Qwen3-1.7B, clearer prompt**

```text
How can I express gratitude in a meaningful way when receiving assistance?
```

**Qwen3-4B, old prompt**

```text
What is the main theme of the following cluster of questions?
```

**Qwen3-4B, clearer prompt**

```text
What are some common ways to express gratitude towards someone?
```

### Cluster 22

- **Size:** 157 members; **purity before:** 0.88 (bin (0.8, 0.9])
- **Gold intents:** cancel\_reservation 138 (88%), calendar\_update 11 (7%), meal\_suggestion 1 (1%), pto\_request\_status 1 (1%)

**10 members**

- remove from calendar jesse's bbq on june 9th _(gold: calendar\_update)_
- get rid of my reservation at chez francois for jennifer _(gold: cancel\_reservation)_
- cancel the dinner reservation i made, okay _(gold: cancel\_reservation)_
- please cancel my dinner reservation for tuesday _(gold: cancel\_reservation)_
- please cancel my reservation for chris at brio _(gold: cancel\_reservation)_
- could you please cancel my reservation for 5 at red robin _(gold: cancel\_reservation)_
- joe and i are to cancel the reservation at zephers now _(gold: cancel\_reservation)_
- i need a reminder to take dinner out of the oven _(gold: reminder\_update)_
- i need you to cancel my reservation for 5 at red robin _(gold: cancel\_reservation)_
- i no longer want my reservation anymore _(gold: cancel\_reservation)_

**Qwen3-0.6B, old prompt**

```text
Can you help me cancel all the dinner reservations and events I've scheduled?
```

**Qwen3-0.6B, clearer prompt**

```text
Can you cancel my dinner reservation for tonight?
```

**Qwen3-1.7B, old prompt**

```text
How can I cancel my dinner reservations and related calendar entries?
```

**Qwen3-1.7B, clearer prompt**

```text
Can you help me cancel my upcoming reservations for dinner and events?
```

**Qwen3-4B, old prompt**

```text
What is the main topic of the following cluster of questions?
```

**Qwen3-4B, clearer prompt**

```text
cancel my dinner reservation please
```

### Cluster 86

- **Size:** 84 members; **purity before:** 0.85 (bin (0.8, 0.9])
- **Gold intents:** spending\_history 71 (85%), transactions 7 (8%), food\_last 3 (4%), how\_busy 1 (1%)

**10 members**

- what transactions did i make yesterday at the flea market _(gold: transactions)_
- how much did i spend on lunches last week _(gold: spending\_history)_
- how much have i spent eating out this week _(gold: spending\_history)_
- what's the total amount i've spent eating out in the last two weeks _(gold: spending\_history)_
- how much have i spent on clothes recently _(gold: spending\_history)_
- have i been giving lot of money to food to food lately _(gold: spending\_history)_
- i have been spending a lot on food out lately _(gold: spending\_history)_
- including the day i missed because of snow, how much time have i take off work so far _(gold: pto\_used)_
- what transactions have i accrued buying dog food _(gold: transactions)_
- how much have i spent on eating out recently _(gold: spending\_history)_

**Qwen3-0.6B, old prompt**

```text
What transactions have I made on liquor in the past month?
```

**Qwen3-0.6B, clearer prompt**

```text
how much have i spent on alcohol recently?
```

**Qwen3-1.7B, old prompt**

```text
What is the total amount spent on food, eating out, alcohol, and other categories in the past month, including recent transactions like dining out, groceries, and coffee?
```

**Qwen3-1.7B, clearer prompt**

```text
What have I spent on beverages recently?
```

**Qwen3-4B, old prompt**

```text
What is the total amount spent on various categories such as food, alcohol, groceries, and other expenses in the past month?
```

**Qwen3-4B, clearer prompt**

```text
What have i spent on various categories of expenses recently?
```

### Cluster 89

- **Size:** 81 members; **purity before:** 0.85 (bin (0.8, 0.9])
- **Gold intents:** schedule\_maintenance 69 (85%), tire\_change 3 (4%), todo\_list 2 (2%), calendar 1 (1%)

**10 members**

- my car needs to be brought for maintenance _(gold: schedule\_maintenance)_
- i want to schedule a tire check up somewhere _(gold: schedule\_maintenance)_
- can i schedule a check up for my tires somewhere _(gold: schedule\_maintenance)_
- is there a special place where i can schedule to check my tires out _(gold: schedule\_maintenance)_
- is there a location i can schedule to check out my tires _(gold: schedule\_maintenance)_
- how i do schedule car maintenance _(gold: schedule\_maintenance)_
- i want to schedule somewhere get my tires checked out _(gold: schedule\_maintenance)_
- can i make an appointment to get my tires checked _(gold: schedule\_maintenance)_
- schedule me an appointment to get my tires checked out _(gold: schedule\_maintenance)_
- help me find somewhere to schedule a check up on my car's tires _(gold: schedule\_maintenance)_

**Qwen3-0.6B, old prompt**

```text
Can you schedule a car maintenance check for me?
```

**Qwen3-0.6B, clearer prompt**

```text
where can i schedule to get my tires checked out?
```

**Qwen3-1.7B, old prompt**

```text
How can I schedule car maintenance and tire checks, including finding local places and making appointments for my vehicle?
```

**Qwen3-1.7B, clearer prompt**

```text
How can I schedule a tire inspection and ensure my car is maintained on time?
```

**Qwen3-4B, old prompt**

```text
How can I schedule car maintenance and tire checks for my vehicle?
```

**Qwen3-4B, clearer prompt**

```text
how do i schedule car maintenance and tire checks
```

### Cluster 140

- **Size:** 160 members; **purity before:** 0.89 (bin (0.8, 0.9])
- **Gold intents:** car\_rental 142 (89%), bill\_due 6 (4%), order 2 (1%), accept\_reservations 1 (1%)

**10 members**

- help me get a rental car for march 2 to 6th in dallas and i would prefer a bmw suv _(gold: car\_rental)_
- i need to find a rental car since i'm travelling to new york tomorrow _(gold: car\_rental)_
- can i get a jeep to rent in bangor from the first of the month to a week after the first _(gold: car\_rental)_
- could i rent a car in seattle from next monday to thursday please _(gold: car\_rental)_
- i need a rental car _(gold: car\_rental)_
- can you help me book a car rental in paris _(gold: car\_rental)_
- what octaine is recommended for this car _(gold: gas\_type)_
- help me book a car rental in chicago for april 1st to 3rd get me an suv if possible _(gold: car\_rental)_
- i want to know when the deadline is to pay my car loan _(gold: bill\_due)_
- can i rent a sports car in augusta for 3/4 through 3/8 _(gold: car\_rental)_

**Qwen3-0.6B, old prompt**

```text
Can you help me book a car rental in Nashville?
```

**Qwen3-0.6B, clearer prompt**

```text
can you help me book a car rental in new york from march 2 to march 4?
```

**Qwen3-1.7B, old prompt**

```text
How can I book a rental car for specific dates and preferences, including location, make, model, and duration?
```

**Qwen3-1.7B, clearer prompt**

```text
How can I find a rental car with specific requirements like a certain make, model, and duration in different cities?
```

**Qwen3-4B, old prompt**

```text
What are the common requests related to car rentals, payments, and reservations?
```

**Qwen3-4B, clearer prompt**

```text
Can you help me book a car rental for a specific date and location with certain preferences?
```

### Cluster 142

- **Size:** 157 members; **purity before:** 0.85 (bin (0.8, 0.9])
- **Gold intents:** no 134 (85%), definition 8 (5%), maybe 4 (3%), change\_volume 2 (1%)

**10 members**

- that's not true _(gold: no)_
- no that is not right _(gold: no)_
- that is not correct _(gold: no)_
- that is false _(gold: no)_
- the answer is no _(gold: no)_
- i'm outta here! _(gold: goodbye)_
- no, that's wrong _(gold: no)_
- what does anachronistic mean _(gold: definition)_
- no, that is incorrect _(gold: no)_
- that is the wrong answer _(gold: no)_

**Qwen3-0.6B, old prompt**

```text
What is the definition of incomprehensible?
```

**Qwen3-0.6B, clearer prompt**

```text
what is the point of sentience?
```

**Qwen3-1.7B, old prompt**

```text
What is the definition of an anachronism and what does it mean for a statement to be false or incorrect?
```

**Qwen3-1.7B, clearer prompt**

```text
What does "no" mean in different contexts?
```

**Qwen3-4B, old prompt**

```text
What is the main theme of the cluster?
```

**Qwen3-4B, clearer prompt**

```text
what is the meaning of no
```

### Cluster 29

- **Size:** 131 members; **purity before:** 0.98 (bin > 0.9)
- **Gold intents:** next\_song 128 (98%), play\_music 2 (2%), update\_playlist 1 (1%)

**10 members**

- play the next musical number _(gold: next\_song)_
- can we stop this song and play the next one _(gold: next\_song)_
- skip to the next song _(gold: next\_song)_
- listen to next song on playlist _(gold: next\_song)_
- play next on the playlist _(gold: next\_song)_
- i am needing the next song to be played _(gold: next\_song)_
- i want the next song played _(gold: next\_song)_
- next song please _(gold: next\_song)_
- play the next one _(gold: next\_song)_
- might we go to the next song _(gold: next\_song)_

**Qwen3-0.6B, old prompt**

```text
What is the next song on the playlist?
```

**Qwen3-0.6B, clearer prompt**

```text
can you play the next song on this playlist?
```

**Qwen3-1.7B, old prompt**

```text
What is the user's request for the next song on the playlist?
```

**Qwen3-1.7B, clearer prompt**

```text
How can I ensure the next song on the playlist is played as requested?
```

**Qwen3-4B, old prompt**

```text
What are the common ways to request the next song in a playlist?
```

**Qwen3-4B, clearer prompt**

```text
play the next song on the playlist
```

### Cluster 67

- **Size:** 100 members; **purity before:** 0.99 (bin > 0.9)
- **Gold intents:** rollover\_401k 99 (99%), account\_blocked 1 (1%)

**10 members**

- i want to rollover my 401k but dont know how _(gold: rollover\_401k)_
- could you roll over my 401k for me _(gold: rollover\_401k)_
- what do i do to rollover my 401k _(gold: rollover\_401k)_
- what are the steps for transferring my 401k _(gold: rollover\_401k)_
- will my 401k carryover or not _(gold: rollover\_401k)_
- rolling over my 401k help _(gold: rollover\_401k)_
- assistance in rolling over my 401k _(gold: rollover\_401k)_
- can 401ks be moved _(gold: rollover\_401k)_
- tell me how to roll over my 401k _(gold: rollover\_401k)_
- i want to rollover my 401k , can i _(gold: rollover\_401k)_

**Qwen3-0.6B, old prompt**

```text
How can I transfer or roll over my 401k account?
```

**Qwen3-0.6B, clearer prompt**

```text
How can I roll over my 401k?
```

**Qwen3-1.7B, old prompt**

```text
How can I transfer or rollover my 401(k) and what steps do I need to follow?
```

**Qwen3-1.7B, clearer prompt**

```text
How can I determine if my 401k can be rolled over to another account?
```

**Qwen3-4B, old prompt**

```text
How can I transfer or rollover my 401k?
```

**Qwen3-4B, clearer prompt**

```text
How can I rollover or transfer my 401k?
```

### Cluster 80

- **Size:** 132 members; **purity before:** 0.98 (bin > 0.9)
- **Gold intents:** roll\_dice 129 (98%), calories 1 (1%), fun\_fact 1 (1%), restaurant\_reservation 1 (1%)

**10 members**

- can you get me a table for 6 at johnnys _(gold: restaurant\_reservation)_
- roll a pair of dice _(gold: roll\_dice)_
- please roll a 6 sided dice _(gold: roll\_dice)_
- will you roll a 2 sided dice _(gold: roll\_dice)_
- could you roll a 6 sided dice _(gold: roll\_dice)_
- roll a 6 sided dice for me _(gold: roll\_dice)_
- shoot the dice! _(gold: roll\_dice)_
- i would like you to roll a dice _(gold: roll\_dice)_
- i need a roll on a 6 sided dice _(gold: roll\_dice)_
- please roll that dice _(gold: roll\_dice)_

**Qwen3-0.6B, old prompt**

```text
What is the number you get when rolling a dice?
```

**Qwen3-0.6B, clearer prompt**

```text
How many calories do you get when rolling a dice?
```

**Qwen3-1.7B, old prompt**

```text
What is the purpose of rolling dice in the context of the cluster?
```

**Qwen3-1.7B, clearer prompt**

```text
What is the typical number of sides on a standard die?
```

**Qwen3-4B, old prompt**

```text
What is a general summary of the cluster of questions?
```

**Qwen3-4B, clearer prompt**

```text
can you roll a dice for me please
```

### Cluster 88

- **Size:** 35 members; **purity before:** 1.00 (bin > 0.9)
- **Gold intents:** are\_you\_a\_bot 35 (100%)

**10 members**

- would you consider yourself to be a bot _(gold: are\_you\_a\_bot)_
- you sound like a bot _(gold: are\_you\_a\_bot)_
- are you a bot right now _(gold: are\_you\_a\_bot)_
- i need to know if you are a bot _(gold: are\_you\_a\_bot)_
- are you actually a bot _(gold: are\_you\_a\_bot)_
- are you considered a bot _(gold: are\_you\_a\_bot)_
- i would like to know if you are a robot _(gold: are\_you\_a\_bot)_
- would it be accurate to call you a bot _(gold: are\_you\_a\_bot)_
- please tell me if you are a bot _(gold: are\_you\_a\_bot)_
- is this a bot _(gold: are\_you\_a\_bot)_

**Qwen3-0.6B, old prompt**

```text
Are you a bot or a person?
```

**Qwen3-0.6B, clearer prompt**

```text
Are you a bot or a person?
```

**Qwen3-1.7B, old prompt**

```text
Are you considered a bot or a human?
```

**Qwen3-1.7B, clearer prompt**

```text
Are you capable of determining whether you are a bot or a human?
```

**Qwen3-4B, old prompt**

```text
Are you a bot or a human?
```

**Qwen3-4B, clearer prompt**

```text
are you a bot or a human
```

### Cluster 144

- **Size:** 114 members; **purity before:** 0.96 (bin > 0.9)
- **Gold intents:** find\_phone 109 (96%), make\_call 2 (2%), bill\_balance 1 (1%), bill\_due 1 (1%)

**10 members**

- find out where my phone is _(gold: find\_phone)_
- please tell me where my phone is _(gold: find\_phone)_
- you need to help me find my cellphone _(gold: find\_phone)_
- tell me where my phone is _(gold: find\_phone)_
- help find my phone _(gold: find\_phone)_
- please help me in finding my phone _(gold: find\_phone)_
- i need your help finding my lost phone _(gold: find\_phone)_
- where would my phone be _(gold: find\_phone)_
- could you help me locate my phone, please _(gold: find\_phone)_
- would you know where to find my phone _(gold: find\_phone)_

**Qwen3-0.6B, old prompt**

```text
Can you help me locate my phone?
```

**Qwen3-0.6B, clearer prompt**

```text
can you locate my phone?
```

**Qwen3-1.7B, old prompt**

```text
How can I locate or find my lost phone or cellphone?
```

**Qwen3-1.7B, clearer prompt**

```text
Can you help me determine where my phone is located?
```

**Qwen3-4B, old prompt**

```text
How can I find my lost or missing phone?
```

**Qwen3-4B, clearer prompt**

```text
can you help me find my lost phone
```
