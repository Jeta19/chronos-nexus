# Chronos Nexus: Optimizimi i një Qytetërimi Ndëryjor

**Autorja:** Jeta Podrimcaku
**Lënda:** Dizajni i analizave te algoritmave
**Profesori:** Adrian Ymeri
**Gjuha:** Python 

## 1. Përshkrimi i problemit

Sistemi menaxhon një galaktikë me planetë, rrugë, anije dhe misione. Ai merr vendime për:

- gjetjen e rrugës më të mirë mes planetëve, me disa objektiva njëkohësisht (distancë, karburant, kohë, rrezik, besueshmëri)
- parashikimin e mungesave të burimeve dhe krijimin e misioneve proaktive
- shpërndarjen e burimeve mes planetëve me tepricë dhe planetëve me mungesë
- caktimin e anijeve dhe misioneve
- zgjedhjen e infrastrukturës që do të ndërtohet me buxhet të kufizuar
- reagimin ndaj ngjarjeve dinamike pa e rillogaritur krejt planin
- zgjedhjen automatike të algoritmit sipas madhësisë së problemit (Meta-Optimizer)

Qëllimi kryesor është të marrim vendime të mira duke eksploruar sa më pak gjendje dhe duke përdorur sa më pak kohë e memorie.

## 2. Struktura e projektit

| Skedari | Roli |
|---|---|
| `src/models.py` | Klasat: Planet, Route, Spacecraft, Mission, Facility |
| `src/generator.py` | Gjeneruesi i galaktikës (small, medium, large), me seed të fiksuar |
| `src/graph.py` | Grafi (lista e fqinjësisë), Dijkstra dhe A* me kosto të ponderuar dhe pasiguri |
| `src/prediction.py` | Parashikimi i mungesave dhe misionet proaktive |
| `src/flow.py` | Min-Cost Flow (Successive Shortest Path me SPFA) dhe baza Greedy |
| `src/scheduler.py` | Skedulimi i misioneve: Greedy + pruning + memoizim + Local Search |
| `src/infrastructure.py` | Knapsack: Dynamic Programming, Greedy, Branch and Bound |
| `src/events.py` | Ngjarjet dinamike dhe re-planning inkremental |
| `src/meta.py` | Meta-Optimizer: zgjedh algoritmin sipas madhësisë |
| `src/stats.py` | Statistikat e planit |
| `src/main.py` | Programi kryesor që i lidh të gjitha pjesët dhe llogarit CivilizationScore |
| `src/experiments.py` | Eksperimentet e shkallëzimit |
| `src/test_*.py` | Testet dhe eksperimentet e secilit modul |

## 3. Si ekzekutohet

Kërkon Python 3.10 ose më të ri. Nuk përdoret asnjë bibliotekë e jashtme.

```
cd src
py main.py                  # programi i plotë (small), ose: py main.py medium
py test_graph.py            # Dijkstra kundrejt A*
py test_prediction.py       # parashikimi i mungesave
py test_scheduler.py        # skedulimi dhe Local Search
py test_diagnose.py         # diagnoza e misioneve të dështuara
py test_infrastructure.py   # Knapsack
py test_flow.py             # Min-Cost Flow kundrejt Greedy
py test_uncertainty.py      # pasiguria në rrugë
py test_events.py           # rrugë e bllokuar, anije e shkatërruar
py test_events2.py          # prodhim -60%, rrugë e rrezikshme, mision emergjent
py test_meta.py             # Meta-Optimizer
py test_stats.py            # statistikat
py experiments.py           # shkallëzimi small dhe medium
```

Në Linux ose macOS përdor `python3` në vend të `py`. Medium zgjat disa minuta.

## 4. Formulimi matematikor

**Grafi.** G = (V, E) është graf i drejtuar. V janë planetët. Çdo skaj e = (u, v) ka: distancë d, kohë t, karburant f, rrezik r (0 deri 1), kapacitet, besueshmëri ρ (0 deri 1) dhe disponueshmëri.

**Kostoja e një rruge.** Për një mision me pesha w = (w1, w2, w3, w4):

```
base(e, w) = w1*d + w2*f + w3*t + w4*100*r
cost(e, w) = base(e, w) + (1 - ρ) * 1000
```

