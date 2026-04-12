# Ontologic — iOS Foundation

Ontologic is an iOS app where users draw a symbol and the app recognises it,
explaining its meaning, origin, category and related symbols.

---

## Project Structure

```
Ontologic/
├── App/
│   ├── OntologicApp.swift          # @main entry point; dependency injection root
│   └── RootTabView.swift           # Tab bar + per-tab NavigationStack
│
├── Core/
│   ├── DesignSystem/
│   │   ├── Colors.swift            # Brand palette (fallback hex + Asset Catalog hooks)
│   │   ├── Typography.swift        # Font scale + View modifier helpers
│   │   └── Components/
│   │       ├── OButton.swift       # Primary / secondary / ghost / destructive buttons
│   │       ├── OCard.swift         # Card container + CandidateCard + ConfidenceBar
│   │       ├── StatusBadge.swift   # CategoryBadge, TagBadge, ConfidenceBadge, FlowLayout
│   │       └── LoadingView.swift   # LoadingView, EmptyStateView, ErrorView
│   │
│   ├── Models/
│   │   ├── SymbolCandidate.swift   # Recognition candidate + SymbolCategory enum
│   │   ├── SymbolDetail.swift      # Full symbol detail with mock data
│   │   ├── RecognitionRequest.swift# Request envelope (image + canvas metadata)
│   │   ├── RecognitionResponse.swift # Response envelope + RecognitionError
│   │   └── HistoryEntry.swift      # Past recognition sessions
│   │
│   ├── Networking/
│   │   ├── Protocols/
│   │   │   └── RecognitionServiceProtocol.swift  # Service contract
│   │   ├── Mock/
│   │   │   └── MockRecognitionService.swift       # In-memory mock with configurable latency
│   │   └── APIClient.swift         # Live URLSession implementation (ready to enable)
│   │
│   └── Persistence/
│       ├── Protocols/
│       │   └── RepositoryProtocol.swift  # Generic + feature-specific repo contracts
│       └── UserDefaultsRepository.swift  # UserDefaults-backed history & favourites
│
└── Features/
    ├── Home/           HomeView + HomeViewModel
    ├── Draw/           DrawView + DrawViewModel + CanvasView (UIViewRepresentable)
    ├── Results/        ResultsView + ResultsViewModel
    ├── SymbolDetail/   SymbolDetailView + SymbolDetailViewModel
    ├── History/        HistoryView + HistoryViewModel
    ├── Favorites/      FavouritesView + FavouritesViewModel
    └── Settings/       SettingsView + SettingsViewModel
```

---

## Architecture

### MVVM + Feature modules

Each feature is a self-contained folder with a **View** (SwiftUI, presentation
only) and a **ViewModel** (`ObservableObject`, owns business logic and state).
Views observe the ViewModel via `@StateObject` / `@ObservedObject`.

```
View  ──(@StateObject)──▶  ViewModel  ──(async/await)──▶  Service / Repository
  ◀──────(@Published)────────────────────────────────────
```

### Navigation

`RootTabView` owns a `TabView` with five tabs. Each tab has its own
`NavigationStack` with typed `navigationDestination` registrations. This means:

- Back navigation works automatically per tab.
- Deep-links can be expressed by appending typed values to the `NavigationPath`.
- No global router singleton — navigation state lives in the view hierarchy.

### Dependency Injection

`OntologicApp` (the `@main` entry) is the **composition root**. It creates all
shared service/repository instances and passes them down. To switch from the
mock service to the live API, change one line:

```swift
// OntologicApp.swift
private let recognitionService: any RecognitionServiceProtocol
    = MockRecognitionService()       // ← replace with APIRecognitionService()
```

### Service protocol

`RecognitionServiceProtocol` decouples all feature code from the concrete
network layer. Tests and Previews use `MockRecognitionService` (zero latency
variant available via `.preview`).

### Persistence

`RepositoryProtocol` provides a generic CRUD contract. The current
implementation (`UserDefaultsRepository`) stores `Codable` entities as JSON
blobs. Migrating to CoreData or SwiftData requires only a new conforming type —
feature ViewModels call only protocol methods.

### Design system

All colours, fonts and reusable components live in `Core/DesignSystem`. Named
colour assets follow the `Onto*` prefix convention. A `hex:` fallback is used
so Previews render correctly even without a compiled Asset Catalog.

---

## Definition of Done — Status

| Criterion | Status |
|---|---|
| App starts | ✅ Entry point + RootTabView |
| Tab navigation | ✅ 5 tabs with NavigationStack per tab |
| Draw screen — local drawing | ✅ UIKit canvas with stroke model |
| Mock recognition flow → Results | ✅ DrawViewModel → MockRecognitionService → ResultsView |
| Results show candidates + confidence | ✅ CandidateCard with ConfidenceBar |
| Detail screen with mock data | ✅ SymbolDetailView with meaning, origin, tags |

---

## Next Steps for Other Agents

1. **API Agent** — implement the live `APIRecognitionService`, wire up
   authentication headers and error retry logic.
2. **ML Agent** — replace the mock with on-device Core ML inference for offline
   recognition.
3. **UI/Polish Agent** — add Canvas ink smoothing (Catmull-Rom splines),
   animations, haptic feedback integration.
4. **Asset Catalog Agent** — add the `Onto*` named colours in
   `Assets.xcassets` with dark/light variants.
5. **Testing Agent** — unit tests for ViewModels and repositories; snapshot
   tests for design system components.
