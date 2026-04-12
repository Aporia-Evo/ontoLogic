// MARK: - HistoryViewModel.swift

import Foundation
import Combine

final class HistoryViewModel: ObservableObject {

    @Published private(set) var entries: [HistoryEntry] = []

    private let repository: UserDefaultsHistoryRepository

    init(repository: UserDefaultsHistoryRepository) {
        self.repository = repository
        reload()
    }

    func reload() {
        entries = repository.fetchSorted()
    }

    func delete(at offsets: IndexSet) {
        for index in offsets {
            repository.delete(id: entries[index].id)
        }
        reload()
    }

    func clearAll() {
        repository.deleteAll()
        reload()
    }
}

// MARK: - Preview helper

extension HistoryViewModel {
    static func preview() -> HistoryViewModel {
        let repo = UserDefaultsHistoryRepository(defaults: UserDefaults(suiteName: "preview")!)
        // Seed mock data
        for entry in HistoryEntry.mockEntries { repo.save(entry) }
        return HistoryViewModel(repository: repo)
    }
}