Faktori 100 e sjell rrezikun (0 deri 1) në të njëjtën shkallë me distancën. Termi `(1 - ρ) * 1000` është kostoja e pritshme e dështimit (probabiliteti i dështimit shumëzuar me koston e një dështimi, vlerë e zgjedhur nga ne).

Çdo lloj misioni ka pesha të ndryshme:

| Lloji | Distancë | Karburant | Kohë | Rrezik |
|---|---|---|---|---|
| cargo | 0.2 | 0.6 | 0.1 | 0.1 |
| emergency | 0.0 | 0.1 | 0.5 | 0.4 |
| balanced | 0.25 | 0.25 | 0.25 | 0.25 |

Misionet me prioritet 1 përdorin `emergency`, ato me ngarkesë karburant, minerale ose materiale përdorin `cargo`, të tjerat `balanced`.

**Pikët e planit të skedulimit** (përdoren nga Local Search, maksimizohen):

```
PlanScore = SUM over missions done ( importance * (6 - priority) * 100 ) - 0.01 * SUM(route cost)
```

**Parashikimi.** Për planet p dhe burim r: `net = production - consumption`. Nëse net < 0, `days_left = stock / (-net)`. Mungesë konsiderohet nëse `days_left <= horizon`.

**Shpërndarja e burimeve (Min-Cost Flow).** Për çdo burim, dhuruesit kanë tepricë, marrësit kanë nevojë. Minimizojmë: kosto transporti + 500 * nevoja e paplotësuar.

**Knapsack.** Maksimizo SUM(value_i * x_i) me kusht SUM(cost_i * x_i) <= B, x_i në {0,1}.

**CivilizationScore** (funksioni global):

```
CivilizationScore = Mission Success + Resource Security + Economic Growth
                    - Transport/10000 - Risk/10

Mission Success   = 100 * misione të kryera / misione gjithsej
Resource Security = 100 * (1 - nevoja e paplotësuar / nevoja totale)
Economic Growth   = vlera e infrastrukturës / 100
```

Peshat janë zgjedhur që çdo komponent të jetë afërsisht në shkallën 0 deri 100, që asnjë të mos dominojë. Janë zgjedhje jonë dhe nuk janë optimizuar eksperimentalisht. Kjo mbulon vetëm një pjesë të termave të kërkuar nga detyra (shih Kufizimet).

## 5. Supozimet

- Koordinatat janë në planin 2D dhe distanca e rrugës është largësia euklidiane mes planetëve.
- Kohën e udhëtimit në scheduler e përafrojmë si `kosto_totale / 10` (shih Kufizimet).
- Dataseti gjenerohet me seed fiks (42), pra rezultatet përsëriten.
- Popullsia është log-uniforme (shumë koloni të vogla, pak qendra të mëdha), konsumi varet nga popullsia, secili planet specializohet në 2 burime.
- 15% e planetëve kanë deficit real në një burim, për të provuar parashikimin.
- Afati i misionit varet nga largësia (`(dist/10 + 20) * slack`), prioriteti 1 është i rrallë dhe ka afat më të ngushtë.

## 6. Strukturat e të dhënave

| Struktura | Përdorimi | Pse |
|---|---|---|
| Lista e fqinjësisë `adj[u]` | Grafi | Memorie O(V + E), kalim i shpejtë i fqinjëve |
| Min-heap (`heapq`) | Dijkstra dhe A* | Nxjerrja e minimumit në O(log n) |
| Dict `dist`, `prev`, set `done` | Kërkimi i rrugës | Ruhen vetëm nyjet e vizituara, jo gjithë grafi |
| Dict cache `(a, b, w) -> (kosto, rruga)` | Scheduler | Memoizim: asnjë rrugë nuk llogaritet dy herë |
| Dict `free_at[ship]`, `loc[ship]` | Scheduler | Gjendja e anijeve, përditësim në O(1) |
| Rrjeti i mbetur (lista skajesh me skaj të kundërt) | Min-Cost Flow | Përditësim i shpejtë i fluksit |
| Deque | SPFA në Min-Cost Flow | Radhë për nyjet që duhen rishikuar |
| Tabela DP `dp[i][c]` | Knapsack | Rindërtimi i zgjedhjes |
| Plani si listë `(mission, ship, start, arrive, path, cost)` | Re-planning | Gjejmë lehtë cilat misione përdorin një rrugë ose anije |

