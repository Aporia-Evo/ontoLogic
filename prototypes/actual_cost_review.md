# Tatsächliche Kosten des Operatorlernens

Stand: 5. September 2026. Retrospektive Messung des vorhandenen Ablaufs.

Frage: Zahlt sich die bestehende Operatorauswahl einschließlich des Lernens auf den 20 bekannten D20-Aufgaben aus?

Ergebnis: Der Lerner wählt wieder C08, `x*x`. Beide Verfahren liefern alle 20 Programme. Lernen plus Anwendung benötigt 5.934.075 ausgeführte arithmetische Operationen; die Basissuche benötigt 785.071. Das Verhältnis beträgt 7,56.

| Phase | Ausgeführte arithmetische Operationen | Signaturauswertungen | Sortiervergleiche |
|---|---:|---:|---:|
| Lernen und Auswahl | 2.031.526 | 94.327 | 278.746 |
| Anwendung des gewählten Operators | 3.902.549 | 118.577 | 310.833 |
| Lernen plus Anwendung | 5.934.075 | 212.904 | 589.579 |
| Basissuche | 785.071 | 29.496 | 75.391 |

Die mediane Laufzeit beträgt rund 790 ms für Lernen plus Anwendung und 91 ms für die Basissuche. Die mediane CPU-Zeit beträgt 957 ms beziehungsweise 99 ms. CPU-Zeit umfasst Prozess-Threads und kann deshalb höher als die verstrichene Zeit sein. Grundlage sind drei aufeinanderfolgende Runden mit wechselnder Reihenfolge der beiden Anwendungsarme im selben Node-Prozess. Die Zähler sind in allen Runden identisch; die Zeiten enthalten den Messaufwand und sind lokale Beobachtungen.

## Was genau abgerechnet wird

Lernen umfasst die Initialisierung des D16-Moduls, den Aufbau seiner Basistabelle, die ursprüngliche Auswahl unter 14 Kandidaten auf 18 Trainingsaufgaben und die Bereitstellung der gewählten Definition. Die bisherige Auswahlregel bleibt bestehen. Sie wird weiterhin anhand der alten modellierten Suchkosten trainiert; gemessen werden hier erstmals die tatsächlich anfallenden Kosten dieses Lernablaufs.

Jeder Anwendungsarm baut eine eigene gemeinsame Suchtabelle bis Kostenstufe 9 und fragt daraus die 20 Ziele ab. Gemessen werden Modulinitialisierung, vollständiger Tabellenaufbau, Abfragen und Programmformatierung. Die Basistabelle aus dem Training endet bei Stufe 7; für die Anwendung baut der vorhandene Ablauf eine neue Tabelle auf. Dateilesen, Berichtsausgabe und nachträgliche Ergebnisprüfungen liegen außerhalb der Phasenmessung.

Die arithmetischen Zähler sitzen direkt an der Ausführung von Addition, Subtraktion und Multiplikation. Auch Arbeit an später verworfenen Ausdrücken wird gezählt. Bei der Anwendung von C08 sind das 104.545 zusätzliche Operationen gegenüber dem bisherigen Zähler für gültige Ausdrücke. Sortierung und andere Laufzeitarbeit sind außerdem in den Zeitmessungen enthalten; Sortiervergleiche werden separat gezählt.

## Korrektur der bisherigen Interpretation

D21 meldete summierte Kosten bis zur vollständigen Fundstufe jeder einzelnen Aufgabe. Der ausgeführte Code baut dagegen gemeinsame Tabellen bis zur festen Suchgrenze. Diese beiden Kostenmodelle beantworten unterschiedliche Fragen. Die frühere Zahl von 26 Prozent Mehrarbeit ist deshalb kein gemessener Laufzeitvergleich dieses Ablaufs.

Weitere Abfragen an dieselbe fertige Tabelle amortisieren deren Aufbau. Das gilt für beide Arme. Eine Hochrechnung, die jede zusätzliche Aufgabe erneut mit der alten vollen Suchersparnis verrechnet, passt daher nicht zu dieser Implementierung.

## Entscheidung

Für diesen bekannten Aufgabenblock ist der Lernaufwand durch die Anwendung nicht ausgeglichen. Die Messung prüft die Kosten des vorhandenen Ablaufs. Ein Vorteil auf einer neuen Aufgabenstruktur bleibt eine offene Forschungsfrage.

Als nächste einzelne Implementierungsfrage bietet sich an: Wie verändert sich die Bilanz, wenn der gemeinsame Suchlauf endet, sobald alle Ziele gefunden sind? Das Abbruchkriterium muss in beiden Armen gleich sein; anschließend werden dieselben Phasen erneut gemessen.

## Reproduktion

Im Verzeichnis `prototypes` des [festgehaltenen Quellstands](https://github.com/Aporia-Evo/ontoLogic/commit/2f7874c0c3dbd8c64c5773669473167f31385cf4):

```sh
node operator_learning_actual_cost_prototype.cjs --check
node operator_learning_actual_cost_prototype.cjs > actual_cost_result.json
```

Das Skript prüft die SHA-256-Werte der beiden Quelldateien. Drei kleine Gegenprüfungen decken einfache, verschachtelte und verworfene Ausdrücke ab. Der ursprüngliche D16-Discovery-Seal wird reproduziert. Alle 120 zurückgegebenen Programme aus drei Runden und zwei Armen stimmen mit D21 überein. Die vollständigen Rohwerte einschließlich der Einzelzeiten stehen in `actual_cost_result.json`.
