# 🚀 autonumba Benchmark Results per Activity

| Activity | Original 🐍 (s) | Boosted 🔥 (s) | Faster % | Speed-up | Winner |
|----------|----------------|----------------|-----------|----------|--------|
| Matrix multiply | 0.0690 | 0.3429 | -396.80% | 0.20x | Original 🐍 |
| Fibonacci | 1.2675 | 0.0554 | 95.63% | 22.88x | Boosted 🔥 |
| Heavy loop | 0.0654 | 0.0073 | 88.86% | 8.98x | Boosted 🔥 |

## 📝 Original 🐍 Output

```console
Running heavy Python demo...
Matrix multiply sum: 253152.7707098199
Matrix multiply done in 0.06902456283569336 seconds

Fibonacci(35): 9227465
Fibonacci done in 1.2674589157104492 seconds

Heavy loop result: 273584229
Heavy loop done in 0.0654146671295166 seconds


```

## 📝 Boosted 🔥 Output

```console
Running heavy Python demo...
Matrix multiply sum: 250896.551632291
Matrix multiply done in 0.34291672706604004 seconds

Fibonacci(35): 9227465
Fibonacci done in 0.05539441108703613 seconds

Heavy loop result: 273584229
Heavy loop done in 0.007287740707397461 seconds


```