## 7. Algoritmet

### 7.1 A* me kosto të ponderuar (Dijkstra si bazë krahasimi)

Dijkstra eksploron nyjet sipas kostos së grumbulluar g(n). A* e rendit sipas `f(n) = g(n) + h(n)`, ku:

```
h(n) = w1 * distanca_euklidiane(n, destinacioni)
```

**Modifikimi ynë:** kostoja e skajit është multi-objektive (peshat ndryshojnë sipas llojit të misionit) dhe përfshin pasigurinë. Heuristika përdor vetëm komponentin e distancës me peshën w1 të misionit. Çdo skaj kushton të paktën `w1 * d`, ku d është largësia euklidiane mes skajeve, sepse peshat e tjera dhe termi i dështimit janë jonegative.

```
astar(start, goal, w):
    heap = [(h(start), start)]; dist[start] = 0
    while heap:
        u = pop_min(heap)
        if u in done: continue
        done.add(u)
        if u == goal: break
        for each available edge (u, v):
            nd = dist[u] + cost(edge, w)
            if nd < dist[v]:
                dist[v] = nd; prev[v] = u
                push(heap, (nd + h(v), v))
    return dist[goal], rindërto rrugën nga prev
```

**Korrektësia.** Heuristika është e pranueshme (nuk e tejkalon kurrë koston reale) dhe konsistente nga pabarazia e trekëndëshit. Për heuristikë të pranueshme dhe konsistente, A* gjen rrugën optimale. Për misionet emergjente w1 = 0, pra h = 0 dhe A* bëhet Dijkstra. Rrugët e bllokuara (`available = False`) anashkalohen.

### 7.2 Pasiguria në rrugë

Çdo rrugë ka probabilitet dështimi 1 - ρ. Kostoja e pritshme shton `(1 - ρ) * 1000`. Provuam edhe modelin `base / ρ` (riprovë gjeometrike) dhe doli pa efekt praktik (shih 10.10). Heuristika mbetet e pranueshme, sepse termi i ri vetëm e rrit koston.

### 7.3 Parashikimi i mungesave (proaktiv)

Për çdo planet dhe burim me `net < 0`, llogaritet `days_left`. Mungesat renditen nga më urgjentja. Çdo mungesë kthehet në mision dërgese nga planeti më i afërt me tepricë të burimit, me afat `max(20, (days_left - lead_time) * 10)` dhe prioritet 1 nëse `days_left < 15`. Shembulli i detyrës (10,000 ushqim, -400 në ditë) jep saktësisht 25.0 ditë.

### 7.4 Shpërndarja e burimeve: Min-Cost Flow

Për çdo burim ndërtohet rrjeti:

```
burimi -> dhuruesi         (kapaciteti = teprica, kosto 0)
dhuruesi -> marrësi        (kapaciteti = nevoja, kosto = largësia * 0.1)
marrësi -> shuma           (kapaciteti = nevoja, kosto 0)
burimi -> marrësi          (kapaciteti = nevoja, kosto = penalitet 500 për njësi)
```

Algoritmi është Successive Shortest Path me SPFA, i shkruar nga ne. Në çdo iteracion gjen rrugën më të lirë në rrjetin e mbetur dhe dërgon fluks sa pengesa më e ngushtë. Pruning: çdo marrës lidhet vetëm me `k` dhuruesit më të afërt (k = None do të thotë të gjithë).

**Korrektësia:** Successive Shortest Path gjen fluksin me kosto minimale, pasi rrjeti fillestar nuk ka cikle negative dhe çdo augmentim ruan këtë veti. Me k të kufizuar, optimaliteti vlen vetëm brenda grafit të prerë.

### 7.5 Skedulimi i misioneve: Greedy me pruning dhe memoizim

```
greedy_schedule(missions, ships, top_k):
    sorto misionet sipas (prioriteti, afati, -rëndësia)
    for mission in misionet:
        kandidatët = top_k anijet më të afërta (vijë e drejtë) me kapacitet të mjaftueshëm
        për secilën: mbërritja = free_at + (A*(anija->origjina) + A*(origjina->destinacioni)) / 10
        mbaj anijen me mbërritjen më të hershme që e respekton afatin
        nëse asnjë: misioni dështon
        përndryshe: cakto, përditëso free_at dhe loc të anijes
```

