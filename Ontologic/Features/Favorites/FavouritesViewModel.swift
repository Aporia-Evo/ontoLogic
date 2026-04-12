// MARK: - FavouritesViewModel.swift

import Foundation
import Combine

final class FavouritesViewModel: ObservableObject {

    @Published private(set) var items: [SymbolDetail] = []

    private let repository: FavouritesRepositoryProtocol

    init(repository: FavouritesRepositoryProtocol) {
        self.repository = repository
        reload()
    }

    func reload() {
        items = repository.fetchAll()
    }

    func remove(_ detail: SymbolDetail) {
        repository.remove(id: detail.id)
        reload()
    }
}
