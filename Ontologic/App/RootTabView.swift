// MARK: - RootTabView.swift
// Top-level tab container. Owns the NavigationPath for each tab so that
// deep-links and programmatic navigation can be handled from a single place.

import SwiftUI

// MARK: - Tab definition

enum AppTab: Int, CaseIterable {
    case home
    case draw
    case history
    case favourites
    case settings

    var title: String {
        switch self {
        case .home:       return "Home"
        case .draw:       return "Draw"
        case .history:    return "History"
        case .favourites: return "Favourites"
        case .settings:   return "Settings"
        }
    }

    var icon: String {
        switch self {
        case .home:       return "house"
        case .draw:       return "pencil.and.scribble"
        case .history:    return "clock.arrow.circlepath"
        case .favourites: return "star"
        case .settings:   return "gearshape"
        }
    }

    var selectedIcon: String {
        switch self {
        case .home:       return "house.fill"
        case .draw:       return "pencil.and.scribble"
        case .history:    return "clock.arrow.circlepath"
        case .favourites: return "star.fill"
        case .settings:   return "gearshape.fill"
        }
    }
}

// MARK: - RootTabView

struct RootTabView: View {

    // MARK: Dependencies
    let recognitionService: any RecognitionServiceProtocol
    let historyRepository: UserDefaultsHistoryRepository
    let favouritesRepository: UserDefaultsFavouritesRepository

    // MARK: State
    @State private var selectedTab: AppTab = .home

    // Per-tab navigation stacks
    @State private var homeNavPath       = NavigationPath()
    @State private var historyNavPath    = NavigationPath()
    @State private var favouritesNavPath = NavigationPath()

    var body: some View {
        TabView(selection: $selectedTab) {

            // Home
            NavigationStack(path: $homeNavPath) {
                HomeView()
                    .navigationDestination(for: SymbolCandidate.self) { candidate in
                        SymbolDetailView(
                            viewModel: SymbolDetailViewModel(
                                candidate: candidate,
                                service: recognitionService,
                                favouritesRepo: favouritesRepository
                            )
                        )
                    }
            }
            .tabItem { Label(AppTab.home.title, systemImage: selectedTab == .home ? AppTab.home.selectedIcon : AppTab.home.icon) }
            .tag(AppTab.home)

            // Draw
            NavigationStack {
                DrawView(
                    viewModel: DrawViewModel(service: recognitionService),
                    onResultsReady: { response in
                        historyRepository.save(
                            HistoryEntry(
                                topCandidate: response.candidates.first ?? SymbolCandidate.mockCandidates[0],
                                allCandidates: response.candidates
                            )
                        )
                    }
                )
            }
            .tabItem { Label(AppTab.draw.title, systemImage: AppTab.draw.icon) }
            .tag(AppTab.draw)

            // History
            NavigationStack(path: $historyNavPath) {
                HistoryView(viewModel: HistoryViewModel(repository: historyRepository))
                    .navigationDestination(for: HistoryEntry.self) { entry in
                        ResultsView(viewModel: ResultsViewModel(response: RecognitionResponse(
                            requestID: entry.id,
                            candidates: entry.allCandidates,
                            processingTimeMs: nil,
                            modelVersion: nil
                        )))
                    }
            }
            .tabItem { Label(AppTab.history.title, systemImage: selectedTab == .history ? AppTab.history.selectedIcon : AppTab.history.icon) }
            .tag(AppTab.history)

            // Favourites
            NavigationStack(path: $favouritesNavPath) {
                FavouritesView(viewModel: FavouritesViewModel(repository: favouritesRepository))
                    .navigationDestination(for: SymbolDetail.self) { detail in
                        SymbolDetailView(
                            viewModel: SymbolDetailViewModel(
                                preloadedDetail: detail,
                                service: recognitionService,
                                favouritesRepo: favouritesRepository
                            )
                        )
                    }
            }
            .tabItem { Label(AppTab.favourites.title, systemImage: selectedTab == .favourites ? AppTab.favourites.selectedIcon : AppTab.favourites.icon) }
            .tag(AppTab.favourites)

            // Settings
            NavigationStack {
                SettingsView(viewModel: SettingsViewModel())
            }
            .tabItem { Label(AppTab.settings.title, systemImage: selectedTab == .settings ? AppTab.settings.selectedIcon : AppTab.settings.icon) }
            .tag(AppTab.settings)
        }
        .tint(.ontoPrimary_fallback())
        .preferredColorScheme(.dark)
    }
}

// MARK: - Preview

#Preview {
    RootTabView(
        recognitionService: MockRecognitionService.preview,
        historyRepository: UserDefaultsHistoryRepository(),
        favouritesRepository: UserDefaultsFavouritesRepository()
    )
}