**Search-space reduction:** pruning (vetëm `top_k` anijet), memoizim i rrugëve, A* në vend të Dijkstra.

**Garancitë:** heuristikë, pa garanci optimaliteti. Respekton kapacitetin e ngarkesës dhe afatin. Mund të dështojë kur anija më e mirë nuk është mes `top_k` më të afërtave në vijë të drejtë, pasi largësia euklidiane nuk është koha reale e rrugës.

### 7.6 Local Search

Pas greedy, merren 20 misionet e dështuara me vlerën më të lartë `importance * (6 - priority)` dhe 20 misionet e planifikuara me vlerën më të ulët. Misionet e dështuara vendosen në fillim të radhës, ato të dobëtat në fund, dhe skedulimi rillogaritet. Ndryshimi pranohet vetëm nëse PlanScore rritet (hill climbing), maksimumi 3 raunde. Rezultati është diskutuar në 10.3: nuk dha përmirësim në të dhënat tona.

### 7.7 Infrastruktura: Knapsack (tri qasje)

- **Dynamic Programming:** `dp[i][c] = max(dp[i-1][c], dp[i-1][c-w_i] + v_i)`. Kostot rrumbullakohen në njësi prej 10. Optimal deri te gabimi i rrumbullakimit.
- **Greedy:** rendit sipas `vlera/kosto`. I shpejtë, jo gjithmonë optimal.
- **Branch and Bound:** kufiri i sipërm nga relaksimi fraksional. Dega pritet nëse kufiri <= zgjidhja më e mirë e njohur. Optimal kur nuk arrin kufirin e nyjeve.

### 7.8 Re-planning inkremental

Kur ndodh një ngjarje, nuk e rillogarisim krejt planin:

```
replan(plan, ngjarja):
    affected = misionet që përdorin rrugën e ndryshuar (ose anijen e shkatërruar)
    keep = plani pa affected
    llogarit gjendjen e anijeve pas keep (koha e lirë, vendndodhja)
    riskedulo vetëm affected me greedy mbi atë gjendje
    return keep + plani_i_ri
```

**Çka rillogaritet:** vetëm misionet e prekura. **Çka mbetet:** të gjitha të tjerat. Zbulimi i misioneve të prekura bëhet duke kaluar planin, O(M * L), ku L është gjatësia e rrugës.

Ngjarje të implementuara (5):

1. rrugë e bllokuar
2. anije e shkatërruar
3. prodhimi i një planeti bie 60% (ndikon te parashikimi)
4. rrugë bëhet shumë më e rrezikshme (rrezik dhe besueshmëri të ndryshuara)
5. mision i ri emergjent (skedulohet pa e prekur planin ekzistues)

### 7.9 Meta-Optimizer

Klasa `MetaOptimizer` zgjedh algoritmin sipas madhësisë së problemit dhe e ruan çdo vendim me arsyen në `meta.log`:

| Komponenti | Kushti | Zgjedhja |
|---|---|---|
| Skedulimi | misione <= 100 | Greedy me top_k = 20 |
| Skedulimi | misione <= 1000 | Greedy me top_k = 10 |
| Skedulimi | misione > 1000 | Greedy me top_k = 5 |
| Infrastruktura | objekte <= 25 | Branch and Bound |
| Infrastruktura | objekte > 25 | Dynamic Programming |
| Shpërndarja | planetë <= 300 | Min-Cost Flow me k = None |
| Shpërndarja | planetë > 300 | Min-Cost Flow me k = 10 |
| Ngjarje | çdo | re-planning inkremental |

Pragjet janë zgjedhje jonë dhe nuk janë optimizuar eksperimentalisht.

## 8. Pjesët NP-hard

| Pjesa | Pse është e vështirë | Çka përdorim |
|---|---|---|
| Skedulimi i misioneve me anije, afate dhe kapacitete | Lidhet me job-shop scheduling dhe vehicle routing (NP-hard) | Greedy + pruning + Local Search |
| Knapsack i infrastrukturës | 0/1 Knapsack është NP-hard (por pseudo-polinomial) | DP për saktësi, B&B për pruning, Greedy për shpejtësi |
| Rrugë me disa objektiva njëkohësisht | Gjetja e të gjitha rrugëve Pareto është NP-hard | Shumë objektiva të kombinuar në një kosto të ponderuar, e zgjidhur në kohë polinomiale |

