// MARK: - HomeViewModel.swift

import Foundation
import Combine

final class HomeViewModel: ObservableObject {

    // MARK: Published state
    @Published var recentEntries: [HistoryEntry] = []
    @Published var featuredSymbol: SymbolDetail? = SymbolDetail.mockOm

    // MARK: Init
    init(historyRepository: UserDefaultsHistoryRepository = .init()) {
        recentEntries = historyRepository.fetchSorted().prefix(3).map { $0 }
    }

    // MARK: Intent
    func refresh(using repository: UserDefaultsHistoryRepository) {
        recentEntries = repository.fetchSorted().prefix(3).map { $0 }
    }
}
