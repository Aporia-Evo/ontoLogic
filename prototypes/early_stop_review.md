# Früher Abbruch: Ergebnis

Auf den 20 bisherigen Aufgaben spart die Abbruchbedingung Arbeit. Der gelernte Operator bleibt insgesamt teurer: Lernen plus Anwendung benötigt 4,23-mal so viele primitive Rechenoperationen wie BASE.

| Phase | Primitive Rechenoperationen | Laufzeit, Median |
|---|---:|---:|
| BASE | 697.935 | 94 ms |
| Lernen | 2.031.526 | 303 ms |
| Anwendung mit C08 `mul(x,x)` | 917.791 | 125 ms |
| Lernen + Anwendung | 2.949.317 | 430 ms |

Der Gesamtmedian stammt aus den gepaarten Summen je Durchlauf. Die drei Zeitmessungen geben nur eine grobe Orientierung; die Operationszähler waren in allen Durchläufen identisch.

## Was geändert wurde

Jeder Sucharm baut eine gemeinsame Tabelle für alle 20 Ziele. Sobald die letzte Zielsignatur aufgenommen ist, endet die Suche unmittelbar innerhalb der aktuellen Kostenschicht. Deren bereits erfolgte Erzeugung und Sortierung zählt weiter zum Aufwand. Das Lernen und die Auswahlregel bleiben gleich.

BASE stoppt bei Kostenstufe 9, C08 bei 8. Trotzdem benötigt C08 bei der Anwendung etwa 32 % mehr primitive Operationen. Eine kürzere Darstellung reicht hier also nicht für eine günstigere Suche.

Gegenüber der vorherigen vollständigen Enumeration sinkt der Anwendungsaufwand mit C08 von 3.902.549 auf 917.791 Operationen; BASE sinkt von 785.071 auf 697.935. Die Gesamtbilanz verbessert sich von 7,56 auf 4,23 BASE-Aufwände.

## Prüfung und Bedeutung

Alle 20 Aufgaben werden in beiden Armen gelöst. Alle 120 Programmrückgaben aus drei Durchläufen stimmen mit dem vorherigen Versuch überein. Die Lernkosten und das Auswahlergebnis C08 bleiben gleich. Kleine gezielte Prüfungen bestätigen den Abbruch innerhalb einer Schicht und das Warten auf sämtliche Ziele in beiden Armen.

Dies ist eine nachträgliche Messung auf dem bekannten D20-Aufgabenblock. Sie zeigt den Nutzen dieser konkreten Suchverbesserung. Der wirtschaftliche Nutzen des Lernens bleibt auf diesem Block unbelegt; die beobachtete Gesamtbilanz ist negativ.

Code vor der Messung festgehalten: `4ccf99fe3fef446664e6ae55cb67a8e06742d4c9`.

Reproduktion neben den unveränderten D16-/D21-Quelldateien:

```sh
node operator_learning_early_stop_prototype.cjs --check
node operator_learning_early_stop_prototype.cjs > early_stop_result.json
```

Die Rohdaten stehen in `early_stop_result.json`, einschließlich Quellhashes, Umgebung, Einzelmessungen und Programmen. Vergleich: `actual_cost_result.json`.