Zgjidhja e saktë e skedulimit eksploron një hapësirë eksponenciale (kombinime anije-mision-kohë), ndaj përdorim heuristika. Min-Cost Flow, në të kundërt, zgjidhet saktë në kohë polinomiale.

## 9. Kompleksiteti

V = planetë, E = rrugë, M = misione, S = anije, K = top_k, n = objekte, B = buxheti, u = njësia e rrumbullakimit, A = misionet e prekura, F = augmentimet e flow-it, R = llojet e burimeve.

| Algoritmi | Koha (rasti më i keq) | Hapësira | Vërejtje |
|---|---|---|---|
| Dijkstra | O((V + E) log V) | O(V) | |
| A* | O((V + E) log V) | O(V) | Në praktikë eksploron shumë më pak nyje |
| Parashikimi | O(V * R + P log P) | O(P) | P = mungesat e gjetura |
| Min-Cost Flow (SSP + SPFA) | O(F * V' * E') | O(V' + E') | V', E' = rrjeti i flow-it, F augmentime (62 në small, 591 në medium) |
| Greedy scheduler | O(M log M + M * (S log S + K * E log V)) | O(V + M + cache) | K konstante |
| Local Search | O(raunde * koha e Greedy) | njëlloj | |
| Knapsack DP | O(n * B/u) | O(n * B/u) | Pseudo-polinomial |
| Knapsack Greedy | O(n log n) | O(n) | |
| Knapsack B&B | O(2^n) | O(n) | Në praktikë shumë më pak (shih 10.4) |
| Re-planning | O(M * L + A * (S log S + K * E log V)) | O(M) | Në vend të të gjithë M |

Kompleksiteti i observuar dallon nga ai teorik, shih shkallëzimin në 10.7.

## 10. Eksperimentet

Metodologjia: dataset i gjeneruar me seed 42, matje me `time.time()` dhe `tracemalloc`. Rezultatet janë nga një ekzekutim i vetëm, pa përsëritje statistikore. Disa eksperimente u kryen me versionin e parë të gjeneratorit (**v1**: afate dhe burime të rastësishme), të tjerat me versionin realist (**v2**). Secila tabelë e tregon versionin. Kodi i A* ndryshoi gjatë projektit (u shtua pasiguria), kështu që matjet e kohës mes eksperimenteve të ndryshme nuk janë gjithmonë të krahasueshme.

### 10.1 Dijkstra kundrejt A* (v1, 1000 planetë, 10,000 rrugë, 100 misione, pesha `cargo`)

| | Kosto totale | Nyje të eksploruara | Koha |
|---|---|---|---|
| Dijkstra | 101,644.8 | 51,222 | 0.445s |
| A* | 101,644.8 | 36,253 | 0.386s |

Kostoja është identike, pra A* gjen të njëjtën rrugë optimale, me **29% më pak nyje**.

### 10.2 Pruning në scheduler (v1, 700 misione, 1000 planetë, 100 anije)

| | Të gjitha anijet | top_k = 10 |
|---|---|---|
| Të planifikuara | 502 | 500 |
| Të dështuara | 198 | 200 |
| Nyje të eksploruara | 14,098,506 | 2,619,032 |
| Koha | rreth 132 deri 143s | 22.6s |

Pruning ul nyjet me **81%** dhe kohën rreth 6 herë, me kosto vetëm 2 misione (0.4%).

### 10.3 Local Search dhe diagnoza e dështimeve

- Në v1 (700 misione): 0 përmirësime. Diagnoza e 100 misioneve të dështuara: **97 kishin afat të pamundur** edhe me anije plotësisht të lirë, vetëm 3 dështuan për shkak të anijeve të zëna, 0 për ngarkesë tepër të madhe. Rirenditja nuk mund të zgjidhë afate të pamundura.
- Pas rregullimit të gjeneratorit (v2, afati varet nga largësia): të gjitha misionet planifikohen (510 nga 510 në small), pra Local Search nuk ka çfarë të shpëtojë (0 përmirësime).

