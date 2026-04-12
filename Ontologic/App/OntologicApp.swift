// MARK: - OntologicApp.swift
// Application entry point. Composes the dependency graph and launches
// the root view. All singletons and shared services are created here.

import SwiftUI

@main
struct OntologicApp: App {

    // MARK: Shared services (dependency injection root)

    /// Swap MockRecognitionService → APIRecognitionService to use the live API.
    private let recognitionService: any RecognitionServiceProtocol = MockRecognitionService()
    private let historyRepository  = UserDefaultsHistoryRepository()
    private let favouritesRepository = UserDefaultsFavouritesRepository()

    // MARK: Scene

    var body: some Scene {
        WindowGroup {
            RootTabView(
                recognitionService: recognitionService,
                historyRepository: historyRepository,
                favouritesRepository: favouritesRepository
            )
        }
    }
}