Përfundim: Local Search me rirenditje është i dobishëm vetëm kur anijet janë pengesa. Në të dhënat tona dështimet vinin nga afatet, kështu që nuk dha përfitim. E raportojmë si kufizim, jo si rezultat pozitiv.

### 10.4 Knapsack (v2, 40 objekte, buxheti 5000)

| Algoritmi | Vlera | Kosto | Objekte | Koha | Nyje |
|---|---|---|---|---|---|
| DP | 3374.8 | 4959.2 | 11 | 0.0089s | n/a |
| Greedy | 3362.8 | 4914.8 | 11 | 0.0001s | n/a |
| B&B | 3374.8 | 4959.2 | 11 | 0.0005s | 229 |

DP dhe B&B japin të njëjtën vlerë optimale. Greedy është 0.36% nën optimumin dhe shumë më i shpejtë. B&B eksploroi 229 nyje nga 2^40 (rreth 1.1 * 10^12) kombinime të mundshme. Vërejtje: në ekzekutimet e tjera DP jep vlera pak më të ulëta (p.sh. 3283.0) sepse buxheti dhe rrumbullakimi i kostove ndryshojnë rezultatin; B&B është i saktë.

### 10.5 Re-planning inkremental (v2, 100 planetë, 50 misione)

| Ngjarja | Misione të prekura | Inkremental | Rillogaritje e plotë | Shpejtësia |
|---|---|---|---|---|
| Rrugë e bllokuar (89->73) | 11 nga 50 | 3,925 nyje, 0.033s | 16,936 nyje, 0.144s | 4.3x |
| Anije e shkatërruar (nr. 17) | 5 nga 50 | 1,397 nyje, 0.016s | 16,526 nyje, 0.148s | 9.5x |

Kontrolli i korrektësisë: pas të dyja ngjarjeve, asnjë mision nuk përdor rrugën e bllokuar ose anijen e shkatërruar (0 shkelje), dhe të 50 misionet mbeten të planifikuara. Sa më pak misione preken, aq më i madh fitimi.

### 10.6 Parashikimi

- Shembulli i detyrës: 25.0 ditë (saktë).
- v2, horizont 120 ditë: small 42 mungesa, medium 395 mungesa.
- Me horizont 60 ditë në small ka vetëm 2 mungesa, kështu që horizonti është parametër i rëndësishëm.

### 10.7 Shkallëzimi (v2, horizont 120)

| Dataset | Planetë | Rrugë | Mungesa | Misione | Planifikuar | Dështuar | Nyje | Koha e skedulimit | Memoria |
|---|---|---|---|---|---|---|---|---|---|
| small | 100 | 500 | 42 | 92 | 92 | 0 | 30,354 | 1.91s | 0.7 MB |
| medium | 1000 | 10,000 | 395 | 700 | 700 | 0 | 1,976,364 | 254.33s | 7.4 MB |

Memoria rritet afërsisht në përpjesëtim me madhësinë (10x). Koha rritet shumë më shpejt (rreth 133x), sepse çdo kërkim A* në graf më të madh eksploron më shumë nyje dhe ka më shumë misione. Datasetet large dhe extreme nuk u provuan (shih Kufizimet).

### 10.8 Statistikat e një ekzekutimi (small, 52 misione, horizont 60)

Misione të kryera: 52, të dështuara: 0. Distanca totale 117,728.9. Karburanti total 105,829.8. Rreziku total 45.77. Nyje të eksploruara 18,025. Koha 1.01s. Memoria maksimale 0.5 MB.

### 10.9 Shpërndarja e burimeve: Min-Cost Flow kundrejt Greedy (v2, horizont 120, penalitet 500)

| Dataset | Metoda | Transport | Paplotësuar | TOTAL | Koha |
|---|---|---|---|---|---|
| small | Greedy | 544,565.5 | 0 | 544,565.5 | 0.003s |
| small | MCF k=5 | 455,668.9 | 2,460.9 | 1,686,105.0 | 0.010s |
| small | MCF k=10 | 544,561.7 | 0 | 544,561.7 | 0.013s |
| small | MCF k=None | 544,561.7 | 0 | 544,561.7 | 0.017s |
| medium | Greedy | 728,785.7 | 0 | 728,785.7 | 0.160s |
| medium | MCF k=5 | 640,190.3 | 12,619.7 | 6,950,056.3 | 0.679s |
| medium | MCF k=10 | 727,763.3 | 0 | 727,763.3 | 0.912s |
| medium | MCF k=20 | 727,763.8 | 0 | 727,763.8 | 1.240s |
| medium | MCF k=None | 727,763.8 | 0 | 727,763.8 | 11.820s |

MCF gjen optimumin. Me k=5 pruning-u është shumë agresiv: shumë marrës ndajnë të njëjtët dhurues të afërt, ata mbarojnë, dhe mbeten nevoja të paplotësuara. Me k=10 arrihet i njëjti optimum si pa pruning, 13 herë më shpejt në medium. Greedy është vetëm 0.14% më i keq se optimumi në këto të dhëna, ndaj përfitimi i MCF është i vogël; vlera e tij është garancia e optimalitetit.

### 10.10 Pasiguria në planifikimin e rrugës (v2, 1000 planetë, 100 misione, pesha balanced)

| Modeli | Probabiliteti mesatar i sukseshit të rrugës | Hop mesatar |
|---|---|---|
| Pa pasiguri | 0.7897 | 4.78 |
| base / ρ (riprovë gjeometrike) | 0.7892 | 4.81 |
| base + (1 − ρ) * 1000 (penalitet dështimi) | 0.8330 | 4.27 |

Modeli i parë nuk ndryshoi zgjedhjet, sepse ρ është 0.90 deri 0.999 dhe faktori 1/ρ ndryshon koston vetëm pak krahasuar me distancën dhe karburantin. Modeli i dytë ka ndikim real: rrugët zgjidhen me 4.3 pikë përqindjeje më shumë sukses, dhe hop mesatar u ul (rrugët e pabesueshme janë shpesh shkurtore). Heuristika e A* mbetet e pranueshme. Kufizim: vlera 1000 e kostos së dështimit është zgjedhje jonë, jo e matur.

### 10.11 Meta-Optimizer (v2, horizont 120)

| Dataset | Skedulimi | Infrastruktura | Shpërndarja | Planifikuar | Nyje | Koha e skedulimit |
|---|---|---|---|---|---|---|
| small | Greedy top_k=20 | DP | MCF k=None | 92 / 92 | 49,662 | 0.52s |
| medium | Greedy top_k=10 | DP | MCF k=10 | 700 / 700 | 2,251,207 | 52.67s |

Meta-Optimizer zgjedh më shumë cilësi (top_k më i madh, MCF pa pruning) kur problemi është i vogël, dhe më shumë pruning kur është i madh. Kujdes: koha 52.67s në medium nuk krahasohet drejtpërdrejt me 254.33s të 10.7, sepse kodi i A* ndryshoi mes dy matjeve (pasiguria) dhe nuk e kemi matur veçmas efektin e Meta-Optimizer. Nuk pretendojmë që Meta-Optimizer e shpejtoi sistemin. Pragjet janë zgjedhje jonë.

### 10.12 Ngjarje shtesë (v2, 100 planetë, 92 misione)

| Ngjarja | Efekti | Reagimi |
|---|---|---|
| Prodhimi i planetit 10 bie 60% | mungesa të parashikuara 42 → 44 | parashikimi rillogaritet, misione proaktive të reja |
| Rruga 56→57 bëhet shumë e rrezikshme (risk 0.5, reliability 0.6) | 9 misione të prekura nga 92 | riplanifikim inkremental, 0.044s, 0 dështime |
| Mision i ri emergjent (medicine, priority 1) | skedulohet pa e prekur planin | 321 nyje, 0.005s, plani 92 → 93 |

Në të gjitha rastet plani mbetet i vlefshëm dhe vetëm pjesa e prekur rillogaritet.

### 10.13 Programi i plotë dhe CivilizationScore (small, `py main.py`)

| Metrika | Vlera |
|---|---|
| Planetë, rrugë, misione, anije | 100, 500, 92, 20 |
| Mungesa të parashikuara | 42 |
| Misione të kryera / të dështuara | 92 / 0 |
| Burime të paplotësuara | 0.0 |
| Transport | 544,561.7 |
| Infrastruktura | 12 objekte, vlera 3283.0, kosto 4962.6 |
| Distanca, karburanti, rreziku | 204,829.3 / 183,419.8 / 77.34 |
| Ngjarje të trajtuara | 2 (rrugë e bllokuar, anije e shkatërruar) |
| Koha mesatare e re-planning | 0.162s |
| Nyje të eksploruara | 54,764 |
| Koha totale, memoria maksimale | 3.94s, 0.9 MB |
| **CivilizationScore** | **170.6** (Mission Success 100, Resource Security 100, Economic 32.8) |

Pas të dy ngjarjeve plani mbeti me 92 misione dhe 0 dështime. Transporti zbret vetëm rreth 54.5 pikë nga score-i, sepse e pjesëtuam me 10,000; ky peshim është zgjedhje jonë.

## 11. Kufizimet (çka nuk bën sistemi)

Raportojmë me ndershmëri çka mungon ose është i thjeshtuar:

- **Nuk kemi implementuar:** Pareto/multi-objective të vërtetë (përdorim shumë të peshuar në një kosto), algoritëm gjenetik, simulated annealing, ndërtimin e infrastrukturës të lidhur me planetët (Knapsack zgjedh nga një listë globale objektesh me buxhet fiks 5000).
- **Pasiguria:** rreziku dhe besueshmëria hyjnë në koston e rrugës, por nuk modelojmë kohë udhëtimi të ndryshueshme (p.sh. 8 deri 15 orë) ose dështim të rrugës në mënyrë stokastike gjatë simulimit.
- **Kufizime fizike:** koha e udhëtimit është përafrim (`kosto / 10`), jo koha reale. Karburanti i anijes dhe kapaciteti i rrugës nuk kontrollohen gjatë skedulimit (kontrollohet vetëm kapaciteti i ngarkesës). Misionet nuk lidhen automatikisht me burimet e shpërndara nga Min-Cost Flow (MCF llogaritet si komponent i veçantë).
- **Pruning gjeometrik:** zgjedhja e `top_k` anijeve më të afërta me vijë të drejtë mund të humbasë anijen më të mirë.
- **Local Search** është i thjeshtë (rirenditje) dhe nuk ndryshon anijet apo rrugët.
- **Meta-Optimizer** përdor pragje fikse sipas madhësisë; nuk mat vetë performancën dhe nuk përdor buxhet kohe ose memorie të vendosur paraprakisht.
- **CivilizationScore** mbulon vetëm disa nga termat e detyrës (Mission Success, Resource Security, Economic Growth, kosto transporti, rrezik). Nuk përfshin Scientific Progress, Territorial Expansion, Population Survival, Energy Consumption dhe Computational Cost si terma të veçantë.
- **Shkallëzimi:** koha rritet shumë me madhësinë. Python është i ngadaltë, dhe datasetet large dhe extreme nuk u provuan. Përmirësime të mundshme: A* dypalësh, ALT me pika referimi, implementim në C++, `top_k` më i vogël.
- Rezultatet janë nga një seed dhe një ekzekutim. Disa eksperimente janë me gjeneratorin v1, të tjerat me v2, dhe kodi ndryshoi gjatë projektit, ndaj disa kohëra nuk krahasohen drejtpërdrejt.

## 12. Përfundime

- A* gjeti të njëjtat rrugë optimale si Dijkstra me 29% më pak nyje.
- Pruning në scheduler uli nyjet me 81% me humbje cilësie shumë të vogël (0.4% e misioneve).
- Re-planning inkremental u tregua 4 deri 10 herë më i shpejtë se rillogaritja e plotë, me plan të vlefshëm pas ngjarjes. U trajtuan 5 lloje ngjarjesh.
- Për Knapsack, DP dhe B&B konfirmojnë optimumin, B&B me pruning shumë të madh.
- Min-Cost Flow arrin optimumin, dhe me k=10 e arrin 13 herë më shpejt se pa pruning. Greedy është vetëm 0.14% më i keq në këto të dhëna.
- Modeli i pasigurisë me penalitet dështimi rriti suksesin e rrugës nga 78.97% në 83.30%; modeli `base/ρ` nuk kishte efekt.
- Local Search nuk dha përfitim në datasetet tona dhe e shpjeguam pse (97% e dështimeve ishin afate të pamundura).
- Pika e dobët është shkallëzimi i kohës në graf të madh në Python.